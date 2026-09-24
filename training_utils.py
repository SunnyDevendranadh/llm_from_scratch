"""
Training utilities: logging, checkpoint management, and progress tracking.
"""
import json
import os
import time
from typing import Optional

class TrainingLogger:
    """CSV-based training metric logger with optional JSON summary export."""

    def __init__(self, log_dir: str = "logs"):
        os.makedirs(log_dir, exist_ok=True)
        self.csv_path = os.path.join(log_dir, "metrics.csv")
        self.json_path = os.path.join(log_dir, "summary.json")
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w") as f:
                f.write("step,loss,ppl,lr,grad_norm,tokens_per_sec,epoch\n")

    def log(self, step: int, loss: float, ppl: float, lr: float,
            grad_norm: float, tokens_per_sec: float, epoch: Optional[int] = None):
        with open(self.csv_path, "a") as f:
            f.write(f"{step},{loss:.4f},{ppl:.2f},{lr:.6f},{grad_norm:.3f},{tokens_per_sec:.0f},{epoch or ''}\n")

    def save_summary(self, total_steps: int, best_loss: float, wall_time: float):
        summary = {
            "total_steps": total_steps,
            "best_loss": best_loss,
            "wall_time_seconds": wall_time,
            "wall_time_hours": wall_time / 3600,
        }
        with open(self.json_path, "w") as f:
            json.dump(summary, f, indent=2)
