#!/usr/bin/env zsh
# Auto-generate GIFs from demo scripts
# Reduces verbosity: single command to generate all demo GIFs

set -e

DEMO_DIR="docs/demos"
OUTPUT_DIR="docs/public/assets/demos"

mkdir -p "$OUTPUT_DIR"

echo "🎬 Generating demo GIFs..."

# VHS terminal recordings
if [ -d "$DEMO_DIR/cli" ]; then
  echo "📹 Processing VHS terminal recordings..."
  for tape in "$DEMO_DIR/cli"/*.tape; do
    if [ -f "$tape" ]; then
      name=$(basename "$tape" .tape)
      echo "  → Generating GIF from $tape..."
      vhs "$tape" -o "$OUTPUT_DIR/${name}.gif" 2>/dev/null || {
        echo "  ⚠️  VHS not installed. Install with: brew install vhs"
      }
    fi
  done
fi

# Playwright browser recordings
if [ -d "recordings" ]; then
  echo "🌐 Processing Playwright browser recordings..."
  
  # Install browsers if needed (minimal, just chromium for demos)
  npx playwright install chromium --with-deps 2>/dev/null || true
  
  for script in recordings/*.spec.ts; do
    if [ -f "$script" ]; then
      name=$(basename "$script" .spec.ts)
      echo "  → Generating demo output from $script..."
      # For now, we just run the test to ensure it passes.
      # True GIF generation requires a plugin or xvfb/ffmpeg setup,
      # but we can capture screenshots/videos as artifacts.
      npx playwright test "$script" --project=chromium || {
        echo "  ⚠️  Failed to run Playwright test $script"
      }
    fi
  done
fi

echo "✅ Demo GIF generation complete!"
echo "   Output: $OUTPUT_DIR"
