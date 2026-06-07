"""
brain.py — optional local-LLM coaching via Ollama.

The maths is done in pure Python (questions.py / tutor.py). The LLM is used
ONLY to write a short, encouraging feedback paragraph for the student. If
Ollama isn't installed or the model isn't pulled, we fall back to a friendly
template — the tutor never breaks and never costs a cent.
"""

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"


def _template_feedback(name, level, pct, per_topic):
    strong = max(per_topic, key=per_topic.get)
    weak = min(per_topic, key=per_topic.get)
    if level == "Beginner":
        tip = "Let's build the fundamentals — take your time with each step."
    elif level == "Intermediate":
        tip = "You've got the basics; this homework pushes you a little further."
    else:
        tip = "Strong work — this set will keep you challenged."
    note = (f"Nice effort, {name}! You scored {pct}% and landed at the "
            f"**{level}** level. Your strongest area is {strong} and "
            f"{weak} could use a bit more practice. {tip}")
    return note


def coach(name, level, pct, per_topic, model=MODEL):
    """Return a short feedback string. Tries Ollama, falls back to template."""
    prompt = (
        f"You are a warm, encouraging maths tutor for a child in grades 4-8. "
        f"The student '{name}' just took a diagnostic on Algebra and Coordinate "
        f"Geometry. They scored {pct}% overall, per-topic {per_topic}, and are "
        f"at the {level} level. Write 2-3 short encouraging sentences: praise "
        f"effort, name their strongest and weakest topic, and motivate them for "
        f"the practice homework. No markdown headers, just plain friendly text."
    )
    payload = json.dumps({"model": model, "prompt": prompt,
                          "stream": False}).encode()
    try:
        req = urllib.request.Request(
            OLLAMA_URL, data=payload,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            text = data.get("response", "").strip()
            if text:
                return text
    except Exception:
        pass
    return _template_feedback(name, level, pct, per_topic)
