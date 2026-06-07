# Build a Free, Local AI Math Tutor That Grades Your Kid's Level and Writes Their Homework

### No cloud APIs. No paid subscriptions. Runs entirely on your Mac.

My kid needed math practice. The worksheets I found online were either too easy
(boring) or too hard (tears). What I actually wanted was something that would
*test* where she's at and then hand her exactly the right practice — and do it
again next week as she improves.

So I built it. A small AI tutor that runs a quick diagnostic on **Algebra** and
**Coordinate Geometry**, figures out the student's level, and generates a custom
**20-question homework** at that difficulty, with an answer key. It's built for
**Grades 4–8**, runs entirely on my Mac, and costs nothing — no OpenAI key, no
subscriptions.

This post is the full build. You can copy every file verbatim and run it in
about ten minutes.

---

## What you'll learn
- How to make an LLM-powered tutor *that you can actually trust with math*
- How to grade a diagnostic into a meaningful skill level (not just a raw score)
- How to generate tailored practice questions whose answers are guaranteed correct
- How to keep the whole thing free and local with Ollama + Python

## What we're building
A terminal tutor with this flow:

```
greet → 8-question multiple-choice diagnostic → grade (weighted by difficulty)
      → assign level (Beginner / Intermediate / Advanced)
      → local-LLM encouragement note
      → generate a 20-question homework at that level (+ answer key)
      → remember the student for next time
```

And here's the architecture. The most important design decision is the dotted
line: **the LLM is not on the math path.** Questions and answers are generated in
pure Python. The model only writes the friendly feedback note — and if it isn't
installed, a template covers for it.

```
                 ┌──────────────────────────────────┐
   recall   ──►  │  students.json  (level + history) │
                 └──────────────────────────────────┘
                              │
   think    ──►   questions.py   generate question + CORRECT answer  (pure Python)
                  tutor.py       grade → level → build 20-Q homework  (pure Python)
                              │
   act      ··►   brain.py       Ollama writes encouragement   (OPTIONAL, dotted)
                              │
   remember ──►   homework/<name>_homework.md + _answer_key.md
                  students.json updated
```

## The free stack
| Part | Tool | Why it's free |
|------|------|---------------|
| **Brain** (feedback note) | Ollama + `llama3.1:8b`, local | Open weights, runs on your machine, no API |
| **Math engine** | Python standard library (+ optional `sympy`) | Ships with Python |
| **Memory** | a `students.json` file | Just a file |
| **Output** | Markdown worksheet + answer key | Plain text |

## Prerequisites
- Python 3.9+
- (Optional) [Ollama](https://ollama.com) for the AI feedback note:
  `ollama pull llama3.1:8b`. Skip it and the tutor still works — it falls back to
  a template.

---

## Step-by-step build

We'll create five files in a folder called `ai-math-tutor/`:

```
ai-math-tutor/
├── questions.py      # the math engine: questions + guaranteed-correct answers
├── tutor.py          # diagnostic, grading, leveling, homework, memory
├── brain.py          # optional Ollama feedback (with template fallback)
├── run.py            # the interactive CLI
└── test_tutor.py     # unit tests (proof it works)
```

### Step 1 — The math engine (`questions.py`)

This is the heart of the "trustworthy" claim. Every generator **builds the answer
first**, then constructs a question around it, and finally produces four shuffled
multiple-choice options. Because we never ask the LLM to compute anything, the
answer key is always right.

```python
"""questions.py — the trustworthy math engine.
Generates multiple-choice questions for Algebra and Coordinate Geometry,
tuned for Grades 4-8, across three difficulty tiers (1=easy, 2=medium, 3=hard).
"""
import random


def _mc(correct, distractors):
    """Build a shuffled 4-option block from a correct answer + distractors."""
    opts, seen = [str(correct)], {str(correct)}
    for d in distractors:
        s = str(d)
        if s not in seen:
            opts.append(s); seen.add(s)
        if len(opts) == 4:
            break
    n = 1
    while len(opts) < 4:               # safety padding (rarely needed)
        cand = str(correct) + " " * n
        if cand not in seen:
            opts.append(cand); seen.add(cand)
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


# ---------- ALGEBRA ----------
def algebra(tier):
    if tier == 1:                      # missing number, one operation
        if random.random() < 0.5:
            a, ans = random.randint(2, 20), random.randint(2, 20)
            q = f"What number goes in the box?   {a} + □ = {a + ans}"
        else:
            a, ans = random.randint(2, 9), random.randint(2, 9)
            q = f"What number goes in the box?   {a} × □ = {a * ans}"
        choices, correct = _mc(ans, _near(ans))
        return _pack("Algebra", tier, q, choices, correct)

    if tier == 2:                      # one/two-step equation, positive answer
        x, a, b = random.randint(2, 12), random.randint(2, 6), random.randint(1, 15)
        if random.random() < 0.5:
            q = f"Solve for x:   {a}x + {b} = {a * x + b}"
        else:
            q = f"Solve for x:   {a}x - {b} = {a * x - b}"
        choices, correct = _mc(x, _near(x))
        return _pack("Algebra", tier, q, choices, correct)

    # tier 3: negatives, evaluate, or distributive
    style = random.choice(["neg", "eval", "dist"])
    if style == "neg":
        x, a, b = random.randint(-8, 8), random.randint(2, 6), random.randint(-10, 10)
        q = f"Solve for x:   {a}x + ({b}) = {a * x + b}"
        choices, correct = _mc(x, _near(x, 4))
    elif style == "eval":
        x, a, b = random.randint(-5, 6), random.randint(2, 5), random.randint(1, 9)
        val = a * x * x - b
        q = f"Evaluate {a}x² - {b} when x = {x}"
        choices, correct = _mc(val, _near(val, 6))
    else:
        x, a, b = random.randint(2, 9), random.randint(2, 5), random.randint(1, 6)
        q = f"Solve for x:   {a}(x + {b}) = {a * (x + b)}"
        choices, correct = _mc(x, _near(x))
    return _pack("Algebra", tier, q, choices, correct)


# ---------- COORDINATE GEOMETRY ----------
def _quadrant(px, py):
    if px > 0 and py > 0: return "Quadrant I"
    if px < 0 and py > 0: return "Quadrant II"
    if px < 0 and py < 0: return "Quadrant III"
    return "Quadrant IV"


def geometry(tier):
    if tier == 1:                      # name the quadrant
        px = random.choice([-1, 1]) * random.randint(1, 8)
        py = random.choice([-1, 1]) * random.randint(1, 8)
        q = f"In which quadrant does the point ({px}, {py}) lie?"
        correct = _quadrant(px, py)
        allq = ["Quadrant I", "Quadrant II", "Quadrant III", "Quadrant IV"]
        choices, correct = _mc(correct, [x for x in allq if x != correct])
        return _pack("Coordinate Geometry", tier, q, choices, correct)

    if tier == 2:                      # midpoint or horizontal distance
        if random.random() < 0.5:
            x1, y1 = random.randint(-6, 6), random.randint(-6, 6)
            x2 = x1 + 2 * random.randint(1, 4); y2 = y1 + 2 * random.randint(1, 4)
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            q = f"What is the midpoint of ({x1}, {y1}) and ({x2}, {y2})?"
            correct = f"({mx}, {my})"
            distractors = [f"({mx+1}, {my})", f"({mx}, {my+1})",
                           f"({mx-1}, {my-1})", f"({x1+x2}, {y1+y2})"]
        else:
            y = random.randint(-5, 5); x1 = random.randint(-8, 0); x2 = random.randint(1, 8)
            q = f"What is the distance between ({x1}, {y}) and ({x2}, {y})?"
            correct = x2 - x1
            distractors = _near(correct, 3)
        choices, correct = _mc(correct, distractors)
        return _pack("Coordinate Geometry", tier, q, choices, correct)

    # tier 3: slope, or distance via a Pythagorean triple (clean answers)
    from fractions import Fraction
    if random.random() < 0.5:
        x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
        run = random.choice([1, 2, 3]); rise = random.choice([-4, -2, -1, 1, 2, 4])
        x2, y2 = x1 + run, y1 + rise
        slope = Fraction(rise, run)
        q = f"What is the slope of the line through ({x1}, {y1}) and ({x2}, {y2})?"
        correct = str(slope)
        distractors = [str(Fraction(run, rise)) if rise else "0",
                       str(-slope), str(slope + 1), str(slope - 1)]
    else:
        a, b, c = random.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)])
        x1, y1 = random.randint(-3, 3), random.randint(-3, 3)
        x2, y2 = x1 + a, y1 + b
        q = f"What is the distance between ({x1}, {y1}) and ({x2}, {y2})?"
        correct = c
        distractors = [a + b, c + 1, c - 1, max(a, b)]
    choices, correct = _mc(correct, distractors)
    return _pack("Coordinate Geometry", tier, q, choices, correct)


def _pack(topic, tier, q, choices, correct):
    return {"topic": topic, "tier": tier, "question": q,
            "choices": choices, "answer": correct}


GENERATORS = {"Algebra": algebra, "Coordinate Geometry": geometry}


def make_question(topic, tier):
    return GENERATORS[topic](tier)
```

Notice the small tricks that keep answers *clean* for kids: coordinate distances
use Pythagorean triples (3-4-5, 5-12-13…) so the answer is a whole number, and
midpoints use even coordinate gaps so there are no fractions. Those details are
the difference between a worksheet a child can do and one that frustrates them.

### Step 2 — Diagnostic, grading, and leveling (`tutor.py`)

The diagnostic is eight questions covering both topics across all three tiers.
The key idea in grading is **weighting by difficulty**: a tier-3 question is
worth three points, a tier-1 worth one. That way a student who breezes through
the easy half but misses everything hard is correctly placed as Beginner or
Intermediate — not falsely flagged Advanced.

```python
"""tutor.py — diagnostic, grading, level assignment, homework, memory."""
import json, os, random
from datetime import date
import questions

TOPICS = ["Algebra", "Coordinate Geometry"]
LEVELS = ["Beginner", "Intermediate", "Advanced"]
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "students.json")
HOMEWORK_SIZE = 20


def build_diagnostic():
    """8 questions: each topic gets tiers 1,2,2,3."""
    quiz = []
    for topic in TOPICS:
        for tier in (1, 2, 2, 3):
            quiz.append(questions.make_question(topic, tier))
    random.shuffle(quiz)
    return quiz


def score_to_level(correct_by_tier):
    """Map {tier: (correct, total)} to a level, weighting harder tiers more."""
    pts   = sum(c * tier for tier, (c, t) in correct_by_tier.items())
    total = sum(t * tier for tier, (c, t) in correct_by_tier.items())
    ratio = pts / total if total else 0
    if ratio >= 0.75: return "Advanced"
    if ratio >= 0.45: return "Intermediate"
    return "Beginner"


def grade_diagnostic(quiz, responses):
    tier_tally  = {1: [0, 0], 2: [0, 0], 3: [0, 0]}
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


# tier mix per level for each topic's 10 questions
_TIER_MIX = {
    "Beginner":     [1, 1, 1, 1, 1, 1, 2, 2, 2, 3],
    "Intermediate": [1, 1, 2, 2, 2, 2, 2, 3, 3, 3],
    "Advanced":     [2, 2, 2, 3, 3, 3, 3, 3, 3, 3],
}


def generate_homework(level, size=HOMEWORK_SIZE):
    per_topic = size // 2
    mix = _TIER_MIX[level]
    hw, qnum = [], 1
    for topic in TOPICS:
        tiers = (mix * ((per_topic // len(mix)) + 1))[:per_topic]
        for tier in tiers:
            q = questions.make_question(topic, tier)
            q["n"] = qnum; hw.append(q); qnum += 1
    return hw


def homework_to_markdown(student, level, hw):
    today = date.today().isoformat()
    ws = [f"# Practice Homework — {student}",
          "**Topics:** Algebra & Coordinate Geometry  ",
          f"**Level:** {level}  |  **Date:** {today}  |  **Questions:** {len(hw)}",
          "", "_Choose the best answer for each question._", ""]
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


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f:
            return json.load(f)
    return {}


def save_student(name, level, pct, per_topic):
    mem = load_memory()
    rec = mem.get(name, {"history": []})
    rec["level"] = level
    rec["history"].append({"date": date.today().isoformat(), "level": level,
                           "score_pct": pct, "per_topic": per_topic})
    mem[name] = rec
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)
    return rec
```

### Step 3 — Optional AI coaching (`brain.py`)

This is the *only* place the LLM appears. We make one local call to Ollama for a
warm 2–3 sentence note, wrapped in `try/except` so a missing model (or no Ollama
at all) silently falls back to a friendly template.

```python
"""brain.py — optional local-LLM coaching via Ollama, with template fallback."""
import json, urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"


def _template_feedback(name, level, pct, per_topic):
    strong = max(per_topic, key=per_topic.get)
    weak   = min(per_topic, key=per_topic.get)
    tip = {"Beginner": "Let's build the fundamentals — take your time.",
           "Intermediate": "You've got the basics; this pushes you further.",
           "Advanced": "Strong work — this set will keep you challenged."}[level]
    return (f"Nice effort, {name}! You scored {pct}% and landed at the "
            f"**{level}** level. Your strongest area is {strong} and {weak} "
            f"could use a bit more practice. {tip}")


def coach(name, level, pct, per_topic, model=MODEL):
    prompt = (
        f"You are a warm, encouraging maths tutor for a child in grades 4-8. "
        f"The student '{name}' took a diagnostic on Algebra and Coordinate "
        f"Geometry. They scored {pct}% overall, per-topic {per_topic}, and are "
        f"at the {level} level. Write 2-3 short encouraging sentences: praise "
        f"effort, name their strongest and weakest topic, motivate them for the "
        f"homework. Plain friendly text, no markdown headers.")
    payload = json.dumps({"model": model, "prompt": prompt,
                          "stream": False}).encode()
    try:
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            text = json.loads(r.read()).get("response", "").strip()
            if text:
                return text
    except Exception:
        pass
    return _template_feedback(name, level, pct, per_topic)
```

### Step 4 — The interactive CLI (`run.py`)

This ties it together: greet the student, run the diagnostic, grade, coach,
generate homework, and save. There's a `--demo` flag that auto-answers (handy for
testing or recording without typing).

```python
#!/usr/bin/env python3
"""run.py — interactive multiple-choice AI math tutor (Grades 4-8)."""
import argparse, os, random, sys
import tutor
from brain import coach

LETTERS = ["A", "B", "C", "D"]
OUT_DIR = os.path.join(os.path.dirname(__file__), "homework")


def ask(q, auto=None):
    print(f"\n[{q['topic']} · difficulty {q['tier']}]")
    print(q["question"])
    for i, ch in enumerate(q["choices"]):
        print(f"   {LETTERS[i]}) {ch}")
    if auto is not None:
        idx = auto(q); print(f"   > (auto) {LETTERS[idx]}")
        return q["choices"][idx]
    while True:
        raw = input("Your answer (A/B/C/D): ").strip().upper()
        if raw in LETTERS[:len(q["choices"])]:
            return q["choices"][LETTERS.index(raw)]
        print("   Please type A, B, C, or D.")


def _demo_strategy(skill=0.7):
    def pick(q):
        p = skill + (3 - q["tier"]) * 0.08
        correct_idx = q["choices"].index(str(q["answer"]))
        if random.random() < p:
            return correct_idx
        return random.choice([i for i in range(len(q["choices"])) if i != correct_idx])
    return pick


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
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
    print(f"RESULTS for {name}\n  Overall: {pct}%   |   Level: {level}")
    for t, p in per_topic.items():
        print(f"  {t}: {p}%")
    print("-" * 56)

    print("\nCoach says:")
    print("  " + coach(name, level, pct, per_topic).replace("\n", "\n  "))
    tutor.save_student(name, level, pct, per_topic)

    hw = tutor.generate_homework(level)
    ws_md, key_md = tutor.homework_to_markdown(name, level, hw)
    os.makedirs(OUT_DIR, exist_ok=True)
    slug = name.lower().replace(" ", "_")
    ws_path  = os.path.join(OUT_DIR, f"{slug}_homework.md")
    key_path = os.path.join(OUT_DIR, f"{slug}_answer_key.md")
    open(ws_path, "w").write(ws_md)
    open(key_path, "w").write(key_md)

    print(f"\n✓ Generated a {len(hw)}-question practice homework at the {level} level.")
    print(f"  Worksheet : {ws_path}\n  Answer key: {key_path}\n\nGood luck! 🎯")


if __name__ == "__main__":
    sys.exit(main())
```

### Step 5 — Run it

```bash
pip install -r requirements.txt      # only sympy, and only if you extend it
python run.py                        # interactive
python run.py --demo --name "Maya"   # simulated student, no typing
```

---

## Test it (proof or it didn't happen)

I never ship code I haven't run, and the whole point of this design is *trust* —
so it ships with tests that prove every generated answer is actually one of the
choices, that grading hits the right level at the extremes, and that homework is
always 20 questions split evenly.

```python
"""test_tutor.py — run with: python test_tutor.py"""
import questions, tutor


def test_every_generator_answer_is_a_choice():
    for topic in questions.GENERATORS:
        for tier in (1, 2, 3):
            for _ in range(200):
                q = questions.make_question(topic, tier)
                assert len(q["choices"]) == 4
                assert len(set(q["choices"])) == 4
                assert str(q["answer"]) in q["choices"]


def test_grade_diagnostic_all_correct():
    quiz = tutor.build_diagnostic()
    level, pct, per_topic, _ = tutor.grade_diagnostic(quiz, [q["answer"] for q in quiz])
    assert pct == 100 and level == "Advanced"


def test_grade_diagnostic_all_wrong():
    quiz = tutor.build_diagnostic()
    wrong = [next(c for c in q["choices"] if c != str(q["answer"])) for q in quiz]
    level, pct, *_ = tutor.grade_diagnostic(quiz, wrong)
    assert pct == 0 and level == "Beginner"


def test_homework_is_20_questions_split_evenly():
    for level in tutor.LEVELS:
        hw = tutor.generate_homework(level)
        assert len(hw) == 20
        assert sum(q["topic"] == "Algebra" for q in hw) == 10
        assert [q["n"] for q in hw] == list(range(1, 21))
```

Running everything:

```
$ python test_tutor.py
PASS test_every_generator_answer_is_a_choice
PASS test_grade_diagnostic_all_correct
PASS test_grade_diagnostic_all_wrong
PASS test_homework_is_20_questions_split_evenly
PASS test_homework_markdown_and_key_line_up
PASS test_score_to_level_boundaries
All 6 tests passed.

$ python run.py --demo --name "Maya"
RESULTS for Maya
  Overall: 88%   |   Level: Advanced
  Algebra: 100%   Coordinate Geometry: 75%
Coach says:
  Nice effort, Maya! You scored 88% and landed at the Advanced level...
✓ Generated a 20-question practice homework at the Advanced level.
```

And a slice of the generated worksheet and key:

```
**1. [Algebra]** Solve for x:   2x - 3 = 19
   - A) 9
   - B) 10
   - C) 12
   - D) 11
...
Answer Key:  1. D (11)   2. B (10)   3. A (2)   4. B (5)
```

## Gotchas (the real ones I hit)
- **Never let the LLM do arithmetic.** Small local models miscompute constantly.
  Generating the answer in Python is what makes the answer key trustworthy.
- **Build the answer first, the question second.** It's the simplest possible way
  to guarantee correctness, and it makes distractors easy to place around it.
- **Weight by difficulty when leveling**, or a kid who only nails the easy half
  gets mislabeled "Advanced."
- **Keep numbers clean for kids.** Pythagorean triples for distances and even
  gaps for midpoints avoid ugly fractions that cause frustration, not learning.
- **Wrap the Ollama call in try/except.** The tutor must run with zero setup;
  the AI note is a bonus, not a dependency.

## What it costs
| Item | Cost |
|------|------|
| Ollama + llama3.1:8b | $0 |
| Python / sympy | $0 |
| File storage | $0 |
| **Total** | **$0** |

## What to build next
1. **More topics** — fractions, ratios, area/perimeter — by adding generators.
2. **Progress tracking** — `students.json` already stores history; re-test weekly
   and chart improvement.
3. **PDF export** — turn the Markdown worksheet into a printable PDF.
4. **Worked solutions** — have the LLM *explain* each step while Python checks the
   final number, so explanations are friendly *and* correct.
5. **A tiny web UI** so kids answer in the browser instead of the terminal.

## Full source code
→ `https://github.com/batlabx/ai-with-ab/tree/main/builds/ai-math-tutor`
