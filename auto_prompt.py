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
    
    # 🔴 AI ko strict kiya hai ki bakwaas na kare
    system_prompt = "You are a Cinematic Director. Output ONLY the requested format. NO intros, NO explanations, NO markdown tables, NO status reports. JUST THE SCENES."
    
    user_prompt = f"""Task: Create a highly engaging, emotional story based on this idea: "{topic}".
    Break this into exactly {target_scenes} scenes for a {duration_sec}-second short video.

    🚨 YOUTUBE MONETIZATION & SAFETY GUIDELINES:
    - 100% Advertiser-Friendly. NO blood, fire, death, or violence. 
    - Keep it sad but safe (tears, rain, loneliness).

    FORMAT RULES (Strictly 2 parts separated by | ):
    [Image Prompt] | [Video Prompt]

    CRITICAL INSTRUCTION:
    DO NOT output any tables. DO NOT output any checklist.
    EVERY single line you output MUST contain EXACTLY ONE '|' symbol separating the image prompt and video prompt.

    Example safe format:
    A sad anthropomorphic little puppy wearing an oversized sweater, sitting on a rainy street, 8k | Fast zoom into face, loud thunder, heavy rain splashing. NO BGM.
    """
    
    print(f"\n🚀 Writing YouTube Monetization-Proof Script...")
    text = smart_ai_request(system_prompt, user_prompt, "Generating Script")
    if text:
        # 🔴 Ye filter table headers ko nikal dega
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
    return "Heart Touching Story 😭 #shorts", "Wait for the end...", "shorts, sad, story"

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
    print("🎉 AI Story Generated Without Tables!")

if __name__ == "__main__":
    process_stories()
