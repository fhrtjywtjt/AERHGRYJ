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
    except: pass
        
    fallbacks = [
        "google/gemini-2.0-flash-lite-preview-02-05:free", 
        "meta-llama/llama-3.3-70b-instruct:free",
        "cognitivecomputations/dolphin3.0-r1-mistral-24b:free"
    ]
    for fb in fallbacks:
        if fb not in models_list: models_list.append(fb)
    return models_list

def generate_realistic_agency_script():
    system_prompt = """You are a Master Cinematic Director and Screenwriter. 
    Output ONLY the requested raw format. NO tables, NO intro, NO markdown."""

    user_prompt = """Task: Write a REALISTIC (NOT Anime) persuasive Story Reel selling a YouTube Automation Service.

    🚨 VISUAL STYLE (CRITICAL): 
    - NO ANIME. NO CARTOONS. 
    - Must be "Ultra-realistic, 8k resolution, cinematic photography, photorealistic humans".
    
    🚨 CHARACTERS & CONVERSATION FLOW (CRITICAL):
    There are TWO characters having a CONTINUOUS CONVERSATION. 
    - Character 1: Rahul (A frustrated, tired 20-year-old Indian creator in a messy room).
    - Character 2: Vikram (A rich, successful 25-year-old Indian entrepreneur in a luxury studio).
    The dialogue MUST flow logically. Rahul asks a question or complains, and Vikram answers with a solution. 
    Example: 
    Scene 1 (Rahul): "Bhai, main din raat edit karta hoon, fir bhi views zero hain."
    Scene 2 (Vikram): "Kyunki tu sab khud kar raha hai. Smart log outsource karte hain."

    🚨 5-SECOND RULE:
    - Dialogue MUST BE exactly 8 to 12 WORDS per scene so it fits perfectly in 5 seconds.
    - Write exactly 10 to 12 scenes.

    🚨 FORMAT (4 columns separated by '|'):
    [Image Prompt (Ultra-realistic)] | [Video Prompt (Camera Angle)] | [On-Screen Text] | [Dialogue in Hindi with Voice Tag]

    Start the continuous conversation immediately:"""

    models = get_live_free_models()
    for attempt in range(1, 10):
        model_name = models[attempt % len(models)]
        print(f"🔄 Attempt {attempt} - Generating Realistic Script using {model_name}...")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.7 # Thoda kam temperature rakha hai taaki logic theek rahe
            )
            text = response.choices[0].message.content
            if text:
                valid_lines = [line.strip() for line in text.split('\n') if line.count('|') >= 3]
                if len(valid_lines) >= 8:
                    print(f"✅ Realistic Conversational Script Generated! (Scenes: {len(valid_lines)})")
                    return "\n".join(valid_lines[:15]) 
        except Exception as e:
            time.sleep(2)
    sys.exit(1)

def generate_metadata():
    system_prompt = "You are a Viral Instagram Reel & YouTube Shorts SEO Expert."
    user_prompt = """Generate high-converting metadata for a Realistic Story selling a YouTube Automation Service (Basic ₹499, Pro ₹999).
    Format exactly like this:
    IG_CAPTION: [3-line punchy caption telling them to DM 'GROW']
    IG_TAGS: #YouTubeAutomation #MakeMoneyOnline [Add 4 more]
    YT_TITLE: [Clickbaity YouTube Shorts Title with 🔥 emoji]
    YT_DESC: [Short description with link placeholder and automation details]
    YT_TAGS: youtube automation, make money online, [add 5 more comma separated]
    MUSIC: trending cinematic background music"""
    
    models = get_live_free_models()
    for model_name in models[:3]:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.7
            )
            text = response.choices[0].message.content
            return text
        except:
            time.sleep(1)
            
    return "IG_CAPTION: DM GROW\nIG_TAGS: #YT\nYT_TITLE: How to make money 🔥\nYT_DESC: DM us\nYT_TAGS: money\nMUSIC: cinematic beat"

if __name__ == "__main__":
    script_output = generate_realistic_agency_script()
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(script_output + "\n")
        
    meta_text = generate_metadata()
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        f.write(meta_text)
        
    try:
        music = re.search(r"MUSIC:\s*(.*)", meta_text).group(1).strip()
    except: music = "cinematic beat"
    
    with open("music_prompt.txt", "w", encoding="utf-8") as f:
        f.write(music)
        
    print("✅ All Brain tasks completed (Realistic Humans & Logical Conversation Ready)!")
