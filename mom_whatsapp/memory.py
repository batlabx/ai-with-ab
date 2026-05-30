# memory.py — simple JSON-based memory, no mem0/Chroma/Qdrant needed
import os
import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / ".memory.json"


def _load() -> list[dict]:
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return []


def _save(memories: list[dict]):
    MEMORY_FILE.write_text(json.dumps(memories, indent=2))


def remember(text: str, metadata: dict | None = None) -> None:
    """Store a fact. Skips duplicates."""
    memories = _load()
    if not any(m["text"] == text for m in memories):
        memories.append({"text": text, "metadata": metadata or {}})
        _save(memories)


def recall(query: str, limit: int = 5) -> list[str]:
    """Return up to `limit` stored facts (most recently added first)."""
    memories = _load()
    # Simple relevance: prefer entries whose text overlaps with query words
    query_words = set(query.lower().split())
    def score(m):
        words = set(m["text"].lower().split())
        return len(query_words & words)
    ranked = sorted(memories, key=score, reverse=True)
    return [m["text"] for m in ranked[:limit]]


def list_all() -> list[dict]:
    return _load()


def forget(text: str) -> bool:
    """Remove a specific memory by exact text. Returns True if found."""
    memories = _load()
    filtered = [m for m in memories if m["text"] != text]
    if len(filtered) < len(memories):
        _save(filtered)
        return True
    return False


if __name__ == "__main__":
    # Edit these facts to reflect your own mother, then run once: python memory.py
    remember("Mother loves her morning tea and prayers.")
    remember("Mother worries when she doesn't hear from me every day.")
    remember("Keep messages to Mother short, warm, and never robotic.")
    print("Seeded. All memories:")
    for m in list_all():
        print(" -", m["text"])
