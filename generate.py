"""
TinyClaude2 generation with KV-cache, repetition penalty, and SmartMemory.
"""

import torch
import torch.nn.functional as F

from config import TinyClaudeConfig, NanoCloudConfig
from model import TinyClaude2
from tokenizer import TinyClaudeTokenizer2, NanoCloudTokenizer


def _get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _parse_response(text: str) -> dict:
    """Split output into thinking / answer sections."""
    thinking = None
    answer   = text

    if "<THINK>" in text and "</THINK>" in text:
        t_start = text.find("<THINK>") + len("<THINK>")
        t_end   = text.find("</THINK>")
        thinking = text[t_start:t_end].strip()
        remainder = text[t_end + len("</THINK>"):].strip()

        if "<ANSWER>" in remainder:
            answer = remainder.split("<ANSWER>", 1)[1].strip()
        else:
            answer = remainder
    elif "<ANSWER>" in text:
        answer = text.split("<ANSWER>", 1)[1].strip()

    return {"thinking": thinking, "answer": answer, "full": text}


@torch.no_grad()
def generate_v3(model, tokenizer, prompt: str,
                max_new_tokens: int = 120,
                temperature: float = 0.7,
                top_k: int = 30,
                repetition_penalty: float = 1.2,
                device=None) -> dict:
    """
    Generate text with KV-cache for fast incremental decoding.
    Returns dict with keys: thinking, answer, full.
    """
    if device is None:
        device = _get_device()

    model.eval()

    input_ids = tokenizer.encode(prompt, add_special_tokens=True)
    input_ids = input_ids[:-1]   # strip EOS — we generate until model outputs EOS
    prompt_len = len(input_ids)
    generated  = list(input_ids)

    # Full-prompt forward pass to fill KV-cache
    inp = torch.tensor([input_ids], device=device)
    _, past_kvs = model(inp)

    eos_id = tokenizer.word_to_id.get("<EOS>", 3)

    for _ in range(max_new_tokens):
        # KV-cache: only feed the last token
        inp = torch.tensor([[generated[-1]]], device=device)
        logits, past_kvs = model(inp, past_kvs=past_kvs)
        next_logits = logits[0, -1, :].float()  # [vocab_size]

        # Repetition penalty on recent tokens
        recent = set(generated[-50:])
        for tid in recent:
            if next_logits[tid] > 0:
                next_logits[tid] /= repetition_penalty
            else:
                next_logits[tid] *= repetition_penalty

        # Temperature + top-k sampling
        k = min(top_k, tokenizer.vocab_size)
        top_vals, top_idx = torch.topk(next_logits / temperature, k)
        probs = F.softmax(top_vals, dim=-1)
        next_tok = top_idx[torch.multinomial(probs, 1)].item()

        if next_tok == eos_id:
            break

        generated.append(next_tok)

    new_tokens = generated[prompt_len:]
    text = tokenizer.decode(new_tokens)
    return _parse_response(text)


class SmartMemory:
    """Simple single-turn memory for multi-turn chat."""

    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.history   = []   # list of (question, short_answer)

    def add(self, question: str, answer: str):
        # Strip <ANSWER> prefix if present, keep ≤15 words
        clean = answer.split("<ANSWER>")[-1].strip()
        short = " ".join(clean.split()[:15])
        self.history.append((question, short))
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]

    def get_prompt(self, question: str) -> str:
        if not self.history:
            return question
        # Only use LAST turn — more context confuses small models
        _, last_a = self.history[-1]
        return f"previously {last_a} now {question}"

    def clear(self):
        self.history = []


# ---------------------------------------------------------------------------
# Load helpers
# ---------------------------------------------------------------------------
def load_model(checkpoint_path: str, device=None):
    """
    Load a saved model from checkpoint.
    Handles both TinyClaude2 (word-level) and NanoCloud (BPE) checkpoints.
    """
    if device is None:
        device = _get_device()

    ckpt = torch.load(checkpoint_path, map_location=device)
    cfg_dict = ckpt["config"]
    model_class = cfg_dict.get("model_class", "TinyClaude2")

    if model_class == "NanoCloud":
        # Try stored absolute path first; fall back to sibling file next to checkpoint.
        # Fallback handles the case where the checkpoint was copied to a different machine.
        stored = ckpt.get("tokenizer_path", "")
        import os as _os
        stem = checkpoint_path.replace(".pt", "_tokenizer.json")
        tok_path = stored if _os.path.exists(stored) else stem
        tokenizer = NanoCloudTokenizer.load(tok_path)
    else:
        tokenizer = TinyClaudeTokenizer2()
        tokenizer.word_to_id = ckpt["tokenizer_word_to_id"]
        tokenizer.id_to_word = ckpt["tokenizer_id_to_word"]
        tokenizer.vocab_size = ckpt["vocab_size"]

    model = TinyClaude2(
        vocab_size  = tokenizer.vocab_size,
        embed_dim   = cfg_dict["embed_dim"],
        num_heads   = cfg_dict["num_heads"],
        num_layers  = cfg_dict["num_layers"],
        ff_dim      = cfg_dict["ff_dim"],
        max_seq_len = cfg_dict["max_seq_len"],
    ).to(device)

    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    return model, tokenizer, device


def model_summary(checkpoint_path: str) -> dict:
    """
    Print a human-readable summary of a saved model checkpoint.
    Returns dict with parameter counts per component.
    """
    ckpt = torch.load(checkpoint_path, map_location="cpu")
    cfg_dict = ckpt["config"]
    model_class = cfg_dict.get("model_class", "TinyClaude2")

    state = ckpt["model_state_dict"]
    total = sum(p.numel() for p in state.values())

    # Count parameters by component type
    embedding_params = 0
    attention_params = 0
    ffn_params = 0
    norm_params = 0
    output_params = 0

    for name, param in state.items():
        n = param.numel()
        if "embedding" in name:
            embedding_params += n
        elif "attention" in name or "query" in name or "key" in name or "value" in name:
            attention_params += n
        elif "ffn" in name:
            ffn_params += n
        elif "norm" in name:
            norm_params += n
        elif "output" in name:
            output_params += n

    info = {
        "model_class": model_class,
        "total_params": total,
        "embed_dim": cfg_dict["embed_dim"],
        "num_heads": cfg_dict["num_heads"],
        "num_layers": cfg_dict["num_layers"],
        "ff_dim": cfg_dict["ff_dim"],
        "max_seq_len": cfg_dict["max_seq_len"],
        "vocab_size": ckpt.get("vocab_size", "?"),
        "breakdown": {
            "embedding": embedding_params,
            "attention": attention_params,
            "ffn": ffn_params,
            "norm": norm_params,
            "output": output_params,
        },
    }

    # Pretty print
    print(f"\n{'='*55}")
    print(f"  Model Summary: {model_class}")
    print(f"{'='*55}")
    print(f"  Architecture:  {cfg_dict['num_layers']} layers, "
          f"{cfg_dict['embed_dim']}d embed, {cfg_dict['num_heads']} heads")
    print(f"  FFN hidden:    {cfg_dict['ff_dim']}")
    print(f"  Max seq len:   {cfg_dict['max_seq_len']}")
    print(f"  Vocab size:    {info['vocab_size']}")
    print(f"  Total params:  {total:,}")
    print(f"  Breakdown:")
    print(f"    Embedding:    {embedding_params:>10,}  ({embedding_params/total*100:5.1f}%)")
    print(f"    Attention:    {attention_params:>10,}  ({attention_params/total*100:5.1f}%)")
    print(f"    FFN (SwiGLU): {ffn_params:>10,}  ({ffn_params/total*100:5.1f}%)")
    print(f"    LayerNorm:    {norm_params:>10,}  ({norm_params/total*100:5.1f}%)")
    print(f"    Output head:  {output_params:>10,}  ({output_params/total*100:5.1f}%)")
    print(f"{'='*55}\n")

    return info



# KV-cache: avoids recomputing attention for all previous tokens during autoregressive generation

# Repetition penalty: applied to logits of recently generated tokens to reduce loops
