import os
import json
import base64
import asyncio
import re
from playwright.async_api import async_playwright

VIDEO_FILE = "final_output/Final_Agency_Reel.mp4"
META_FILE = "metadata.txt"

def get_metadata():
    caption = "Stop working manually. Get our YouTube Automation setup! DM 'GROW' for details."
    tags = "#YouTubeAutomation #PassiveIncome"
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            try:
                caption = re.search(r"CAPTION:\s*(.*)", content).group(1).strip()
                tags = re.search(r"TAGS:\s*(.*)", content).group(1).strip()
            except: pass
    return f"{caption}\n\n{tags}"

async def upload_to_instagram():
    cookie_b64 = os.getenv("IG_COOKIES_BASE64")
    if not cookie_b64:
        print("❌ ERROR: IG_COOKIES_BASE64 secret is missing!")
        return

    # Base64 cookies ko file me save karna
    with open("ig_cookies.json", "w") as f:
        f.write(base64.b64decode(cookie_b64).decode("utf-8"))

    final_caption = get_metadata()
    print("🚀 Starting Instagram Auto-Upload...")

    async with async_playwright() as p:
        # iPhone 13 jaisa mobile browser khulega taaki IG block na kare
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state="ig_cookies.json",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()

        try:
            await page.goto("https://www.instagram.com/", timeout=60000)
            await asyncio.sleep(5)
            
            # Plus icon / New Post pe click
            await page.locator("[aria-label='New post']").click()
            await asyncio.sleep(2)
            
            # File Upload
            file_input = page.locator("input[accept^='video/']")
            await file_input.set_input_files(VIDEO_FILE)
            await asyncio.sleep(5)

            # Next Buttons
            await page.get_by_text("Next").click()
            await asyncio.sleep(2)
            await page.get_by_text("Next").click()
            await asyncio.sleep(2)

            # Type Caption
            await page.locator("textarea[aria-label='Write a caption...']").fill(final_caption)
            await asyncio.sleep(3)

            # Share Button
            await page.get_by_text("Share").click()
            print("⏳ Uploading to IG Servers... Please wait.")
            
            # Wait for upload to complete
            await page.wait_for_selector("text='Your reel has been shared.'", timeout=90000)
            print("✅ BOOM! REEL UPLOADED TO INSTAGRAM SUCCESSFULLY!")
            
        except Exception as e:
            print(f"❌ Instagram Upload Failed: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload_to_instagram())
