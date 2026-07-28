#!/bin/bash
# ─────────────────────────────────────────────────────────────────────
#  wxo-video-studio — Setup script
#  Run once after cloning: chmod +x setup.sh && ./setup.sh
# ─────────────────────────────────────────────────────────────────────

set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "🎬  wxo-video-studio Setup"
echo "──────────────────────────"

# ── 1. Check Node.js v22+ ─────────────────────────────────────────────
echo ""
echo "1/6  Checking Node.js..."
if ! command -v node &> /dev/null; then
  echo "     ❌  Node.js not found."
  echo "     👉  Install it: https://nodejs.org (LTS version)"
  exit 1
fi
NODE_MAJOR=$(node --version | sed 's/v//' | cut -d. -f1)
if [ "$NODE_MAJOR" -lt 22 ]; then
  echo "     ⚠️   Node.js $(node --version) — need v22+."
  # Try nvm auto-switch
  if [ -s "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
    nvm install 22 --silent && nvm use 22 --silent
    echo "     ✅  Switched to Node.js $(node --version) via nvm"
  else
    echo "     👉  Update Node.js: https://nodejs.org (LTS version)"
    exit 1
  fi
fi
echo "     ✅  Node.js $(node --version)"

# ── 2. Check Python 3 ────────────────────────────────────────────────
echo ""
echo "2/6  Checking Python..."
if ! command -v python3 &> /dev/null; then
  echo "     ❌  Python 3 not found."
  echo "     👉  Install it: https://www.python.org/downloads/"
  exit 1
fi
echo "     ✅  Python $(python3 --version)"

# ── 3. Check FFmpeg ──────────────────────────────────────────────────
echo ""
echo "3/6  Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
  echo "     ❌  FFmpeg not found."
  if command -v brew &> /dev/null; then
    echo "     🔧  Installing FFmpeg via Homebrew..."
    brew install ffmpeg -q
    echo "     ✅  FFmpeg installed"
  else
    echo "     👉  Install Homebrew first, then run: brew install ffmpeg"
    echo "         Homebrew: https://brew.sh"
    exit 1
  fi
fi
echo "     ✅  FFmpeg $(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')"

# ── 4. Install HyperFrames CLI ───────────────────────────────────────
echo ""
echo "4/6  Installing HyperFrames..."
npm install -g hyperframes --silent
echo "     ✅  HyperFrames ready"

# ── 5. Install Kokoro TTS Python packages ────────────────────────────
echo ""
echo "5/6  Installing Kokoro TTS..."
pip3 install -r "$REPO_DIR/_engine/tts/requirements.txt" -q
echo "     ✅  Kokoro TTS ready"

# ── 6. Download Kokoro model files ───────────────────────────────────
echo ""
echo "6/6  Downloading voice model files..."

MODEL="$REPO_DIR/kokoro-v1.0.int8.onnx"
VOICES="$REPO_DIR/voices-v1.0.bin"
BASE_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"

if [ ! -f "$MODEL" ] || [ "$(wc -c < "$MODEL")" -lt 1000000 ]; then
  echo "     ⬇️   Downloading kokoro-v1.0.int8.onnx (88MB)..."
  curl -L --progress-bar -o "$MODEL" "$BASE_URL/kokoro-v1.0.int8.onnx"
  echo "     ✅  Model downloaded"
else
  echo "     ✅  Model already present"
fi

if [ ! -f "$VOICES" ] || [ "$(wc -c < "$VOICES")" -lt 1000000 ]; then
  echo "     ⬇️   Downloading voices-v1.0.bin (27MB)..."
  curl -L --progress-bar -o "$VOICES" "$BASE_URL/voices-v1.0.bin"
  echo "     ✅  Voices downloaded"
else
  echo "     ✅  Voices already present"
fi

# ── Done ─────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────"
echo "✅  Setup complete! You're ready to make videos."
echo ""
echo "👉  Next step:"
echo "    Open this folder in IBM Bob and say:"
echo "    'I want to make a feature video for [your feature]'"
echo ""
echo "📖  Or read HOW-TO-MAKE-A-VIDEO.md to get started."
echo ""
