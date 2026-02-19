#!/usr/bin/env python3
"""
Hook Rust Migration - Benchmark Analysis Tool

Analyzes benchmark results to produce performance reports,
trends, and optimization recommendations.
"""

import json
import sys
import statistics
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime


@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    name: str
    command: str
    mean: float
    median: float
    stddev: float
    min: float
    max: float
    times: List[float]

    @property
    def p95(self) -> float:
        """95th percentile"""
        return self._percentile(0.95)

    @property
    def p99(self) -> float:
        """99th percentile"""
        return self._percentile(0.99)

    def _percentile(self, p: float) -> float:
        """Calculate percentile"""
        sorted_times = sorted(self.times)
        idx = int(len(sorted_times) * p)
        return sorted_times[min(idx, len(sorted_times) - 1)]


@dataclass
class ComparisonResult:
    """Comparison of baseline vs current"""
    operation: str
    baseline_mean: float
    current_mean: float
    speedup: float
    improvement_percent: float
    baseline_p95: float
    current_p95: float

    @property
    def faster(self) -> bool:
        """Is current faster?"""
        return self.speedup > 1.0

    @property
    def status(self) -> str:
        """Status emoji"""
        if self.speedup > 10:
            return "⭐"  # Huge win
        elif self.speedup > 5:
            return "✅"  # Major win
        elif self.speedup > 2:
            return "📈"  # Good
        elif self.speedup > 1:
            return "📊"  # Slight improvement
        else:
            return "⚠️"   # Regression


class BenchmarkAnalyzer:
    """Analyze benchmark results"""

    def __init__(self, baseline_dir: Path, current_dir: Path):
        self.baseline_dir = Path(baseline_dir)
        self.current_dir = Path(current_dir)
        self.baseline_results: Dict[str, BenchmarkResult] = {}
        self.current_results: Dict[str, BenchmarkResult] = {}

    def load_results(self):
        """Load benchmark results from JSON files"""
        self._load_from_dir(self.baseline_dir, self.baseline_results)
        self._load_from_dir(self.current_dir, self.current_results)

    def _load_from_dir(self, dir_path: Path, results: Dict[str, BenchmarkResult]):
        """Load all benchmark JSONs from directory"""
        if not dir_path.exists():
            return

        for json_file in sorted(dir_path.glob("*.json")):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    if "results" in data and data["results"]:
                        result_data = data["results"][0]
                        name = json_file.stem
                        result = BenchmarkResult(
                            name=name,
                            command=result_data.get("command", ""),
                            mean=result_data.get("mean", 0),
                            median=result_data.get("median", 0),
                            stddev=result_data.get("stddev", 0),
                            min=result_data.get("min", 0),
                            max=result_data.get("max", 0),
                            times=result_data.get("times", []),
                        )
                        results[name] = result
            except Exception as e:
                print(f"Warning: Failed to load {json_file}: {e}", file=sys.stderr)

    def compare(self) -> List[ComparisonResult]:
        """Compare baseline and current results"""
        comparisons = []

        # Match baseline and current by operation name
        for base_name, baseline_result in self.baseline_results.items():
            # Extract operation name (e.g., "01_hook_init" from "01_hook_init_bash")
            operation = base_name.rsplit("_", 1)[0]

            # Find corresponding current result
            for curr_name, current_result in self.current_results.items():
                curr_operation = curr_name.rsplit("_", 1)[0]
                if curr_operation == operation:
                    speedup = baseline_result.mean / current_result.mean
                    improvement = (1 - current_result.mean / baseline_result.mean) * 100
                    comparisons.append(
                        ComparisonResult(
                            operation=operation,
                            baseline_mean=baseline_result.mean,
                            current_mean=current_result.mean,
                            speedup=speedup,
                            improvement_percent=improvement,
                            baseline_p95=baseline_result.p95,
                            current_p95=current_result.p95,
                        )
                    )
                    break

        # Sort by speedup (best first)
        return sorted(comparisons, key=lambda c: c.speedup, reverse=True)

    def generate_report(self) -> str:
        """Generate markdown report"""
        comparisons = self.compare()

        if not comparisons:
            return "# Benchmark Report\n\nNo results to compare.\n"

        report = []
        report.append("# Hook Rust Migration - Benchmark Analysis")
        report.append(f"\n_Generated: {datetime.now().isoformat()}_\n")

        # Summary table
        report.append("## Summary\n")
        report.append("| Operation | Baseline | Current | Speedup | Improvement |")
        report.append("|-----------|----------|---------|---------|-------------|")

        for comp in comparisons:
            speedup_str = f"{comp.speedup:.1f}x"
            improvement_str = f"{comp.improvement_percent:.0f}%"
            report.append(
                f"| {comp.status} {comp.operation} | {comp.baseline_mean*1000:.2f}ms | "
                f"{comp.current_mean*1000:.2f}ms | {speedup_str} | {improvement_str} |"
            )

        # Detailed analysis
        report.append("\n## Detailed Results\n")

        for comp in comparisons:
            report.append(f"### {comp.operation}\n")
            report.append(f"**Speedup**: {comp.speedup:.1f}x ({comp.improvement_percent:.0f}% faster)\n")
            report.append(f"- Baseline mean: {comp.baseline_mean*1000:.2f}ms")
            report.append(f"- Current mean: {comp.current_mean*1000:.2f}ms")
            report.append(f"- Baseline P95: {comp.baseline_p95*1000:.2f}ms")
            report.append(f"- Current P95: {comp.current_p95*1000:.2f}ms")
            report.append("")

        # Statistical summary
        report.append("## Statistics\n")
        speedups = [c.speedup for c in comparisons]
        report.append(f"- **Average speedup**: {statistics.mean(speedups):.1f}x")
        report.append(f"- **Median speedup**: {statistics.median(speedups):.1f}x")
        report.append(f"- **Min speedup**: {min(speedups):.1f}x")
        report.append(f"- **Max speedup**: {max(speedups):.1f}x")

        if len(speedups) > 2:
            report.append(f"- **Std dev**: {statistics.stdev(speedups):.2f}x")

        report.append("\n## Recommendations\n")
        report.extend(self._generate_recommendations(comparisons))

        return "\n".join(report)

    def _generate_recommendations(self, comparisons: List[ComparisonResult]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Group by improvement level
        huge_wins = [c for c in comparisons if c.speedup > 10]
        major_wins = [c for c in comparisons if 5 < c.speedup <= 10]
        good_wins = [c for c in comparisons if 2 < c.speedup <= 5]
        regressions = [c for c in comparisons if c.speedup < 1]

        if huge_wins:
            recommendations.append(f"### Huge Performance Wins ({len(huge_wins)})")
            for comp in huge_wins:
                recommendations.append(
                    f"- **{comp.operation}**: {comp.speedup:.0f}x faster - "
                    f"Ready for Phase 2 rollout"
                )

        if major_wins:
            recommendations.append(f"\n### Major Performance Improvements ({len(major_wins)})")
            for comp in major_wins:
                recommendations.append(
                    f"- **{comp.operation}**: {comp.speedup:.1f}x faster - "
                    f"High priority for optimization"
                )

        if good_wins:
            recommendations.append(f"\n### Good Performance Gains ({len(good_wins)})")
            for comp in good_wins:
                recommendations.append(
                    f"- **{comp.operation}**: {comp.speedup:.1f}x faster - "
                    f"Worthwhile improvement"
                )

        if regressions:
            recommendations.append(f"\n### ⚠️ Regressions ({len(regressions)})")
            for comp in regressions:
                recommendations.append(
                    f"- **{comp.operation}**: {comp.speedup:.2f}x - "
                    f"Investigate before rollout"
                )

        # Overall assessment
        avg_speedup = statistics.mean([c.speedup for c in comparisons])
        recommendations.append(f"\n### Overall Assessment")
        if avg_speedup > 5:
            recommendations.append(
                f"✅ **Excellent**: Average {avg_speedup:.1f}x speedup across all operations. "
                "Ready for Phase 2 implementation."
            )
        elif avg_speedup > 2:
            recommendations.append(
                f"📈 **Good**: Average {avg_speedup:.1f}x speedup. "
                "Ready for gradual Phase 2 rollout with monitoring."
            )
        elif avg_speedup > 1:
            recommendations.append(
                f"📊 **Modest**: Average {avg_speedup:.1f}x speedup. "
                "Requires investigation before Phase 2."
            )
        else:
            recommendations.append(
                f"⚠️ **Concerning**: {avg_speedup:.2f}x speedup. "
                "Needs major optimization before proceeding."
            )

        return recommendations

    def generate_json_summary(self) -> Dict:
        """Generate JSON summary"""
        comparisons = self.compare()

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_operations": len(comparisons),
                "average_speedup": statistics.mean([c.speedup for c in comparisons])
                if comparisons else 0,
                "median_speedup": statistics.median([c.speedup for c in comparisons])
                if comparisons else 0,
            },
            "results": [
                {
                    "operation": c.operation,
                    "baseline_ms": c.baseline_mean * 1000,
                    "current_ms": c.current_mean * 1000,
                    "speedup": c.speedup,
                    "improvement_percent": c.improvement_percent,
                }
                for c in comparisons
            ],
        }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze hook-rust benchmark results"
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        required=True,
        help="Baseline results directory",
    )
    parser.add_argument(
        "--current-dir",
        type=Path,
        required=True,
        help="Current results directory",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default="benchmark-report.md",
        help="Output report path",
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        default="benchmark-summary.json",
        help="Output summary path",
    )
    parser.add_argument(
        "--title",
        default="Benchmark Comparison",
        help="Report title",
    )

    args = parser.parse_args()

    analyzer = BenchmarkAnalyzer(args.baseline_dir, args.current_dir)
    analyzer.load_results()

    # Generate and save report
    report = analyzer.generate_report()
    args.report_path.write_text(report)
    print(f"Report: {args.report_path}")

    # Generate and save summary
    summary = analyzer.generate_json_summary()
    args.summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Summary: {args.summary_path}")

    # Print to stdout
    print("\n" + report)


if __name__ == "__main__":
    main()
