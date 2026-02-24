#!/usr/bin/env python3
"""
Multi-Harness Benchmark Script
============================
Tests codex, helios, claude, droid with same model (minimax-m2.5 via cliproxy)
"""

import subprocess
import time
import os

CLIPROXY_URL = os.environ.get("CLIPROXY_URL", "http://localhost:8317")

def run_helios(prompt):
    """Run helios CLI."""
    start = time.time()
    try:
        r = subprocess.run(
            ["helios", "task", "--prompt", prompt, "--model", "minimax-m2.5"],
            capture_output=True, text=True, timeout=30
        )
        elapsed = (time.time() - start) * 1000
        success = "Success" in r.stdout
        return {"harness": "helios", "latency": elapsed, "success": success}
    except Exception as e:
        return {"harness": "helios", "latency": 0, "success": False, "error": str(e)}

def run_codex(prompt):
    """Run codex CLI with cliproxy."""
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = f"{CLIPROXY_URL}/v1"
    env["ANTHROPIC_API_KEY"] = "test"
    
    start = time.time()
    try:
        r = subprocess.run(
            ["codex", "exec", "--skip-git-repo-check", prompt],
            capture_output=True, text=True, timeout=30, env=env
        )
        elapsed = (time.time() - start) * 1000
        # Success if we got any stdout (response received)
        success = len(r.stdout) > 10 and "error" not in r.stderr.lower()
        return {"harness": "codex", "latency": elapsed, "success": success, "stdout": r.stdout[:100], "stderr": r.stderr[:100]}
    except Exception as e:
        return {"harness": "codex", "latency": 0, "success": False, "error": str(e)}

def run_claude(prompt):
    """Run claude CLI with cliproxy."""
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = f"{CLIPROXY_URL}/v1"
    
    start = time.time()
    try:
        r = subprocess.run(
            ["claude", "-p", "--no-verbose", prompt],
            capture_output=True, text=True, timeout=30, env=env
        )
        elapsed = (time.time() - start) * 1000
        # Success if we got any stdout (response received)
        success = len(r.stdout) > 10 and r.returncode == 0
        return {"harness": "claude", "latency": elapsed, "success": success, "stdout": r.stdout[:100], "stderr": r.stderr[:100]}
    except Exception as e:
        return {"harness": "claude", "latency": 0, "success": False, "error": str(e)}

def main():
    prompt = "say hello"
    results = []
    
    print("="*60)
    print("MULTI-HARNESS BENCHMARK")
    print(f"Model: minimax-m2.5 via {CLIPROXY_URL}")
    print("="*60)
    
    # Test helios
    print("\n[1] Testing helios...")
    for i in range(3):
        r = run_helios(prompt)
        results.append(r)
        print(f"  Run {i+1}: {r['latency']:.0f}ms {'✓' if r['success'] else '✗'}")
    
    # Test codex
    print("\n[2] Testing codex (via cliproxy)...")
    for i in range(3):
        r = run_codex(prompt)
        results.append(r)
        print(f"  Run {i+1}: {r['latency']:.0f}ms {'✓' if r['success'] else '✗'}")
        if not r['success']:
            print(f"    Error: {r.get('error', r.get('stdout', 'unknown'))[:50]}")
    
    # Test claude
    print("\n[3] Testing claude (via cliproxy)...")
    for i in range(3):
        r = run_claude(prompt)
        results.append(r)
        print(f"  Run {i+1}: {r['latency']:.0f}ms {'✓' if r['success'] else '✗'}")
        if not r['success']:
            print(f"    Error: {r.get('error', r.get('stdout', 'unknown'))[:50]}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Harness':<15} {'Success':<10} {'Avg Latency':<15}")
    print("-"*50)
    
    for harness in ["helios", "codex", "claude"]:
        harness_results = [r for r in results if r["harness"] == harness]
        if harness_results:
            successful = [r for r in harness_results if r["success"]]
            if successful:
                avg_lat = sum(r["latency"] for r in successful) / len(successful)
                print(f"{harness:<15} {len(successful)}/{len(harness_results):<5} {avg_lat:>10.0f}ms")
            else:
                print(f"{harness:<15} 0/{len(harness_results):<5} N/A")

if __name__ == "__main__":
    main()
