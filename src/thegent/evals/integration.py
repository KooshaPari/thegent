"""GW-74: LLM evals integration — abstract evaluator framework for comparing model outputs.

Provides evaluators for automated scoring of model outputs against expected
responses. Designed for integration with the GW-70 online eval routing system.

# @trace FR-EVAL-074
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public data structures
# ---------------------------------------------------------------------------


@dataclass
class EvalCase:
    """A single evaluation case: prompt, expected output, and metadata."""

    id: str
    prompt: str  # the prompt/question
    expected: str  # expected output (for automated evals)
    metadata: dict = field(default_factory=dict)  # arbitrary tags


@dataclass
class EvalResult:
    """Result of evaluating a model's output against an EvalCase."""

    case_id: str
    model: str
    output: str  # actual model output
    score: float  # 0.0-1.0 score
    passed: bool  # score >= threshold
    evaluator: str  # name of evaluator used
    details: dict = field(default_factory=dict)  # evaluator-specific details


# ---------------------------------------------------------------------------
# Abstract base evaluator
# ---------------------------------------------------------------------------


class Evaluator:
    """Base class for LLM output evaluators."""

    name: str = "base"

    def evaluate(self, output: str, expected: str, case: "EvalCase") -> EvalResult:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Concrete evaluators
# ---------------------------------------------------------------------------


class ExactMatchEvaluator(Evaluator):
    """Score 1.0 if output.strip() == expected.strip(), else 0.0."""

    name = "exact_match"

    def __init__(self, threshold: float = 1.0) -> None:
        self._threshold = threshold

    def evaluate(self, output: str, expected: str, case: EvalCase) -> EvalResult:
        score = 1.0 if output.strip() == expected.strip() else 0.0
        passed = score >= self._threshold
        _log.debug("ExactMatchEvaluator case=%r score=%.2f passed=%s", case.id, score, passed)
        return EvalResult(
            case_id=case.id,
            model="",
            output=output,
            score=score,
            passed=passed,
            evaluator=self.name,
        )


class ContainsEvaluator(Evaluator):
    """Score 1.0 if expected is found in output, else 0.0. Case-insensitive by default."""

    name = "contains"

    def __init__(self, case_sensitive: bool = False) -> None:
        self._case_sensitive = case_sensitive

    def evaluate(self, output: str, expected: str, case: EvalCase) -> EvalResult:
        if self._case_sensitive:
            found = expected in output
        else:
            found = expected.lower() in output.lower()
        score = 1.0 if found else 0.0
        passed = score > 0
        _log.debug("ContainsEvaluator case=%r found=%s score=%.2f", case.id, found, score)
        return EvalResult(
            case_id=case.id,
            model="",
            output=output,
            score=score,
            passed=passed,
            evaluator=self.name,
        )


class RegexEvaluator(Evaluator):
    """Score 1.0 if pattern is found in output, else 0.0."""

    name = "regex"

    def __init__(self, pattern: str, flags: int = re.IGNORECASE) -> None:
        self._pattern = pattern
        self._flags = flags
        self._compiled = re.compile(pattern, flags)

    def evaluate(self, output: str, expected: str, case: EvalCase) -> EvalResult:
        match = self._compiled.search(output)
        score = 1.0 if match is not None else 0.0
        passed = score > 0
        _log.debug("RegexEvaluator case=%r match=%s score=%.2f", case.id, match is not None, score)
        return EvalResult(
            case_id=case.id,
            model="",
            output=output,
            score=score,
            passed=passed,
            evaluator=self.name,
            details={"compiled_pattern": self._compiled},
        )


class KeywordCoverageEvaluator(Evaluator):
    """Score = (# keywords found in output) / len(keywords)."""

    name = "keyword_coverage"

    def __init__(
        self,
        keywords: list,
        threshold: float = 0.8,
        case_sensitive: bool = False,
    ) -> None:
        if not keywords:
            raise ValueError("keywords must be a non-empty list")
        self._keywords = list(keywords)
        self._threshold = threshold
        self._case_sensitive = case_sensitive

    def evaluate(self, output: str, expected: str, case: EvalCase) -> EvalResult:
        compare_output = output if self._case_sensitive else output.lower()
        found_count = 0
        for kw in self._keywords:
            compare_kw = kw if self._case_sensitive else kw.lower()
            if compare_kw in compare_output:
                found_count += 1
        score = found_count / len(self._keywords)
        passed = score >= self._threshold
        _log.debug(
            "KeywordCoverageEvaluator case=%r found=%d/%d score=%.4f passed=%s",
            case.id,
            found_count,
            len(self._keywords),
            score,
            passed,
        )
        return EvalResult(
            case_id=case.id,
            model="",
            output=output,
            score=score,
            passed=passed,
            evaluator=self.name,
        )


# ---------------------------------------------------------------------------
# EvalSuite
# ---------------------------------------------------------------------------


class EvalSuite:
    """A named collection of EvalCases run through a single Evaluator."""

    def __init__(self, name: str, evaluator: Evaluator) -> None:
        self.name = name
        self.evaluator = evaluator
        self._cases: list = []
        self._results: list = []

    def add_case(self, case: EvalCase) -> None:
        """Add a case to the suite."""
        self._cases.append(case)

    def run(self, model: str, outputs: dict) -> list:
        """Run the evaluator on all cases.

        Parameters
        ----------
        model:
            Name of the model being evaluated (stamped onto each EvalResult).
        outputs:
            Mapping of case_id -> model output string.
        """
        results: list = []
        for case in self._cases:
            output = outputs.get(case.id, "")
            result = self.evaluator.evaluate(output, case.expected, case)
            # Stamp the model onto the result produced by the evaluator.
            result.model = model
            results.append(result)
            _log.debug(
                "EvalSuite %r run: case=%r model=%r score=%.4f passed=%s",
                self.name,
                case.id,
                model,
                result.score,
                result.passed,
            )
        self._results = results
        return results

    def summary(self) -> dict:
        """Return summary statistics for the last run.

        Keys: total, passed, failed, pass_rate, avg_score, model.
        """
        if not self._results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "avg_score": 0.0,
                "model": "",
            }
        total = len(self._results)
        passed = sum(1 for r in self._results if r.passed)
        failed = total - passed
        pass_rate = passed / total
        avg_score = sum(r.score for r in self._results) / total
        model = self._results[0].model if self._results else ""
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "avg_score": avg_score,
            "model": model,
        }

    def results(self) -> list:
        """Return all results from the last run."""
        return list(self._results)
