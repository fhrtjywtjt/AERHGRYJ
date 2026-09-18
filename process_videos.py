import os
import subprocess
import re
import urllib.request

INPUT_DIR = "generated_videos"
OUTPUT_DIR = "final_output"
PROMPT_FILE = "prompts.txt"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_FILE = "Roboto-Bold.ttf"

def download_font():
    if not os.path.exists(FONT_FILE):
        print("📥 Downloading Font...")
        font_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
        urllib.request.urlretrieve(font_url, FONT_FILE)

def process_clip(idx, text_overlay):
    v_path = os.path.join(INPUT_DIR, f"video_{idx}.mp4")
    out_path = os.path.join(OUTPUT_DIR, f"clip_{idx}.mp4")
    
    if not os.path.exists(v_path):
        print(f"⚠️ Video {v_path} not found. Skipping scene {idx}...")
        return None

    # Text overlay logic
    safe_text = text_overlay.replace("'", "").replace(":", "")
    drawtext = f"drawtext=fontfile={FONT_FILE}:text='{safe_text}':fontcolor=white:fontsize=65:x=(w-text_w)/2:y=(h-text_h)/2+200:bordercolor=black:borderw=4"
    
    # 🔴 Yahan ffmpeg sirf video par text lagayega aur Upsampler ki original audio ko copy kar lega (-c:a copy)
    cmd = [
        "ffmpeg", "-y", 
        "-i", v_path, 
        "-vf", f"scale=1080:1920:flags=lanczos:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,{drawtext}", 
        "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", 
        "-c:a", "copy", # Audio waise ki waise hi rahegi jaisi upsampler ne di
        out_path
    ]
    
    print(f"⚙️ Rendering Scene {idx} (Built-in Upsampler Voice + Text)...")
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out_path

def main():
    download_font()
    
    texts = {}
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f.readlines(), 1):
                parts = line.split("|")
                if len(parts) >= 3:
                    texts[i] = parts[2].strip()

    video_files = [f for f in os.listdir(INPUT_DIR) if f.startswith("video_") and f.endswith(".mp4")]
    if not video_files: return
    video_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    
    processed_clips = []
    for v_name in video_files:
        idx = int(re.search(r'\d+', v_name).group())
        clip = process_clip(idx, texts.get(idx, ""))
        if clip: processed_clips.append(clip)

    if not processed_clips: return

    list_path = "list.txt"
    with open(list_path, "w") as f:
        for clip in processed_clips: f.write(f"file '{clip}'\n")

    temp_output = os.path.join(OUTPUT_DIR, "temp_master.mp4")
    print("🎬 Merging all clips...")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", temp_output], check=True)

    final_output = os.path.join(OUTPUT_DIR, "Final_Agency_Reel.mp4")

    # BGM mix karna (Upsampler Voice ki volume 2.0 (Tez) rakhi hai, BGM 0.1 (Halka))
    if os.path.exists("bgm.wav"):
        print("🎵 Mixing BGM with Upsampler Voice...")
        cmd = [
            "ffmpeg", "-y", "-i", temp_output, "-stream_loop", "-1", "-i", "bgm.wav", 
            "-filter_complex", "[0:a]volume=2.0[a1];[1:a]volume=0.1[a2];[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[a]", 
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", final_output
        ]
        subprocess.run(cmd, check=True)
    else:
        os.rename(temp_output, final_output)
    
    print("🎉 FINAL REEL IS READY!")

if __name__ == "__main__": 
    main()
