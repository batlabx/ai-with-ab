"""
questions.py — the trustworthy math engine.

Generates multiple-choice questions for Algebra and Coordinate Geometry,
tuned for Grades 4-8, across three difficulty tiers (1=easy, 2=medium, 3=hard).

Every question is built in pure Python so the *answer is always correct* — the
local LLM is only ever used to reword, never to compute. Each generator returns:

    {
      "topic":   "Algebra" | "Coordinate Geometry",
      "tier":    1 | 2 | 3,
      "question": "....",
      "choices":  ["A", "B", "C", "D"],   # shuffled
      "answer":   "the correct choice string",
    }
"""

import random


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def _mc(correct, distractors):
    """Build a shuffled 4-option multiple-choice block from a correct answer
    and a list of (at least 3) distractor values. All cast to str."""
    opts = [str(correct)]
    seen = {str(correct)}
    for d in distractors:
        s = str(d)
        if s not in seen:
            opts.append(s)
            seen.add(s)
        if len(opts) == 4:
            break
    # pad if we somehow lack uniques
    n = 1
    while len(opts) < 4:
        cand = str(correct) + " " * n  # never matches; safety only
        if cand not in seen:
            opts.append(cand)
            seen.add(cand)
        n += 1
    random.shuffle(opts)
    return opts, str(correct)


def _near(value, spread=3):
    """A few plausible wrong numbers near `value`."""
    out = set()
    while len(out) < 5:
        delta = random.randint(-spread, spread)
        if delta != 0:
            out.add(value + delta)
    return list(out)


# ----------------------------------------------------------------------
# ALGEBRA
# ----------------------------------------------------------------------
def algebra(tier):
    if tier == 1:
        # missing-number / one-step addition or multiplication
        kind = random.choice(["add", "mult"])
        if kind == "add":
            a = random.randint(2, 20)
            ans = random.randint(2, 20)
            total = a + ans
            q = f"What number goes in the box?   {a} + □ = {total}"
        else:
            a = random.randint(2, 9)
            ans = random.randint(2, 9)
            prod = a * ans
            q = f"What number goes in the box?   {a} × □ = {prod}"
        choices, correct = _mc(ans, _near(ans))
        return _pack("Algebra", tier, q, choices, correct)

    if tier == 2:
        # one-step / two-step linear equation, positive solution
        x = random.randint(2, 12)
        a = random.randint(2, 6)
        b = random.randint(1, 15)
        if random.random() < 0.5:
            c = a * x + b
            q = f"Solve for x:   {a}x + {b} = {c}"
        else:
            c = a * x - b
            q = f"Solve for x:   {a}x - {b} = {c}"
        choices, correct = _mc(x, _near(x))
        return _pack("Algebra", tier, q, choices, correct)

    # tier 3: two-step with negatives or evaluate / distributive
    style = random.choice(["neg", "eval", "dist"])
    if style == "neg":
        x = random.randint(-8, 8)
        a = random.randint(2, 6)
        b = random.randint(-10, 10)
        c = a * x + b
        q = f"Solve for x:   {a}x + ({b}) = {c}"
        choices, correct = _mc(x, _near(x, 4))
        return _pack("Algebra", tier, q, choices, correct)
    if style == "eval":
        x = random.randint(-5, 6)
        a = random.randint(2, 5)
        b = random.randint(1, 9)
        val = a * x * x - b
        q = f"Evaluate {a}x² - {b} when x = {x}"
        choices, correct = _mc(val, _near(val, 6))
        return _pack("Algebra", tier, q, choices, correct)
    # distributive
    x = random.randint(2, 9)
    a = random.randint(2, 5)
    b = random.randint(1, 6)
    rhs = a * (x + b)
    q = f"Solve for x:   {a}(x + {b}) = {rhs}"
    choices, correct = _mc(x, _near(x))
    return _pack("Algebra", tier, q, choices, correct)


# ----------------------------------------------------------------------
# COORDINATE GEOMETRY
# ----------------------------------------------------------------------
def _quadrant(px, py):
    if px > 0 and py > 0:
        return "Quadrant I"
    if px < 0 and py > 0:
        return "Quadrant II"
    if px < 0 and py < 0:
        return "Quadrant III"
    return "Quadrant IV"


def geometry(tier):
    if tier == 1:
        # name the quadrant of a point
        px = random.choice([-1, 1]) * random.randint(1, 8)
        py = random.choice([-1, 1]) * random.randint(1, 8)
        q = f"In which quadrant does the point ({px}, {py}) lie?"
        correct = _quadrant(px, py)
        all_q = ["Quadrant I", "Quadrant II", "Quadrant III", "Quadrant IV"]
        choices, correct = _mc(correct, [x for x in all_q if x != correct])
        return _pack("Coordinate Geometry", tier, q, choices, correct)

    if tier == 2:
        # midpoint with integer coords, or horizontal/vertical distance
        if random.random() < 0.5:
            x1, y1 = random.randint(-6, 6), random.randint(-6, 6)
            x2, y2 = x1 + 2 * random.randint(1, 4), y1 + 2 * random.randint(1, 4)
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            q = (f"What is the midpoint of the segment joining "
                 f"({x1}, {y1}) and ({x2}, {y2})?")
            correct = f"({mx}, {my})"
            distractors = [f"({mx+1}, {my})", f"({mx}, {my+1})",
                           f"({mx-1}, {my-1})", f"({x1+x2}, {y1+y2})"]
        else:
            y = random.randint(-5, 5)
            x1 = random.randint(-8, 0)
            x2 = random.randint(1, 8)
            dist = x2 - x1
            q = (f"What is the distance between ({x1}, {y}) and ({x2}, {y})?")
            correct = dist
            distractors = _near(dist, 3)
        choices, correct = _mc(correct, distractors)
        return _pack("Coordinate Geometry", tier, q, choices, correct)

    # tier 3: slope, or distance via 3-4-5 style Pythagorean triple
    if random.random() < 0.5:
        x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
        run = random.choice([1, 2, 3])
        rise = random.choice([-4, -2, -1, 1, 2, 4])
        x2, y2 = x1 + run, y1 + rise
        from fractions import Fraction
        slope = Fraction(rise, run)
        q = f"What is the slope of the line through ({x1}, {y1}) and ({x2}, {y2})?"
        correct = str(slope)
        distractors = [str(Fraction(run, rise)) if rise else "0",
                       str(-slope), str(slope + 1), str(slope - 1)]
        choices, correct = _mc(correct, distractors)
        return _pack("Coordinate Geometry", tier, q, choices, correct)
    else:
        triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)]
        a, b, c = random.choice(triples)
        x1, y1 = random.randint(-3, 3), random.randint(-3, 3)
        x2, y2 = x1 + a, y1 + b
        q = (f"What is the distance between ({x1}, {y1}) and ({x2}, {y2})?")
        correct = c
        distractors = [a + b, c + 1, c - 1, max(a, b)]
        choices, correct = _mc(correct, distractors)
        return _pack("Coordinate Geometry", tier, q, choices, correct)


def _pack(topic, tier, q, choices, correct):
    return {"topic": topic, "tier": tier, "question": q,
            "choices": choices, "answer": correct}


GENERATORS = {"Algebra": algebra, "Coordinate Geometry": geometry}


def make_question(topic, tier):
    """Public entry point."""
    return GENERATORS[topic](tier)


if __name__ == "__main__":
    for topic in GENERATORS:
        for tier in (1, 2, 3):
            print(make_question(topic, tier))
