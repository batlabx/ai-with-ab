# Repurposing & Publish Pack — AI Math Tutor

## Substack Note
Built a free, fully local AI math tutor for my kid this weekend. It gives an
8-question diagnostic on Algebra + Coordinate Geometry, figures out their level,
then writes a custom 20-question homework at exactly the right difficulty. The
trick: the *maths* is pure Python (always correct), the local LLM only writes
the "nice job, here's what to practice" note. $0, runs on your Mac. Full
write-up + code ↓

## X / LinkedIn thread
1/ I built an AI math tutor for grades 4–8 that grades a student's level and
auto-generates their homework. 100% free, 100% local. No OpenAI key. Here's how 🧵

2/ The core idea: never trust a small LLM to do arithmetic. I generate every
question AND its correct answer in pure Python. The model never computes — it
only writes encouragement.

3/ Flow: 8-question multiple-choice diagnostic → weighted grading → Beginner /
Intermediate / Advanced → a 20-question homework (10 Algebra + 10 Coordinate
Geometry) at that level, plus an answer key.

4/ Stack, all $0: Ollama + llama3.1:8b (local brain), Python stdlib (math
engine), a JSON file (memory), Markdown (output).

5/ Leveling is weighted by difficulty so a kid who only aces the easy questions
isn't called "advanced." ≥75% → Advanced, 45–74% → Intermediate, else Beginner.

6/ It ships with unit tests proving every generated answer is among the choices
and that homework is always 20 questions split evenly. Tested or it doesn't ship.

7/ Full code + tutorial (free): github.com/batlabx/ai-with-ab → builds/ai-math-tutor

## r/LocalLLaMA / Show HN one-liner
Free local AI math tutor (Ollama + Python): diagnoses a kid's level in Algebra &
Coordinate Geometry and generates a tailored 20-question homework — maths in
pure Python so answers are always correct, LLM only writes feedback.

---

# YouTube Package

**Title:** I Built a FREE Local AI Math Tutor That Grades Your Kid and Writes Their Homework (Ollama + Python)

**Description:**
A fully local, $0 AI tutor for grades 4–8. It runs a short multiple-choice
diagnostic on Algebra and Coordinate Geometry, grades it to assign a level, and
auto-generates a custom 20-question homework with an answer key. The maths is
pure Python (always correct); a local LLM via Ollama only writes the
encouragement note. No cloud APIs, no subscriptions. Code is free on GitHub.

Chapters:
0:00 The idea — tutor that grades + assigns homework
0:40 Why the LLM must NOT do the maths
1:30 The free stack (Ollama + Python)
2:30 Building the question engine
4:00 Diagnostic + weighted leveling
5:30 Generating the 20-question homework
6:30 Demo run + the answer key
7:30 Tests & gotchas
8:30 What to build next

**Tags:** ollama, local llm, ai tutor, math tutor, python, free ai, llama 3.1,
homework generator, edtech, coordinate geometry, algebra, no api

**Thumbnail concept:** Split screen — left: a kid's quiz with a big green
"LEVEL: INTERMEDIATE" stamp; right: a printed 20-question worksheet. Top text:
"FREE AI MATH TUTOR". Corner badge: "$0 · runs on your Mac".

## Voiceover script (timed, ~8 min)
[0:00] "What if your computer could test your kid in math, figure out exactly
what level they're at, and then print out the perfect practice homework — for
free, without sending a single byte to the cloud? Let's build it."
[0:40] "Here's the most important rule: we never let the AI do the arithmetic.
Small local models get math wrong all the time. So we generate every question
AND its answer in plain Python."
[1:30] "Our stack is completely free: Ollama running Llama 3.1 locally as the
brain, Python for the math engine, a JSON file for memory, and Markdown for the
worksheet."
[2:30] "Each generator builds the answer first, then wraps a question around it,
and produces four shuffled choices..."
[4:00] "The diagnostic is eight questions across both topics and three
difficulty tiers. We weight harder questions more, so the level is honest."
[5:30] "Once we know the level, we pick a tier mix and generate twenty
questions — ten algebra, ten coordinate geometry — plus a separate answer key."
[6:30] "Let's run it. Watch it grade the student, call them Intermediate, and
drop a ready-to-print worksheet."
[7:30] "It's all tested — every answer is guaranteed to be a real choice, and
homework is always twenty questions. Here are the gotchas I hit."
[8:30] "Next, add fractions, progress tracking, or a PDF export. Code's free in
the description. See you in the next one."
