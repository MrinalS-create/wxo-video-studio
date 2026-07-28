# How to make a feature video with Bob

Read this once. After that, the prompts folder handles everything.

---

## The big picture

You are the **director**. Bob is the **crew**.

| Your job | Bob's job |
|---|---|
| Write the script (the words) | Generate the voice narration |
| Give a feature name + tagline | Build the animated scenes |
| Optionally share a screenshot or Figma link | Sync animations to the audio |
| Review and request changes | Re-render until it's right |

---

## Step 1 — Write your script

Open `SCRIPT-TEMPLATE.md` and fill it in. It looks like this:

```
Feature name:   AI Agents
Tagline:        Automate any workflow

Narration:
Meet AI Agents — the fastest way to automate your workflows.
Instead of building rules by hand, you describe what you want
in plain English and the agent figures out the rest.
Ship your first automation in minutes, not weeks.

Animation notes (optional):
- Scene 1: title card, dark background, name fades in
- Scene 2: show the agent builder screenshot
- Scene 3: CTA with tagline
```

The **narration** is what gets spoken out loud.
The **animation notes** are optional hints for Bob on what to show visually.

---

## Step 2 — Share your visuals (optional but recommended)

Bob can use three kinds of visuals:

**A — Figma link**
Paste your Figma frame URL directly in the chat. Bob reads the design automatically.
> "Here's the screen: https://figma.com/design/abc123/..."

**B — Screenshot or export**
Drop a PNG/JPG into the `assets/` folder. Tell Bob the filename.
> "Use assets/agent-builder-screenshot.png for scene 2"

**C — No visuals**
Bob builds animated placeholder scenes. Works fine for a first draft.

---

## Step 3 — Open Bob and use a prompt

Open this folder in IBM Bob, then copy-paste the right prompt:

- **Starting a new video** → `prompts/start-a-video.md`
- **Editing an existing video** → `prompts/edit-a-video.md`
- **Using a Figma design** → `prompts/figma-video.md`

---

## Step 4 — Review the output

Bob renders the video to `output/`. Open it, watch it, then tell Bob what to change:

- *"The second scene is too fast"* → Bob adjusts timing, re-renders
- *"Change the narration in sentence 2"* → Bob edits script, regenerates voice, re-renders
- *"Use our brand purple instead of this blue"* → Bob updates brand tokens, re-renders
- *"Add our logo in the top left"* → Drop logo in `assets/`, tell Bob

---

## What good sync looks like

Scenes should switch **when a sentence ends** in the narration, not mid-word.
If it feels off, just say *"the sync feels off on the second scene"* and Bob will fix it.

---

## Voice options

Bob uses a warm American female voice by default. You can request:

| Say this to Bob | Voice |
|---|---|
| "use a male voice" | American male (Adam) |
| "use a British female voice" | British female (Emma) |
| "use a British male voice" | British male (George) |

---

## Common questions

**Can I use my own brand colours?**
Yes — open `_engine/templates/brand.css` and change the colour values once.
Every future video will automatically use your brand.

**Can I add a background music track?**
Yes — drop an `.mp3` or `.wav` in `assets/` and tell Bob: *"add assets/music.mp3 as background music at 20% volume"*

**How do I share the video with my team?**
The finished MP4 is in `output/`. Share it like any video file — Slack, email, upload to Loom, etc.

**Can my team use this without Bob?**
No — Bob is the engine that drives everything. Each teammate needs IBM Bob open in their IDE.

**The video rendered but there's no sound?**
Make sure you ran `setup.sh` (or the `.pkg` installer) first. If the issue persists, tell Bob.

---

## The golden rule

> You only need to write the script.
> Everything else is Bob's job.
