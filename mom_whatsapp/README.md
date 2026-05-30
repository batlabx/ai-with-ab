# WhatsApp Mother Agent

A local AI agent that automatically sends and replies to your mother on WhatsApp — no cloud APIs, no paid subscriptions, runs entirely on your Mac.

## What It Does

- **Sends a morning message** drafted by a local LLM, based on your conversation history — you approve before it sends
- **Watches her chat** and auto-replies to whatever she says, in real time
- **Remembers things** about her across days in a simple JSON file
- **Costs $0** — Ollama runs the LLM locally, Playwright drives a real browser

---

## Prerequisites

- macOS (Apple Silicon or Intel)
- Python 3.12 via Homebrew: `brew install python@3.12`
- [Ollama](https://ollama.com) installed and running
- A WhatsApp account

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/yourusername/ai-with-ab.git
cd ai-with-ab/mom_whatsapp

python3.12 -m venv .venv
source .venv/bin/activate

pip install langgraph langchain-core langchain-ollama playwright python-dotenv
python -m playwright install chromium
```

### 2. Pull the local model

```bash
ollama pull llama3.1:8b
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env` and set `MOM_CONTACT_NAME` to the exact name of your mother's contact in WhatsApp.

### 4. Seed memory

Edit the facts in `memory.py` to reflect your mother, then run once:

```bash
python memory.py
```

This creates a `.memory.json` file on your machine. You can edit it by hand any time.

---

## Running

### Morning message (run once a day)

```bash
source .venv/bin/activate
python run.py
```

The agent drafts a message based on your conversation history. You approve, edit, or cancel it in the terminal. If approved, it opens WhatsApp Web and sends it.

**First run:** a browser window will open showing a QR code — scan it with your phone once. After that it stays logged in.

### Reply loop (runs continuously)

```bash
source .venv/bin/activate
python reply_loop.py
```

Checks your mother's chat every 12 seconds. The moment she sends a message, the LLM reads exactly what she wrote and sends a warm, contextual reply.

### Schedule the morning message (optional)

```bash
crontab -e
```

Add:
```
0 9 * * * cd /path/to/mom_whatsapp && /path/to/.venv/bin/python run.py >> agent.log 2>&1
```

---

## Project Structure

```
mom_whatsapp/
├── .env.example      # config template — copy to .env
├── memory.py         # read/write .memory.json
├── whatsapp_tool.py  # Playwright → WhatsApp Web
├── agent.py          # LangGraph morning message flow
├── run.py            # send the morning message
└── reply_loop.py     # watch for messages and auto-reply
```

**Files created at runtime (not in repo):**
- `.env` — your config
- `.memory.json` — facts about your mother
- `.wa_profile/` — WhatsApp Web session

---

## Stack

| Component | Role | Cost |
|-----------|------|------|
| [Ollama](https://ollama.com) + llama3.1:8b | Local LLM | Free |
| [Playwright](https://playwright.dev) | Browser automation | Free |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Agent orchestration | Free |
| JSON file | Memory store | Free |

---

## Extending

- **Add more contacts** — duplicate the reply loop pattern for siblings, friends, etc.
- **Custom tone** — adjust the prompts in `reply_loop.py` and `agent.py`
- **Richer memory** — add birthdays, favourite topics, inside jokes to `.memory.json`
- **Phone approval** — route the morning review gate to Telegram so you can approve from your phone

---

*Part of the AI with AB series.*
