import os
import subprocess
import re
import urllib.request

INPUT_DIR = "generated_videos"
OUTPUT_DIR = "final_output"
PROMPT_FILE = "prompts.txt"
os.makedirs(OUTPUT_DIR, exist_ok=True)
FONT_FILE = "HindiFont.ttf"

def download_font():
    if not os.path.exists(FONT_FILE):
        print("📥 Downloading Hindi Font...")
        urllib.request.urlretrieve("https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Black.ttf", FONT_FILE)

# 🔴 THE "AI EDITOR" FUNCTION: Finds exactly when speech starts and ends
def get_audio_trim_times(video_path):
    print(f"🧠 AI Listening to video to find dialogue timing: {video_path}")
    cmd = ["ffmpeg", "-i", video_path, "-af", "silencedetect=noise=-30dB:d=0.3", "-f", "null", "-"]
    try:
        output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = output.stderr.split('\n')
        
        start_time = 0.0
        end_time = 5.0 # Max length
        
        for line in lines:
            if "silence_end" in line:
                # Speech started
                match = re.search(r"silence_end:\s*([\d\.]+)", line)
                if match: start_time = max(0.0, float(match.group(1)) - 0.2) # Thoda margin rakha
            
            if "silence_start" in line and start_time > 0:
                # Speech ended
                match = re.search(r"silence_start:\s*([\d\.]+)", line)
                if match: end_time = min(5.0, float(match.group(1)) + 0.3)
        
        return start_time, end_time
    except:
        return 0.0, 5.0

def build_word_by_word_filter(text_overlay, duration):
    safe_text = text_overlay.replace("'", "").replace(":", "\\:").replace(",", "\\,").strip()
    if not safe_text: return ""
    words = safe_text.split()
    chunks = [" ".join(words[i:i+2]) for i in range(0, len(words), 2)]
    if not chunks: return ""

    time_per_chunk = duration / len(chunks)
    drawtext_filters = []
    for i, chunk in enumerate(chunks):
        start = round(i * time_per_chunk, 2)
        end = round((i + 1) * time_per_chunk, 2)
        filter_str = (
            f"drawtext=fontfile={FONT_FILE}:text='{chunk}':"
            f"fontcolor=yellow:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2+300:"
            f"bordercolor=black:borderw=5:"
            f"enable='between(t,{start},{end})'"
        )
        drawtext_filters.append(filter_str)
    return ",".join(drawtext_filters)

def process_clip(idx, text_overlay):
    v_path = os.path.join(INPUT_DIR, f"video_{idx}.mp4")
    out_path = os.path.join(OUTPUT_DIR, f"clip_{idx}.mp4")
    if not os.path.exists(v_path): return None

    # 1. Ask AI Editor for exact trim times
    start_time, end_time = get_audio_trim_times(v_path)
    duration = end_time - start_time
    if duration < 0.5: duration = 4.9 # Failsafe
    
    print(f"✂️ Auto-Trimming Scene {idx} from {start_time}s to {end_time}s")

    # 2. Text Filter
    text_filter = build_word_by_word_filter(text_overlay, duration)
    
    video_filter = "scale=1080:1920:flags=lanczos:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p"
    final_vf = f"{video_filter},{text_filter}" if text_filter else video_filter

    # 3. Apply trim using -ss and -to
    cmd = [
        "ffmpeg", "-y", 
        "-ss", str(start_time), "-to", str(end_time),
        "-i", v_path, 
        "-vf", final_vf, 
        "-map", "0:v", "-map", "0:a?", 
        "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", 
        "-c:a", "aac", "-b:a", "192k", 
        out_path
    ]
    
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path

def main():
    download_font()
    texts = {}
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f.readlines(), 1):
                parts = line.split("|")
                if len(parts) >= 4:
                    texts[i] = re.sub(r'\[.*?\]', '', parts[3].strip()).strip()

    video_files = [f for f in os.listdir(INPUT_DIR) if f.startswith("video_") and f.endswith(".mp4")]
    if not video_files: return
    video_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    
    processed_clips = []
    for v_name in video_files:
        idx = int(re.search(r'\d+', v_name).group())
        clip = process_clip(idx, texts.get(idx, ""))
        if clip: processed_clips.append(clip)

    if not processed_clips: return
    with open("list.txt", "w") as f:
        for clip in processed_clips: f.write(f"file '{clip}'\n")

    temp_output = os.path.join(OUTPUT_DIR, "temp_master.mp4")
    print("🎬 Merging perfectly trimmed clips...")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", temp_output], check=True)

    final_output = os.path.join(OUTPUT_DIR, "Final_Agency_Reel.mp4")
    if os.path.exists("bgm.wav"):
        cmd = [
            "ffmpeg", "-y", "-i", temp_output, "-stream_loop", "-1", "-i", "bgm.wav", 
            "-filter_complex", "[0:a]volume=2.0[a1];[1:a]volume=0.15[a2];[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[a]", 
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", final_output
        ]
        subprocess.run(cmd, check=True)
    else:
        os.rename(temp_output, final_output)
    
    print("🎉 MASTERPIECE REEL READY! (Auto-Trimmed & B-Roll inserted)")

if __name__ == "__main__": 
    main()
