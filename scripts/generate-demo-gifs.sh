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
if [ -d "$DEMO_DIR/web" ]; then
  echo "🌐 Processing Playwright browser recordings..."
  cd "$DEMO_DIR/web"
  
  # Install browsers if needed
  npx playwright install --with-deps chromium 2>/dev/null || true
  
  for script in *.spec.ts; do
    if [ -f "$script" ]; then
      name=$(basename "$script" .spec.ts)
      echo "  → Generating GIF from $script..."
      npx playwright test "$script" --project=chromium --gif="$OUTPUT_DIR/${name}.gif" || {
        echo "  ⚠️  Failed to generate GIF from $script"
      }
    fi
  done
  
  cd - > /dev/null
fi

echo "✅ Demo GIF generation complete!"
echo "   Output: $OUTPUT_DIR"
