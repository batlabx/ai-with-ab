# run.py — kick off one daily message
import asyncio
import traceback
from dotenv import load_dotenv

load_dotenv()

from agent import build_graph


async def main():
    print("[1/4] Building graph...")
    graph = build_graph()
    config = {"configurable": {"thread_id": "daily-mom-message"}}

    print("[2/4] Invoking graph (recall → draft → review → send)...")
    try:
        result = await graph.ainvoke(
            {
                "topic": "a warm daily check-in for mom",
                "context": [],
                "draft": "",
                "approved": False,
                "status": "",
            },
            config=config,
        )
        print("Status:", result["status"])
    except Exception as e:
        print("ERROR during graph run:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
