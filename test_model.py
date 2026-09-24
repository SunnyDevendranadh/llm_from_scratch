"""
Hard evaluation of TinyClaude2.
Tests: reasoning chains, multi-step math, logic, comparisons, edge cases.

Usage:
    python test_model.py                                    # default checkpoint
    python test_model.py checkpoints/tinyclaude2_best.pt   # specific checkpoint
    python test_model.py --json                             # JSON output
    python test_model.py --interactive                      # manual query mode
"""

import argparse
import json
import sys
from generate import load_model, generate_v3
from config import TinyClaudeConfig

DEFAULT_CHECKPOINT = "checkpoints/tinyclaude2_best.pt"

# Hard test queries grouped by category
TESTS = [
    # --- Reasoning / logic ---
    ("LOGIC-1",  "if all dogs are mammals and all mammals breathe air do dogs breathe air"),
    ("LOGIC-2",  "if it rains the ground gets wet the ground is dry did it rain"),
    ("LOGIC-3",  "a is taller than b and b is taller than c who is the tallest"),
    ("LOGIC-4",  "there are 3 boxes one has a ball you open box 1 it is empty you open box 2 it is empty where is the ball"),

    # --- Multi-step math ---
    ("MATH-1",   "what is 7 times 8"),
    ("MATH-2",   "what is 144 divided by 12"),
    ("MATH-3",   "if a train travels 60 miles per hour for 3 hours how far does it go"),
    ("MATH-4",   "what is 15 percent of 200"),
    ("MATH-5",   "what is 9 plus 13 minus 4"),

    # --- Factual / science ---
    ("SCI-1",    "why does the moon orbit the earth"),
    ("SCI-2",    "what happens to water when it freezes"),
    ("SCI-3",    "why is the sky blue"),
    ("SCI-4",    "what is photosynthesis"),

    # --- Comparison / ranking ---
    ("COMP-1",   "which is larger the pacific ocean or the atlantic ocean"),
    ("COMP-2",   "which is heavier a kilogram of feathers or a kilogram of gold"),
    ("COMP-3",   "is light faster than sound"),

    # --- Instruction following ---
    ("INST-1",   "name three planets in our solar system"),
    ("INST-2",   "give one example of a renewable energy source"),
    ("INST-3",   "define gravity in one sentence"),
    ("INST-4",   "what are the three states of matter"),

    # --- Adversarial / tricky ---
    ("TRICK-1",  "what color is a red apple"),
    ("TRICK-2",  "how many sides does a triangle have"),
    ("TRICK-3",  "if you have 5 apples and give away 5 apples how many do you have"),
    ("TRICK-4",  "can a cat fly"),
]

cfg = TinyClaudeConfig()

def run_tests(checkpoint: str):
    print(f"Loading model from {checkpoint} ...\n")
    model, tokenizer, device = load_model(checkpoint)
    print(f"Device: {device}\n")
    print("=" * 70)

    results = []
    for label, query in TESTS:
        result = generate_v3(
            model, tokenizer, query,
            max_new_tokens=cfg.max_new_tokens,
            temperature=cfg.temperature,
            top_k=cfg.top_k,
            repetition_penalty=cfg.repetition_penalty,
            device=device,
        )
        thinking = result["thinking"] or ""
        answer   = result["answer"]

        print(f"[{label}] Q: {query}")
        if thinking:
            print(f"  THINK: {thinking[:120]}{'...' if len(thinking)>120 else ''}")
        print(f"  ANS:   {answer}")
        print()
        results.append((label, query, thinking, answer))

    # Quick grading: look for obviously correct answers
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    graded = {
        "MATH-1": "56",
        "MATH-2": "12",
        "MATH-3": "180",
        "MATH-4": "30",
        "MATH-5": "18",
        "LOGIC-1": "yes",
        "LOGIC-2": "no",
        "LOGIC-3": "a",
        "TRICK-1": "red",
        "TRICK-2": "3",
        "TRICK-3": "0",
        "COMP-3": "yes",
    }
    correct = 0
    total_graded = len(graded)
    for label, _, _, answer in results:
        if label in graded:
            expected = graded[label]
            hit = expected in answer.lower()
            mark = "PASS" if hit else "FAIL"
            if hit:
                correct += 1
            print(f"  {mark}  [{label}]  expected={expected!r}  got={answer[:60]!r}")

    print(f"\nAuto-graded: {correct}/{total_graded} correct")
    print("\nNote: qualitative answers (SCI-*, COMP-*, INST-*) need manual review.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate TinyClaude2 / NanoCloud on benchmark tests")
    parser.add_argument("checkpoint", nargs="?", default=DEFAULT_CHECKPOINT,
                        help="Path to model checkpoint")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--interactive", action="store_true",
                        help="Interactive manual query mode")
    args = parser.parse_args()

    if args.interactive:
        print(f"Loading model from {args.checkpoint} ...")
        model, tokenizer, device = load_model(args.checkpoint)
        print(f"Model ready on {device}. Type 'quit' to exit.\n")
        while True:
            try:
                query = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break
            if query.lower() in ("quit", "exit"):
                break
            if not query:
                continue
            result = generate_v3(model, tokenizer, query, device=device)
            if result["thinking"]:
                print(f"[Think] {result['thinking'][:150]}")
            print(f"[Answer] {result['answer']}")
            print()
    elif args.json:
        # JSON output mode
        model, tokenizer, device = load_model(args.checkpoint)
        results = []
        for label, query in TESTS:
            result = generate_v3(model, tokenizer, query, device=device)
            results.append({
                "label": label,
                "query": query,
                "thinking": result["thinking"],
                "answer": result["answer"],
            })
        print(json.dumps(results, indent=2))
    else:
        run_tests(args.checkpoint)

