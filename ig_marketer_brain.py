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

def generate_anime_agency_script():
    system_prompt = """You are a Master Anime Director, Cinematographer, and a clever Marketer. 
    Output ONLY the requested raw format. NO tables, NO intro, NO markdown."""

    user_prompt = """Task: Write a HIGHLY DETAILED, persuasive Anime Story Reel (around 1 to 1.5 minutes long) selling our YouTube Automation Service.

    🚨 CRITICAL 5-SECOND RULE FOR AI (READ CAREFULLY):
    - Our video generator ONLY makes 5-SECOND CLIPS per scene.
    - Therefore, the Voiceover Dialogue for EVERY SINGLE SCENE MUST be short enough to be spoken in 5 seconds (MAXIMUM 10 to 15 WORDS per scene).
    - If you have a lot to say, DO NOT write long dialogues in one scene. Instead, break the story across MANY scenes (Generate 10 to 15 scenes total).

    🚨 STORY & AGENCY PITCH RULES:
    1. THE HOOK: Scene 1 must be an extreme 5-second hook (e.g., "Mera dost kal 1 lakh rupaye cash laya...").
    2. THE DETAIL: Make the story interesting. Talk about the struggle of editing, failing algorithms, and how "Smart people outsource to Expert Teams". Build trust.
    3. THE PRICING: Explain the value. Basic Plan ₹499/month (1 Video Daily), Pro Plan ₹999/month (2 Videos Daily). Make it sound like an absolute steal. Tell them to DM "GROW".
    4. VISUAL CONSISTENCY: Invent ONE specific anime character and ONE background. Copy-paste this EXACT description into EVERY Image Prompt.
    5. CAMERA & MOTION: Every video prompt MUST include "Character talking, lips moving, blinking" AND a "Dynamic Camera Angle" (e.g., Fast zoom, slow pan, tracking shot).

    🚨 FORMAT (4 columns separated by '|'):
    [Image Prompt] | [Video Prompt (Include Camera Angle)] | [On-Screen Text] | [Voiceover Dialogue in Hindi (STRICTLY 10-15 WORDS MAX)]

    Generate 10 to 15 scenes to make a detailed, convincing story. Keep dialogues SHORT per scene. Start immediately:"""

    models = get_live_free_models()
    
    for attempt in range(1, 10):
        model_name = models[attempt % len(models)]
        print(f"🔄 Attempt {attempt} - Generating Detailed Anime Pitch using {model_name}...")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.9
            )
            text = response.choices[0].message.content
            
            if text:
                valid_lines = [line.strip() for line in text.split('\n') if line.count('|') >= 3]
                # Ab hum 5 nahi, balki 10 se 15 scenes tak allow karenge (matlab 1 min+ video)
                if len(valid_lines) >= 8:
                    print(f"✅ Detailed Script Generated Successfully! (Total Scenes: {len(valid_lines)})")
                    return "\n".join(valid_lines[:15]) # Max 15 scenes (1 min 15 sec reel)
        except Exception as e:
            print(f"⚠️ Model failed: {e}")
            time.sleep(2)
            
    print("❌ ERROR: Failed to generate script.")
    sys.exit(1)

def generate_ig_metadata():
    system_prompt = "You are a Viral Instagram Reel SEO Expert."
    user_prompt = """Generate a high-converting Instagram Reel caption for an Anime Story reel selling a YouTube Automation Service (Basic ₹499, Pro ₹999).
    Format exactly like this:
    CAPTION: [Write a 3-line punchy caption telling them to DM 'GROW']
    TAGS: #AnimeStory #YouTubeAutomation #MakeMoneyOnline #PassiveIncome [Add 4 more]
    MUSIC: trendy anime lofi beat"""
    
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
            
    return "Stop scrolling and start earning! Our YouTube Automation team handles everything. 🚀 DM 'GROW' for details!", "#YouTubeAutomation #MakeMoneyOnline #FacelessChannel #PassiveIncome", "lofi chill anime background beat"

if __name__ == "__main__":
    print("🧠 Starting LONG-FORM Cinematic Anime Brain...")
    
    script_output = generate_anime_agency_script()
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(script_output + "\n")
        
    caption, tags, music = generate_ig_metadata()
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        f.write(f"CAPTION: {caption}\nTAGS: {tags}\n")
        
    with open("music_prompt.txt", "w", encoding="utf-8") as f:
        f.write(music)
        
    print("✅ All Brain tasks completed! Ready for Epic Anime Generation.")
