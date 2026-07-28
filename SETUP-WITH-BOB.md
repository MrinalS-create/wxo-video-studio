# Setup with Bob

Three steps. That's it.

---

## Step 1 — Clone this repo

```bash
git clone https://github.com/YOUR-ORG/wxo-video-studio.git
cd wxo-video-studio
```

---

## Step 2 — Open in IBM Bob

Open the `wxo-video-studio` folder in your IDE with IBM Bob active.

> **Don't have Bob?** Ask your team lead to get you access to IBM Bob.

---

## Step 3 — Paste this prompt into Bob

```
Hey Bob, I just cloned wxo-video-studio. 
Please set me up and get me ready to make videos.
```

Bob will check what's installed on your machine, install anything missing,
and tell you when you're ready. Just follow along — no Terminal knowledge needed.

---

## That's it.

Once Bob says you're ready, read **HOW-TO-MAKE-A-VIDEO.md** and make your first video.

---

## Troubleshooting

**"Bob doesn't seem to know about video studio"**
Make sure you opened the `wxo-video-studio` folder — not a parent folder.
Bob reads the skill from `.bob/skills/video-studio/SKILL.md` inside this folder.

**"Bob says Node.js needs updating"**
Just tell Bob: *"help me update Node.js"* — Bob will walk you through it.

**"The model download is taking a long time"**
Normal — it's ~115MB total. Leave it running, go get a coffee.

**"Something else went wrong"**
Tell Bob exactly what happened. Bob will diagnose and fix it.
