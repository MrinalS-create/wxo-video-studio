# Prompt: Overlay animations on your own video

Use this when you already have a recorded screen capture or video, and you
want to add narration, animated captions, callouts, a spotlight effect,
a lower-third bar, and/or an intro/outro title card on top of it.

Copy, paste into Bob, and fill in the [brackets].

---

```
I have a video I recorded at assets/[filename.mp4].
I want to add overlays and animations on top of it.

Feature name: [what the video shows]
Tagline: [one sentence — appears on the intro/outro card]

Narration:
[Paste the narration text here. Bob will generate the voice with Kokoro
 and sync the captions to it automatically.]

Overlays I want:
- [x] Intro title card before the video starts
- [x] Animated captions synced to narration
- [x] Lower-third bar with feature name
- [x] Outro CTA card at the end
- [ ] Callout chip at [top/left pixel position on screen] — label: "[text]", shown from [Xs] to [Ys]
- [ ] Spotlight box around [region description] — from [Xs] to [Ys]

Voice: [af_heart / am_adam / bf_emma / bm_george — or leave blank for default]
Original video audio: [keep at 15% / mute — default is muted]
Trim first [N] seconds of video: [yes/no]

Please generate the composition and render to output/[slug].mp4
```

---

## What each overlay does

| Overlay | Description |
|---|---|
| **Intro title card** | 3-second branded title screen before the video starts. Shows feature name + tagline. |
| **Animated captions** | Bottom-centre text bars, fade in/out synced to narration sentences. |
| **Lower third** | Persistent bottom bar with feature name — slides in after the intro, fades out before outro. |
| **Callout chip** | Blue pill label that appears near a UI element on screen. Position by pixel coordinates. |
| **Spotlight box** | Glowing border around a region of the screen, dims everything else. |
| **Outro CTA card** | Branded closing card. Shows the last two narration sentences in large type. |
| **Ken Burns** | Subtle slow zoom applied to the entire recording (always on, adds production quality). |

---

## Tuning overlays after first render

```
I watched the video. A few tweaks:

- Caption 2 appears too early — push it 1.5 seconds later
- The spotlight box is in the wrong place — move it to top:320 left:640 width:580 height:300
- Remove the callout chip entirely
- The intro card is 3 seconds — make it 4

Please re-render.
```

---

## Adding more captions or callouts

```
Add a 4th caption at 18s that says:
"Every flow run is tracked in the Runs tab — latency, cost, and status at a glance."
Show it until 23s.
```

```
Add a second callout chip at top:440 left:920 with text "Run button"
Show it from 12s to 16s.
```

---

## Swapping the narration voice

```
Regenerate the narration with British male voice (George) and re-render.
```

---

## Keeping the original video audio

```
Set the original video volume to 20% so we can hear the ambient UI sounds
underneath the narration.
```
