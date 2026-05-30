# agent.py — Layer 1 orchestration
import os
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama

try:
    from langfuse.decorators import observe
except ImportError:
    def observe(name=None):
        def decorator(fn): return fn
        return decorator

from memory import recall, remember
from whatsapp_tool import send_whatsapp

llm = ChatOllama(
    model=os.environ["OLLAMA_MODEL"],
    base_url=os.environ["OLLAMA_BASE_URL"],
)


class State(TypedDict):
    topic: str
    context: list[str]
    draft: str
    approved: bool
    status: str


# --- Nodes: think → act → observe ---------------------------------------------
@observe(name="recall_context")
def recall_node(state: State) -> State:
    state["context"] = recall(state["topic"], limit=5)
    return state


@observe(name="draft_message")
def draft_node(state: State) -> State:
    facts = "\n".join(f"- {c}" for c in state["context"])
    prompt = f"""You are writing a morning WhatsApp message FROM me TO my Mummy.
Write in warm, natural Hinglish — a casual mix of Hindi and English, like a loving child texting their mum.

What I remember about her and our recent exchanges:
{facts}

If she said something recently, acknowledge it naturally and build on it.
If there's nothing recent, just send a warm good morning check-in.

Keep it 1-3 sentences. Sound genuine, not robotic.
Write only the message text, nothing else."""
    state["draft"] = llm.invoke(prompt).content.strip()
    return state


@observe(name="review_gate")
def review_node(state: State) -> State:
    print("\n--- DRAFT MESSAGE TO MOM ---\n" + state["draft"] + "\n")
    answer = input("Send this? [y/N/edit] ").strip().lower()
    if answer == "edit":
        state["draft"] = input("Type the message to send: ").strip()
        state["approved"] = True
    else:
        state["approved"] = answer == "y"
    return state


@observe(name="send_message")
async def send_node(state: State) -> State:
    if not state["approved"]:
        state["status"] = "cancelled"
        return state
    # Call send_whatsapp directly — no MCP middleman needed for a local agent
    state["status"] = await send_whatsapp(
        contact=os.environ["MOM_CONTACT_NAME"],
        message=state["draft"],
    )
    remember(f"Message to Mom delivered: {state['draft']}")
    return state


def build_graph():
    g = StateGraph(State)
    g.add_node("recall", recall_node)
    g.add_node("draft", draft_node)
    g.add_node("review", review_node)
    g.add_node("send", send_node)
    g.add_edge(START, "recall")
    g.add_edge("recall", "draft")
    g.add_edge("draft", "review")
    g.add_edge("review", "send")
    g.add_edge("send", END)
    return g.compile(checkpointer=MemorySaver())
