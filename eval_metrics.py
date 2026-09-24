"""Evaluation metrics for LLM training."""
import math
import torch

def compute_perplexity(loss: float) -> float:
    """Convert cross-entropy loss to perplexity."""
    return math.exp(min(loss, 20))

def compute_token_accuracy(logits: torch.Tensor, targets: torch.Tensor, ignore_idx: int = -100) -> float:
    """Token-level top-1 accuracy, ignoring padding."""
    mask = targets != ignore_idx
    if mask.sum() == 0:
        return 0.0
    preds = logits.argmax(dim=-1)
    correct = (preds == targets) & mask
    return correct.sum().item() / mask.sum().item()

def compute_topk_accuracy(logits: torch.Tensor, targets: torch.Tensor, k: int = 5, ignore_idx: int = -100) -> float:
    """Token-level top-k accuracy."""
    mask = targets != ignore_idx
    if mask.sum() == 0:
        return 0.0
    _, topk_preds = logits.topk(k, dim=-1)
    correct = topk_preds.eq(targets.unsqueeze(-1)).any(dim=-1) & mask
    return correct.sum().item() / mask.sum().item()
