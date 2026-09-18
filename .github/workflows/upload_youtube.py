import os
import re
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

VIDEO_FILE = "final_output/Final_Agency_Reel.mp4"
META_FILE = "metadata.txt"

def get_yt_metadata():
    title = "Best YouTube Automation Agency 🔥 #shorts"
    desc = "Start your automated YouTube journey with us! DM 'GROW' on Instagram."
    tags = ["youtube automation", "make money online", "faceless channel"]
    
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            try:
                title = re.search(r"YT_TITLE:\s*(.*)", content).group(1).strip()
                desc = re.search(r"YT_DESC:\s*(.*)", content).group(1).strip()
                raw_tags = re.search(r"YT_TAGS:\s*(.*)", content).group(1).strip()
                tags = [t.strip() for t in raw_tags.split(',')]
            except: pass
    
    # Ensure #shorts is in title for maximum reach
    if "#shorts" not in title.lower():
        title += " #shorts"
        
    return title, desc, tags

def upload_to_youtube():
    # 🔴 GitHub Secrets se OAuth Token lena
    yt_creds_json = os.getenv("YT_OAUTH_JSON")
    
    if not yt_creds_json:
        print("❌ ERROR: YT_OAUTH_JSON secret is missing! Skipped YouTube Upload.")
        return

    if not os.path.exists(VIDEO_FILE):
        print("❌ ERROR: Final Video not found!")
        return

    title, desc, tags = get_yt_metadata()
    print(f"🎬 Preparing to upload to YouTube Shorts: {title}")

    try:
        # JSON string se Credentials object banana
        creds_data = json.loads(yt_creds_json)
        credentials = Credentials.from_authorized_user_info(creds_data)
        
        youtube = build("youtube", "v3", credentials=credentials)

        body = {
            "snippet": {
                "title": title,
                "description": desc,
                "tags": tags,
                "categoryId": "27" # Education/Tech category
            },
            "status": {
                "privacyStatus": "public", # Direct public upload
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(VIDEO_FILE, chunksize=-1, resumable=True, mimetype="video/mp4")

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = request.execute()
        print(f"✅ BOOM! YouTube Shorts Uploaded Successfully!")
        print(f"🎥 Video URL: https://youtube.com/shorts/{response['id']}")

    except Exception as e:
        print(f"❌ YouTube Upload Failed: {e}")

if __name__ == "__main__":
    upload_to_youtube()
