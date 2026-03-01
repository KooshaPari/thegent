"""Metadata for AI models including cost and quality scores."""

from dataclasses import dataclass


@dataclass
class ModelMetadata:
    id: str
    quality_score: float  # 0.0 to 1.0 (capability/intelligence)
    cost_per_1k_input: float  # USD
    cost_per_1k_output: float  # USD
    avg_latency_ms: float  # Baseline latency


MODEL_METADATA = {
    "claude-opus-4.6": ModelMetadata(
        id="claude-opus-4.6",
        quality_score=0.98,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        avg_latency_ms=5000,
    ),
    "claude-sonnet-4.5": ModelMetadata(
        id="claude-sonnet-4.5",
        quality_score=0.92,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        avg_latency_ms=2000,
    ),
    "claude-sonnet-4.5-1m": ModelMetadata(
        id="claude-sonnet-4.5-1m",
        quality_score=0.92,
        cost_per_1k_input=0.004,
        cost_per_1k_output=0.018,
        avg_latency_ms=2500,
    ),
    "claude-haiku-4.5": ModelMetadata(
        id="claude-haiku-4.5",
        quality_score=0.75,
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.00125,
        avg_latency_ms=500,
    ),
    "gemini-2.0-pro": ModelMetadata(
        id="gemini-2.0-pro",
        quality_score=0.95,
        cost_per_1k_input=0.007,
        cost_per_1k_output=0.021,
        avg_latency_ms=3500,
    ),
    "gemini-2.0-flash": ModelMetadata(
        id="gemini-2.0-flash",
        quality_score=0.82,
        cost_per_1k_input=0.0001,
        cost_per_1k_output=0.0003,
        avg_latency_ms=400,
    ),
    "gpt-5.3-codex": ModelMetadata(
        id="gpt-5.3-codex",
        quality_score=0.90,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        avg_latency_ms=2500,
    ),
}
