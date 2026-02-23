#!/usr/bin/env python3
"""
Deep audit for legacy/older tools and modern alternatives
"""
import re
import orjson as json
from pathlib import Path
from collections import defaultdict

# Legacy dependencies and their modern alternatives
LEGACY_ALTERNATIVES = {
    # Rust
    "rust": {
        "lazy_static": {
            "modern": "std::sync::OnceLock",
            "reason": "Deprecated in favor of std::sync::OnceLock (Rust 1.70+)",
            "priority": "HIGH",
            "effort": "Medium",
            "benefit": "No external dependency, better performance"
        },
        "md5": {
            "modern": "sha2 or blake3",
            "reason": "MD5 is cryptographically broken. Use SHA-256 or BLAKE3",
            "priority": "HIGH",
            "effort": "Low",
            "benefit": "Security improvement"
        },
        "hex": {
            "modern": "base16ct or base16",
            "reason": "hex 0.4 is old. base16ct/base16 are faster and more modern",
            "priority": "MEDIUM",
            "effort": "Low",
            "benefit": "Better performance, maintained"
        },
        "which": {
            "modern": "which 6.0+ (already updated)",
            "reason": "Ensure using latest which crate",
            "priority": "LOW",
            "effort": "None",
            "benefit": "Already updated"
        },
        "thiserror": {
            "modern": "thiserror 2.0+",
            "reason": "thiserror 1.0 → 2.0 has better error handling",
            "priority": "MEDIUM",
            "effort": "Low",
            "benefit": "Better error types, const generics"
        },
        "async-trait": {
            "modern": "async-trait 0.1 (check for 0.2 beta)",
            "reason": "Check for async-trait 0.2 beta with better performance",
            "priority": "LOW",
            "effort": "Low",
            "benefit": "Performance improvements"
        },
        "log": {
            "modern": "tracing (already using)",
            "reason": "tracing is more modern than log",
            "priority": "LOW",
            "effort": "None",
            "benefit": "Already using tracing"
        },
        "chrono": {
            "modern": "time crate (optional)",
            "reason": "time crate is lighter and faster than chrono",
            "priority": "LOW",
            "effort": "Medium",
            "benefit": "Smaller binary, better performance"
        },
        "serde_yaml": {
            "modern": "yaml-rust or yaml-rs",
            "reason": "Check if newer yaml parsers are faster",
            "priority": "LOW",
            "effort": "Low",
            "benefit": "Potential performance"
        },
        "crossbeam-channel": {
            "modern": "tokio::sync::mpsc (if using tokio)",
            "reason": "If already using tokio, use tokio channels",
            "priority": "LOW",
            "effort": "Medium",
            "benefit": "Fewer dependencies"
        },
    },
    # Go
    "go": {
        "github.com/lib/pq": {
            "modern": "github.com/jackc/pgx/v5",
            "reason": "pgx is faster, more modern, and actively maintained",
            "priority": "HIGH",
            "effort": "Medium",
            "benefit": "Better performance, modern API"
        },
        "github.com/gorilla/mux": {
            "modern": "github.com/go-chi/chi or stdlib http",
            "reason": "chi is lighter, stdlib is simpler",
            "priority": "MEDIUM",
            "effort": "Medium",
            "benefit": "Smaller binary, better performance"
        },
        "github.com/labstack/echo": {
            "modern": "github.com/gin-gonic/gin or stdlib",
            "reason": "Gin is faster, or use stdlib for simplicity",
            "priority": "LOW",
            "effort": "High",
            "benefit": "Performance (if needed)"
        },
        "gorm.io/gorm": {
            "modern": "sqlc or sqlx",
            "reason": "sqlc/sqlx are faster, type-safe, and generate code",
            "priority": "MEDIUM",
            "effort": "High",
            "benefit": "Type safety, better performance"
        },
        "github.com/golang-jwt/jwt": {
            "modern": "github.com/golang-jwt/jwt/v5 (already using)",
            "reason": "Already updated to v5",
            "priority": "LOW",
            "effort": "None",
            "benefit": "Already modern"
        },
    },
    # Python
    "python": {
        "pyyaml": {
            "modern": "ruamel.yaml (already using) or yaml-rs-py",
            "reason": "ruamel.yaml preserves formatting, yaml-rs-py is faster",
            "priority": "LOW",
            "effort": "Low",
            "benefit": "Already using ruamel.yaml"
        },
        "watchdog": {
            "modern": "watchfiles (already using)",
            "reason": "watchfiles is faster and more modern",
            "priority": "LOW",
            "effort": "None",
            "benefit": "Already using watchfiles"
        },
        "psycopg2-binary": {
            "modern": "psycopg (psycopg3) or asyncpg",
            "reason": "psycopg3 is modern, asyncpg is async-native",
            "priority": "MEDIUM",
            "effort": "Medium",
            "benefit": "Better async support, modern API"
        },
        "httpx": {
            "modern": "httpx (already modern) or curl-cffi",
            "reason": "httpx is modern, curl-cffi is faster",
            "priority": "LOW",
            "effort": "Low",
            "benefit": "curl-cffi already in optional deps"
        },
        "uvicorn": {
            "modern": "granian (already added)",
            "reason": "granian is Rust-based, much faster",
            "priority": "LOW",
            "effort": "Low",
            "benefit": "Already added granian"
        },
        "pydantic": {
            "modern": "pydantic 2.x (already using)",
            "reason": "Already using modern pydantic",
            "priority": "LOW",
            "effort": "None",
            "benefit": "Already modern"
        },
    }
}

def find_rust_dependencies():
    """Find all Rust dependencies"""
    deps = defaultdict(set)
    base_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush")

    for cargo_file in base_path.rglob("Cargo.toml"):
        if ".venv" in str(cargo_file) or "venv" in str(cargo_file):
            continue

        try:
            content = cargo_file.read_text()
            # Extract dependencies
            for dep_name in LEGACY_ALTERNATIVES["rust"]:
                patterns = [
                    rf'{dep_name}\s*=\s*["\']([^"\']+)["\']',
                    rf'{dep_name}\s*=\s*\{{[^}}]*version\s*=\s*["\']([^"\']+)["\']',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        deps[dep_name].add((str(cargo_file.relative_to(base_path)), matches[0]))
        except Exception as e:
            print(f"Error reading {cargo_file}: {e}")

    return deps

def find_go_dependencies():
    """Find all Go dependencies"""
    deps = defaultdict(set)
    base_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush")

    for go_mod in base_path.rglob("go.mod"):
        if ".venv" in str(go_mod) or "venv" in str(go_mod):
            continue

        try:
            content = go_mod.read_text()
            for dep_name in LEGACY_ALTERNATIVES["go"]:
                pattern = rf'({re.escape(dep_name)})\s+v?([\d.]+)'
                matches = re.findall(pattern, content)
                if matches:
                    for match in matches:
                        deps[dep_name].add((str(go_mod.relative_to(base_path)), match[1]))
        except Exception as e:
            print(f"Error reading {go_mod}: {e}")

    return deps

def find_python_dependencies():
    """Find all Python dependencies"""
    deps = defaultdict(set)
    base_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush")

    for pyproject in base_path.rglob("pyproject.toml"):
        if ".venv" in str(pyproject) or "venv" in str(pyproject):
            continue

        try:
            content = pyproject.read_text()
            for dep_name in LEGACY_ALTERNATIVES["python"]:
                patterns = [
                    rf'["\']{re.escape(dep_name)}[^"\']*["\']',
                    rf'{re.escape(dep_name)}\s*>=\s*([\d.]+)',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        deps[dep_name].add((str(pyproject.relative_to(base_path)), matches[0] if matches else "present"))
        except Exception as e:
            print(f"Error reading {pyproject}: {e}")

    return deps

def generate_report():
    """Generate comprehensive audit report"""
    print("🔍 Deep Legacy Dependency Audit")
    print("=" * 80)

    rust_deps = find_rust_dependencies()
    go_deps = find_go_dependencies()
    python_deps = find_python_dependencies()

    report = {
        "rust": {},
        "go": {},
        "python": {}
    }

    # Rust audit
    print("\n📦 RUST DEPENDENCIES")
    print("-" * 80)
    for dep, files in rust_deps.items():
        if dep in LEGACY_ALTERNATIVES["rust"]:
            alt = LEGACY_ALTERNATIVES["rust"][dep]
            report["rust"][dep] = {
                "found_in": list(files),
                "alternative": alt["modern"],
                "reason": alt["reason"],
                "priority": alt["priority"],
                "effort": alt["effort"],
                "benefit": alt["benefit"]
            }
            print(f"\n⚠️  {dep}")
            print(f"   Found in: {len(files)} file(s)")
            print(f"   Modern alternative: {alt['modern']}")
            print(f"   Priority: {alt['priority']}")
            print(f"   Reason: {alt['reason']}")
            print(f"   Effort: {alt['effort']}")
            print(f"   Benefit: {alt['benefit']}")

    # Go audit
    print("\n📦 GO DEPENDENCIES")
    print("-" * 80)
    for dep, files in go_deps.items():
        if dep in LEGACY_ALTERNATIVES["go"]:
            alt = LEGACY_ALTERNATIVES["go"][dep]
            report["go"][dep] = {
                "found_in": list(files),
                "alternative": alt["modern"],
                "reason": alt["reason"],
                "priority": alt["priority"],
                "effort": alt["effort"],
                "benefit": alt["benefit"]
            }
            print(f"\n⚠️  {dep}")
            print(f"   Found in: {len(files)} file(s)")
            print(f"   Modern alternative: {alt['modern']}")
            print(f"   Priority: {alt['priority']}")
            print(f"   Reason: {alt['reason']}")
            print(f"   Effort: {alt['effort']}")
            print(f"   Benefit: {alt['benefit']}")

    # Python audit
    print("\n📦 PYTHON DEPENDENCIES")
    print("-" * 80)
    for dep, files in python_deps.items():
        if dep in LEGACY_ALTERNATIVES["python"]:
            alt = LEGACY_ALTERNATIVES["python"][dep]
            report["python"][dep] = {
                "found_in": list(files),
                "alternative": alt["modern"],
                "reason": alt["reason"],
                "priority": alt["priority"],
                "effort": alt["effort"],
                "benefit": alt["benefit"]
            }
            print(f"\n⚠️  {dep}")
            print(f"   Found in: {len(files)} file(s)")
            print(f"   Modern alternative: {alt['modern']}")
            print(f"   Priority: {alt['priority']}")
            print(f"   Reason: {alt['reason']}")
            print(f"   Effort: {alt['effort']}")
            print(f"   Benefit: {alt['benefit']}")

    # Save report
    report_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/LEGACY_AUDIT_REPORT.json")
    report_path.write_text(json.dumps(report, indent=2).decode().decode())
    print(f"\n✅ Report saved to: {report_path}")

    # Summary
    print("\n📊 SUMMARY")
    print("-" * 80)
    high_priority = []
    for lang, deps in report.items():
        for dep, info in deps.items():
            if info["priority"] == "HIGH":
                high_priority.append((lang, dep, info))

    if high_priority:
        print(f"\n🚨 HIGH PRIORITY ({len(high_priority)}):")
        for lang, dep, info in high_priority:
            print(f"   [{lang.upper()}] {dep} → {info['alternative']}")

    return report

if __name__ == "__main__":
    generate_report()
