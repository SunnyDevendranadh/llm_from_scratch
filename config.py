from dataclasses import dataclass, field


def _validate_config(cfg) -> None:
    """Validate config constraints. Raises ValueError on invalid settings."""
    if cfg.vocab_size <= 0:
        raise ValueError(f"vocab_size ({cfg.vocab_size}) must be positive")
    if cfg.embed_dim <= 0:
        raise ValueError(f"embed_dim ({cfg.embed_dim}) must be positive")
    if cfg.num_heads <= 0:
        raise ValueError(f"num_heads ({cfg.num_heads}) must be positive")
    if cfg.embed_dim % cfg.num_heads != 0:
        raise ValueError(
            f"embed_dim ({cfg.embed_dim}) must be divisible by "
            f"num_heads ({cfg.num_heads})"
        )
    if cfg.ff_dim <= 0:
        raise ValueError(f"ff_dim ({cfg.ff_dim}) must be positive")
    if cfg.num_layers <= 0:
        raise ValueError(f"num_layers ({cfg.num_layers}) must be positive")
    if cfg.max_seq_len < 16:
        raise ValueError(f"max_seq_len ({cfg.max_seq_len}) must be >= 16")


@dataclass
class NanoCloudConfig:
    """~138M parameter model config for GPU training (RTX 5090 / vast.ai)."""

    # Model architecture
    vocab_size: int = 32000
    embed_dim: int = 768
    num_heads: int = 12         # head_dim = 768/12 = 64
    num_layers: int = 12
    ff_dim: int = 3072          # SwiGLU hidden dim
    max_seq_len: int = 1024
    dropout: float = 0.1

    # Training
    batch_size: int = 32
    grad_accum_steps: int = 8   # effective batch = 256
    learning_rate: float = 3e-4
    min_lr: float = 3e-5        # cosine decay floor
    weight_decay: float = 0.1
    label_smoothing: float = 0.1
    warmup_steps: int = 500
    max_train_steps: int = 76294  # ~20B tokens at batch=32, seq=1024, accum=8
    checkpoint_every: int = 2000

    # Generation
    temperature: float = 0.7
    top_k: int = 50
    repetition_penalty: float = 1.2
    max_new_tokens: int = 200

    def __post_init__(self):
        _validate_config(self)


@dataclass
class TinyClaudeConfig:
    # Model architecture
    vocab_size: int = 8000
    embed_dim: int = 384
    num_heads: int = 6          # head_dim = 384/6 = 64
    num_layers: int = 8
    ff_dim: int = 1024          # SwiGLU hidden dim
    max_seq_len: int = 512
    dropout: float = 0.1

    # Training
    batch_size: int = 16
    grad_accum_steps: int = 4   # effective batch = 64
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    label_smoothing: float = 0.1
    warmup_pct: float = 0.05
    phase1_epochs: int = 64
    phase2_epochs: int = 16
    phase2_lr: float = 1e-4

    # Generation
    temperature: float = 0.7
    top_k: int = 30
    repetition_penalty: float = 1.2
    max_new_tokens: int = 120

    def __post_init__(self):
        _validate_config(self)



# Phase 1: general pretraining on Wikipedia + reasoning; Phase 2: reasoning-only fine-tuning
