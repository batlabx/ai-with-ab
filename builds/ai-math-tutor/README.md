# AI Math Tutor — Algebra & Coordinate Geometry (Grades 4–8)

A local, **100% free** AI tutor that gives a student a short multiple-choice
diagnostic on **Algebra** and **Coordinate Geometry**, grades it to assign a
**level** (Beginner / Intermediate / Advanced), then auto-generates a tailored
**20-question practice homework** at that level — with a separate answer key.

No cloud APIs. No paid subscriptions. Runs entirely on your Mac.

## Why it's trustworthy
The maths is generated and checked in **pure Python** (`questions.py`), so every
answer is correct by construction. A local LLM (Ollama) is used *only* to write
the encouraging feedback note — and if Ollama isn't running, it falls back to a
friendly template. The tutor never breaks and never costs a cent.

## The free stack
| Part | Tool | Cost |
|------|------|------|
| Question/answer engine | Python stdlib (+ optional sympy) | $0 |
| Brain (feedback note) | Ollama + `llama3.1:8b` (local) | $0 |
| Memory | `students.json` file | $0 |
| Output | Markdown worksheet + answer key | $0 |

## Setup (one command)
```bash
pip install -r requirements.txt
```
Optional, for the AI feedback note:
```bash
# install Ollama from https://ollama.com, then:
ollama pull llama3.1:8b
```

## Run it
Interactive (a student answers in the terminal):
```bash
python run.py
```
Auto-demo (simulated student, no typing — great for a quick look):
```bash
python run.py --demo --name "Maya"
```
Homework is written to `homework/<name>_homework.md` and
`homework/<name>_answer_key.md`.

## Test it
```bash
python test_tutor.py        # 6 tests: answer-correctness, grading, 20-Q split
```

## How leveling works
The 8-question diagnostic spans both topics across three difficulty tiers.
Harder questions are weighted more, so the level reflects *what* a student can
do, not just how many they got right:
- **≥ 75%** weighted → Advanced
- **45–74%** → Intermediate
- **< 45%** → Beginner

The 20-question homework then uses a tier mix matched to that level (10 Algebra
+ 10 Coordinate Geometry).

## Files
- `questions.py` — the math engine (generates MC questions + correct answers)
- `tutor.py` — diagnostic, grading, level logic, homework, memory
- `brain.py` — optional Ollama feedback (with template fallback)
- `run.py` — interactive CLI
- `test_tutor.py` — unit tests
