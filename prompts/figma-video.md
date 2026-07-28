# Prompt: Make a video from a Figma design

Use this when you have a Figma frame you want to feature in the video.
Bob will read the design directly — colours, layout, fonts — and build a scene that matches it.

Copy and paste into Bob, fill in the [brackets].

---

```
I want to make a feature video using a Figma design.

Figma link: [paste your Figma frame URL here]
Feature name: [e.g. "AI Agents"]
Tagline: [e.g. "Automate any workflow"]

Narration:
[paste your script here]

Please:
1. Read the Figma design and extract the visual style (colours, layout, key elements)
2. Use those design elements to build the video scenes — make it look like our actual product
3. Generate the voice narration with Kokoro TTS
4. Sync the scenes to the audio beats
5. Render to output/[feature-slug].mp4
```

---

## How to get a Figma frame URL

1. Open your Figma file
2. Click on the frame you want (the outermost rectangle/artboard)
3. Copy the URL from your browser — it should look like:
   `https://figma.com/design/abc123/My-File?node-id=1-2`
4. Paste that URL into the prompt above

---

## What Bob can extract from Figma

| What Bob reads | How it's used |
|---|---|
| Background colour | Video background |
| Primary/accent colours | Headings, highlights, animated elements |
| Font family | All text in the video |
| Layout structure | Scene composition and element positioning |
| Component details | Replicates UI elements as HTML/CSS |
| Screenshots of frames | Used as scene visuals |

---

## Tip

If you want Bob to use the Figma design **as a screenshot** (not reconstruct it):
> "Export frame 'Feature Demo' from Figma as PNG, save to assets/, and use it in scene 2"

If you want Bob to **replicate the design in HTML** (animated, clean):
> "Read the Figma design and build a matching HTML scene — don't use a screenshot"
