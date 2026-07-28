#!/bin/bash
# ─────────────────────────────────────────────────────────────────────
#  wxo-video-studio — Mac .pkg Installer Builder
#
#  This script builds a double-click Mac installer (.pkg) so teammates
#  can set up the video studio without ever opening Terminal.
#
#  Run this ONCE on your Mac to produce: install/wxo-video-studio-installer.pkg
#  Then share that .pkg file with your team.
#
#  Requirements to BUILD the installer: macOS, Xcode CLI tools
#  Requirements to RUN the installer:   macOS 12+, internet connection
# ─────────────────────────────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR/pkg-build"
OUTPUT_PKG="$SCRIPT_DIR/wxo-video-studio-installer.pkg"

echo ""
echo "📦  Building wxo-video-studio Mac Installer"
echo "────────────────────────────────────────────"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/scripts"
mkdir -p "$BUILD_DIR/payload/usr/local/wxo-video-studio"

# ── Write the postinstall script (runs on the user's Mac after .pkg installs) ──
cat > "$BUILD_DIR/scripts/postinstall" << 'POSTINSTALL'
#!/bin/bash
set -e
LOG="/var/log/wxo-video-studio-install.log"
exec > >(tee -a "$LOG") 2>&1

echo ""
echo "🎬  wxo-video-studio Installer"
echo "Installing required tools..."

# ── Install Homebrew (if not present) ──────────────────────────────────────────
if ! command -v brew &> /dev/null; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" < /dev/null
fi

# Add Homebrew to PATH for Apple Silicon
export PATH="/opt/homebrew/bin:$PATH"

# ── Install Node.js v22 via nvm ───────────────────────────────────────────────
if ! command -v nvm &> /dev/null; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
fi
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
nvm install 22
nvm use 22
nvm alias default 22

# ── Install FFmpeg ────────────────────────────────────────────────────────────
if ! command -v ffmpeg &> /dev/null; then
  brew install ffmpeg
fi

# ── Install HyperFrames ───────────────────────────────────────────────────────
npm install -g hyperframes --silent

# ── Install Python packages ───────────────────────────────────────────────────
pip3 install kokoro-onnx soundfile numpy -q

# ── Download Kokoro model files ───────────────────────────────────────────────
STUDIO_DIR="$HOME/wxo-video-studio"
mkdir -p "$STUDIO_DIR"
BASE="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"

if [ ! -f "$STUDIO_DIR/kokoro-v1.0.int8.onnx" ]; then
  curl -L --progress-bar -o "$STUDIO_DIR/kokoro-v1.0.int8.onnx" "$BASE/kokoro-v1.0.int8.onnx"
fi
if [ ! -f "$STUDIO_DIR/voices-v1.0.bin" ]; then
  curl -L --progress-bar -o "$STUDIO_DIR/voices-v1.0.bin" "$BASE/voices-v1.0.bin"
fi

echo ""
echo "✅  wxo-video-studio is ready."
echo "Open the wxo-video-studio folder in IBM Bob to get started."
POSTINSTALL

chmod +x "$BUILD_DIR/scripts/postinstall"

# ── Build the .pkg ────────────────────────────────────────────────────────────
echo ""
echo "Building .pkg..."

pkgbuild \
  --nopayload \
  --scripts "$BUILD_DIR/scripts" \
  --identifier "com.ibm.wxo-video-studio" \
  --version "1.0.0" \
  "$OUTPUT_PKG"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "────────────────────────────────────────────"
echo "✅  Installer built: $OUTPUT_PKG"
echo ""
echo "Share this file with your team."
echo "They double-click it — that's the entire setup."
echo ""
