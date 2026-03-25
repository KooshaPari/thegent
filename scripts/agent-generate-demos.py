#!/usr/bin/env python3
"""
Agent workflow: Auto-generate demo GIFs from documentation.

Part of VitePress Rich Documentation Implementation Plan - Phase 2.
"""

import re
import subprocess
import sys
from pathlib import Path


def find_demo_scripts(docs_dir: Path) -> list[Path]:
    """Find demo scripts in documentation."""
    demos = []

    for md_file in docs_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        # Find code blocks marked as demos
        # Pattern: ```bash demo or ```python demo
        demo_pattern = r"```(python|bash|sh).*demo"
        if re.search(demo_pattern, content, re.IGNORECASE):
            demos.append(md_file)

        # Also check for explicit demo markers
        if "<!-- demo:" in content or "[demo]" in content.lower():
            demos.append(md_file)

    return demos


def extract_code_block(content: str, lang: str = "bash") -> str | None:
    """Extract code block from markdown."""
    pattern = rf"```{lang}.*?\n(.*?)```"
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()
    return None


def generate_vhs_tape(script_content: str, output_path: Path) -> bool:
    """Generate VHS tape file from script content."""
    tape_content = f"""Output {output_path.stem}.gif
Set FontSize 14
Set Width 1200
Set Height 600
Set Theme "Catppuccin Mocha"

Type "{script_content.replace(chr(10), " ")}"
Sleep 500ms
Enter
Sleep 2s
"""

    tape_path = output_path.parent / f"{output_path.stem}.tape"
    tape_path.write_text(tape_content, encoding="utf-8")
    return True


def generate_gif_from_tape(tape_path: Path, output_dir: Path) -> bool:
    """Generate GIF from VHS tape file."""
    if not tape_path.exists():
        return False

    # Check if VHS is installed
    try:
        subprocess.run(["vhs", "--version"], capture_output=True, check=True)
    except subprocess.CalledProcessError, FileNotFoundError:
        print(f"Warning: VHS not installed. Skipping {tape_path.name}", file=sys.stderr)
        return False

    output_gif = output_dir / f"{tape_path.stem}.gif"

    try:
        subprocess.run(["vhs", str(tape_path), "-o", str(output_gif)], check=True, capture_output=True)
        print(f"✅ Generated: {output_gif}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating GIF from {tape_path}: {e}", file=sys.stderr)
        return False


def process_demo_file(md_file: Path, demos_dir: Path, output_dir: Path) -> bool:
    """Process a single demo markdown file."""
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not read {md_file}: {e}", file=sys.stderr)
        return False

    # Extract bash/python code blocks
    for lang in ["bash", "python", "sh"]:
        code = extract_code_block(content, lang)
        if code:
            # Generate tape file
            tape_name = f"{md_file.stem}_{lang}"
            tape_path = demos_dir / "cli" / f"{tape_name}.tape"
            tape_path.parent.mkdir(parents=True, exist_ok=True)

            if generate_vhs_tape(code, tape_path):
                # Generate GIF
                generate_gif_from_tape(tape_path, output_dir)
                return True

    return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-generate demo GIFs from docs")
    parser.add_argument("--docs-dir", type=str, default="docs", help="Documentation directory")
    parser.add_argument("--demos-dir", type=str, default="docs/demos", help="Demos directory")
    parser.add_argument("--output-dir", type=str, default="docs/public/assets/demos", help="Output directory for GIFs")
    parser.add_argument(
        "--generate-tapes-only", action="store_true", help="Only generate tape files, do not create GIFs"
    )

    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    demos_dir = Path(args.demos_dir)
    output_dir = Path(args.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    demo_files = find_demo_scripts(docs_dir)
    print(f"Found {len(demo_files)} demo files")

    for md_file in demo_files:
        print(f"Processing: {md_file.relative_to(Path.cwd())}")
        process_demo_file(md_file, demos_dir, output_dir)

    if not args.generate_tapes_only:
        # Also run the generate-demo-gifs.sh script
        gif_script = Path(__file__).parent / "generate-demo-gifs.sh"
        if gif_script.exists():
            print("\nRunning generate-demo-gifs.sh...")
            subprocess.run(["bash", str(gif_script)], check=False)

    print(f"\n✅ Demo generation complete. Output: {output_dir}")


if __name__ == "__main__":
    main()
