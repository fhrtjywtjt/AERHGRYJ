import os
import sys
import math
import re
import time
import json
import urllib.request
from openai import OpenAI

STORY_FILE = "story.txt"
PROMPT_FILE = "prompts.txt"
METADATA_FILE = "metadata.txt"

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("❌ OPENROUTER_API_KEY is missing!")
    sys.exit(1)

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

def get_live_free_models():
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/models")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
        free_models = [m["id"] for m in data.get("data", []) if m.get("pricing", {}).get("prompt") == "0" and m.get("pricing", {}).get("completion") == "0"]
        return free_models[:5] if free_models else ["google/gemini-2.0-flash-lite-preview-02-05:free"]
    except:
        return ["google/gemini-2.0-flash-lite-preview-02-05:free", "meta-llama/llama-3.2-3b-instruct:free"]

def smart_ai_request(system_prompt, user_prompt, description):
    free_models = get_live_free_models()
    for model_name in free_models:
        print(f"🔄 {description} using {model_name}...")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.7
            )
            text = response.choices[0].message.content
            if text: return text
        except:
            time.sleep(2)
    return None

def generate_ai_script(duration_sec, topic):
    target_scenes = max(2, math.ceil(int(duration_sec) / 5))
    
    system_prompt = "You are a highly aggressive Action-Drama Director for TikTok/YouTube Shorts. Output ONLY the requested format. NO tables, NO markdown."
    
    # 🔴 YAHAN MAGIC HAI: HIGH ACTION, HIGH RETENTION, CONSTANT MOVEMENT
    user_prompt = f"""Task: Create a FAST-PACED, highly engaging, emotional action story based on: "{topic}".
    Break this into exactly {target_scenes} scenes for a {duration_sec}-second short video.

    🚨 HIGH-RETENTION VISUAL STORYTELLING (CRITICAL):
    - NO STATIC SCENES! The character must NEVER just "stand" or "sit". They must be in CONSTANT MOTION (running, stumbling, dodging, desperately crawling, panicking, reaching out, falling).
    - CLEAR VISUAL PLOT: The audience must instantly know WHERE they came from, WHY they are panicking, and WHAT they are trying to do. (e.g., escaping a collapsing house, chasing a moving truck, desperately hiding from shadows).
    - AGGRESSIVE PACING: The visual action and camera angle MUST change drastically in every scene to keep the viewer hooked.

    🚨 YOUTUBE MONETIZATION & SAFETY:
    - 100% Advertiser-Friendly. Safe but deeply emotional/intense. No blood/gore/fire. Use "storm, shadows, or collapsing ruins" instead of fire/blood.

    FORMAT RULES (Strictly 2 parts separated by | ):
    [Image Prompt] | [Video Prompt]

    CRITICAL INSTRUCTION:
    1. Invent a specific character and copy-paste it at the beginning of EVERY Image prompt.
    2. DO NOT output any tables. EVERY line MUST contain EXACTLY ONE '|'.
    
    Example of a High-Action Story Format:
    A sad anthropomorphic little puppy wearing a torn red sweater, frantically sprinting out of an abandoned collapsing house, clutching a torn family photo in his mouth, looking back in terror, 8k | Shaky handheld tracking shot following him running, loud wooden crashing sounds, frantic panting, rapid heavy footsteps. NO BGM.
    A sad anthropomorphic little puppy wearing a torn red sweater, stumbling and falling face-first into a deep muddy puddle while trying to dodge a speeding shadow, 8k | Fast whip pan, loud splashing sound, desperate yelping echo, mud dripping sound. NO BGM.
    A sad anthropomorphic little puppy wearing a torn red sweater, desperately clawing at a locked iron gate in the rain trying to get inside, 8k | Fast zoom-in, aggressive metal rattling sounds, heavy rain pouring, loud whimpering. NO BGM.
    """
    
    print(f"\n🚀 Writing High-Retention Action/Emotional Script...")
    text = smart_ai_request(system_prompt, user_prompt, "Generating Script")
    if text:
        valid_lines = [line.strip() for line in text.split('\n') if '|' in line and not line.strip().startswith('|') and '---' not in line]
        if valid_lines:
            return "\n".join(valid_lines[:target_scenes])
    return None

def generate_ai_metadata(topic):
    system_prompt = "You are a YouTube SEO Expert."
    user_prompt = f"Topic: '{topic}'.\nCreate viral YouTube Shorts TITLE, DESC, and TAGS.\nFormat:\nTITLE: [Title]\nDESC: [Description]\nTAGS: [tag1, tag2]"
    text = smart_ai_request(system_prompt, user_prompt, "Generating Metadata")
    if text:
        try:
            title = re.search(r"TITLE:\s*(.*)", text).group(1).strip()
            desc = re.search(r"DESC:\s*([\s\S]*?)TAGS:", text).group(1).strip()
            tags = re.search(r"TAGS:\s*(.*)", text).group(1).strip()
            return title, desc, tags
        except: pass
    return "Heart Touching Emotional Story 😭 #shorts", "Wait for the end... emotional short video.", "shorts, sad, story, emotional"

def process_stories():
    if not os.path.exists(STORY_FILE): sys.exit(1)
    with open(STORY_FILE, "r", encoding="utf-8") as f: content = f.read().strip()
    if not content: sys.exit(1)
        
    topics = [t.strip() for t in content.split("\n") if t.strip()]
    parts = topics[0].split("|")
    duration_sec, topic = (int(re.search(r'\d+', parts[0]).group()), parts[1].strip()) if len(parts) > 1 else (30, topics[0])

    ai_output = generate_ai_script(duration_sec, topic)
    if not ai_output: sys.exit(1)
        
    with open(PROMPT_FILE, "w", encoding="utf-8") as f: f.write(ai_output + "\n")
    title, desc, tags = generate_ai_metadata(topic)
    with open(METADATA_FILE, "w", encoding="utf-8") as f: f.write(f"TITLE: {title}\nDESC: {desc}\nTAGS: {tags}")
    with open(STORY_FILE, "w", encoding="utf-8") as f: f.write("\n".join(topics[1:]) + "\n" if len(topics) > 1 else "")
    print("🎉 AI High-Action Visual Story Generated Successfully!")

if __name__ == "__main__":
    process_stories()
