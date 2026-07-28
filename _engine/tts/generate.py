"""
wxo-video-studio — Kokoro TTS engine
Converts a script .md file into narration.wav + transcript.json

Usage:
  python3 _engine/tts/generate.py --input scripts/my-feature.md --out compositions/my-feature/
  python3 _engine/tts/generate.py --input scripts/my-feature.md --out compositions/my-feature/ --voice am_adam
"""

import argparse
import json
import os
import re
import sys


# ── Voice options ──────────────────────────────────────────────────────────────
VOICES = {
    "af_heart":  "American female — warm (default)",
    "am_adam":   "American male",
    "bf_emma":   "British female",
    "bm_george": "British male",
}

# ── Model file paths (relative to repo root) ──────────────────────────────────
REPO_ROOT   = os.path.join(os.path.dirname(__file__), "..", "..")
MODEL_PATH  = os.path.join(REPO_ROOT, "kokoro-v1.0.int8.onnx")
VOICES_PATH = os.path.join(REPO_ROOT, "voices-v1.0.bin")


def read_script(path: str) -> str:
    """Read a markdown script file and strip markdown syntax, keeping narration only."""
    with open(path, "r") as f:
        text = f.read()

    # If template format: extract only the Narration section
    narration_match = re.search(r"## Narration\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if narration_match:
        text = narration_match.group(1).strip()

    # Strip remaining markdown
    text = re.sub(r"^#+\s.*$", "", text, flags=re.MULTILINE)   # headers
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE) # bullets
    text = re.sub(r"\*\*|__|\*|_|`", "", text)                  # bold/italic/code
    text = re.sub(r"\[.*?\]", "", text)                          # links
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text


def generate_voice(text: str, output_dir: str, voice: str = "af_heart"):
    """Generate narration.wav using Kokoro-ONNX (fully offline, Apache 2.0)."""
    try:
        from kokoro_onnx import Kokoro
        import soundfile as sf
    except ImportError:
        print("❌  Kokoro not installed.")
        print("    Run: pip install -r _engine/tts/requirements.txt")
        sys.exit(1)

    # Check model files exist
    if not os.path.exists(MODEL_PATH):
        print(f"❌  Model file not found: {MODEL_PATH}")
        print("    Run setup.sh (or the .pkg installer) to download it.")
        sys.exit(1)

    if not os.path.exists(VOICES_PATH):
        print(f"❌  Voices file not found: {VOICES_PATH}")
        print("    Run setup.sh (or the .pkg installer) to download it.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    wav_path        = os.path.join(output_dir, "narration.wav")
    txt_path        = os.path.join(output_dir, "narration.txt")
    transcript_path = os.path.join(output_dir, "transcript.json")

    print(f"🎙️  Generating voice ({voice} — {VOICES.get(voice, 'custom')})...")
    kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
    samples, sample_rate = kokoro.create(text, voice=voice, speed=1.0, lang="en-us")

    import soundfile as sf
    sf.write(wav_path, samples, sample_rate)
    print(f"✅  narration.wav  → {wav_path}")

    # Save plain text copy
    with open(txt_path, "w") as f:
        f.write(text)

    # Build word-level timestamps (character-proportional, bounded to total duration)
    words          = text.split()
    total_duration = len(samples) / sample_rate
    total_chars    = sum(len(w) for w in words)
    transcript     = []
    t = 0.0
    for word in words:
        word_dur = (len(word) / total_chars) * total_duration
        transcript.append({
            "word":  word,
            "start": round(t, 3),
            "end":   round(min(t + word_dur, total_duration), 3),
        })
        t = min(t + word_dur, total_duration)

    with open(transcript_path, "w") as f:
        json.dump({"duration": round(total_duration, 3), "words": transcript}, f, indent=2)
    print(f"✅  transcript.json → {transcript_path}")
    print(f"📊  Total duration: {round(total_duration, 1)}s  |  {len(words)} words")

    return wav_path, transcript_path, round(total_duration, 3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate voice narration from a script.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--input",  required=True,  help="Path to your script .md file")
    parser.add_argument("--out",    required=True,  help="Output directory (e.g. compositions/my-feature/)")
    parser.add_argument("--voice",  default="af_heart",
                        help="Voice to use. Options:\n" +
                             "\n".join(f"  {k}  — {v}" for k, v in VOICES.items()))
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌  Script not found: {args.input}")
        sys.exit(1)

    text = read_script(args.input)
    if not text:
        print("❌  Script is empty after parsing. Check your file has a Narration section.")
        sys.exit(1)

    print(f"📝  Script loaded ({len(text.split())} words)")
    generate_voice(text, args.out, voice=args.voice)
