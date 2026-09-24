def make_math_examples():
    examples = []

    # Addition (1-19 × 1-19)
    for a in range(1, 20):
        for b in range(1, 20):
            c = a + b
            examples.append(
                f"what is {a} plus {b} "
                f"<THINK> the user wants addition {a} plus {b} equals {c} </THINK> "
                f"<ANSWER> the answer is {c}"
            )

    # Subtraction (positive results)
    for a in range(2, 20):
        for b in range(1, a):
            c = a - b
            examples.append(
                f"what is {a} minus {b} "
                f"<THINK> the user wants subtraction {a} minus {b} equals {c} </THINK> "
                f"<ANSWER> the answer is {c}"
            )

    # Multiplication (2-9 × 2-9)
    for a in range(2, 10):
        for b in range(2, 10):
            c = a * b
            examples.append(
                f"what is {a} times {b} "
                f"<THINK> the user wants multiplication {a} times {b} equals {c} </THINK> "
                f"<ANSWER> the answer is {c}"
            )

    # Division (whole-number results only)
    for a in range(2, 15):
        for b in range(2, 15):
            c = a * b  # guarantee whole-number result
            examples.append(
                f"what is {c} divided by {a} "
                f"<THINK> the user wants division {c} divided by {a} equals {b} </THINK> "
                f"<ANSWER> the answer is {b}"
            )

    # Larger addition (20-50 step 5)
    for a in range(20, 51, 5):
        for b in range(20, 51, 5):
            c = a + b
            examples.append(
                f"what is {a} plus {b} "
                f"<THINK> the user wants addition {a} plus {b} equals {c} </THINK> "
                f"<ANSWER> the answer is {c}"
            )

    # Larger subtraction (positive)
    for a in range(25, 51, 5):
        for b in range(5, a, 5):
            c = a - b
            examples.append(
                f"what is {a} minus {b} "
                f"<THINK> the user wants subtraction {a} minus {b} equals {c} </THINK> "
                f"<ANSWER> the answer is {c}"
            )

    # Squares (2-20)
    for n in range(2, 21):
        c = n * n
        examples.append(
            f"what is {n} squared "
            f"<THINK> the user wants to square {n} which means {n} times {n} equals {c} </THINK> "
            f"<ANSWER> the answer is {c}"
        )

    # Simple percentages (10%, 25%, 50%)
    for pct, pct_word in [(10, "ten"), (25, "twenty five"), (50, "fifty")]:
        for base in [100, 200, 400, 50, 80, 60, 40, 20]:
            result = base * pct // 100
            examples.append(
                f"what is {pct_word} percent of {base} "
                f"<THINK> percent means per hundred "
                f"{pct} percent of {base} equals {base} times {pct} divided by 100 equals {result} </THINK> "
                f"<ANSWER> {pct_word} percent of {base} is {result}"
            )

    # Extended percentages (5%, 15%, 20%, 30%, 40%, 75%)
    for pct, pct_word in [(5, "five"), (15, "fifteen"), (20, "twenty"), (30, "thirty"), (40, "forty"), (75, "seventy five")]:
        for base in [100, 200, 400, 50, 80, 60, 40, 20]:
            result = base * pct // 100
            examples.append(
                f"what is {pct_word} percent of {base} "
                f"<THINK> percent means per hundred "
                f"{pct} percent of {base} equals {base} times {pct} divided by 100 equals {result} </THINK> "
                f"<ANSWER> {pct_word} percent of {base} is {result}"
            )

    # Chained operations (a+b-c)
    for a in range(5, 20):
        for b in range(1, 10):
            for c in range(1, b + 1):
                result = a + b - c
                examples.append(
                    f"what is {a} plus {b} minus {c} "
                    f"<THINK> the user wants chained operations {a} plus {b} equals {a+b} then {a+b} minus {c} equals {result} </THINK> "
                    f"<ANSWER> the answer is {result}"
                )

    return examples
