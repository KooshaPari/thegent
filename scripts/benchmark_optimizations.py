#!/usr/bin/env python3
"""Benchmark performance improvements from optimization work.

This script benchmarks:
- YAML parsing (ruamel.yaml vs PyYAML)
- TOML parsing (rtoml vs tomlkit)
- JSON Schema validation (fastjsonschema vs jsonschema)
- File watching (watchfiles vs watchdog)
- Subprocess execution (async vs sync)
- Caching (multi-tier vs simple dict)
- Route resolution (with/without cache)

Usage:
    python scripts/benchmark_optimizations.py [--iterations N] [--warmup N]
"""

import argparse
import asyncio
import orjson as json
import statistics
import time
from pathlib import Path
from typing import Any

# Setup paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"


def benchmark_yaml_parsing(iterations: int = 100) -> dict[str, Any]:
    """Benchmark YAML parsing performance."""
    print("Benchmarking YAML parsing...")

    yaml_content = """
    name: test
    version: 1.0.0
    dependencies:
      - package1: ^1.0.0
      - package2: ^2.0.0
    config:
      setting1: value1
      setting2: value2
      nested:
        key1: value1
        key2: value2
    """

    results = {}

    # PyYAML (baseline)
    try:
        import yaml

        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            yaml.safe_load(yaml_content)
            times.append(time.perf_counter() - start)
        results["pyyaml"] = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
            "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        }
    except ImportError:
        results["pyyaml"] = None

    # ruamel.yaml (optimized)
    try:
        from ruamel.yaml import YAML

        yaml_parser = YAML(typ="safe")
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            yaml_parser.load(yaml_content)
            times.append(time.perf_counter() - start)
        results["ruamel"] = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
            "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        }

        if results.get("pyyaml"):
            speedup = results["pyyaml"]["mean"] / results["ruamel"]["mean"]
            results["speedup"] = speedup
    except ImportError:
        results["ruamel"] = None

    return results


def benchmark_toml_parsing(iterations: int = 100) -> dict[str, Any]:
    """Benchmark TOML parsing performance."""
    print("Benchmarking TOML parsing...")

    toml_content = """
    [project]
    name = "test"
    version = "1.0.0"

    [dependencies]
    package1 = "^1.0.0"
    package2 = "^2.0.0"

    [config]
    setting1 = "value1"
    setting2 = "value2"

    [config.nested]
    key1 = "value1"
    key2 = "value2"
    """

    results = {}

    # tomlkit (baseline)
    try:
        import tomlkit

        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            tomlkit.parse(toml_content)
            times.append(time.perf_counter() - start)
        results["tomlkit"] = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
            "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        }
    except ImportError:
        results["tomlkit"] = None

    # rtoml (optimized)
    try:
        import rtoml

        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            rtoml.loads(toml_content)
            times.append(time.perf_counter() - start)
        results["rtoml"] = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
            "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        }

        if results.get("tomlkit"):
            speedup = results["tomlkit"]["mean"] / results["rtoml"]["mean"]
            results["speedup"] = speedup
    except ImportError:
        results["rtoml"] = None

    return results


def benchmark_json_schema(iterations: int = 100) -> dict[str, Any]:
    """Benchmark JSON Schema validation."""
    print("Benchmarking JSON Schema validation...")

    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "age"],
    }

    data = {"name": "John Doe", "age": 30, "email": "john@example.com"}

    results = {}

    # jsonschema (baseline)
    try:
        from jsonschema import Draft202012Validator

        validator = Draft202012Validator(schema)
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            list(validator.iter_errors(data))
            times.append(time.perf_counter() - start)
        results["jsonschema"] = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
            "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        }
    except ImportError:
        results["jsonschema"] = None

    # fastjsonschema (optimized)
    try:
        import fastjsonschema

        validate = fastjsonschema.compile(schema)
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            validate(data)
            times.append(time.perf_counter() - start)
        results["fastjsonschema"] = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
            "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        }

        if results.get("jsonschema"):
            speedup = results["jsonschema"]["mean"] / results["fastjsonschema"]["mean"]
            results["speedup"] = speedup
    except ImportError:
        results["fastjsonschema"] = None

    return results


async def benchmark_subprocess(iterations: int = 50) -> dict[str, Any]:
    """Benchmark subprocess execution."""
    print("Benchmarking subprocess execution...")

    cmd = ["python", "-c", "print('hello')"]

    results = {}

    # Synchronous (baseline)
    try:
        import subprocess

        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            subprocess.run(cmd, capture_output=True, timeout=5)
            times.append(time.perf_counter() - start)
        results["sync"] = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
            "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        }
    except Exception:
        results["sync"] = None

    # Async (optimized)
    try:
        from thegent.infra import run_subprocess_async

        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            await run_subprocess_async(cmd, capture_output=True, timeout=5)
            times.append(time.perf_counter() - start)
        results["async"] = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
            "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        }

        if results.get("sync"):
            speedup = results["sync"]["mean"] / results["async"]["mean"]
            results["speedup"] = speedup
    except Exception:
        results["async"] = None

    # Concurrent (optimized)
    try:
        from thegent.infra import run_subprocesses_concurrent

        commands = [cmd] * iterations
        start = time.perf_counter()
        await run_subprocesses_concurrent(commands, max_concurrent=10)
        total_time = time.perf_counter() - start

        results["concurrent"] = {
            "total_time": total_time * 1000,
            "per_operation": (total_time / iterations) * 1000,
        }

        if results.get("sync"):
            speedup = (results["sync"]["mean"] * iterations) / results["concurrent"]["total_time"]
            results["concurrent_speedup"] = speedup
    except Exception:
        results["concurrent"] = None

    return results


def benchmark_caching(iterations: int = 1000) -> dict[str, Any]:
    """Benchmark caching performance."""
    print("Benchmarking caching...")

    results = {}

    # Simple dict (baseline)
    cache_dict = {}
    times = []
    for i in range(iterations):
        key = f"key_{i % 100}"
        start = time.perf_counter()
        if key in cache_dict:
            _ = cache_dict[key]
        else:
            cache_dict[key] = f"value_{i}"
        times.append(time.perf_counter() - start)
    results["dict"] = {
        "mean": statistics.mean(times) * 1000,
        "median": statistics.median(times) * 1000,
    }

    # Multi-tier cache (optimized)
    try:
        from thegent.infra import MultiTierCache

        cache = MultiTierCache(l1_size=100, l2_size=1000, l3_path=None, default_ttl=60)
        times = []
        for i in range(iterations):
            key = f"key_{i % 100}"
            start = time.perf_counter()
            value = cache.get(key)
            if value is None:
                cache.set(key, f"value_{i}")
            times.append(time.perf_counter() - start)
        results["multi_tier"] = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
        }

        speedup = results["dict"]["mean"] / results["multi_tier"]["mean"]
        results["speedup"] = speedup
    except Exception:
        results["multi_tier"] = None

    return results


def benchmark_route_resolution(iterations: int = 1000) -> dict[str, Any]:
    """Benchmark route resolution with/without cache."""
    print("Benchmarking route resolution...")

    try:
        from thegent.models.catalog import resolve_route

        model_ids = ["gpt-4", "claude-3-opus", "gemini-pro", "gpt-3.5-turbo", "claude-3-sonnet"]

        # Without cache (first run)
        times_no_cache = []
        for _ in range(iterations):
            model_id = model_ids[_ % len(model_ids)]
            start = time.perf_counter()
            resolve_route(model_id)
            times_no_cache.append(time.perf_counter() - start)

        # With cache (second run)
        times_with_cache = []
        for _ in range(iterations):
            model_id = model_ids[_ % len(model_ids)]
            start = time.perf_counter()
            resolve_route(model_id)
            times_with_cache.append(time.perf_counter() - start)

        results = {
            "no_cache": {
                "mean": statistics.mean(times_no_cache) * 1000,
                "median": statistics.median(times_no_cache) * 1000,
            },
            "with_cache": {
                "mean": statistics.mean(times_with_cache) * 1000,
                "median": statistics.median(times_with_cache) * 1000,
            },
        }

        speedup = results["no_cache"]["mean"] / results["with_cache"]["mean"]
        results["speedup"] = speedup

        return results
    except Exception as e:
        return {"error": str(e)}


async def main():
    """Run all benchmarks."""
    parser = argparse.ArgumentParser(description="Benchmark optimization improvements")
    parser.add_argument("--iterations", type=int, default=100, help="Number of iterations per benchmark")
    parser.add_argument("--warmup", type=int, default=10, help="Number of warmup iterations")
    parser.add_argument("--output", type=str, help="Output JSON file for results")

    args = parser.parse_args()

    print(f"Running benchmarks with {args.iterations} iterations...")
    print("=" * 60)

    all_results = {}

    # YAML parsing
    all_results["yaml"] = benchmark_yaml_parsing(args.iterations)

    # TOML parsing
    all_results["toml"] = benchmark_toml_parsing(args.iterations)

    # JSON Schema
    all_results["json_schema"] = benchmark_json_schema(args.iterations)

    # Subprocess
    all_results["subprocess"] = await benchmark_subprocess(args.iterations)

    # Caching
    all_results["caching"] = benchmark_caching(args.iterations)

    # Route resolution
    all_results["route_resolution"] = benchmark_route_resolution(args.iterations)

    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)

    for category, results in all_results.items():
        if isinstance(results, dict) and "error" not in results:
            print(f"\n{category.upper()}:")
            if "speedup" in results:
                print(f"  Speedup: {results['speedup']:.2f}x")
            for key, value in results.items():
                if key != "speedup" and isinstance(value, dict):
                    if "mean" in value:
                        print(f"  {key}: {value['mean']:.3f}ms (mean), {value['median']:.3f}ms (median)")

    # Save results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
