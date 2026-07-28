# Prompt: Start a new video

Copy and paste this into Bob (IBM Bob IDE). Fill in the [brackets].

---

```
I want to make a feature video using the wxo-video-studio pipeline.

Here is my script:

---
[paste your filled-in SCRIPT-TEMPLATE.md here]
---

Please:
1. Save the script to scripts/[feature-slug].md
2. Generate the voice narration with Kokoro TTS
3. Build the HTML composition synced to the audio beats
4. Render the final MP4 to output/[feature-slug].mp4
5. Tell me the file path and duration when done

Use the brand colours from _engine/templates/brand.css.
```

---

## Tips for better results

- **Be specific about tone** — add "energetic and fast-paced" or "calm and professional" to the narration section
- **Mention your visuals** — if you dropped a screenshot in `assets/`, say so: *"use assets/my-screenshot.png in scene 2"*
- **Figma link** — if you have one, add: *"here's the Figma design: [URL]"* and Bob will pull colours and layout from it
- **Length** — if you need a specific duration, say: *"keep it under 30 seconds"*
