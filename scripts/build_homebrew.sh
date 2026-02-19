#!/bin/bash
# scripts/build_homebrew.sh
# Generates a Homebrew formula from the template

set -e

VERSION=${1:-"0.1.0"}
TEMPLATE_FILE="templates/homebrew/thegent.rb"
OUTPUT_FILE="thegent.rb"

# If we have a tarball, calculate SHA256, otherwise use a placeholder
if [ -f "dist/thegent-$VERSION.tar.gz" ]; then
    SHA256=$(shasum -a 256 "dist/thegent-$VERSION.tar.gz" | awk '{print $1}')
else
    SHA256="PLACEHOLDER_SHA256"
fi

echo "Generating Homebrew formula for version $VERSION..."

sed -e "s/{{VERSION}}/$VERSION/g" \
    -e "s/{{SHA256}}/$SHA256/g" \
    "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo "Formula generated at $OUTPUT_FILE"
