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

# 1. API KEY CHECK
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY is missing! GitHub Secrets mein key add karo.")
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
        try:
            print(f"🔄 Trying model: {model_name} for {description}...")
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.8
            )
            text = response.choices[0].message.content
            if text: 
                print(f"✅ Success with {model_name}!")
                return text
        except Exception as e:
            print(f"⚠️ Model {model_name} failed: {e}")
            time.sleep(2)
    return None

def generate_ai_script(duration_sec, topic):
    target_scenes = max(2, math.ceil(int(duration_sec) / 5))
    system_prompt = "You are a Master Visual Storyteller and a Strict YouTube Compliance Officer. Output ONLY the requested format. NO tables. NO markdown."
    
    user_prompt = f"""Task: Create a COMPLETE, highly engaging, and 100% YOUTUBE-SAFE visual story based on: "{topic}".
    Total Video Duration: {duration_sec} seconds.
    You MUST generate EXACTLY {target_scenes} scenes.

    🚨 YOUTUBE STRICT SAFETY RULES:
    - STRICTLY NO blood, NO weapons, NO gore, NO extreme violence.
    - Must be 100% Family-Friendly.

    🚨 PERFECT STORY ARC:
    - Scene 1: Introduce character and background.
    - Middle: Struggle/Action.
    - Last Scene: Clear ENDING.

    🚨 BACKGROUND & CHARACTER CONSISTENCY:
    - Invent a specific character and specific location.
    - KEEP THEM SAME in every prompt. Do not change backgrounds randomly.

    🚨 AUDIO: NO BGM. NO VOICE. ONLY FOLEY SOUNDS. End video prompt with "NO BGM, NO VOICE."

    FORMAT: [Image Prompt] | [Video Prompt]
    """
    
    text = smart_ai_request(system_prompt, user_prompt, "Generating Script")
    if text:
        valid_lines = [line.strip() for line in text.split('\n') if '|' in line and not line.strip().startswith('|') and '---' not in line]
        if valid_lines: return "\n".join(valid_lines[:target_scenes])
    return None

def generate_ai_metadata(topic):
    system_prompt = "You are a highly creative Music Director and YouTube SEO Expert."
    user_prompt = f"""Story Topic: '{topic}'.
    Create Advertiser-Friendly YouTube Shorts metadata and a Custom Music Prompt.
    Format EXACTLY like this:
    TITLE: [Title]
    DESC: [Description]
    TAGS: [tag1, tag2, tag3]
    MUSIC: [Unique 5-8 word music prompt]"""
    
    text = smart_ai_request(system_prompt, user_prompt, "Generating Metadata")
    music_prompt = "dark emotional cinematic background score" 
    
    if text:
        try:
            title = re.search(r"TITLE:\s*(.*)", text).group(1).strip()
            desc = re.search(r"DESC:\s*([\s\S]*?)TAGS:", text).group(1).strip()
            tags = re.search(r"TAGS:\s*(.*)", text).group(1).strip()
            music_prompt = re.search(r"MUSIC:\s*(.*)", text).group(1).strip()
            with open("music_prompt.txt", "w", encoding="utf-8") as f: f.write(music_prompt)
            return title, desc, tags
        except: pass
        
    with open("music_prompt.txt", "w", encoding="utf-8") as f: f.write(music_prompt)
    return "Heart Touching Emotional Story 😭", "A very sad emotional story about life.", "shorts, sad, story, emotional, viral"

def process_stories():
    # 2. STORY FILE EXIST CHECK
    if not os.path.exists(STORY_FILE):
        print(f"❌ ERROR: {STORY_FILE} file not found!")
        sys.exit(1)
        
    with open(STORY_FILE, "r", encoding="utf-8") as f: content = f.read().strip()
    
    # 3. STORY FILE EMPTY CHECK
    if not content:
        print(f"❌ ERROR: {STORY_FILE} is empty. Koi topic nahi mila!")
        sys.exit(1)
        
    topics = [t.strip() for t in content.split("\n") if t.strip()]
    parts = topics[0].split("|")
    duration_sec, topic = (int(re.search(r'\d+', parts[0]).group()), parts[1].strip()) if len(parts) > 1 else (30, topics[0])
    
    print(f"📝 Topic: {topic}, Duration: {duration_sec}s")
    
    ai_output = generate_ai_script(duration_sec, topic)
    
    # 4. AI OUTPUT CHECK
    if not ai_output:
        print("❌ ERROR: AI se script generate nahi ho payi (Response None aaya).")
        sys.exit(1)
        
    with open(PROMPT_FILE, "w", encoding="utf-8") as f: f.write(ai_output + "\n")
    
    title, desc, tags = generate_ai_metadata(topic)
    with open(METADATA_FILE, "w", encoding="utf-8") as f: f.write(f"TITLE: {title}\nDESC: {desc}\nTAGS: {tags}")
    with open(STORY_FILE, "w", encoding="utf-8") as f: f.write("\n".join(topics[1:]) + "\n" if len(topics) > 1 else "")
    print("✅ All processes completed successfully!")

if __name__ == "__main__":
    process_stories()
