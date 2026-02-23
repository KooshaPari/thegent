#!/usr/bin/env python3
"""
Friction Detector

Automatically detects CLI/UX/DX/AX friction patterns, optimizations, and process inefficiencies.

Detects:
- CLI verbosity patterns (cd &&, 2>&1, head, etc.)
- Process/agent workflow inefficiencies (sequential calls, manual coordination)
- File operation optimizations (multiple reads, full reads, caching)
- Code quality anti-patterns (custom retry/cache, manual file watching)
- Performance bottlenecks (subprocess overhead, regex in loops)
- Error handling issues (bare except, silent failures)
- Type safety gaps (missing hints, Any usage)
- Agent process optimizations (delegation, parallelization, context management)

Called by hooks and can be invoked manually.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FrictionPattern:
    """A friction pattern to detect."""

    name: str
    pattern: re.Pattern
    category: str  # dx, ux, ax
    friction_type: str
    description: str
    solution: str
    priority: str = "P2"


# Comprehensive friction patterns - detects UX/DX/AX friction, optimizations, and process inefficiencies
FRICTION_PATTERNS = [
    # ========== CLI/UX Verbosity Patterns ==========
    FrictionPattern(
        name="cd_and_command",
        pattern=re.compile(r"cd\s+[^\s]+\s+&&\s+\w+"),
        category="ux",
        friction_type="verbosity",
        description="Commands requiring 'cd &&' instead of working from any directory",
        solution="CLI should handle working directory internally",
        priority="P1",
    ),
    FrictionPattern(
        name="stderr_redirect",
        pattern=re.compile(r"2>&1"),
        category="ux",
        friction_type="error_handling",
        description="Commands requiring '2>&1' for error handling",
        solution="CLI should send errors to stderr automatically",
        priority="P1",
    ),
    FrictionPattern(
        name="head_pagination",
        pattern=re.compile(r"\|\s*head\s+(-n\s*)?\d+|head\s+(-n\s*)?\d+|head\s+-?\d+"),
        category="ux",
        friction_type="pagination",
        description="Commands requiring 'head' for output limiting",
        solution="CLI should have built-in --limit option",
        priority="P1",
    ),
    FrictionPattern(
        name="grep_filtering",
        pattern=re.compile(r"\|\s*grep\s+-v"),
        category="ux",
        friction_type="filtering",
        description="Commands requiring grep -v to filter noise",
        solution="CLI should filter noise automatically or have --quiet flag",
        priority="P2",
    ),
    FrictionPattern(
        name="tail_pagination",
        pattern=re.compile(r"\|\s*tail\s+(-n\s*)?\d+|tail\s+(-n\s*)?\d+|tail\s+-?\d+"),
        category="ux",
        friction_type="pagination",
        description="Commands requiring 'tail' for output limiting",
        solution="CLI should have built-in --limit or --tail option",
        priority="P2",
    ),
    FrictionPattern(
        name="sed_awk_filtering",
        pattern=re.compile(r"\|\s*(sed|awk)\s+"),
        category="ux",
        friction_type="filtering",
        description="Commands requiring sed/awk for output transformation",
        solution="CLI should have native filtering/transformation options",
        priority="P2",
    ),
    # ========== Process/Agent Workflow Patterns ==========
    FrictionPattern(
        name="bash_wrapper_loop",
        pattern=re.compile(r"for\s+\w+\s+in\s+.*;\s+do\s+(thegent|thegent\s+\w+)"),
        category="dx",
        friction_type="complexity",
        description="Bash loops wrapping thegent commands",
        solution="CLI should have --repeat or native loop support",
        priority="P1",
    ),
    FrictionPattern(
        name="while_loop_polling",
        pattern=re.compile(r"while\s+.*;\s+do\s+(thegent|sleep|wait)"),
        category="dx",
        friction_type="polling",
        description="Bash while loops for polling/waiting",
        solution="Use thegent plan wait-next or thegent wait <session_id> instead",
        priority="P1",
    ),
    FrictionPattern(
        name="sequential_agent_calls",
        pattern=re.compile(r"thegent\s+\w+.*\n.*thegent\s+\w+.*\n.*thegent\s+\w+"),
        category="dx",
        friction_type="parallelization",
        description="Sequential agent calls that could be parallelized",
        solution="Use thegent bg for parallel execution or delegate to swarm",
        priority="P1",
    ),
    FrictionPattern(
        name="manual_session_management",
        pattern=re.compile(r"thegent\s+ps.*\n.*thegent\s+wait.*\n.*thegent\s+status"),
        category="dx",
        friction_type="coordination",
        description="Manual session management instead of unified command",
        solution="Use thegent plan loop or unified monitoring command",
        priority="P2",
    ),
    FrictionPattern(
        name="manual_work_claiming",
        pattern=re.compile(r"(claim|CLAIMED).*manual|manually.*claim"),
        category="dx",
        friction_type="coordination",
        description="Manual work claiming instead of auto-claim",
        solution="Implement auto-claim on work start",
        priority="P2",
    ),
    FrictionPattern(
        name="blocking_wait_busy_loop",
        pattern=re.compile(r"while.*sleep.*do.*check|for.*in.*sleep.*do"),
        category="dx",
        friction_type="polling",
        description="Busy loops with sleep instead of blocking wait",
        solution="Use thegent plan wait-next or thegent wait instead",
        priority="P1",
    ),
    # ========== File Operation Patterns ==========
    FrictionPattern(
        name="multiple_read_calls",
        pattern=re.compile(r"read_file\([^)]+\)\s+read_file\([^)]+\)\s+read_file\([^)]+\)"),
        category="dx",
        friction_type="efficiency",
        description="Multiple sequential read_file calls",
        solution="Use batch_read_files() helper",
        priority="P2",
    ),
    FrictionPattern(
        name="manual_path_resolution",
        pattern=re.compile(r"Path\([^)]+\)\.resolve\(\)\.expanduser\(\)"),
        category="dx",
        friction_type="complexity",
        description="Manual path resolution instead of helper",
        solution="Use normalize_path() helper",
        priority="P2",
    ),
    FrictionPattern(
        name="full_file_reads",
        pattern=re.compile(r"read_file\([^)]+\)(?!.*offset|.*limit)"),
        category="dx",
        friction_type="efficiency",
        description="Full file reads when only portion needed",
        solution="Use read_file with offset/limit for large files",
        priority="P2",
    ),
    FrictionPattern(
        name="repeated_file_reads",
        pattern=re.compile(r"read_file\(([^)]+)\).*\n.*read_file\(\1\)"),
        category="dx",
        friction_type="caching",
        description="Reading same file multiple times",
        solution="Cache file contents or read once and reuse",
        priority="P1",
    ),
    FrictionPattern(
        name="ls_in_project_root",
        pattern=re.compile(r"ls\s+-l\s+\.|ls\s+-l\s+$"),
        category="dx",
        friction_type="performance",
        description="ls -l in project root (slow with node_modules/.venv)",
        solution="Use fd -t f -d 1 or ls -l subdir/ instead",
        priority="P1",
    ),
    # ========== Code Quality Patterns ==========
    FrictionPattern(
        name="custom_retry_loop",
        pattern=re.compile(r"for\s+.*\s+in\s+range\(.*\):.*try:.*except.*continue|while.*try:.*except.*retry"),
        category="dx",
        friction_type="library_usage",
        description="Custom retry loops instead of tenacity",
        solution="Use tenacity library with @retry decorator",
        priority="P1",
    ),
    FrictionPattern(
        name="custom_cache_logic",
        pattern=re.compile(r"cache\s*=\s*\{\}|if\s+.*\s+in\s+cache:|cache\[.*\]\s*="),
        category="dx",
        friction_type="library_usage",
        description="Custom caching logic instead of cachetools",
        solution="Use cachetools.TTLCache or diskcache",
        priority="P2",
    ),
    FrictionPattern(
        name="custom_file_watching",
        pattern=re.compile(r"while.*os\.walk|while.*glob|time\.sleep.*os\.path"),
        category="dx",
        friction_type="library_usage",
        description="Polling file system instead of watchdog",
        solution="Use watchdog library for file watching",
        priority="P1",
    ),
    FrictionPattern(
        name="manual_http_requests",
        pattern=re.compile(r"urllib\.|requests\.|http\.client\."),
        category="dx",
        friction_type="library_usage",
        description="Using urllib/requests instead of httpx",
        solution="Use httpx library (async support, better API)",
        priority="P2",
    ),
    FrictionPattern(
        name="print_debugging",
        pattern=re.compile(r'print\(.*debug|print\(.*DEBUG|print\(f".*\{.*\}'),
        category="dx",
        friction_type="logging",
        description="Using print() for debugging instead of logging",
        solution="Use logging.getLogger() or structlog",
        priority="P2",
    ),
    # ========== Agent Process Optimization Patterns ==========
    FrictionPattern(
        name="sequential_exploration",
        pattern=re.compile(r"codebase_search.*\n.*codebase_search.*\n.*codebase_search"),
        category="dx",
        friction_type="parallelization",
        description="Sequential codebase searches that could be parallel",
        solution="Launch multiple explore agents in parallel",
        priority="P1",
    ),
    FrictionPattern(
        name="reading_many_files",
        pattern=re.compile(
            r"read_file\([^)]+\)\s*\n.*read_file\([^)]+\)\s*\n.*read_file\([^)]+\)\s*\n.*read_file\([^)]+\)"
        ),
        category="dx",
        friction_type="delegation",
        description="Reading >3 files sequentially (should delegate)",
        solution="Delegate exploration to subagent or use batch_read_files()",
        priority="P1",
    ),
    FrictionPattern(
        name="manual_context_management",
        pattern=re.compile(r"#.*context|#.*keep.*context|#.*remember"),
        category="dx",
        friction_type="context",
        description="Manual context management comments",
        solution="Use delegation pattern or context manager",
        priority="P2",
    ),
    FrictionPattern(
        name="not_delegating_large_scope",
        pattern=re.compile(r"#.*TODO.*delegate|#.*should.*delegate|#.*delegate.*later"),
        category="dx",
        friction_type="delegation",
        description="Comments indicating should delegate but didn't",
        solution="Delegate to thegent free --bg or subagent",
        priority="P1",
    ),
    FrictionPattern(
        name="finishing_when_work_ongoing",
        pattern=re.compile(r"#.*work.*ongoing|#.*agents.*running|#.*background.*task"),
        category="dx",
        friction_type="workflow",
        description="Finishing conversation when work is ongoing",
        solution="Use thegent plan wait-next or thegent plan loop",
        priority="P1",
    ),
    FrictionPattern(
        name="manual_agent_coordination",
        pattern=re.compile(r"thegent\s+ps.*\n.*thegent\s+wait.*\n.*thegent\s+bg"),
        category="dx",
        friction_type="coordination",
        description="Manual agent coordination instead of unified workflow",
        solution="Use thegent plan loop for continuous work",
        priority="P1",
    ),
    # ========== Performance/Optimization Patterns ==========
    FrictionPattern(
        name="subprocess_overhead",
        pattern=re.compile(r"subprocess\.(run|call|check_output)\(.*shell=True"),
        category="dx",
        friction_type="performance",
        description="Using shell=True in subprocess (overhead)",
        solution="Use shell=False with list args, or FastSubprocess helper",
        priority="P2",
    ),
    FrictionPattern(
        name="multiple_subprocess_calls",
        pattern=re.compile(
            r"subprocess\.(run|call)\([^)]+\)\s*\n.*subprocess\.(run|call)\([^)]+\)\s*\n.*subprocess\.(run|call)\([^)]+\)"
        ),
        category="dx",
        friction_type="performance",
        description="Multiple sequential subprocess calls",
        solution="Batch commands or use parallel execution",
        priority="P2",
    ),
    FrictionPattern(
        name="synchronous_http_calls",
        pattern=re.compile(r"httpx\.(get|post|put|delete)\([^)]+\)\s*\n.*httpx\.(get|post|put|delete)\([^)]+\)"),
        category="dx",
        friction_type="performance",
        description="Sequential HTTP calls that could be async",
        solution="Use async/await with httpx.AsyncClient",
        priority="P2",
    ),
    FrictionPattern(
        name="inefficient_string_ops",
        pattern=re.compile(r"\+.*\+.*\+|\.join\(\[.*,.*,.*,.*,.*\]\)"),
        category="dx",
        friction_type="performance",
        description="Multiple string concatenations",
        solution="Use .join() for multiple strings",
        priority="P2",
    ),
    FrictionPattern(
        name="regex_in_loop",
        pattern=re.compile(r"for\s+.*\s+in\s+.*:\s*\n.*re\.(compile|search|match)"),
        category="dx",
        friction_type="performance",
        description="Compiling regex inside loop",
        solution="Compile regex once before loop",
        priority="P1",
    ),
    # ========== Error Handling Patterns ==========
    FrictionPattern(
        name="bare_except",
        pattern=re.compile(r"except\s*:|except\s+Exception\s*:"),
        category="dx",
        friction_type="error_handling",
        description="Bare except or catching all exceptions",
        solution="Catch specific exceptions or use Exception with logging",
        priority="P1",
    ),
    FrictionPattern(
        name="silent_failure",
        pattern=re.compile(r"except.*pass|except.*continue|except.*return\s+None"),
        category="dx",
        friction_type="error_handling",
        description="Silently swallowing exceptions",
        solution="Log errors or raise with context",
        priority="P1",
    ),
    FrictionPattern(
        name="missing_error_context",
        pattern=re.compile(r"except\s+\w+\s+as\s+\w+:\s*\n\s*raise"),
        category="dx",
        friction_type="error_handling",
        description="Re-raising without adding context",
        solution="Use 'raise ... from e' or add context",
        priority="P2",
    ),
    # ========== Type Safety Patterns ==========
    FrictionPattern(
        name="missing_type_hints",
        pattern=re.compile(r"^def\s+\w+\([^)]*\)\s*->\s*:"),
        category="dx",
        friction_type="type_safety",
        description="Function missing return type hint",
        solution="Add return type annotation",
        priority="P2",
    ),
    FrictionPattern(
        name="any_type_usage",
        pattern=re.compile(r":\s*Any\s*[=,)]|Dict\[str,\s*Any\]|List\[Any\]"),
        category="dx",
        friction_type="type_safety",
        description="Using Any type instead of specific types",
        solution="Use more specific types or Union types",
        priority="P2",
    ),
    # ========== Documentation Patterns ==========
    FrictionPattern(
        name="missing_docstring",
        pattern=re.compile(r'^def\s+\w+\([^)]*\):\s*\n\s*""'),
        category="dx",
        friction_type="documentation",
        description="Function missing docstring",
        solution="Add docstring with Args/Returns",
        priority="P2",
    ),
    FrictionPattern(
        name="todo_in_code",
        pattern=re.compile(r"#\s*TODO|#\s*FIXME|#\s*XXX|#\s*HACK"),
        category="dx",
        friction_type="documentation",
        description="TODO/FIXME comments in committed code",
        solution="Create task or fix immediately",
        priority="P1",
    ),
]


def detect_friction_in_content(content: str, file_path: str | None = None) -> list[dict[str, Any]]:
    """
    Detect friction patterns in content.

    Enhanced to detect:
    - CLI/UX verbosity patterns
    - Process/agent workflow inefficiencies
    - File operation optimizations
    - Code quality anti-patterns
    - Performance bottlenecks
    - Error handling issues
    - Type safety gaps

    Args:
        content: Content to scan
        file_path: Optional file path for context

    Returns:
        List of detected friction points
    """
    findings = []
    lines = content.split("\n")

    # Single-line pattern detection
    for line_num, line in enumerate(lines, 1):
        for pattern in FRICTION_PATTERNS:
            if pattern.pattern.search(line):
                findings.append(
                    {
                        "pattern": pattern.name,
                        "category": pattern.category,
                        "type": pattern.friction_type,
                        "location": f"{file_path}:{line_num}" if file_path else f"line {line_num}",
                        "line": line.strip(),
                        "description": pattern.description,
                        "solution": pattern.solution,
                        "priority": pattern.priority,
                    }
                )

    # Multi-line pattern detection (for patterns spanning multiple lines)
    content_joined = "\n".join(lines)
    for pattern in FRICTION_PATTERNS:
        # Skip if already found in single-line scan
        if any(f["pattern"] == pattern.name for f in findings):
            continue

        if pattern.pattern.search(content_joined):
            # Find line number of match
            match = pattern.pattern.search(content_joined)
            if match:
                match_start = match.start()
                line_num = content[:match_start].count("\n") + 1
                findings.append(
                    {
                        "pattern": pattern.name,
                        "category": pattern.category,
                        "type": pattern.friction_type,
                        "location": f"{file_path}:{line_num}" if file_path else f"line {line_num}",
                        "line": lines[line_num - 1].strip() if line_num <= len(lines) else "",
                        "description": pattern.description,
                        "solution": pattern.solution,
                        "priority": pattern.priority,
                    }
                )

    # Deduplicate findings (same pattern at same location)
    seen = set()
    unique_findings = []
    for finding in findings:
        key = (finding["pattern"], finding["location"])
        if key not in seen:
            seen.add(key)
            unique_findings.append(finding)

    return unique_findings


def detect_friction_in_file(file_path: Path) -> list[dict[str, Any]]:
    """Detect friction patterns in a file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        return detect_friction_in_content(content, str(file_path))
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []


def detect_friction_in_command(command: str) -> list[dict[str, Any]]:
    """Detect friction patterns in a command string."""
    return detect_friction_in_content(command, "command")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect UX/DX/AX friction patterns, optimizations, and process inefficiencies"
    )
    parser.add_argument("--file", type=Path, help="File to scan")
    parser.add_argument("--command", help="Command string to scan")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    parser.add_argument("--category", choices=["ux", "dx", "ax", "all"], default="all", help="Filter by category")
    parser.add_argument("--priority", choices=["P1", "P2", "all"], default="all", help="Filter by priority")

    args = parser.parse_args()

    findings = []
    if args.file:
        findings = detect_friction_in_file(args.file)
    elif args.command:
        findings = detect_friction_in_command(args.command)
    else:
        parser.print_help()
        sys.exit(1)

    # Filter findings
    filtered_findings = findings
    if args.category != "all":
        filtered_findings = [f for f in filtered_findings if f["category"] == args.category]
    if args.priority != "all":
        filtered_findings = [f for f in filtered_findings if f["priority"] == args.priority]

    if args.format == "json":
        import json

        print(json.dumps(filtered_findings, indent=2).decode().decode())
    else:
        if not filtered_findings:
            print("No friction patterns detected.")
            return

        # Group by category and priority
        by_category = {}
        for finding in filtered_findings:
            cat = finding["category"].upper()
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(finding)

        print(f"Found {len(filtered_findings)} friction pattern(s):\n")

        # Sort categories: UX first, then DX, then AX
        cat_order = ["UX", "DX", "AX"]
        for cat in cat_order:
            if cat not in by_category:
                continue

            print(f"=== {cat} ({len(by_category[cat])} pattern(s)) ===")
            # Sort by priority (P1 first)
            sorted_findings = sorted(by_category[cat], key=lambda x: (x["priority"] != "P1", x["type"]))

            for finding in sorted_findings:
                print(f"\n[{finding['priority']}] {finding['type']}")
                print(f"  Pattern: {finding['pattern']}")
                print(f"  Location: {finding['location']}")
                print(f"  Issue: {finding['description']}")
                print(f"  Solution: {finding['solution']}")
                if finding["line"]:
                    print(f"  Line: {finding['line'][:80]}...")
            print()


if __name__ == "__main__":
    main()
