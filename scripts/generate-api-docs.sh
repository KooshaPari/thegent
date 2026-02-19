#!/bin/bash
# Wrapper script for generate-api-docs.py
# Auto-generates API docs from Python docstrings for VitePress documentation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
SOURCE_DIR="${SOURCE_DIR:-src/thegent}"
OUTPUT_DIR="${OUTPUT_DIR:-docs/reference/api}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --source)
            SOURCE_DIR="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --module)
            MODULE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--source DIR] [--output DIR] [--module MODULE]"
            echo ""
            echo "Options:"
            echo "  --source DIR    Source directory (default: src/thegent)"
            echo "  --output DIR   Output directory (default: docs/reference/api)"
            echo "  --module MOD   Process single module (e.g., cli.py)"
            echo "  --help, -h     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the Python script
if [ -n "$MODULE" ]; then
    python3 "$SCRIPT_DIR/generate-api-docs.py" --source "$SOURCE_DIR" --output "$OUTPUT_DIR" --module "$MODULE"
else
    python3 "$SCRIPT_DIR/generate-api-docs.py" --source "$SOURCE_DIR" --output "$OUTPUT_DIR"
fi
