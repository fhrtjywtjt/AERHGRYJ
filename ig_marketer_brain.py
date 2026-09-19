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
    system_prompt = "You are a Master Film Director. Output ONLY raw format. NO markdown."
    
    user_prompt = """Task: Write a REALISTIC persuasive Story Reel selling a YouTube Automation Service.

    🚨 PROBLEM TO SOLVE: AI Face inconsistency & Boring visual pacing.
    SOLUTION: Use the "A-Roll / B-Roll" technique. DO NOT show the character's face in every scene.
    Alternate between a Face shot (A-Roll) and an Object/Environment shot (B-Roll) where the face is NOT visible.

    🚨 CHARACTER DETAILS (EXTREMELY SPECIFIC TO KEEP FACE CONSISTENT):
    - Rahul (A-Roll): "20-year-old Indian male, wearing thick black square glasses, messy hair, faded black hoodie. Dimly lit bedroom."
    - Rahul (B-Roll examples): "Close up of a hand holding a glowing smartphone", "Close up of a computer monitor showing a red downward arrow graph".
    - Vikram (A-Roll): "25-year-old Indian entrepreneur, neat beard, wearing a crisp navy blue suit, gold watch. Luxury office."
    - Vikram (B-Roll examples): "Close up of an iPad showing 100k subscribers", "Coffee cup on a mahogany desk with a city view behind".

    🚨 DIALOGUE RULES (PREVENT AI MUMBLING):
    - Use VERY SIMPLE Hindi words. Avoid complex words. (e.g., Use "Views" instead of "वृद्धि", Use "Idea" instead of "विचार").
    - Dialogue must be exactly 8 to 12 words.
    
    🚨 FORMAT (4 columns separated by '|'):
    [Image Prompt] | [Video Prompt (Continuous camera motion)] | [On-Screen Text] | [Dialogue in Simple Hindi]

    Write a 10-scene logical conversation, alternating between Face shots and B-Roll shots:"""

    models = get_live_free_models()
    for attempt in range(1, 10):
        model_name = models[attempt % len(models)]
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.4
            )
            text = response.choices[0].message.content
            if text:
                valid_lines = [line.strip() for line in text.split('\n') if line.count('|') >= 3]
                if len(valid_lines) >= 8:
                    return "\n".join(valid_lines[:12]) 
        except:
            time.sleep(2)
    sys.exit(1)

def generate_metadata():
    return "IG_CAPTION: Stop wasting time editing. DM GROW to start your automated channel today! 🚀\nIG_TAGS: #YouTubeAutomation #MakeMoneyOnline #CreatorEconomy\nYT_TITLE: Why YouTubers Fail (And How To Fix It) 🔥 #shorts\nYT_DESC: Get a full team for your channel. DM us 'GROW' on Instagram!\nYT_TAGS: youtube automation, video editing, make money online\nMUSIC: deep cinematic bass pulse"

if __name__ == "__main__":
    script_output = generate_cinematic_agency_script()
    with open(PROMPT_FILE, "w", encoding="utf-8") as f: f.write(script_output + "\n")
    with open(METADATA_FILE, "w", encoding="utf-8") as f: f.write(generate_metadata())
