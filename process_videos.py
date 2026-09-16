import os
import subprocess
import re

INPUT_DIR = "generated_videos"
OUTPUT_DIR = "final_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🔴 YAHAN APNA YA CLIENT KA NAAM LIKHO! (e.g. "@SadStoryHub")
CHANNEL_NAME = "@THAKURSAHAB" 

def process_smooth_fade(v_path, index):
    out_path = os.path.join(OUTPUT_DIR, f"clip_{index}.mp4")
    fade_dur = 0.5
    
    # 🔴 WATERMARK MAGIC: Top-Center (x=(w-text_w)/2, y=80), Transparent White (white@0.4), Size (50)
    vf = f"scale=1080:1920:flags=lanczos:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,fade=t=in:st=0:d={fade_dur},fade=t=out:st=4.5:d={fade_dur},drawtext=text='{CHANNEL_NAME}':fontcolor=white@0.4:fontsize=50:x=(w-text_w)/2:y=100"
    
    af = f"volume=3.0,afade=t=in:st=0:d={fade_dur},afade=t=out:st=4.5:d={fade_dur}"
    
    cmd = [
        "ffmpeg", "-y", "-i", v_path, "-vf", vf, "-af", af,
        "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-c:a", "aac", "-b:a", "320k", out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out_path

def main():
    video_files = [f for f in os.listdir(INPUT_DIR) if f.startswith("video_") and f.endswith(".mp4")]
    if not video_files:
        print("❌ No videos found to merge!")
        return

    video_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    processed_clips = []
    
    for v_name in video_files:
        v_path = os.path.join(INPUT_DIR, v_name)
        idx = int(re.search(r'\d+', v_name).group())
        processed_clips.append(process_smooth_fade(v_path, idx))

    list_path = "list.txt"
    with open(list_path, "w") as f:
        for clip in processed_clips: 
            f.write(f"file '{clip}'\n")

        # OUTRO VIDEO FIX
        if os.path.exists("outro.mp4"):
            outro_out = os.path.join(OUTPUT_DIR, "processed_outro.mp4")
            vf_outro = "scale=1080:1920:flags=lanczos:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p"
            subprocess.run([
                "ffmpeg", "-y", "-i", "outro.mp4", "-vf", vf_outro,
                "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-c:a", "aac", "-b:a", "320k", outro_out
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            f.write(f"file '{outro_out}'\n")

    final_output = os.path.join(OUTPUT_DIR, "Final_4K_Monetizable_Short.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", final_output], check=True)
    print(f"🎉 MASTERPIECE GENERATED WITH WATERMARK: {final_output}")

if __name__ == "__main__": 
    main()
