import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.functional import scaled_dot_product_attention
import math


class RoPEEmbedding:
    """Rotary Position Embedding — applied to Q and K in attention."""

    def __init__(self, head_dim: int, max_seq_len: int, theta: float = 10000.0):
        freqs = 1.0 / (theta ** (torch.arange(0, head_dim, 2).float() / head_dim))
        t = torch.arange(max_seq_len).float()
        freqs = torch.outer(t, freqs)          # [max_seq_len, head_dim/2]
        self.cos = torch.cos(freqs)            # [max_seq_len, head_dim/2]
        self.sin = torch.sin(freqs)

    def apply(self, x: torch.Tensor, seq_start: int = 0) -> torch.Tensor:
        """
        x: [B, heads, T, head_dim]
        Returns x with RoPE applied.
        """
        T = x.shape[2]
        cos = self.cos[seq_start:seq_start + T].to(x.device)   # [T, head_dim/2]
        sin = self.sin[seq_start:seq_start + T].to(x.device)
        # Reshape for broadcasting: [1, 1, T, head_dim/2]
        cos = cos.unsqueeze(0).unsqueeze(0)
        sin = sin.unsqueeze(0).unsqueeze(0)

        x_r = x[..., ::2]   # even indices
        x_i = x[..., 1::2]  # odd indices
        # Rotate: [x_r, x_i] → [x_r*cos - x_i*sin, x_r*sin + x_i*cos]
        x_rotated = torch.stack(
            [x_r * cos - x_i * sin,
             x_r * sin + x_i * cos],
            dim=-1
        )
        return x_rotated.flatten(-2)  # [B, heads, T, head_dim]


class SwiGLUFFN(nn.Module):
    """SwiGLU feed-forward: better than GELU FFN with same parameter count."""

    def __init__(self, embed_dim: int, ff_dim: int, dropout: float = 0.1):
        super().__init__()
        self.gate_proj = nn.Linear(embed_dim, ff_dim, bias=False)
        self.up_proj   = nn.Linear(embed_dim, ff_dim, bias=False)
        self.down_proj = nn.Linear(ff_dim, embed_dim, bias=False)
        self.dropout   = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x)))


class TinyClaude2Attention(nn.Module):
    """Multi-head self-attention with RoPE and optional KV-cache."""

    def __init__(self, embed_dim: int, num_heads: int, max_seq_len: int,
                 dropout: float = 0.1):
        super().__init__()
        assert embed_dim % num_heads == 0

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim  = embed_dim // num_heads

        self.query      = nn.Linear(embed_dim, embed_dim, bias=False)
        self.key        = nn.Linear(embed_dim, embed_dim, bias=False)
        self.value      = nn.Linear(embed_dim, embed_dim, bias=False)
        self.output_proj = nn.Linear(embed_dim, embed_dim, bias=False)
        self.dropout    = nn.Dropout(dropout)

        self.rope = RoPEEmbedding(self.head_dim, max_seq_len)

    def forward(self, x: torch.Tensor, past_kv=None):
        """
        x:       [B, T, embed_dim]
        past_kv: tuple (K_past, V_past) each [B, heads, T_past, head_dim], or None
        Returns: (output [B, T, embed_dim], present_kv (K, V))
        """
        B, T, _ = x.shape

        Q = self.query(x).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.key(x).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.value(x).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)

        # Determine positional offset for RoPE (KV-cache case)
        seq_start = 0 if past_kv is None else past_kv[0].shape[2]

        # Apply RoPE to Q and K (not V)
        Q = self.rope.apply(Q, seq_start=seq_start)
        K = self.rope.apply(K, seq_start=seq_start)

        # Append past KV if using cache
        if past_kv is not None:
            K = torch.cat([past_kv[0], K], dim=2)  # [B, heads, T_past+T, head_dim]
            V = torch.cat([past_kv[1], V], dim=2)

        present_kv = (K, V)

        # is_causal=True during training (Q and K same length, no past cache).
        # is_causal=False during KV-cache generation (Q is 1 token, K is longer).
        # PyTorch 2.6+ dispatches to FlashAttention-2 on CUDA automatically.
        is_causal_pass = (Q.size(2) == K.size(2))
        dropout_p = self.dropout.p if self.training else 0.0
        out = scaled_dot_product_attention(Q, K, V,
                                           is_causal=is_causal_pass,
                                           dropout_p=dropout_p)

        out = out.transpose(1, 2).contiguous().view(B, T, self.embed_dim)
        out = self.output_proj(out)

        return out, present_kv


class TinyClaude2Block(nn.Module):
    """Pre-norm transformer block with SwiGLU FFN and RoPE attention."""

    def __init__(self, embed_dim: int, num_heads: int, ff_dim: int,
                 max_seq_len: int, dropout: float = 0.1):
        super().__init__()
        self.norm1     = nn.LayerNorm(embed_dim)
        self.attention = TinyClaude2Attention(embed_dim, num_heads, max_seq_len, dropout)
        self.norm2     = nn.LayerNorm(embed_dim)
        self.ffn       = SwiGLUFFN(embed_dim, ff_dim, dropout)
        self.dropout   = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, past_kv=None):
        """Returns (x, present_kv)."""
        attn_out, present_kv = self.attention(self.norm1(x), past_kv=past_kv)
        x = x + self.dropout(attn_out)
        x = x + self.ffn(self.norm2(x))
        return x, present_kv


class TinyClaude2(nn.Module):
    """
    ~17M parameter transformer with RoPE + SwiGLU + KV-cache.
    Architecture: embed → 8× Block → LayerNorm → head
    """

    def __init__(self, vocab_size: int, embed_dim: int = 384, num_heads: int = 6,
                 num_layers: int = 8, ff_dim: int = 1024, max_seq_len: int = 512,
                 dropout: float = 0.1):
        super().__init__()
        self.max_seq_len = max_seq_len

        # Word embedding only — RoPE handles position
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.emb_drop  = nn.Dropout(dropout)

        self.blocks = nn.ModuleList([
            TinyClaude2Block(embed_dim, num_heads, ff_dim, max_seq_len, dropout)
            for _ in range(num_layers)
        ])

        self.final_norm = nn.LayerNorm(embed_dim)
        self.output_head = nn.Linear(embed_dim, vocab_size, bias=False)

        # Weight tying (must come BEFORE apply(_init_weights))
        self.output_head.weight = self.embedding.weight

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, token_ids: torch.Tensor, past_kvs=None):
        """
        token_ids: [B, T]
        past_kvs:  list of (K, V) per layer, or None
        Returns:   (logits [B, T, vocab_size], present_kvs list)
        """
        x = self.emb_drop(self.embedding(token_ids))

        present_kvs = []
        for i, block in enumerate(self.blocks):
            pkv = past_kvs[i] if past_kvs is not None else None
            x, pv = block(x, past_kv=pkv)
            present_kvs.append(pv)

        x = self.final_norm(x)
        logits = self.output_head(x)
        return logits, present_kvs

    def count_params(self) -> int:
        return sum(p.numel() for p in self.parameters())





# RoPE: precompute cos/sin tensors for efficiency during inference

# Usage: model.forward(token_ids) for training, model.generate(prompt) for inference

# Weight tying between embedding and output_head reduces params by vocab_size * embed_dim
