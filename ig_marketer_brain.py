import os
import sys
import time
import json
import urllib.request
import re
from openai import OpenAI

PROMPT_FILE = "prompts.txt"
METADATA_FILE = "metadata.txt"

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY is missing!")
    sys.exit(1)

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

def get_live_free_models():
    models_list = []
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/models")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
        models_list = [m["id"] for m in data.get("data", []) if m.get("pricing", {}).get("prompt") == "0" and m.get("pricing", {}).get("completion") == "0"]
    except:
        pass
        
    fallbacks = [
        "google/gemini-2.0-flash-lite-preview-02-05:free", 
        "meta-llama/llama-3.3-70b-instruct:free",
        "cognitivecomputations/dolphin3.0-r1-mistral-24b:free"
    ]
    for fb in fallbacks:
        if fb not in models_list:
            models_list.append(fb)
    return models_list

def generate_agency_script():
    system_prompt = """You are a highly aggressive, millionaire Digital Marketing Agency Owner. 
    Your goal is to SELL your 'YouTube Automation Service' via Instagram Reels. 
    Output ONLY the requested raw format. NO tables, NO intro, NO markdown."""

    user_prompt = """Task: Write a 5-scene viral Instagram Reel script to sell our Faceless YouTube Video Creation service.

    🚨 OUR PRICING & PITCH (MUST INCLUDE IN SCENE 4 and 5):
    - Basic Plan: ₹499/month (We make 1 Video Daily)
    - Pro Plan: ₹999/month (We make 2 Videos Daily - Morning & Evening)
    - CTA: "DM me 'GROW' to start."

    🚨 MARKETING ANGLES (Pick ONE randomly for this script):
    1. Pain: Stop editing manually, you are wasting time. Hire our expert team.
    2. Flex: People are making lakhs with faceless channels. We do the work, you make money.
    3. Monetization: 1000 Subs and 4000 hours not completing? Our premium videos will do it.

    🚨 FORMAT RULES (Exactly 4 columns separated by '|'):
    [Cinematic Image Prompt] | [Motion Prompt for Video] | [On-Screen Text in Hinglish] | [Voiceover Speech in Hinglish]

    EXAMPLE:
    A dark luxury office with a man looking stressed at a laptop, cinematic lighting | Slow zoom in, moody shadows | Views nahi aa rahe? | Kya tum bhi roz ghanto editing karke thak gaye ho aur views fir bhi zero aate hain?
    Matrix style glowing green code, neon lights | Fast matrix code falling | Stop working like a robot | Toh manual kaam karna band karo aur smart bano. Humari expert team ko apna channel do.
    A briefcase full of money and a gold play button | Shiny gold glowing | Basic ₹499 (1 Vid/Day) | Humari agency aapko degi ready videos. Basic plan sirf char so ninyanve rupaye mahina, roz ek video.
    A glowing neon sign saying DM NOW | Flashing lights | DM 'GROW' to start | Pro plan mein roz do videos. Abhi DM karo GROW aur apna YouTube empire shuru karo.

    Generate exactly 5 scenes. Start immediately with Scene 1:"""

    models = get_live_free_models()
    
    for attempt in range(1, 10):
        model_name = models[attempt % len(models)]
        print(f"🔄 Attempt {attempt} - Generating Agency Pitch using {model_name}...")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.85
            )
            text = response.choices[0].message.content
            
            if text:
                valid_lines = [line.strip() for line in text.split('\n') if line.count('|') >= 3]
                if len(valid_lines) >= 4:
                    print("✅ Marketing Script Generated Successfully!")
                    return "\n".join(valid_lines[:5])
        except Exception as e:
            print(f"⚠️ Model failed: {e}")
            time.sleep(2)
            
    print("❌ ERROR: Failed to generate script.")
    sys.exit(1)

def generate_ig_metadata():
    system_prompt = "You are a Viral Instagram Reel SEO Expert."
    user_prompt = """Generate a high-converting Instagram Reel caption to sell a YouTube Automation Service (Basic ₹499, Pro ₹999).
    Format exactly like this:
    CAPTION: [Write a 3-line punchy caption telling them to DM 'GROW']
    TAGS: #FacelessYouTube #MakeMoneyOnline #YouTubeAutomation #PassiveIncome [Add 4 more]
    MUSIC: aggressive phonk motivational bass"""
    
    models = get_live_free_models()
    for model_name in models[:3]:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.7
            )
            text = response.choices[0].message.content
            
            caption = re.search(r"CAPTION:\s*([\s\S]*?)TAGS:", text).group(1).strip()
            tags = re.search(r"TAGS:\s*(.*)", text).group(1).strip()
            music = re.search(r"MUSIC:\s*(.*)", text).group(1).strip()
            return caption, tags, music
        except:
            time.sleep(1)
            
    return "Stop editing manually! Let our expert team handle your YouTube channel. 🚀 DM 'GROW' for details!", "#YouTubeAutomation #MakeMoneyOnline #FacelessChannel #PassiveIncome", "dark intense motivational bass"

if __name__ == "__main__":
    print("🧠 Starting Agency Brain...")
    
    script_output = generate_agency_script()
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(script_output + "\n")
        
    caption, tags, music = generate_ig_metadata()
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        f.write(f"CAPTION: {caption}\nTAGS: {tags}\n")
        
    with open("music_prompt.txt", "w", encoding="utf-8") as f:
        f.write(music)
        
    print("✅ All Brain tasks completed! No story.txt needed.")
