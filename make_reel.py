import os
import re
import subprocess
import urllib.request

def download_font():
    if not os.path.exists("Font.ttf"):
        urllib.request.urlretrieve("https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Black.ttf", "Font.ttf")

def parse_data():
    with open("reel_data.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    hook = re.search(r"HOOK:\s*(.*)", content).group(1).strip().replace("'", "").replace(":", "\\:")
    # Body text ki multiple lines ko ffmpeg ke format me convert karna
    body_raw = re.search(r"BODY:\s*(.*?)(?=IG_CAPTION:)", content, re.DOTALL).group(1).strip()
    body = body_raw.replace("'", "").replace(":", "\\:").replace("\n", " ") # Ek line me laakar lamba text banaya
    
    # Text ko break karna taaki screen ke bahar na jaye
    words = body.split()
    body_lines = [" ".join(words[i:i+4]) for i in range(0, len(words), 4)]
    body_formatted = "\\n".join(body_lines) # FFmpeg line break
    
    return hook, body_formatted

def create_video():
    download_font()
    hook, body = parse_data()
    
    # Assuming Bing Image creator saves the image as scene_1.jpg in scene_images/
    img_path = "scene_images/scene_1.jpg"
    bgm_path = "bgm.wav"
    out_path = "Final_Agency_Reel.mp4"
    
    if not os.path.exists(img_path):
        print("❌ Image not found!")
        return

    print("🎬 Rendering 15-Second Cinematic Reel...")

    # 🔴 MAGIC: 
    # 1. zoompan = Photo me dheere-dheere zoom hoga 15 second tak (Video feel)
    # 2. drawtext (Hook) = Upar bada yellow text, kaale background ke sath
    # 3. drawtext (Body) = Beech mein white text, kaale background ke sath
    
    filter_complex = (
        "scale=1080:1920,setsar=1,"
        "zoompan=z='min(zoom+0.001,1.15)':d=450:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,"
        f"drawtext=fontfile=Font.ttf:text='{hook}':fontcolor=#FFD700:fontsize=90:x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.7:boxborderw=20,"
        f"drawtext=fontfile=Font.ttf:text='{body}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=(h-text_h)/2+200:box=1:boxcolor=black@0.6:boxborderw=20:line_spacing=20"
    )

    cmd = [
        "ffmpeg", "-y", 
        "-loop", "1", "-i", img_path, # Loop image
        "-stream_loop", "-1", "-i", bgm_path, # Loop BGM
        "-t", "15", # EXACTLY 15 SECONDS
        "-vf", filter_complex, 
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        out_path
    ]
    
    subprocess.run(cmd, check=True)
    
    # Move to final_output folder so your upload scripts find it
    os.makedirs("final_output", exist_ok=True)
    os.rename(out_path, "final_output/Final_Agency_Reel.mp4")
    print("✅ 15-Second Viral Reel Ready!")

if __name__ == "__main__":
    create_video()
