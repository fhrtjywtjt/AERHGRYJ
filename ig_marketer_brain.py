import os
import sys
import random
import urllib.request
import json
from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY: sys.exit(1)
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

def generate_viral_concept():
    # हर बार अलग थीम देने के लिए रैंडम वर्ड
    themes = ["Luxury Car", "Neon City Rooftop", "Private Jet", "Modern Office", "Hacker Setup", "Beach Mansion"]
    current_theme = random.choice(themes)

    system_prompt = "You are a Viral Instagram Reel Creator. Output ONLY raw text in the exact requested format."
    user_prompt = f"""Create a highly engaging 15-second static Reel concept selling a YouTube Automation Agency.
    Theme of the image: {current_theme}
    
    Make it completely NEW and DIFFERENT from previous ones.
    
    FORMAT EXACTLY LIKE THIS:
    IMAGE_PROMPT: [Ultra-realistic 8k cinematic photo prompt based on the theme. Describe a wealthy faceless or back-facing character]
    HOOK: [1 Short Punchy Line in Hindi/Hinglish (e.g., "YOUTUBE SE ₹1 LAKH/MONTH?")]
    BODY: [2-3 lines detailing the service (e.g., "Bina editing kiye channel grow karo.\\nHum script, edit aur upload karenge.\\nDM 'GROW' to start.")]
    IG_CAPTION: Stop thinking, start earning! DM GROW 🚀 #YouTubeAutomation #MakeMoneyOnline
    YT_TITLE: Secret to YouTube Growth 🔥 #shorts
    """

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.9 # High temperature = Naya idea har baar
        )
        return response.choices[0].message.content
    except:
        return """IMAGE_PROMPT: Ultra realistic cinematic shot of a young entrepreneur in a modern glass office overlooking a neon city at night, working on a glowing laptop, 8k, photorealistic
        HOOK: EDITING MEIN TIME WASTE MAT KARO!
        BODY: Hamari team aapke liye YouTube videos banayegi.\nScript -> Voice -> Edit -> Upload.\nDM "GROW" to start today.
        IG_CAPTION: DM GROW to automate your channel! 🚀 #MakeMoneyOnline #YouTubeAutomation
        YT_TITLE: How Smart Creators Make Money 🔥 #shorts"""

if __name__ == "__main__":
    content = generate_viral_concept()
    with open("reel_data.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Viral Brain Concept Generated!")
