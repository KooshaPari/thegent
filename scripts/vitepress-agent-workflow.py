#!/usr/bin/env python3
"""
Unified agent workflow for auto-populating VitePress documentation.

Part of VitePress Rich Documentation Implementation Plan - Phase 3.
Combines all generators into a single workflow.
"""

import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def run_script(script_path: Path, args: list[str] | None = None) -> bool:
    """Run a Python script and return success status."""
    if not script_path.exists():
        print(f"Warning: Script not found: {script_path}", file=sys.stderr)
        return False

    cmd = ["python3", str(script_path)] + (args or [])
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path.name}: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return False


def get_changed_files() -> set[Path]:
    """Get list of changed files using git."""
    try:
        result = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True, check=True)
        changed = set()
        for line in result.stdout.strip().split("\n"):
            if line:
                changed.add(Path(line))
        return changed
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()


def should_regenerate(script_path: Path, changed_files: set[Path], source_dirs: list[str]) -> bool:
    """Check if script should run based on changed files."""
    if not changed_files:
        return True  # No git info, regenerate everything

    # Check if any source files changed
    for changed_file in changed_files:
        for source_dir in source_dirs:
            if source_dir in str(changed_file):
                return True

    return False


def run_shell_script(script_path: Path, args: list[str] | None = None) -> bool:
    """Run a shell script and return success status."""
    if not script_path.exists():
        print(f"Warning: Script not found: {script_path}", file=sys.stderr)
        return False

    cmd = ["bash", str(script_path)] + (args or [])
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path.name}: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified agent workflow for VitePress documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all generators
  python3 scripts/vitepress-agent-workflow.py

  # Run only API docs
  python3 scripts/vitepress-agent-workflow.py --api-docs

  # Run in watch mode (requires watchdog)
  python3 scripts/vitepress-agent-workflow.py --watch
        """,
    )

    parser.add_argument("--api-docs", action="store_true", help="Generate API docs (Python)")
    parser.add_argument("--api-docs-ts", action="store_true", help="Generate API docs (TypeScript/JavaScript)")
    parser.add_argument("--architecture", action="store_true", help="Generate architecture diagrams")
    parser.add_argument("--cli-examples", action="store_true", help="Generate CLI examples")
    parser.add_argument("--demos", action="store_true", help="Generate demo GIFs")
    parser.add_argument("--sidebar", action="store_true", help="Generate sidebar")
    parser.add_argument("--llms", action="store_true", help="Generate LLM-friendly docs")
    parser.add_argument("--watch", action="store_true", help="Watch mode (auto-regenerate on changes)")
    parser.add_argument("--skip-demos", action="store_true", help="Skip demo generation (slow)")
    parser.add_argument("--parallel", action="store_true", help="Run generators in parallel (faster)")
    parser.add_argument("--incremental", action="store_true", help="Only regenerate changed files (requires git)")

    args = parser.parse_args()

    scripts_dir = Path(__file__).parent

    # If no specific flags, run all
    run_all = not any(
        [args.api_docs, args.api_docs_ts, args.architecture, args.cli_examples, args.demos, args.sidebar, args.llms]
    )

    results = {}
    changed_files = get_changed_files() if args.incremental else set()

    # Define tasks with their source directories for incremental checking
    tasks = []

    if run_all or args.api_docs:
        tasks.append(
            (
                "api_docs",
                "Phase 1: Generating Python API Documentation",
                scripts_dir / "generate-api-docs.py",
                [],
                ["src/"],
            )
        )

    if run_all or args.api_docs_ts:
        tasks.append(
            (
                "api_docs_ts",
                "Phase 1b: Generating TypeScript/JavaScript API Documentation",
                scripts_dir / "generate-api-docs-typescript.py",
                [],
                ["docs/.vitepress/"],
            )
        )

    if run_all or args.architecture:
        tasks.append(
            (
                "architecture",
                "Phase 2: Generating Architecture Diagrams",
                scripts_dir / "generate-architecture-diagrams.py",
                ["--type", "both"],
                ["src/"],
            )
        )

    if run_all or args.cli_examples:
        tasks.append(
            (
                "cli_examples",
                "Phase 3: Generating CLI Examples",
                scripts_dir / "generate-cli-examples.py",
                [],
                ["src/thegent/cli/"],
            )
        )

    if (run_all or args.demos) and not args.skip_demos:
        tasks.append(
            (
                "demos",
                "Phase 4: Generating Demo GIFs",
                scripts_dir / "agent-generate-demos.py",
                ["--generate-tapes-only"],
                ["docs/demos/"],
            )
        )

    if run_all or args.sidebar:
        tasks.append(("sidebar", "Phase 5: Generating Sidebar", scripts_dir / "generate-sidebar.py", [], ["docs/"]))

    if run_all or args.llms:
        tasks.append(
            (
                "llms",
                "Phase 6: Generating LLM-Friendly Documentation",
                scripts_dir / "generate-llms-docs.py",
                [],
                ["docs/"],
            )
        )

    # Filter tasks for incremental mode
    if args.incremental:
        original_count = len(tasks)
        tasks = [t for t in tasks if should_regenerate(t[2], changed_files, t[4])]
        if len(tasks) < original_count:
            print(f"📊 Incremental mode: {len(tasks)}/{original_count} tasks need regeneration")

    # Execute tasks (parallel or sequential)
    if args.parallel and len(tasks) > 1:
        print("🚀 Running generators in parallel...")
        with ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as executor:
            futures = {}
            for task_id, phase_name, script_path, script_args, _ in tasks:
                print(f"  → Starting: {phase_name}")
                future = executor.submit(run_script, script_path, script_args)
                futures[future] = (task_id, phase_name)

            for future in as_completed(futures):
                task_id, phase_name = futures[future]
                try:
                    results[task_id] = future.result()
                    status = "✅" if results[task_id] else "❌"
                    print(f"  {status} Completed: {phase_name}")
                except Exception as e:
                    results[task_id] = False
                    print(f"  ❌ Failed: {phase_name} - {e}", file=sys.stderr)
    else:
        # Sequential execution
        for task_id, phase_name, script_path, script_args, _ in tasks:
            print("=" * 60)
            print(phase_name)
            print("=" * 60)
            results[task_id] = run_script(script_path, script_args)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for phase, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {phase.replace('_', ' ').title()}")

    all_success = all(results.values())

    if all_success:
        print("\n✅ All phases completed successfully!")
        print("\nNext steps:")
        print("  1. Review generated files in docs/")
        print("  2. Update docs/.vitepress/config.ts to use generated sidebar")
        print("  3. Run 'bun run docs:dev' to preview")
        return 0
    print("\n⚠️  Some phases failed. Check errors above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
