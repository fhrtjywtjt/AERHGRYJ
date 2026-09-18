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

    user_prompt = """Task: Write a HIGHLY DETAILED, persuasive Anime Story Reel selling our YouTube Automation Service.

    🚨 CRITICAL 5-SECOND RULE FOR AI (READ CAREFULLY):
    - Our video generator ONLY makes 5-SECOND CLIPS per scene.
    - Therefore, the Character Dialogue for EVERY SINGLE SCENE MUST be extremely short.
    - STRICT LIMIT: MAXIMUM 5 TO 8 WORDS per scene! If it's longer, the video will cut out.
    - Break the story across 10 to 15 scenes total.

    🚨 STORY & AGENCY PITCH RULES:
    1. THE HOOK: Scene 1 must be an extreme hook (e.g., "Mera dost kal 1 lakh laya...").
    2. THE DETAIL: Talk about the struggle of editing and failing algorithms. "Smart people outsource".
    3. THE PRICING: Basic Plan ₹499/mo (1 Video Daily), Pro Plan ₹999/mo (2 Videos). DM "GROW".
    4. VISUALS: Invent ONE specific anime character and ONE background. Put this in EVERY Image Prompt.
    5. CAMERA: Every video prompt MUST include "Character talking, lips moving" AND a "Dynamic Camera Angle".

    🚨 FORMAT (4 columns separated by '|'):
    [Image Prompt] | [Video Prompt (Camera Angle)] | [On-Screen Text] | [Dialogue in Hindi (STRICTLY 5-8 WORDS)]

    Start immediately:"""

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
                if len(valid_lines) >= 8:
                    print(f"✅ Detailed Script Generated Successfully! (Total Scenes: {len(valid_lines)})")
                    return "\n".join(valid_lines[:15]) 
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
        
    print("✅ All Brain tasks completed!")
