import os
import re
import json
import base64
from instagrapi import Client

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

def upload_reel():
    cookie_b64 = os.getenv("IG_COOKIES_BASE64")

    if not cookie_b64:
        print("❌ ERROR: IG_COOKIES_BASE64 secret is missing!")
        return

    if not os.path.exists(VIDEO_FILE):
        print(f"❌ ERROR: Video file not found at {VIDEO_FILE}")
        return

    # 1. Decode Base64 and find 'sessionid' from the Cookie JSON
    sessionid = None
    try:
        cookies_json = base64.b64decode(cookie_b64).decode("utf-8")
        cookies_list = json.loads(cookies_json)
        
        for cookie in cookies_list:
            if cookie.get("name") == "sessionid":
                sessionid = cookie.get("value")
                break
                
        if not sessionid:
            print("❌ ERROR: 'sessionid' nahi mila tumhari cookies mein. Nayi cookie export karo!")
            return
    except Exception as e:
        print(f"❌ ERROR parsing cookies: {e}")
        return

    final_caption = get_metadata()
    print("🚀 Starting Instagram Auto-Upload via Instagrapi (Cookie Session)...")

    cl = Client()
    try:
        print("⏳ Logging into Instagram using Session ID...")
        # 2. Login using the extracted sessionid
        cl.login_by_sessionid(sessionid)
        print("✅ Login Successful from Cookies!")
        
        print("⏳ Uploading Reel... Please wait, this might take a minute.")
        media = cl.clip_upload(
            VIDEO_FILE,
            final_caption
        )
        print(f"✅ BOOM! REEL UPLOADED SUCCESSFULLY! Media ID: {media.pk}")
        
    except Exception as e:
        print(f"❌ Instagram Upload Failed: {e}")

if __name__ == "__main__":
    upload_reel()
