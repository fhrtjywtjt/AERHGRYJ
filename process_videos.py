import os
import subprocess
import re

INPUT_DIR = "generated_videos"
OUTPUT_DIR = "final_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_smooth_fade(v_path, index):
    out_path = os.path.join(OUTPUT_DIR, f"clip_{index}.mp4")
    
    fade_dur = 0.5
    
    # Video Filter: 4K Lanczos scaling
    vf = f"scale=2160:3840:flags=lanczos:force_original_aspect_ratio=increase,crop=2160:3840,setsar=1,fps=30,format=yuv420p,fade=t=in:st=0:d={fade_dur},fade=t=out:st=4.5:d={fade_dur}"
    
    # 🔴 AUDIO MAGIC: volume=3.0 (Awaaz 3 guna (300%) tez kar di hai)
    af = f"volume=3.0,afade=t=in:st=0:d={fade_dur},afade=t=out:st=4.5:d={fade_dur}"
    
    # 🔴 SERVER CRASH FIX: preset 'fast' kiya hai taaki GitHub cancel na kare
    cmd = [
        "ffmpeg", "-y", "-i", v_path,
        "-vf", vf, "-af", af,
        "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-c:a", "aac", "-b:a", "320k",
        out_path
    ]
    print(f"⚙️ Rendering 4K Quality for Scene {index} (With Loud Audio)...")
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out_path

def main():
    video_files = [f for f in os.listdir(INPUT_DIR) if f.startswith("video_") and f.endswith(".mp4")]
    if not video_files:
        print("❌ No videos found to merge!")
        return

    video_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    processed_clips = []
    
    print("✂️ Processing 4K Fades & Boosting Audio Volume...")
    for v_name in video_files:
        v_path = os.path.join(INPUT_DIR, v_name)
        idx = int(re.search(r'\d+', v_name).group())
        processed_clips.append(process_smooth_fade(v_path, idx))

    list_path = "list.txt"
    with open(list_path, "w") as f:
        for clip in processed_clips: 
            f.write(f"file '{clip}'\n")
            
    final_output = os.path.join(OUTPUT_DIR, "Final_4K_Monetizable_Short.mp4")
    print("🎬 Merging all clips into Final Masterpiece...")
    
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", final_output], check=True)
    
    print(f"🎉 MASTERPIECE GENERATED (4K, LOUD AUDIO): {final_output}")

if __name__ == "__main__": 
    main()
