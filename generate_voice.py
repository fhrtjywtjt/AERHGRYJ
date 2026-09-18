import os
import asyncio
import edge_tts

PROMPT_FILE = "prompts.txt"
VOICE_DIR = "generated_voices"
os.makedirs(VOICE_DIR, exist_ok=True)

async def generate_audio(text, output_file):
    # 'hi-IN-MadhurNeural' ek bohot professional aur deep aawaz hai
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+5%")
    await communicate.save(output_file)
    print(f"✅ Voice generated: {output_file}")

async def main():
    if not os.path.exists(PROMPT_FILE):
        print("❌ prompts.txt not found!")
        return

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    tasks = []
    for idx, line in enumerate(lines, 1):
        parts = line.strip().split("|")
        if len(parts) >= 4:
            voice_text = parts[3].strip()
            out_path = os.path.join(VOICE_DIR, f"voice_{idx}.mp3")
            tasks.append(generate_audio(voice_text, out_path))
            
    if tasks:
        await asyncio.gather(*tasks)
        print("🎉 All Voiceovers Generated Successfully!")

if __name__ == "__main__":
    asyncio.run(main())
