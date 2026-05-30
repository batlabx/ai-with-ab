# reply_loop.py — watches Mummy's chat and auto-replies in Hinglish
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from langchain_ollama import ChatOllama
from memory import recall, remember

load_dotenv()

PROFILE_DIR = str(Path(__file__).parent / ".wa_profile")
CONTACT = os.environ["MOM_CONTACT_NAME"]
POLL_INTERVAL = 12  # seconds between checks

llm = ChatOllama(
    model=os.environ["OLLAMA_MODEL"],
    base_url=os.environ["OLLAMA_BASE_URL"],
)


def generate_reply(her_message: str, context: list[str]) -> str:
    facts = "\n".join(f"- {c}" for c in context) if context else ""
    prompt = f"""You are writing a WhatsApp reply FROM me TO my mother.
Write in warm, natural Hinglish — a casual mix of Hindi and English, like a loving child texting their mum.

What I know about her:
{facts}

She just said: "{her_message}"

Write a reply that directly responds to what she said. Keep it 1-3 sentences. Sound natural, not robotic.
Write only the reply text, nothing else."""
    return llm.invoke(prompt).content.strip()


async def get_last_incoming_message(page) -> str | None:
    return await page.evaluate("""() => {
        const incoming = [...document.querySelectorAll('.message-in')];
        if (!incoming.length) return null;
        const last = incoming[incoming.length - 1];
        for (const sel of ['.selectable-text', '.copyable-text', 'span[dir]']) {
            const el = last.querySelector(sel);
            if (el && el.innerText.trim()) return el.innerText.trim();
        }
        const raw = last.innerText.trim();
        return raw.replace(/\n?\d{1,2}:\d{2}\s*(AM|PM)?$/i, '').trim() || null;
    }""")


async def open_chat(page):
    search = page.locator('input[data-tab="3"][role="textbox"]')
    await search.wait_for(timeout=15_000)
    await search.click()
    await search.fill(CONTACT)
    await page.wait_for_timeout(2000)
    await page.get_by_text(CONTACT, exact=True).first.click()
    await page.wait_for_timeout(1500)


async def send_message(page, text: str):
    compose = page.locator('footer div[contenteditable="true"]').first
    await compose.wait_for(timeout=10_000)
    await compose.click()
    await compose.fill(text)
    await page.wait_for_timeout(500)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1000)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--no-sandbox"],
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

        print("Waiting for WhatsApp Web to load...")
        await page.wait_for_selector('#pane-side, [data-testid="qrcode"]', timeout=60_000)

        if await page.locator('[data-testid="qrcode"]').count() > 0:
            print("\n>>> Scan the QR code in the browser, then press Enter here...")
            input()
            await page.wait_for_selector("#pane-side", timeout=60_000)

        await page.wait_for_timeout(2000)
        await open_chat(page)

        # Seed seen so we don't reply to existing messages on startup
        seen: set[str] = set()
        existing = await get_last_incoming_message(page)
        if existing:
            seen.add(existing)
            print(f"Ignoring existing message: '{existing[:60]}'")

        print(f"\n✅ Watching {CONTACT} — checking every {POLL_INTERVAL}s\n")

        while True:
            try:
                last_msg = await get_last_incoming_message(page)

                if last_msg and last_msg not in seen:
                    seen.add(last_msg)
                    print(f"📩 Mummy: {last_msg}")

                    context = recall("facts about mother and recent messages", limit=5)
                    reply = generate_reply(last_msg, context)
                    print(f"💬 Replying: {reply}")

                    await send_message(page, reply)
                    remember(f"Mummy said: {last_msg}. I replied: {reply}")
                    print("✅ Sent!\n")

            except Exception as e:
                print(f"⚠️  Error: {e}")

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
