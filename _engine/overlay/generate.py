#!/usr/bin/env python3
"""
wxo-video-studio — overlay generator
=====================================
Ingests a user-supplied video and builds a HyperFrames composition that
adds GSAP overlays (captions, callouts, spotlight, Ken Burns, lower-third,
intro/outro cards) on top of the recording.

Usage
-----
python3 _engine/overlay/generate.py \\
  --video   assets/my-recording.mp4  \\
  --script  scripts/my-feature.md    \\
  --out     compositions/my-feature/ \\
  [--tts]                            \\  # regenerate narration from script
  [--voice  af_heart]                \\  # Kokoro voice flag
  [--video-start  2.5]               \\  # trim: skip first N seconds of video
  [--video-volume 0.15]              \\  # original audio volume (0=mute, 1=full)
  [--no-intro]                       \\  # skip intro title card
  [--no-outro]                       \\  # skip outro CTA card

What it produces
----------------
compositions/<slug>/
  index.html        — filled template ready for `npx hyperframes render`
  brand.css         — copied from _engine/templates/brand.css
  narration.wav     — TTS output (or copied from existing)
  transcript.json   — word-level timestamps from TTS
  narration.txt     — plain text version of narration

The user's video is referenced by relative path from the composition dir,
so it can stay in assets/ — nothing is copied (keeps the repo lean).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ── Repo root = two levels up from this script ──
REPO_ROOT   = Path(__file__).resolve().parents[2]
TEMPLATES   = REPO_ROOT / "_engine" / "templates"
TTS_SCRIPT  = REPO_ROOT / "_engine" / "tts" / "generate.py"


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def die(msg: str):
    print(f"[overlay] ✗ {msg}", file=sys.stderr)
    sys.exit(1)


def info(msg: str):
    print(f"[overlay] {msg}")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def ffprobe_duration(video_path: Path) -> float:
    """Return the duration of a video file in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        str(video_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                return float(stream["duration"])
    except (subprocess.CalledProcessError, KeyError, ValueError):
        pass
    die(f"Could not read duration from {video_path}. Is ffprobe installed?")


def parse_script(script_path: Path) -> dict:
    """
    Parse a SCRIPT-TEMPLATE.md file.
    Returns dict with keys: feature_name, tagline, narration, animation_notes.
    """
    text = script_path.read_text(encoding="utf-8")
    sections = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip().lower().replace(" ", "_")
            sections[current] = []
        elif current:
            sections[current].append(line)

    def get(key):
        return "\n".join(sections.get(key, [])).strip()

    return {
        "feature_name":    get("feature_name"),
        "tagline":         get("tagline"),
        "narration":       get("narration"),
        "animation_notes": get("animation_notes"),
    }


def sentence_boundaries(transcript: list) -> list:
    """
    Given a list of word dicts [{word, start, end}, ...],
    return a list of sentence end times (float seconds)
    by detecting words ending in . ! ?
    """
    boundaries = []
    for w in transcript:
        word = w.get("word", "").strip()
        if word.endswith((".", "!", "?")):
            boundaries.append(round(w["end"], 3))
    return boundaries


def fill_template(template_text: str, replacements: dict) -> str:
    """Replace all {{KEY}} placeholders. Keys are case-sensitive."""
    for key, value in replacements.items():
        template_text = template_text.replace("{{" + key + "}}", str(value))
    return template_text


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="wxo-video-studio overlay generator")
    parser.add_argument("--video",        required=True,  help="Path to user's MP4/MOV recording")
    parser.add_argument("--script",       required=True,  help="Path to script .md file")
    parser.add_argument("--out",          required=False, help="Output composition directory (auto-derived from slug if omitted)")
    parser.add_argument("--tts",          action="store_true", help="Regenerate TTS narration from script")
    parser.add_argument("--voice",        default="af_heart", help="Kokoro voice (default: af_heart)")
    parser.add_argument("--video-start",  type=float, default=0.0, help="Skip first N seconds of the video (trim)")
    parser.add_argument("--video-volume", type=float, default=0.0, help="Volume of original video audio (0=mute)")
    parser.add_argument("--no-intro",     action="store_true", help="Omit the intro title card")
    parser.add_argument("--no-outro",     action="store_true", help="Omit the outro CTA card")
    args = parser.parse_args()

    video_path  = Path(args.video).resolve()
    script_path = Path(args.script).resolve()

    if not video_path.exists():
        die(f"Video not found: {video_path}")
    if not script_path.exists():
        die(f"Script not found: {script_path}")

    # ── Parse script ──
    script = parse_script(script_path)
    feature_name = script["feature_name"] or script_path.stem
    slug         = slugify(feature_name)
    tagline      = script["tagline"] or "IBM watsonx Orchestrate"

    # ── Derive output path ──
    out_dir = Path(args.out).resolve() if args.out else (REPO_ROOT / "compositions" / slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    info(f"Composition → {out_dir.relative_to(REPO_ROOT)}/")

    # ── Copy brand.css ──
    brand_src = TEMPLATES / "brand.css"
    if brand_src.exists():
        shutil.copy2(brand_src, out_dir / "brand.css")
        info("brand.css copied")

    # ── TTS ──
    narration_wav   = out_dir / "narration.wav"
    transcript_json = out_dir / "transcript.json"
    narration_txt   = out_dir / "narration.txt"

    if args.tts or not narration_wav.exists():
        info("Generating TTS narration…")
        if not TTS_SCRIPT.exists():
            die(f"TTS script not found: {TTS_SCRIPT}")
        tts_cmd = [
            sys.executable, str(TTS_SCRIPT),
            "--input",  str(script_path),
            "--out",    str(out_dir),
            "--voice",  args.voice,
        ]
        subprocess.run(tts_cmd, check=True)
        info("TTS done ✅")
    else:
        info("Narration already exists — skipping TTS (pass --tts to regenerate)")

    # ── Read transcript ──
    if not transcript_json.exists():
        die(f"transcript.json not found at {transcript_json}. TTS may have failed.")

    with open(transcript_json, encoding="utf-8") as f:
        transcript_data = json.load(f)

    words          = transcript_data.get("words", transcript_data.get("segments", []))
    total_duration = round(transcript_data.get("duration", words[-1]["end"] if words else 60), 3)
    boundaries     = sentence_boundaries(words)

    info(f"Narration duration: {total_duration}s, sentence boundaries: {boundaries}")

    # ── Video timing ──
    video_duration_raw = ffprobe_duration(video_path)
    video_start        = args.video_start
    video_duration     = round(video_duration_raw - video_start, 3)
    video_src          = os.path.relpath(video_path, out_dir)

    # The video starts after the intro (if any).
    # Intro = 3s, outro = last 4s of total audio duration.
    intro_duration = 0.0 if args.no_intro else 3.0
    outro_start    = total_duration - 4.0 if not args.no_outro else total_duration

    # ── Caption timing from sentence boundaries ──
    # Distribute available boundaries across 3 caption slots.
    num_captions   = min(3, len(boundaries))
    cap_starts     = []
    cap_ends       = []

    if num_captions > 0:
        step = max(1, len(boundaries) // max(num_captions, 1))
        selected = [boundaries[i * step] for i in range(num_captions)]

        for i, t in enumerate(selected):
            # Caption starts 0.1s before the sentence ends (already on screen when sentence finishes)
            cap_start = round(max(intro_duration, t - 6.0), 3)
            cap_end   = round(t + 0.5, 3)
            cap_starts.append(cap_start)
            cap_ends.append(cap_end)
    else:
        # Fallback: evenly spaced
        for i in range(3):
            cap_starts.append(round(intro_duration + i * (total_duration / 3), 3))
            cap_ends.append(round(intro_duration + (i + 1) * (total_duration / 3) - 0.5, 3))

    # Pad to 3 entries
    while len(cap_starts) < 3:
        cap_starts.append(cap_starts[-1] + 2.0)
        cap_ends.append(cap_ends[-1] + 2.0)

    # ── Callout / spotlight (sensible defaults — Bob will tune) ──
    callout_start     = round(intro_duration + 2.0, 3)
    callout_end       = round(callout_start + 4.0, 3)
    spotlight_start   = callout_start
    spotlight_end     = callout_end

    lower_third_start = round(intro_duration + 0.5, 3)
    lower_third_end   = round(outro_start - 0.5, 3)

    # ── Parse narration sentences for captions ──
    narration = script["narration"]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", narration) if s.strip()]

    def caption_text(idx):
        if idx < len(sentences):
            return sentences[idx]
        return ""

    # ── Title card lines ──
    words_in_name = feature_name.split()
    title_line1   = " ".join(words_in_name[:2]) if len(words_in_name) > 2 else feature_name
    title_line2   = " ".join(words_in_name[2:]) if len(words_in_name) > 2 else ""

    # ── Build placeholder map ──
    r = {
        # Meta
        "COMPOSITION_ID":         slug,
        "PRODUCT_NAME":           "IBM watsonx Orchestrate",
        "FEATURE_TITLE_LINE1":    title_line1,
        "FEATURE_TITLE_LINE2":    title_line2,
        "FEATURE_TAGLINE":        tagline,
        "TOTAL_DURATION":         total_duration,
        # Video
        "VIDEO_SRC":              video_src,
        "VIDEO_START":            intro_duration,
        "VIDEO_DURATION":         video_duration,
        "VIDEO_VOLUME":           args.video_volume,
        # Intro / outro
        "INTRO_EXIT":             round(intro_duration - 0.4, 3),
        "OUTRO_START":            outro_start,
        "OUTRO_START_PLUS_0_3":   round(outro_start + 0.3, 3),
        "OUTRO_START_PLUS_0_9":   round(outro_start + 0.9, 3),
        "OUTRO_START_PLUS_1_5":   round(outro_start + 1.5, 3),
        "OUTRO_LINE1":            sentences[-2] if len(sentences) >= 2 else tagline,
        "OUTRO_LINE2":            sentences[-1] if sentences else tagline,
        # Captions
        "CAPTION_1_TEXT":         caption_text(0),
        "CAPTION_1_START":        cap_starts[0],
        "CAPTION_1_END":          cap_ends[0],
        "CAPTION_2_TEXT":         caption_text(1),
        "CAPTION_2_START":        cap_starts[1],
        "CAPTION_2_END":          cap_ends[1],
        "CAPTION_3_TEXT":         caption_text(2),
        "CAPTION_3_START":        cap_starts[2],
        "CAPTION_3_END":          cap_ends[2],
        # Callout / spotlight (positional defaults — Bob will override)
        "CALLOUT_1_TEXT":         feature_name,
        "CALLOUT_1_TOP":          80,
        "CALLOUT_1_LEFT":         80,
        "CALLOUT_1_START":        callout_start,
        "CALLOUT_1_END":          callout_end,
        "SPOTLIGHT_1_TOP":        200,
        "SPOTLIGHT_1_LEFT":       200,
        "SPOTLIGHT_1_W":          400,
        "SPOTLIGHT_1_H":          240,
        "SPOTLIGHT_1_START":      spotlight_start,
        "SPOTLIGHT_1_END":        spotlight_end,
        # Lower third
        "LOWER_THIRD_TITLE":      feature_name,
        "LOWER_THIRD_SUB":        tagline,
        "LOWER_THIRD_START":      lower_third_start,
        "LOWER_THIRD_END":        lower_third_end,
    }

    # ── Fill template ──
    template_path = TEMPLATES / "overlay-scene.html"
    if not template_path.exists():
        die(f"Template not found: {template_path}")

    html = template_path.read_text(encoding="utf-8")
    html = fill_template(html, r)

    # Strip unused intro/outro blocks if flags set
    if args.no_intro:
        html = re.sub(r'<!-- ══.*?OPTIONAL.*?intro.*?</div>\s*', '', html, flags=re.DOTALL | re.IGNORECASE)
    if args.no_outro:
        html = re.sub(r'<div id="outro-card".*?</div>\s*(?=\s*<!--)', '', html, flags=re.DOTALL)

    index_path = out_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    info(f"index.html written ✅")
    info("")
    info("Next step — render:")
    info(f"  npx hyperframes render compositions/{slug}/ --output output/{slug}.mp4")
    info("")
    info("After watching the video, tune overlays:")
    info(f"  Edit: compositions/{slug}/index.html")
    info(f"  Re-render: npx hyperframes render compositions/{slug}/ --output output/{slug}.mp4")


if __name__ == "__main__":
    main()
