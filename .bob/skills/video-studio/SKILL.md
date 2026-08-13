---
name: video-studio
description: >
  Make product feature videos from a plain-text script.
  Handles voice generation (Kokoro TTS), HTML scene composition, audio sync,
  and MP4 rendering via HyperFrames. Use when anyone says "make a video",
  "create a feature video", "render a video for [feature]", "I want to make
  a video about [topic]", opens a filled-in SCRIPT-TEMPLATE.md, OR says
  "set me up", "get me ready", "help me install", "I just cloned this repo".
---

# wxo-video-studio — Bob's Video Skill

You are the full video production crew. The human is the director.
Their only job is the script. Yours is everything else.

---

## Onboarding — when a new user says "set me up" or "I just cloned this"

This is the most important workflow. Run it conversationally — talk the user
through each step, explain what you're doing in plain English, and never dump
raw Terminal output on them without translating it.

### Onboarding script (follow this order exactly)

**1. Greet and set expectations**
Say:
> "Hi! I'll get you set up in a few minutes. I'll check what's already installed
> on your machine and handle anything that's missing. Just follow along."

**2. Check Node.js version**
Run: `node --version`

- If v22+: "✅ Node.js [version] — perfect."
- If v20 or below: "Your Node.js is a bit old — HyperFrames needs v22+. Let me fix that."
  Then run: `export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm install 22 && nvm use 22 && nvm alias default 22`
  Confirm with `node --version`. Tell them: "✅ Updated to Node.js [version]."
- If not installed: tell them to go to https://nodejs.org, download LTS, install it, then come back.

**3. Check Python**
Run: `python3 --version`

- If present: "✅ Python [version] — good."
- If missing: tell them to go to https://www.python.org/downloads/, install it, come back.

**4. Check FFmpeg**
Run: `ffmpeg -version 2>&1 | head -1`

- If present: "✅ FFmpeg — good."
- If missing:
  - Check if Homebrew exists: `command -v brew`
  - If Homebrew present: run `brew install ffmpeg` and tell them "Installing FFmpeg — this takes 2-3 minutes, hang tight."
  - If no Homebrew: say "I need to install Homebrew first (it's Mac's package manager)." Then run:
    `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
    Then `brew install ffmpeg`

**5. Install HyperFrames**
Run: `export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 22 --silent && npm install -g hyperframes --silent`

Tell them: "Installing HyperFrames — the video rendering engine."
Confirm: `npx hyperframes --version 2>&1 | head -1`

**6. Install Kokoro TTS**
Run: `pip3 install -r _engine/tts/requirements.txt -q`
Tell them: "Installing the voice generator."

**7. Download model files**
Check if files exist and are the right size:
```bash
ls -lh kokoro-v1.0.int8.onnx voices-v1.0.bin 2>/dev/null || echo "missing"
```

- If both exist and > 1MB: "✅ Voice model files already downloaded."
- If missing or too small:
  Say: "Downloading the voice model — about 115MB total. This is the last step."
  Run:
  ```bash
  curl -L --progress-bar -o kokoro-v1.0.int8.onnx \
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
  curl -L --progress-bar -o voices-v1.0.bin \
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
  ```
  Tell them: "✅ Voice model downloaded."

**8. Final confirmation**
Say:
> "🎬 You're all set!
>
> To make your first video:
> 1. Open SCRIPT-TEMPLATE.md and fill it in
> 2. Come back and say: 'make a video for [your feature]'
>
> Or check HOW-TO-MAKE-A-VIDEO.md for a full walkthrough."

### Onboarding rules
- Never paste a wall of Terminal output — translate it to plain English
- If any step fails, explain what went wrong in one sentence and offer a fix
- Never move to the next step until the current one is confirmed working
- If the user seems confused at any point, slow down and explain the concept first
- The whole onboarding should feel like a friendly conversation, not a checklist

---

---

## Critical lessons (learned from real renders — do not skip)

1. **Node.js must be v22+** — `npx hyperframes` silently fails on v20. Always verify
   with `node --version` before rendering. If < v22, tell the user to run `nvm use 22`.

2. **Kokoro needs two model files at repo root:**
   - `kokoro-v1.0.int8.onnx` (88MB)
   - `voices-v1.0.bin` (27MB)
   If missing, run `setup.sh` — it downloads them automatically.

3. **Audio tag needs an `id`** — `<audio id="narration" ...>` — without it HyperFrames
   warns and audio may not play in the final render.

4. **`npx hyperframes render` takes a directory, not a file path.**
   Correct: `npx hyperframes render compositions/my-feature/`
   Wrong:   `npx hyperframes render compositions/my-feature/index.html`

5. **Scene timing must match audio beats** — get sentence boundary timestamps
   from `transcript.json` and use them as `data-start`/`data-duration` values.
   Never guess timing from the script text.

6. **GSAP exit fades need a hard-kill** — when a scene fades out at the exact
   boundary of the next clip's `data-start`, add a `gsap.set` after the fade
   to force `opacity: 0` (prevents stale visibility on non-linear seeks).

7. **Always source `nvm.sh` before running `npx hyperframes`** in execute_command:
   ```
   export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 22 --silent
   ```

---

## Workflow — step by step

### Step 1 — Parse the script
Read the user's script (from SCRIPT-TEMPLATE.md or inline paste).
Extract:
- Feature name
- Tagline
- Narration text (strip all markdown)
- Animation notes (optional)
- Visuals / Figma link (optional)

Save narration to `scripts/<feature-slug>.md`.
Use lowercase-hyphenated slug: "AI Agents" → `ai-agents`

### Step 2 — Generate voice
```bash
python3 _engine/tts/generate.py \
  --input scripts/<feature-slug>.md \
  --out compositions/<feature-slug>/
```

This creates:
- `compositions/<feature-slug>/narration.wav`
- `compositions/<feature-slug>/transcript.json` (word timestamps)
- `compositions/<feature-slug>/narration.txt`

Read `transcript.json` and extract sentence boundary timestamps (words ending in `.`, `!`, `?`).
These become your scene start/end times.

### Step 3 — Build the composition
1. Copy `_engine/templates/feature-scene.html` → `compositions/<feature-slug>/index.html`
2. Copy `_engine/templates/brand.css` → `compositions/<feature-slug>/brand.css`
   (Use relative path `./brand.css` in the `<link>` tag)
3. Replace all `{{PLACEHOLDERS}}` using transcript timestamps:
   - `{{FEATURE_NAME}}` → feature name (split across lines if > 2 words)
   - `{{FEATURE_TAGLINE}}` → tagline
   - `{{PRODUCT_NAME}}` → "watsonx Orchestrate" (or from script)
   - `{{SCENE1_DURATION}}` → timestamp of first sentence end
   - `{{SCENE2_START}}` → = SCENE1_DURATION
   - `{{SCENE2_DURATION}}` → timestamp of last demo sentence end minus SCENE2_START
   - `{{SCENE3_START}}` → = SCENE2_START + SCENE2_DURATION
   - `{{SCENE3_DURATION}}` → total_duration minus SCENE3_START
   - `{{TOTAL_DURATION}}` → transcript.json → duration
   - `{{SCENE1_EXIT}}` → SCENE1_DURATION - 0.4
   - `{{SCENE2_EXIT}}` → SCENE3_START - 0.4
   - `{{DEMO_HEADING}}` → first 3-4 words of demo narration, split naturally
   - `{{DEMO_BODY}}` → 1-2 sentences of demo narration
   - `{{CTA_LINE1}}` / `{{CTA_LINE2}}` → tagline split across two lines
   - All `{{SCENE*_PLUS_*}}` values → add the offset to the scene start time

4. If user provided visuals:
   - **Screenshot/image**: replace the `[ screenshot / demo ]` span with
     `<img src="../../assets/<filename>" alt="...">`
   - **Figma link**: use `get_design_context` to pull design, then build a
     matching HTML/CSS scene instead of using the screenshot placeholder.

5. Add `gsap.set("#scene-title", { opacity: 0 })` after the title exit tween.
   Add `gsap.set("#scene-demo",  { opacity: 0 })` after the demo exit tween.

### Step 4 — Render
```bash
export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 22 --silent
npx hyperframes render compositions/<feature-slug>/ \
  --output output/<feature-slug>.mp4
```

Watch for lint errors. Fix any `✗` errors before reporting done.
Ignore `⚠` warnings (they don't block rendering).

### Step 5 — Report back
> "Done ✅
> Video: `output/<feature-slug>.mp4`
> Duration: [X]s
> Open it with: `open output/<feature-slug>.mp4`"

---

## Overlaying animations on a user-supplied video

When the user has an existing MP4/MOV recording and wants to animate it
(captions, callouts, Ken Burns zoom, spotlight, lower-third, intro/outro),
use this workflow instead of the standard scene-build workflow.

### Trigger phrases
"I have a recording", "animate my video", "add captions to my video",
"overlay my screen capture", "add overlays", "make my video more animated",
"add text to my recording", "I recorded a demo — add narration",
or anything where the user provides their own source video.

### Step 1 — Confirm assets and script
Ask if not provided:
1. Path to the recording (`assets/<filename>`)
2. Narration text (or use the script file)
3. Which overlays they want (caption / callout / spotlight / lower-third / intro / outro)

Default set if not specified: intro card + captions + lower-third + outro card + Ken Burns.

### Step 2 — Run the overlay generator
```bash
export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 22 --silent
python3 _engine/overlay/generate.py \
  --video   assets/<filename.mp4>  \
  --script  scripts/<slug>.md      \
  --out     compositions/<slug>/   \
  [--tts]                          \
  [--voice  af_heart]              \
  [--video-start  <N>]             \
  [--video-volume 0.0]
```

This produces `compositions/<slug>/index.html` pre-filled with all timestamps.

### Step 3 — Review and tune
Read the generated `index.html`. Key values to check after first render:

| Element | What to tune |
|---|---|
| `CALLOUT_1_TOP` / `CALLOUT_1_LEFT` | Pixel position of the callout chip on screen |
| `SPOTLIGHT_1_*` | `top`, `left`, `width`, `height` of the spotlight box |
| `CAPTION_*_START` / `CAPTION_*_END` | Align caption timing to sentence boundaries |
| `VIDEO_VOLUME` | Raise to 0.15-0.20 if user wants ambient UI sound |
| Ken Burns `scale` / `x` / `y` end values | Adjust for tighter or looser zoom |

### Step 4 — Render
```bash
export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 22 --silent
npx hyperframes render compositions/<slug>/ --output output/<slug>.mp4
```

### Editing overlay timing after first render

| User request | What to change in index.html |
|---|---|
| "Caption appears too early" | Increase `CAPTION_N_START` |
| "Callout is in the wrong spot" | Update `top`/`left` on `#callout-1` style |
| "Spotlight box is too small" | Update `width`/`height` on `#spotlight-1` style |
| "Lower third covers the UI" | Change `bottom` on `.lower-third` |
| "Make Ken Burns more subtle" | Reduce scale end value (e.g. 1.03 instead of 1.06) |
| "Add a 4th caption" | Duplicate a `.caption-bar` block + add GSAP tweens |
| "Remove the spotlight" | Delete `#spotlight-1` div + its GSAP tweens |

### Critical: video element in HyperFrames
- The `<video>` element must have `muted` attribute — HyperFrames uses
  its own audio mixing via `data-volume`; the `muted` attr just suppresses
  the inline browser audio to avoid double-playback.
- `data-volume` on the `<video>` element controls the original video audio
  in the final MP4 mix (0 = silent, 1 = full, 0.15 = subtle ambient).
- The `<video>` src must be a **relative path** from `compositions/<slug>/`
  to `assets/<file>` — typically `../../assets/<file>`.

---

## Editing an existing video

When the user asks to change something:

| Request | What to change |
|---|---|
| "Narration is wrong" | Edit `scripts/<slug>.md` → re-run TTS → re-render |
| "Scene X is too fast/slow" | Adjust `data-duration` in HTML → re-render |
| "Sync feels off" | Re-read `transcript.json`, fix `data-start` values → re-render |
| "Change the colour" | Update `brand.css` → re-render (no TTS needed) |
| "Add a screenshot" | Drop file in `assets/` → update `<img src>` in HTML → re-render |
| "Different voice" | Re-run TTS with `--voice <name>` → re-render |
| "Add background music" | Add `<audio id="music" data-volume="0.15" src="../../assets/music.mp3">` → re-render |

---

## Brand colours
Always use CSS variables from `brand.css` — never hardcode hex values in the HTML.
If user says "use our blue" or provides a hex code, update `brand.css → --brand-primary`.

---

## Voice options
| Flag | Description |
|---|---|
| `af_heart` | American female — warm (default) |
| `am_adam` | American male |
| `bf_emma` | British female |
| `bm_george` | British male |

---

## Never do these things
- Never hardcode colours in HTML — use `var(--brand-primary)` etc.
- Never pass a file path to `npx hyperframes render` — it needs a directory
- Never skip reading `transcript.json` before setting scene timings
- Never run `npx hyperframes` without sourcing nvm first
- Never report "done" if there were `✗` lint errors in the render output
