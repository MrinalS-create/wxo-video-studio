# wxo-video-studio

Turn a plain-text script into a polished, voiced product feature video — in minutes, with Bob.

**No video editing skills needed. No timeline scrubbing. No exports. Just write and talk to Bob.**

---

## How it works

```
You write a script  →  Bob generates the voice  →  Bob builds the scenes  →  MP4 ✅
```

---

## New here? Start with these two files

1. **[HOW-TO-MAKE-A-VIDEO.md](./HOW-TO-MAKE-A-VIDEO.md)** — read this first (5 min)
2. **[SCRIPT-TEMPLATE.md](./SCRIPT-TEMPLATE.md)** — fill this in for your feature

Then open this folder in IBM Bob and paste the prompt from `prompts/start-a-video.md`.

---

## One-time setup

### Option A — Mac installer (recommended for non-developers)
Download and double-click `install/wxo-video-studio-installer.pkg`
> Installs Node.js v22, FFmpeg, HyperFrames, and Kokoro TTS silently. No Terminal needed.

### Option B — Terminal (for developers)
```bash
chmod +x setup.sh && ./setup.sh
```

---

## Folder guide

| Folder | What goes here |
|---|---|
| `scripts/` | Your script `.md` files — one per feature video |
| `assets/` | Screenshots, logos, brand images |
| `output/` | Finished MP4s appear here after rendering |
| `prompts/` | Copy-paste prompts for Bob |
| `_engine/` | The technical machinery — you never need to touch this |

---

## Brand colours

Open `_engine/templates/brand.css` and set your colours once.
Every video you make will automatically use them.

```css
:root {
  --brand-primary:    #7c6bff;  /* ← change this to your brand colour */
  --brand-bg:         #0d0d14;  /* ← dark background */
  --brand-text:       #ffffff;  /* ← main text */
  --brand-text-muted: rgba(255,255,255,0.55); /* ← secondary text */
}
```

---

## License

All tooling (HyperFrames + Kokoro TTS + FFmpeg) is free and open-source (Apache 2.0).
This studio template is MIT licensed — use it however you like.
