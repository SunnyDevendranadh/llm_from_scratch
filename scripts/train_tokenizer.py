"""
Train a NanoCloud BPE tokenizer on Wikipedia + FineWeb-Edu samples.

Usage:
    python scripts/train_tokenizer.py
    python scripts/train_tokenizer.py --tokens 10000000 --vocab 32000
    python scripts/train_tokenizer.py --output checkpoints/nanocloud_tokenizer.json

After training, verify with:
    python -c "
    from tokenizer import NanoCloudTokenizer
    tok = NanoCloudTokenizer.load('checkpoints/nanocloud_tokenizer.json')
    ids = tok.encode('<THINK> test </THINK>')
    print('IDs:', ids)
    assert 4 in ids and 5 in ids, 'THINK tokens missing!'
    print('THINK token check: PASSED')
    "
"""

import argparse
import os
import sys

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer import NanoCloudTokenizer


def text_stream(target_tokens: int):
    """Yield text strings until ~target_tokens tokens have been seen."""
    from datasets import load_dataset

    seen = 0

    # FineWeb-Edu: high-quality educational text
    print("Streaming FineWeb-Edu...")
    fineweb = load_dataset(
        "HuggingFaceFW/fineweb-edu", name="sample-10BT",
        streaming=True, split="train"
    )
    for example in fineweb:
        text = example.get("text", "")
        if not text:
            continue
        yield text
        seen += len(text.split())
        if seen >= target_tokens * 0.6:
            break
    print(f"  FineWeb-Edu: ~{seen:,} tokens seen so far")

    # Wikipedia: factual background
    print("Streaming Wikipedia...")
    wiki = load_dataset(
        "wikimedia/wikipedia", "20231101.en",
        streaming=True, split="train"
    )
    for example in wiki:
        text = example.get("text", "")
        if not text:
            continue
        yield text[:3000]   # clip very long articles
        seen += len(text[:3000].split())
        if seen >= target_tokens:
            break
    print(f"  Wikipedia: ~{seen:,} tokens seen total")


def main():
    parser = argparse.ArgumentParser(description="Train NanoCloud BPE tokenizer")
    parser.add_argument("--tokens", type=int, default=10_000_000,
                        help="Approximate number of tokens to train on (default 10M)")
    parser.add_argument("--vocab", type=int, default=32000,
                        help="BPE vocabulary size (default 32000)")
    parser.add_argument("--output", type=str,
                        default="checkpoints/nanocloud_tokenizer.json",
                        help="Output path for tokenizer JSON")
    args = parser.parse_args()

    print(f"Training BPE tokenizer: vocab={args.vocab}, target={args.tokens:,} tokens")
    print(f"Output: {args.output}\n")

    tokenizer = NanoCloudTokenizer()
    tokenizer.train(text_stream(args.tokens), vocab_size=args.vocab)

    tokenizer.save(args.output)
    print(f"\nSaved tokenizer to: {args.output}")
    print(f"Vocab size: {tokenizer.vocab_size}")

    # Verify special tokens survived
    print("\nVerifying special tokens...")
    test_ids = tokenizer.encode("<THINK> test reasoning </THINK> <ANSWER> result")
    print(f"  encode('<THINK> test </THINK> <ANSWER> result'): {test_ids}")

    ok = True
    for name, expected_id in [("<THINK>", 4), ("</THINK>", 5), ("<ANSWER>", 6)]:
        if expected_id in test_ids:
            print(f"  {name} → id {expected_id}: PASS")
        else:
            print(f"  {name} → id {expected_id}: FAIL (not found in {test_ids})")
            ok = False

    if ok:
        print("\nAll checks passed. Tokenizer is ready for NanoCloud training.")
    else:
        print("\nWARNING: Some special tokens missing — do not proceed with training.")
        sys.exit(1)


if __name__ == "__main__":
    main()
