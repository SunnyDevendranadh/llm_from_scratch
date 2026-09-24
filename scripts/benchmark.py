"""
Throughput benchmark for NanoCloud on GPU (run on vast.ai before full training).

Usage:
    python scripts/benchmark.py
    python scripts/benchmark.py --batch 32 --seq 1024 --steps 100

Expected output on RTX 5090 (bfloat16 + compile):
    Throughput: ~100,000+ tok/sec
    20B tokens: ~55h @ ~$22

If throughput < 60,000 tok/sec, check:
  - torch.compile is active (--no-compile to test without)
  - FlashAttention-2 dispatching (pip show flash-attn)
  - bfloat16 is actually running (check dtype output)
"""

import argparse
import os
import sys
import time

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import NanoCloudConfig
from model import TinyClaude2


def main():
    parser = argparse.ArgumentParser(description="NanoCloud throughput benchmark")
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--seq", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--no-compile", action="store_true",
                        help="Disable torch.compile (for comparison)")
    args = parser.parse_args()

    if not torch.cuda.is_available():
        print("ERROR: No CUDA device found. This benchmark requires a GPU.")
        sys.exit(1)

    device = torch.device("cuda")
    cfg = NanoCloudConfig()

    print(f"NanoCloud benchmark")
    print(f"  Model: embed={cfg.embed_dim} heads={cfg.num_heads} "
          f"layers={cfg.num_layers} ff={cfg.ff_dim}")
    print(f"  Batch={args.batch}, seq={args.seq}, steps={args.steps}")
    print(f"  torch.compile: {'disabled' if args.no_compile else 'enabled'}")
    print()

    model = TinyClaude2(
        vocab_size  = cfg.vocab_size,
        embed_dim   = cfg.embed_dim,
        num_heads   = cfg.num_heads,
        num_layers  = cfg.num_layers,
        ff_dim      = cfg.ff_dim,
        max_seq_len = cfg.max_seq_len,
        dropout     = 0.0,   # no dropout for benchmarking
    ).cuda()

    print(f"  Parameters: {model.count_params():,}")

    if not args.no_compile:
        print("  Compiling model (first call will be slow)...")
        model = torch.compile(model)

    x = torch.randint(0, cfg.vocab_size, (args.batch, args.seq), device=device)

    # Verify bfloat16 is active
    print("\nVerifying bfloat16...")
    with torch.autocast("cuda", dtype=torch.bfloat16):
        test_out, _ = model(x[:2, :64])
    print(f"  Output dtype: {test_out.dtype}  (should be torch.bfloat16)")

    # Warmup (triggers torch.compile compilation)
    print("\nWarmup (10 steps)...")
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        for _ in range(10):
            logits, _ = model(x)
    torch.cuda.synchronize()

    # Benchmark
    print(f"Benchmarking {args.steps} steps...")
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        start = time.time()
        for _ in range(args.steps):
            logits, _ = model(x)
        torch.cuda.synchronize()
        elapsed = time.time() - start

    tok_per_sec = (args.steps * args.batch * args.seq) / elapsed

    # Budget estimates (vast.ai RTX 5090 ~$0.405/hr)
    cost_per_hr = 0.405
    hours_10b  = (10e9 / tok_per_sec) / 3600
    hours_20b  = (20e9 / tok_per_sec) / 3600

    print(f"\nResults:")
    print(f"  Throughput    : {tok_per_sec:>12,.0f} tok/sec")
    print(f"  10B tokens    : {hours_10b:>6.1f}h  (${hours_10b * cost_per_hr:.2f})")
    print(f"  20B tokens    : {hours_20b:>6.1f}h  (${hours_20b * cost_per_hr:.2f})")

    if tok_per_sec < 60_000:
        print("\nWARNING: Throughput below 60k tok/sec — something may be wrong.")
        print("  - Check: pip show flash-attn")
        print("  - Check: torch.compile is not disabled")
        print("  - Check: bfloat16 dtype above says torch.bfloat16")
    else:
        print(f"\nThroughput looks good. Recommended: aim for 20B tokens.")

    # Token math verification
    max_steps = cfg.max_train_steps
    batch_tokens = cfg.batch_size * cfg.max_seq_len * cfg.grad_accum_steps
    total_tokens = max_steps * batch_tokens
    print(f"\nToken math check:")
    print(f"  max_train_steps={max_steps} × batch_tokens={batch_tokens:,} "
          f"= {total_tokens/1e9:.1f}B tokens")


if __name__ == "__main__":
    main()
