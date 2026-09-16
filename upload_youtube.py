import os
import re
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

# 🔴 Yahan pehle galat file name tha. Ab final merge hone wali file ka path diya hai
VIDEO_FILE = "final_output/Final_4K_Monetizable_Short.mp4"
META_FILE = "metadata.txt"  # Aapka auto_prompt .txt banata hai .json nahi
CATEGORY_ID = "24" # 24 = Entertainment

def parse_metadata():
    title = "रहस्यमयी कहानी 😱"
    description = ""
    tags = "shorts, viral, story"
    
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            try:
                title = re.search(r"TITLE:\s*(.*)", content).group(1).strip()
                desc_match = re.search(r"DESC:\s*([\s\S]*?)TAGS:", content)
                if desc_match:
                    description = desc_match.group(1).strip()
                else:
                    description = re.search(r"DESC:\s*([\s\S]*)", content).group(1).strip()
                tags = re.search(r"TAGS:\s*(.*)", content).group(1).strip()
            except Exception as e:
                print(f"⚠️ Error parsing metadata: {e}")
    return title, description, tags

def upload_video():
    if not os.path.exists(VIDEO_FILE):
        print(f"❌ Video file not found at: {VIDEO_FILE}")
        return
        
    title, description, tags_string = parse_metadata()
    tags = [tag.strip() for tag in tags_string.split(",")]
    
    # ⚠️ AI ALTERED CONTENT DISCLAIMER
    ai_disclaimer = (
        "यह एक ओरिजिनल कहानी है जिसे हमारी टीम द्वारा बहुत मेहनत से लिखा, डायरेक्ट और एडिट किया गया है। "
        "कहानी को विजुअली शानदार बनाने के लिए हमने क्रिएटिव एडिटिंग और AI (AI visuals & voice) का इस्तेमाल किया है। "
        "हमारा मकसद आपको बेहतरीन एंटरटेनमेंट देना है।\n\n"
    )
    
    final_description = ai_disclaimer + description

    print(f"📌 UPLOADING: {title}")
    
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.upload'])
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "categoryId": CATEGORY_ID,
            "title": title[:100],
            "description": final_description[:5000],
            "tags": tags[:15]
        },
        "status": {
            "privacyStatus": "public", 
            "selfDeclaredMadeForKids": False
        }
    }

    media_file = MediaFileUpload(VIDEO_FILE, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media_file)
    
    try:
        response = request.execute()
        print(f"✅ VIDEO SUCCESSFULLY UPLOADED! Link: https://youtu.be/{response['id']}")
    except Exception as e:
        print(f"❌ Upload Failed: {e}")

if __name__ == "__main__":
    upload_video()
