"""
tutor.py — diagnostic, grading, level assignment, and homework generation.

Pure logic, no I/O of its own (so it is easy to unit-test). The interactive
shell lives in run.py.
"""

import json
import os
import random
from datetime import date

import questions

TOPICS = ["Algebra", "Coordinate Geometry"]
LEVELS = ["Beginner", "Intermediate", "Advanced"]
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "students.json")

# how many homework questions and how the 20 are split per level
HOMEWORK_SIZE = 20


# ----------------------------------------------------------------------
# diagnostic
# ----------------------------------------------------------------------
def build_diagnostic():
    """8 questions: each topic gets tiers 1,2,3 plus one extra tier-2.
    Returns a list of question dicts."""
    quiz = []
    for topic in TOPICS:
        for tier in (1, 2, 2, 3):
            quiz.append(questions.make_question(topic, tier))
    random.shuffle(quiz)
    return quiz


def score_to_level(correct_by_tier):
    """Map a {tier: (correct, total)} tally to a level.

    Logic: weight by tier. A student who clears the easy tier but misses
    hard ones is Beginner/Intermediate; one who clears hard tiers is Advanced.
    """
    pts = 0
    total = 0
    for tier, (c, t) in correct_by_tier.items():
        pts += c * tier        # harder questions are worth more
        total += t * tier
    ratio = pts / total if total else 0
    if ratio >= 0.75:
        return "Advanced"
    if ratio >= 0.45:
        return "Intermediate"
    return "Beginner"


def grade_diagnostic(quiz, responses):
    """quiz: list of question dicts. responses: list of chosen strings.
    Returns (level, pct, per_topic_pct, tier_tally)."""
    tier_tally = {1: [0, 0], 2: [0, 0], 3: [0, 0]}
    topic_tally = {t: [0, 0] for t in TOPICS}
    correct_n = 0
    for q, chosen in zip(quiz, responses):
        tier_tally[q["tier"]][1] += 1
        topic_tally[q["topic"]][1] += 1
        if str(chosen).strip() == str(q["answer"]).strip():
            correct_n += 1
            tier_tally[q["tier"]][0] += 1
            topic_tally[q["topic"]][0] += 1
    tally = {k: tuple(v) for k, v in tier_tally.items()}
    level = score_to_level(tally)
    pct = round(100 * correct_n / len(quiz)) if quiz else 0
    per_topic = {t: (round(100 * c / n) if n else 0)
                 for t, (c, n) in topic_tally.items()}
    return level, pct, per_topic, tally


# ----------------------------------------------------------------------
# homework
# ----------------------------------------------------------------------
# tier mix per level for the 20-question homework (Algebra + Geometry split 10/10)
_TIER_MIX = {
    "Beginner":     [1, 1, 1, 1, 1, 1, 2, 2, 2, 3],   # mostly easy, a stretch
    "Intermediate": [1, 1, 2, 2, 2, 2, 2, 3, 3, 3],   # core medium
    "Advanced":     [2, 2, 2, 3, 3, 3, 3, 3, 3, 3],   # mostly hard
}


def generate_homework(level, size=HOMEWORK_SIZE):
    """Build `size` MC questions split evenly across the two topics, with the
    tier mix matched to the student's level."""
    per_topic = size // 2
    mix = _TIER_MIX[level]
    hw = []
    qnum = 1
    for topic in TOPICS:
        tiers = (mix * ((per_topic // len(mix)) + 1))[:per_topic]
        for tier in tiers:
            q = questions.make_question(topic, tier)
            q["n"] = qnum
            hw.append(q)
            qnum += 1
    return hw


def homework_to_markdown(student, level, hw):
    """Return (worksheet_md, answer_key_md)."""
    today = date.today().isoformat()
    ws = [f"# Practice Homework — {student}",
          f"**Topics:** Algebra & Coordinate Geometry  ",
          f"**Level:** {level}  |  **Date:** {today}  |  **Questions:** {len(hw)}",
          "",
          "_Choose the best answer for each question._", ""]
    key = [f"# Answer Key — {student} ({level}, {today})", ""]
    letters = ["A", "B", "C", "D"]
    for q in hw:
        ws.append(f"**{q['n']}. [{q['topic']}]** {q['question']}")
        correct_letter = "?"
        for i, ch in enumerate(q["choices"]):
            ws.append(f"   - {letters[i]}) {ch}")
            if str(ch).strip() == str(q["answer"]).strip():
                correct_letter = letters[i]
        ws.append("")
        key.append(f"{q['n']}. {correct_letter}  ({q['answer']})")
    return "\n".join(ws), "\n".join(key)


# ----------------------------------------------------------------------
# memory
# ----------------------------------------------------------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f:
            return json.load(f)
    return {}


def save_student(name, level, pct, per_topic):
    mem = load_memory()
    rec = mem.get(name, {"history": []})
    rec["level"] = level
    rec["history"].append({"date": date.today().isoformat(),
                           "level": level, "score_pct": pct,
                           "per_topic": per_topic})
    mem[name] = rec
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)
    return rec
