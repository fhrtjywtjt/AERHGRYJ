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
    themes = ["Luxury Sports Car", "Neon Cyberpunk City Rooftop", "Private Jet Interior", "Modern Glass Office", "High-tech Setup"]
    current_theme = random.choice(themes)

    system_prompt = "You are a Viral Instagram Reel Creator. Output ONLY raw text."
    user_prompt = f"""Create a concept for a YouTube Automation Agency Reel.
    Theme: {current_theme}
    
    🚨 CRITICAL: The AI Image Generator will write the text INSIDE the image. 
    Use short ENGLISH text in the prompt (DALL-E fails at Hindi). 
    Make it completely NEW and DIFFERENT from previous ones.
    
    FORMAT EXACTLY LIKE THIS:
    IMAGE_PROMPT: Ultra-realistic 8k cinematic vertical photo of a wealthy faceless entrepreneur in a {current_theme}. Floating bold glowing neon text in the image says "NO VIEWS?". Below it, bold elegant text says "DM GROW". Cinematic lighting.
    IG_CAPTION: Stop thinking, start earning! DM GROW 🚀
    IG_TAGS: #YouTubeAutomation #MakeMoneyOnline #PassiveIncome
    YT_TITLE: Secret to YouTube Growth 🔥 #shorts
    YT_DESC: DM us 'GROW' on Instagram to start your faceless channel!
    YT_TAGS: youtube automation, passive income, faceless channel
    MUSIC: trending cinematic bass pulse
    """

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.9
        )
        return response.choices[0].message.content
    except:
        return """IMAGE_PROMPT: Ultra-realistic 8k vertical photo of a young man working on a laptop on a neon city rooftop. Huge bold glowing 3D text floating says "YOUTUBE AUTOMATION". Text below says "DM GROW". Cinematic lighting.
IG_CAPTION: DM GROW to automate your channel! 🚀
IG_TAGS: #YouTubeAutomation #MakeMoneyOnline
YT_TITLE: How Smart Creators Make Money 🔥 #shorts
YT_DESC: DM us GROW on Insta.
YT_TAGS: youtube automation, make money online
MUSIC: cinematic trap beat"""

if __name__ == "__main__":
    content = generate_viral_concept()
    with open("reel_data.txt", "w", encoding="utf-8") as f: f.write(content)
