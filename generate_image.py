import sys
import os
import asyncio
import requests
from playwright.async_api import async_playwright

SAVE_FOLDER = "scene_images"
os.makedirs(SAVE_FOLDER, exist_ok=True)

async def generate_single_image(prompt_text):
    out_img_path = os.path.join(SAVE_FOLDER, "scene_1.jpg")
    
    async with async_playwright() as p:
        for attempt in range(1, 6):
            print(f"🔄 Attempt {attempt}/5: Opening Bing...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1280, 'height': 720})
            page = await context.new_page()
            
            try:
                await page.goto("https://www.bing.com/images/create", timeout=60000)
                await asyncio.sleep(3)
                await page.locator("textarea, input[placeholder*='Describe']").first.fill(prompt_text)
                await page.locator("button:has-text('Generate'), button:has-text('Create')").first.click()
                print("⏳ Waiting for Bing generation...")
                
                download_btn = page.locator("button[title='Download']:not([disabled]), a:has-text('Download')").first
                await download_btn.wait_for(state="visible", timeout=90000)
                await asyncio.sleep(5) 
                
                async with page.expect_download() as download_info:
                    await download_btn.click()
                
                download = await download_info.value
                await download.save_as(out_img_path)
                print("✅ Image Generated Successfully!")
                await browser.close()
                return True
                
            except Exception as e:
                print(f"⚠️ Error: {str(e)[:50]}... Retrying!")
                await browser.close()
                await asyncio.sleep(4)
                
        print("❌ Failed to generate image.")
        return False

async def main():
    if os.path.exists("prompts.txt"):
        with open("prompts.txt", "r", encoding="utf-8") as f:
            prompt = f.read().strip()
    else:
        prompt = "Cinematic 8k vertical shot of luxury car"
        
    await generate_single_image(prompt)

if __name__ == "__main__":
    asyncio.run(main())
