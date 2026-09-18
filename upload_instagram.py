import os
import re
import json
import base64
import subprocess
from instagrapi import Client

VIDEO_FILE = "final_output/Final_Agency_Reel.mp4"
THUMB_FILE = "final_output/thumb.jpg"
META_FILE = "metadata.txt"

def get_metadata():
    caption = "Stop working manually. Get our YouTube Automation setup! DM 'GROW'."
    tags = "#YouTubeAutomation #PassiveIncome"
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            try:
                caption = re.search(r"IG_CAPTION:\s*(.*)", content).group(1).strip()
                tags = re.search(r"IG_TAGS:\s*(.*)", content).group(1).strip()
            except: pass
    return f"{caption}\n\n{tags}"

def create_thumbnail():
    print("📸 FFmpeg se Thumbnail nikal rahe hain...")
    try:
        # Video ka pehla frame nikal kar thumb.jpg bana dega
        subprocess.run(
            ["ffmpeg", "-y", "-i", VIDEO_FILE, "-vframes", "1", "-q:v", "2", THUMB_FILE], 
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print("✅ Thumbnail ready!")
    except Exception as e:
        print(f"⚠️ Thumbnail fail: {e}")

def upload_reel():
    cookie_b64 = os.getenv("IG_COOKIES_BASE64")

    if not cookie_b64:
        print("❌ ERROR: IG_COOKIES_BASE64 secret is missing!")
        return

    if not os.path.exists(VIDEO_FILE):
        print(f"❌ ERROR: Video file not found at {VIDEO_FILE}")
        return

    sessionid = None
    try:
        cookies_json = base64.b64decode(cookie_b64).decode("utf-8")
        cookies_list = json.loads(cookies_json)
        
        for cookie in cookies_list:
            if cookie.get("name") == "sessionid":
                sessionid = cookie.get("value")
                break
                
        if not sessionid:
            print("❌ ERROR: 'sessionid' nahi mila cookies mein.")
            return
    except Exception as e:
        print(f"❌ ERROR parsing cookies: {e}")
        return

    final_caption = get_metadata()
    create_thumbnail() # Thumbnail banaya

    print("🚀 Starting Instagram Auto-Upload...")
    cl = Client()
    
    try:
        cl.login_by_sessionid(sessionid)
        print("✅ IG Login Successful!")
        
        # Instagram ko video ke sath thumbnail pass kar diya, ab wo moviepy nahi mangega!
        if os.path.exists(THUMB_FILE):
            media = cl.clip_upload(VIDEO_FILE, final_caption, thumbnail=THUMB_FILE)
        else:
            media = cl.clip_upload(VIDEO_FILE, final_caption)
            
        print(f"✅ BOOM! REEL UPLOADED! Media ID: {media.pk}")
        
    except Exception as e:
        print(f"❌ Instagram Upload Failed: {e}")
        raise e 

if __name__ == "__main__":
    upload_reel()
