# whatsapp_tool.py — Layer 4: send a message via direct Playwright (no LLM needed)
import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

PROFILE_DIR = os.path.join(os.path.dirname(__file__), ".wa_profile")


async def send_whatsapp(contact: str, message: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--no-sandbox"],
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

        # Wait for either QR code or chat list (first run = QR scan needed)
        print("Waiting for WhatsApp Web to load...")
        await page.wait_for_selector(
            '#pane-side, [data-testid="qrcode"]',
            timeout=60_000,
        )

        # If QR code is shown, wait for user to scan
        if await page.locator('[data-testid="qrcode"]').count() > 0:
            print("\n>>> Scan the WhatsApp QR code in the browser, then press Enter here...")
            input()
            await page.wait_for_selector("#pane-side", timeout=60_000)

        print(f"Searching for contact: {contact}")

        # Give the app a moment to fully render
        await page.wait_for_timeout(3000)

        # Use stable attributes from debug: data-tab="3" + role="textbox"
        search = page.locator('input[data-tab="3"][role="textbox"]')
        await search.wait_for(timeout=10_000)
        await search.click()
        await search.fill(contact)
        await page.wait_for_timeout(2000)

        await search.click()
        await search.fill(contact)
        await page.wait_for_timeout(2000)

        # Click the first matching result
        result = page.get_by_text(contact, exact=True).first
        if await result.count() == 0:
            result = page.get_by_text(contact).first
        await result.click()
        await page.wait_for_timeout(1000)

        # Type message into the compose box
        compose = page.locator('div[contenteditable="true"][data-tab="10"], div[contenteditable="true"][title="Type a message"], footer div[contenteditable="true"]').first
        await compose.wait_for(timeout=10_000)
        await compose.click()
        await compose.fill(message)
        await page.wait_for_timeout(500)

        # Send
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)

        print("Message sent.")
        await browser.close()
        return "sent"
