"""
TinyClaude2 / NanoCloud CLI entry point.

Usage:
    python run.py train                                 # full TinyClaude2 training
    python run.py train --phase1-epochs 5               # smoke test
    python run.py train --resume checkpoints/tinyclaude2_phase1.pt
    python run.py nanocloud                             # NanoCloud GPU training
    python run.py nanocloud --max-steps 10000            # custom step count
    python run.py chat                                  # interactive chat
    python run.py chat --checkpoint checkpoints/tinyclaude2_best.pt
"""

import argparse
import sys


def run_train(args):
    import subprocess
    cmd = [sys.executable, "train.py"]
    if args.phase1_epochs is not None:
        cmd += ["--phase1-epochs", str(args.phase1_epochs)]
    if args.phase2_epochs is not None:
        cmd += ["--phase2-epochs", str(args.phase2_epochs)]
    if args.wiki_articles is not None:
        cmd += ["--wiki-articles", str(args.wiki_articles)]
    if args.resume:
        cmd += ["--resume", args.resume]
    import os
    os.execv(sys.executable, cmd)


def run_nanocloud(args):
    """Launch NanoCloud GPU training via train.py --nanocloud."""
    import subprocess
    cmd = [sys.executable, "train.py", "--nanocloud"]
    if args.max_steps is not None:
        cmd += ["--max-steps", str(args.max_steps)]
    if args.checkpoint_every is not None:
        cmd += ["--checkpoint-every", str(args.checkpoint_every)]
    if args.resume:
        cmd += ["--resume", args.resume]
    if args.hf_repo:
        cmd += ["--hf-repo", args.hf_repo]
    if args.tokenizer_path:
        cmd += ["--tokenizer-path", args.tokenizer_path]
    import os
    os.execv(sys.executable, cmd)


def run_summary(args):
    """Print model architecture and parameter summary."""
    from generate import model_summary
    checkpoint = args.checkpoint or "checkpoints/tinyclaude2_best.pt"
    model_summary(checkpoint)


def run_chat(args):
    from generate import load_model, generate_v3, SmartMemory
    from config import TinyClaudeConfig

    cfg = TinyClaudeConfig()
    checkpoint = args.checkpoint or "checkpoints/tinyclaude2_best.pt"

    print(f"Loading model from {checkpoint}...")
    model, tokenizer, device = load_model(checkpoint)
    print(f"Model ready on {device}. Type 'quit' to exit, 'clear' to reset memory.\n")

    memory = SmartMemory(max_turns=3)
    use_memory = True

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            print("Bye!")
            break
        if question.lower() == "clear":
            memory.clear()
            print("Memory cleared.")
            continue
        if question.lower() == "nomemory":
            use_memory = False
            print("Memory disabled for next response.")
            continue

        prompt = memory.get_prompt(question) if use_memory else question

        result = generate_v3(
            model, tokenizer, prompt,
            max_new_tokens=cfg.max_new_tokens,
            temperature=cfg.temperature,
            top_k=cfg.top_k,
            repetition_penalty=cfg.repetition_penalty,
            device=device,
        )

        if result["thinking"]:
            print(f"[Thinking] {result['thinking']}")
        print(f"TinyClaude: {result['answer']}\n")

        memory.add(question, result["answer"])
        use_memory = True


def main():
    parser = argparse.ArgumentParser(
        description="TinyClaude2 / NanoCloud — from-scratch LLM training and inference")
    sub = parser.add_subparsers(dest="command")

    # train
    train_p = sub.add_parser("train", help="TinyClaude2 local training (epoch-based)")
    train_p.add_argument("--phase1-epochs", type=int, default=None)
    train_p.add_argument("--phase2-epochs", type=int, default=None)
    train_p.add_argument("--wiki-articles", type=int, default=None)
    train_p.add_argument("--resume", type=str, default=None)

    # nanocloud
    nc_p = sub.add_parser("nanocloud", help="NanoCloud GPU training (step-based, streaming)")
    nc_p.add_argument("--max-steps", type=int, default=None)
    nc_p.add_argument("--checkpoint-every", type=int, default=None)
    nc_p.add_argument("--resume", type=str, default=None)
    nc_p.add_argument("--hf-repo", type=str, default=None)
    nc_p.add_argument("--tokenizer-path", type=str, default=None)

    # summary
    sum_p = sub.add_parser("summary", help="Print model architecture and parameter breakdown")
    sum_p.add_argument("checkpoint", nargs="?", default=None,
                       help="Path to model checkpoint")

    # chat
    chat_p = sub.add_parser("chat", help="Interactive chat with a trained model")
    chat_p.add_argument("--checkpoint", type=str, default=None)

    args = parser.parse_args()

    if args.command == "train":
        run_train(args)
    elif args.command == "nanocloud":
        run_nanocloud(args)
    elif args.command == "summary":
        run_summary(args)
    elif args.command == "chat":
        run_chat(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

