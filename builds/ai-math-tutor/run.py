#!/usr/bin/env python3
"""
run.py — interactive multiple-choice AI math tutor (Grades 4-8).

Flow:  greet -> diagnostic quiz -> grade -> assign level -> local-LLM coaching
       -> generate a 20-question practice homework at that level -> save files.

Everything runs locally and free. Ollama is optional (used only for the
encouragement note); the maths and grading are pure Python.

Usage:
    python run.py            # interactive
    python run.py --demo     # auto-answer simulation (no input needed)
"""

import argparse
import os
import sys

import tutor
from brain import coach

LETTERS = ["A", "B", "C", "D"]
OUT_DIR = os.path.join(os.path.dirname(__file__), "homework")


def ask(q, auto=None):
    """Show a question, return the chosen choice string.
    If auto is given (a strategy fn), use it instead of input()."""
    print(f"\n[{q['topic']} · difficulty {q['tier']}]")
    print(q["question"])
    for i, ch in enumerate(q["choices"]):
        print(f"   {LETTERS[i]}) {ch}")
    if auto is not None:
        idx = auto(q)
        print(f"   > (auto) {LETTERS[idx]}")
        return q["choices"][idx]
    while True:
        raw = input("Your answer (A/B/C/D): ").strip().upper()
        if raw in LETTERS[:len(q["choices"])]:
            return q["choices"][LETTERS.index(raw)]
        print("   Please type A, B, C, or D.")


def _demo_strategy(skill=0.7):
    """Return an auto-answer fn that gets a question right `skill` of the time,
    and is better at easier tiers."""
    import random

    def pick(q):
        p = skill + (3 - q["tier"]) * 0.08
        correct_idx = q["choices"].index(str(q["answer"]))
        if random.random() < p:
            return correct_idx
        wrong = [i for i in range(len(q["choices"])) if i != correct_idx]
        return random.choice(wrong)
    return pick


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true",
                    help="run a simulated student (no typing needed)")
    ap.add_argument("--name", default=None)
    args = ap.parse_args()

    print("=" * 56)
    print("   AI MATH TUTOR  —  Algebra & Coordinate Geometry")
    print("   Grades 4-8  ·  100% local & free")
    print("=" * 56)

    auto = _demo_strategy() if args.demo else None
    name = args.name or ("Demo Student" if args.demo else
                         input("\nWhat's your name? ").strip() or "Student")

    print(f"\nHi {name}! First, a short quiz so I can find your level...")
    quiz = tutor.build_diagnostic()
    responses = [ask(q, auto) for q in quiz]

    level, pct, per_topic, tally = tutor.grade_diagnostic(quiz, responses)

    print("\n" + "-" * 56)
    print(f"RESULTS for {name}")
    print(f"  Overall: {pct}%   |   Level: {level}")
    for t, p in per_topic.items():
        print(f"  {t}: {p}%")
    print("-" * 56)

    print("\nCoach says:")
    print("  " + coach(name, level, pct, per_topic).replace("\n", "\n  "))

    tutor.save_student(name, level, pct, per_topic)

    # homework
    hw = tutor.generate_homework(level)
    ws_md, key_md = tutor.homework_to_markdown(name, level, hw)
    os.makedirs(OUT_DIR, exist_ok=True)
    slug = name.lower().replace(" ", "_")
    ws_path = os.path.join(OUT_DIR, f"{slug}_homework.md")
    key_path = os.path.join(OUT_DIR, f"{slug}_answer_key.md")
    with open(ws_path, "w") as f:
        f.write(ws_md)
    with open(key_path, "w") as f:
        f.write(key_md)

    print(f"\n✓ Generated a {len(hw)}-question practice homework at the "
          f"{level} level.")
    print(f"  Worksheet : {ws_path}")
    print(f"  Answer key: {key_path}")
    print("\nGood luck! 🎯")


if __name__ == "__main__":
    sys.exit(main())
