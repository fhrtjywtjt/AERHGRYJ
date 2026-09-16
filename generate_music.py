import os
import time
import requests

API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
HF_TOKEN = os.getenv("HF_TOKEN")

def generate_bgm():
    if not HF_TOKEN:
        print("⚠️ HF_TOKEN is missing! BGM skip kar rahe hain.")
        return

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    prompt = "sad cinematic emotional piano"
    if os.path.exists("music_prompt.txt"):
        with open("music_prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read().strip()
            
    print(f"🎵 Sending request to AI API for Music: '{prompt}'")
    
    payload = {"inputs": prompt}
    max_retries = 3 
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                with open("bgm.wav", "wb") as f:
                    f.write(response.content)
                print("✅ 100% Original AI Background Music Generated Successfully!")
                return
            else:
                print(f"⏳ API is loading/busy (Attempt {attempt}). Waiting 20 seconds...")
                time.sleep(20)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(10)
            
    print("❌ Failed to generate music this time. Video will render without BGM.")

if __name__ == "__main__":
    generate_bgm()
