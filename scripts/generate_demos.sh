#!/bin/bash
# scripts/generate_demos.sh - Generate GIFs for documentation

set -e

# Directories
DEMO_SRC="docs/demos"
DEMO_DEST="docs/public/assets/demos"
mkdir -p "$DEMO_DEST"

echo "🚀 Generating documentation demos..."

# 1. Generate CLI demos using vhs
if command -v vhs >/dev/null 2>&1; then
    echo "📼 Generating CLI demos with vhs..."
    for tape in "$DEMO_SRC"/cli/*.tape; do
        if [ -f "$tape" ]; then
            filename=$(basename "$tape" .tape)
            echo "  - Processing $filename..."
            vhs < "$tape"
        fi
    done
else
    echo "⚠️ vhs not found. Skipping CLI demos."
    echo "Install vhs: brew install vhs"
fi

# 2. Generate Web demos using Playwright
# We'll look for playwright tests in docs/demos/web
if [ -d "$DEMO_SRC/web" ] && [ "$(ls -A "$DEMO_SRC/web")" ]; then
    echo "🎭 Generating Web demos with Playwright..."
    # Check if we should use npx playwright or pytest
    if [ -f "package.json" ] && grep -q "playwright" package.json; then
        echo "  - Running Playwright (Node.js)..."
        npx playwright test "$DEMO_SRC/web"
    elif [ -f "pyproject.toml" ] && grep -q "playwright" pyproject.toml; then
         echo "  - Running Playwright (Python)..."
         pytest "$DEMO_SRC/web"
    fi
    
    # Optional: Convert videos to GIFs if ffmpeg is available
    if command -v ffmpeg >/dev/null 2>&1; then
        echo "🎞️ Converting Playwright videos to GIFs..."
        # This is a simplified example, real path would depend on playwright config
        find "$DEMO_SRC"/web/test-results -type f \( -name "video.webm" -o -name "video.mp4" \) -print0 | while IFS= read -r -d '' video; do
            output_name=$(basename "$(dirname "$video")").gif
            ffmpeg -nostdin -i "$video" -vf "fps=10,scale=1200:-1:flags=lanczos" "$DEMO_DEST/$output_name" -y
        done
    fi
else
    echo "ℹ️ No web demos found in $DEMO_SRC/web."
fi

echo "✅ Demo generation complete!"
