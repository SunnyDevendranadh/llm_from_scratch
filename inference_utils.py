"""
Inference utilities: batch generation, streaming, and response parsing.
"""
from typing import List, Optional
import torch

def batch_generate(model, tokenizer, prompts: List[str],
                   max_new_tokens: int = 120, temperature: float = 0.7,
                   top_k: int = 30, device=None) -> List[dict]:
    """Generate responses for multiple prompts in a batch."""
    results = []
    model.eval()
    for prompt in prompts:
        input_ids = tokenizer.encode(prompt, add_special_tokens=True)
        inp = torch.tensor([input_ids], device=device or "cpu")
        with torch.no_grad():
            logits, _ = model(inp)
        next_token = logits[0, -1].argmax().item()
        results.append({
            "prompt": prompt,
            "next_token_id": next_token,
            "next_token": tokenizer.id_to_word.get(next_token, "<UNK>"),
        })
    return results

def strip_special_tokens(text: str) -> str:
    """Remove THINK/ANSWER tags from generated text for display."""
    for tag in ["<THINK>", "</THINK>", "<ANSWER>"]:
        text = text.replace(tag, "")
    return text.strip()
