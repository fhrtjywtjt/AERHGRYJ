import asyncio
import os
import sys
import time
import requests
from playwright.async_api import async_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

IMAGE_DIR = "scene_images"
VIDEO_DIR = "generated_videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

def send_telegram_photo(photo_path, caption=""):
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as file:
                requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": file}, timeout=20)
    except: pass

def send_telegram_video(video_path, caption=""):
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    try:
        if os.path.exists(video_path):
            with open(video_path, "rb") as file:
                requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"video": file}, timeout=120)
    except: pass

async def live_screenshot_monitor(page, machine_id, stop_event):
    shot_count = 1
    while not stop_event.is_set():
        await asyncio.sleep(25) 
        if stop_event.is_set(): break
        try:
            shot_path = os.path.join(VIDEO_DIR, f"live_video_m{machine_id}.png")
            await page.screenshot(path=shot_path, timeout=5000)
            send_telegram_photo(shot_path, f"🎬 [Machine {machine_id}] Upsampler Status #{shot_count}")
            shot_count += 1
        except: pass

def read_combined_prompts():
    if not os.path.exists("prompts.txt"):
        return {}
    with open("prompts.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    combined_prompts = {}
    for idx, line in enumerate(lines, start=1):
        parts = line.split("|")
        # Column 2 (Video Prompt)
        vid_prompt = parts[1].strip() if len(parts) >= 2 else "Cinematic motion"
        # Column 4 (Dialogue)
        dialogue = parts[3].strip() if len(parts) >= 4 else ""
        
        # 🔴 MAGIC YAHAN HAI: Dono ko jod kar 1 hi text banaya jo dabbe mein paste hoga
        if dialogue:
            combined_prompts[idx] = f"{vid_prompt} | Character speaking dialogue: {dialogue}"
        else:
            combined_prompts[idx] = vid_prompt
            
    return combined_prompts


async def main():
    machine_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    combined_prompts = read_combined_prompts()
    
    img_name = f"scene_{machine_id}.jpg"
    img_path = os.path.join(IMAGE_DIR, img_name)

    if not os.path.exists(img_path):
        print(f"⚠️ Image {img_name} not found! Fallback to bing folder...")
        img_path = os.path.join("bing_automated_images", f"Generated_Image_{machine_id}.jpg")
        if not os.path.exists(img_path):
             print(f"❌ Image not found anywhere for Machine {machine_id}.")
             return

    # Ye wo final text hai jo Upsampler ke dabbe mein jayega
    final_prompt_text = combined_prompts.get(machine_id, "Cinematic slow motion movement, character talking")
    
    print(f"🖥️ Machine {machine_id} pasting FULL PROMPT (Video + Dialogue) in one box...")

    async with async_playwright() as p:
        max_browser_restarts = 10  
        
        for attempt in range(1, max_browser_restarts + 1):
            print(f"\n🔄 [Attempt {attempt}/{max_browser_restarts}] Opening FRESH Browser...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(accept_downloads=True, viewport={'width': 1280, 'height': 720})
            page = await context.new_page()

            stop_tracker = asyncio.Event()
            asyncio.create_task(live_screenshot_monitor(page, machine_id, stop_tracker))

            try:
                await page.goto("https://upsampler.com/free-video-generator-no-signup", wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(3)

                try:
                    accept_btn = page.get_by_role("button", name="Accept")
                    if await accept_btn.is_visible(timeout=3000): await accept_btn.click()
                except: pass

                # 1. Image Upload
                file_input = page.locator("input[type='file']").first
                await file_input.set_input_files(img_path)
                await asyncio.sleep(3)

                # 2. Paste Full Text in the SINGLE Prompt Box
                # (Aapki photo ke hisaab se pehla textarea hi target banega)
                print(f"✍️ Typing Prompt: {final_prompt_text[:50]}...")
                selectors = ["textarea", "input[placeholder*='prompt' i]", "textarea[placeholder*='prompt' i]"]
                for sel in selectors:
                    loc = page.locator(sel).first
                    if await loc.is_visible(timeout=2000):
                        try:
                            await loc.fill(final_prompt_text)
                            break
                        except: continue

                # 3. Set Duration 5 Seconds
                try:
                    duration_dropdown = page.get_by_text("3 seconds")
                    if await duration_dropdown.is_visible(timeout=3000):
                        await duration_dropdown.click()
                        await asyncio.sleep(1)
                        await page.get_by_text("5 seconds", exact=True).click()
                except: pass

                # 4. Generate
                generate_btn = page.get_by_role("button", name="Generate Video", exact=True)
                if not await generate_btn.is_visible(timeout=3000):
                    generate_btn = page.locator("button:has-text('Generate')").first

                if await generate_btn.is_visible():
                    await generate_btn.click()
                
                await asyncio.sleep(8)

                gpu_error = page.get_by_text("free GPUs are in high demand", exact=False)
                ip_limit_error = page.get_by_text("used up today", exact=False)

                if await ip_limit_error.is_visible() or await gpu_error.is_visible():
                    print(f"⚠️ Limit/GPU Error on Attempt {attempt}! Restarting...")
                    stop_tracker.set()
                    await browser.close()
                    await asyncio.sleep(5)
                    continue 

                print("✅ Generation Started! Waiting for video...")
                see_result_btn = page.locator("button:has-text('See result'), a:has-text('See result')").first
                video_element = page.locator("video:not([src*='_static'])").first

                start_time = time.time()
                video_ready = False

                while time.time() - start_time < 360:
                    await asyncio.sleep(5)
                    if await ip_limit_error.is_visible() or await gpu_error.is_visible(): break 
                         
                    if await see_result_btn.is_visible():
                        await see_result_btn.click()
                        await asyncio.sleep(2)

                    if await video_element.count() > 0 and await video_element.is_visible():
                        video_ready = True
                        break

                if video_ready:
                    stop_tracker.set() 
                    await asyncio.sleep(2)
                    
                    video_filename = os.path.join(VIDEO_DIR, f"video_{machine_id}.mp4")
                    video_src = await video_element.get_attribute("src")

                    if video_src:
                        download_btn = page.locator("a:has-text('Download'), button:has-text('Download')").first
                        if await download_btn.is_visible():
                            async with page.expect_download() as download_info:
                                await download_btn.click()
                            download = await download_info.value
                            await download.save_as(video_filename)
                        else:
                            v_data = requests.get(video_src).content
                            with open(video_filename, "wb") as f:
                                f.write(v_data)

                        print(f"🎉 Video #{machine_id} Downloaded Successfully!")
                        send_telegram_video(video_filename, f"🎬 Scene #{machine_id} Video Ready!")
                        await browser.close()
                        return 

            except Exception as e:
                print(f"⚠️ Something crashed: {e}. Restarting browser...")
            
            stop_tracker.set()
            await browser.close()
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
