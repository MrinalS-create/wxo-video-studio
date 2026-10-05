# wxo-video-studio

> Turn a plain-text script into a polished, voiced product feature video — in minutes, with IBM Bob.

**No video editing. No timeline scrubbing. No exports. Just write and talk to Bob.**

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Requires IBM Bob](https://img.shields.io/badge/requires-IBM%20Bob-purple.svg)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)

---

## How it works

```
You fill in a script  →  Bob generates the voice  →  Bob builds the scenes  →  MP4 ✅
```

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **IBM Bob** | Required — Bob is the engine that drives everything |
| **macOS** | Setup script targets Mac; Windows/Linux support coming |
| **Node.js v22+** | `setup.sh` installs it automatically via nvm if missing |
| **Python 3** | Needed for Kokoro TTS voice generation |
| **FFmpeg** | `setup.sh` installs it automatically via Homebrew if missing |

> **No IBM Bob?** Request access through your IBM Tools team. Without it, the studio won't run.

---

## Quick start

### 1 — Clone and set up

```bash
git clone https://github.com/MrinalS-create/wxo-video-studio.git
cd wxo-video-studio
chmod +x setup.sh && ./setup.sh
```

Setup takes ~2 minutes. It downloads all dependencies and the Kokoro voice model (~115MB total).

### 2 — Write your script

Open [`SCRIPT-TEMPLATE.md`](./SCRIPT-TEMPLATE.md) and fill it in. Only the **Narration** section is required.

```
Feature name:   AI Agents
Tagline:        Automate any workflow

Narration:
Meet AI Agents — the fastest way to automate your workflows.
Describe what you want in plain English.
Ship your first automation in minutes, not weeks.
```

### 3 — Open Bob and start

Open this folder in IBM Bob, then copy-paste the prompt from [`prompts/start-a-video.md`](./prompts/start-a-video.md).

Bob will:
1. Save your script
2. Generate voiced narration (Kokoro TTS, runs offline)
3. Build animated HTML scenes synced to the audio
4. Render a final MP4 to `output/`

### 4 — Review and iterate

Watch the video in `output/`. Then just tell Bob what to change:

- *"The second scene is too fast"*
- *"Change the narration in sentence 2"*
- *"Use our brand purple instead of this blue"*
- *"Add our logo in the top left"*

Bob re-renders until it's right.

---

## Folder guide

| Folder | What goes here |
|---|---|
| `scripts/` | Your script `.md` files — one per video |
| `assets/` | Screenshots, logos, brand images, recordings |
| `output/` | Finished MP4s land here after render |
| `prompts/` | Copy-paste prompts for Bob |
| `_engine/` | The pipeline machinery — you never need to touch this |

---

## Prompts reference

| Task | Prompt file |
|---|---|
| Start a new video from scratch | [`prompts/start-a-video.md`](./prompts/start-a-video.md) |
| Edit an existing video | [`prompts/edit-a-video.md`](./prompts/edit-a-video.md) |
| Use a Figma design as the visual | [`prompts/figma-video.md`](./prompts/figma-video.md) |
| Add animation on top of a screen recording | [`prompts/overlay-a-video.md`](./prompts/overlay-a-video.md) |

---

## Brand colours

Open [`_engine/templates/brand.css`](./_engine/templates/brand.css) and set your colours once.
Every video you make will automatically use them.

```css
:root {
  --brand-primary:    #7c6bff;  /* ← your brand colour */
  --brand-bg:         #0d0d14;  /* ← dark background   */
  --brand-text:       #ffffff;  /* ← main text         */
  --brand-text-muted: rgba(255,255,255,0.55);
}
```

---

## Voice options

Bob uses a warm American female voice by default. You can request:

| Ask Bob | Voice |
|---|---|
| "use a male voice" | American male (Adam) |
| "use a British female voice" | British female (Emma) |
| "use a British male voice" | British male (George) |

---

## Full guide

For detailed instructions, see **[HOW-TO-MAKE-A-VIDEO.md](./HOW-TO-MAKE-A-VIDEO.md)**.

---

## License

This studio template is **MIT licensed** — use it however you like.

The underlying tools are free and open-source:
- [HyperFrames](https://github.com/hyperframes/hyperframes) — Apache 2.0
- [Kokoro TTS](https://github.com/thewh1teagle/kokoro-onnx) — Apache 2.0
- [FFmpeg](https://ffmpeg.org) — LGPL 2.1+
