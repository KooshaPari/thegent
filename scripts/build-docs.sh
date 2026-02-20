#!/usr/bin/env zsh
set -e

# Multi-version VitePress build script
# Builds docs from different branches into versioned directories

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Version branches to build
VERSION_BRANCHES=("main")
OUTPUT_DIR="docs-dist"

echo "Building VitePress docs for ${#VERSION_BRANCHES[@]} version(s)..."

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Build main branch (current)
echo "Building main version..."
pnpm docs:build

# Copy to main directory
mkdir -p "$OUTPUT_DIR/main"
cp -r docs/.vitepress/dist/* "$OUTPUT_DIR/main/"

echo "Build complete: $OUTPUT_DIR/"
echo "Versions built: ${VERSION_BRANCHES[*]}"

# Create index.html that redirects to default version
cat > "$OUTPUT_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="0;url=main/">
</head>
<body>
  <p>Redirecting to <a href="main/">main documentation</a></p>
</body>
</html>
EOF

echo "Created index.html redirect to main/"
