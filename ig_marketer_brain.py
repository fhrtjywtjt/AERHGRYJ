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
    fallbacks = ["google/gemini-2.0-flash-lite-preview-02-05:free", "meta-llama/llama-3.3-70b-instruct:free"]
    for fb in fallbacks:
        if fb not in models_list: models_list.append(fb)
    return models_list

def generate_cinematic_agency_script():
    system_prompt = """You are an Elite Cinematic Director. Your job is to create a 100% REALISTIC, seamless video script. Output ONLY the raw format. NO markdown."""

    user_prompt = """Task: Write a REALISTIC persuasive Story Reel selling a YouTube Automation Service.

    🚨 RULE 1: STRICT VISUAL CONSISTENCY (NO AI HALLUCINATIONS)
    To make it look 100% real, the background and outfits MUST NEVER CHANGE randomly.
    - Character 1 (Rahul): 20-year-old Indian male, wearing a faded black hoodie.
    - Location A (Rahul's Room): "dimly lit messy bedroom, RGB led strips, dual monitors showing zero views".
    - Character 2 (Vikram): 25-year-old Indian entrepreneur, wearing a crisp navy blue suit.
    - Location B (Vikram's Office): "bright luxury glass office, panoramic city view, clean mahogany desk".
    COPY-PASTE THESE EXACT DESCRIPTIONS in every single image prompt for that character. Do NOT invent new backgrounds.

    🚨 RULE 2: SEAMLESS "INVISIBLE" CUTS
    To hide the fact that we generate 5-second clips, the camera motion must match. 
    In the Video Prompt, always use continuous motion like "Slow continuous pan right" or "Slow continuous push-in". When clips join, the continuous motion hides the cut.

    🚨 RULE 3: LOGICAL CONVERSATION
    Rahul asks a frustrated question -> Vikram answers with the Agency solution. 
    Exactly 10 to 12 words per scene. Hindi dialogue.

    🚨 FORMAT (4 columns separated by '|'):
    [Image Prompt (Exact outfit & Exact location locked)] | [Video Prompt (Continuous camera motion)] | [On-Screen Text] | [Dialogue in Hindi (10-12 words)]

    Start the continuous conversation immediately:"""

    models = get_live_free_models()
    for attempt in range(1, 10):
        model_name = models[attempt % len(models)]
        print(f"🔄 Generating Masterpiece Script using {model_name}...")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.4 # VERY LOW temperature so it doesn't randomly change backgrounds
            )
            text = response.choices[0].message.content
            if text:
                valid_lines = [line.strip() for line in text.split('\n') if line.count('|') >= 3]
                if len(valid_lines) >= 8:
                    print(f"✅ Masterpiece Script Generated! (Scenes: {len(valid_lines)})")
                    return "\n".join(valid_lines[:12]) 
        except Exception as e:
            time.sleep(2)
    sys.exit(1)

def generate_metadata():
    return "IG_CAPTION: Stop wasting time editing. DM GROW to start your automated channel today! 🚀\nIG_TAGS: #YouTubeAutomation #MakeMoneyOnline #CreatorEconomy\nYT_TITLE: Why YouTubers Fail (And How To Fix It) 🔥 #shorts\nYT_DESC: Get a full team for your channel. DM us 'GROW' on Instagram!\nYT_TAGS: youtube automation, video editing, make money online\nMUSIC: deep cinematic bass pulse"

if __name__ == "__main__":
    script_output = generate_cinematic_agency_script()
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(script_output + "\n")
        
    meta_text = generate_metadata()
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        f.write(meta_text)
    
    with open("music_prompt.txt", "w", encoding="utf-8") as f:
        f.write("deep cinematic bass pulse")
        
    print("✅ Director's Brain tasks completed! Locked Backgrounds & Seamless Cuts Ready.")
