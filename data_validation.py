"""Data validation utilities for training data quality checks."""
from typing import List

def validate_example(text: str, min_words: int = 5, max_words: int = 2000) -> bool:
    """Check if a training example meets quality thresholds."""
    words = text.split()
    if len(words) < min_words:
        return False
    if len(words) > max_words:
        return False
    if text.count('<THINK>') != text.count('</THINK>'):
        return False
    return True

def filter_examples(texts: List[str], min_words: int = 5) -> List[str]:
    """Filter training data for quality."""
    return [t for t in texts if validate_example(t, min_words=min_words)]

def compute_data_stats(texts: List[str]) -> dict:
    """Compute summary statistics for a dataset."""
    lengths = [len(t.split()) for t in texts]
    return {
        "count": len(texts),
        "min_words": min(lengths) if lengths else 0,
        "max_words": max(lengths) if lengths else 0,
        "avg_words": sum(lengths) / len(lengths) if lengths else 0,
        "total_words": sum(lengths),
    }
