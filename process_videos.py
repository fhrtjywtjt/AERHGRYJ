import os
import subprocess
import re
import urllib.request
import math

INPUT_DIR = "generated_videos"
OUTPUT_DIR = "final_output"
PROMPT_FILE = "prompts.txt"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🔴 FIX 1: HINDI FONT DOWNLOAD (Dabbe hatane ke liye)
FONT_FILE = "HindiFont.ttf"

def download_font():
    if not os.path.exists(FONT_FILE):
        print("📥 Downloading Hindi Compatible Font...")
        # Google ka official Noto Sans Devanagari font (Black/Bold)
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Black.ttf"
        try:
            urllib.request.urlretrieve(font_url, FONT_FILE)
            print("✅ Hindi Font Downloaded!")
        except Exception as e:
            print(f"❌ Font Download Error: {e}")

# 🔴 FIX 2: WORD-BY-WORD TEXT LOGIC
def build_word_by_word_filter(text_overlay):
    safe_text = text_overlay.replace("'", "").replace(":", "\\:").strip()
    if not safe_text:
        return ""
        
    words = safe_text.split()
    chunks = []
    
    # Text ko 2-2 words ke tukdo (chunks) mein baatna taaki padhne me asaan ho aur fast lage
    chunk_size = 2 
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
        
    total_chunks = len(chunks)
    if total_chunks == 0:
        return ""

    # Upsampler ki video theek 5 second ki hoti hai
    video_duration = 5.0 
    time_per_chunk = video_duration / total_chunks
    
    drawtext_filters = []
    
    # Har chunk ko ek fix time (start to end) assign karna
    for i, chunk in enumerate(chunks):
        start_time = round(i * time_per_chunk, 2)
        end_time = round((i + 1) * time_per_chunk, 2)
        
        # Yellow color text with Black thick border (Hormozi/Viral Reel style)
        filter_str = (
            f"drawtext=fontfile={FONT_FILE}:text='{chunk}':"
            f"fontcolor=yellow:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2+300:"
            f"bordercolor=black:borderw=5:"
            f"enable='between(t,{start_time},{end_time})'"
        )
        drawtext_filters.append(filter_str)
        
    # Saare filters ko comma se jodna
    return ",".join(drawtext_filters)


def process_clip(idx, text_overlay):
    v_path = os.path.join(INPUT_DIR, f"video_{idx}.mp4")
    out_path = os.path.join(OUTPUT_DIR, f"clip_{idx}.mp4")
    
    if not os.path.exists(v_path):
        print(f"⚠️ Video {v_path} not found. Skipping scene {idx}...")
        return None

    # Text filter generate karna
    text_filter = build_word_by_word_filter(text_overlay)
    
    # Video Scale/Crop logic
    video_filter = "scale=1080:1920:flags=lanczos:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p"
    
    # Agar text hai, toh video filter ke sath text filter jod do
    if text_filter:
        final_vf = f"{video_filter},{text_filter}"
    else:
        final_vf = video_filter

    cmd = [
        "ffmpeg", "-y", 
        "-i", v_path, 
        "-vf", final_vf, 
        "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", 
        "-c:a", "copy", 
        out_path
    ]
    
    print(f"⚙️ Rendering Scene {idx} (Pop-up Hindi Text)...")
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out_path

def main():
    download_font()
    
    texts = {}
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f.readlines(), 1):
                parts = line.split("|")
                # Column 4 (Dialogue) mein se brackets [...] hata kar text nikalna
                if len(parts) >= 4:
                    raw_text = parts[3].strip()
                    clean_text = re.sub(r'\[.*?\]', '', raw_text).strip()
                    texts[i] = clean_text

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

    if os.path.exists("bgm.wav"):
        print("🎵 Mixing BGM with Character Voice...")
        cmd = [
            "ffmpeg", "-y", "-i", temp_output, "-stream_loop", "-1", "-i", "bgm.wav", 
            "-filter_complex", "[0:a]volume=2.0[a1];[1:a]volume=0.1[a2];[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[a]", 
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", final_output
        ]
        subprocess.run(cmd, check=True)
    else:
        os.rename(temp_output, final_output)
    
    print("🎉 FINAL REEL IS READY WITH DYNAMIC HINDI CAPTIONS!")

if __name__ == "__main__": 
    main()
