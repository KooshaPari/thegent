"""WP-14001: Cost-aware objective selector for multi-objective optimization."""

from dataclasses import dataclass
from typing import Any

from thegent.planning.models_meta import MODEL_METADATA, ModelMetadata


@dataclass
class ObjectiveWeights:
    quality: float = 0.5
    latency: float = 0.25
    cost: float = 0.25

    def validate(self) -> None:
        total = self.quality + self.latency + self.cost
        if not (0.99 <= total <= 1.01):
            raise ValueError("Weights must sum to 1.0")


class ObjectiveSelector:
    """Optimizes model selection across multiple objectives (WP-14001)."""

    def __init__(self, weights: ObjectiveWeights | None = None) -> None:
        self.weights = weights or ObjectiveWeights()
        self.weights.validate()

    def select(self, models: list[dict[str, Any]], profile: ObjectiveWeights | None = None) -> dict[str, Any]:
        """Select the best model from a list of model dictionaries."""
        if not models:
            return {}

        weights = profile or self.weights

        def score_model(m):
            # Higher is better
            q = m.get("quality", 0.5)
            # Latency: normalize (0.1s -> 1.0, 10s -> 0.0)
            l = max(0, 1.0 - (m.get("latency", 1.0) / 10.0))
            # Cost: normalize ($0.01 -> 1.0, $1.0 -> 0.0)
            c = max(0, 1.0 - (m.get("cost", 0.1) / 1.0))

            return (q * weights.quality) + (l * weights.latency) + (c * weights.cost)

        return max(models, key=score_model)

    def select_best_model(self, candidate_ids: list[str]) -> str:
        """Score and select the best model from the candidates."""
        if not candidate_ids:
            return "gemini-2.0-flash"  # Default fallback

        scores = {}
        for mid in candidate_ids:
            meta = MODEL_METADATA.get(mid)
            if not meta:
                continue
            scores[mid] = self._calculate_score(meta, mid)

        if not scores:
            return candidate_ids[0]

        return max(scores, key=lambda k: scores[k])

    def _calculate_score(self, meta: ModelMetadata, model_id: str | None = None) -> float:
        """Calculate a normalized score for a model based on current weights."""
        # Use quality/speed indices when available (TB2.0 + proxy metrics)
        quality_score = meta.quality_score
        speed_score = max(0, 1.0 - (meta.avg_latency_ms / 10000))

        if model_id:
            try:
                from thegent.models.quality_values import get_model_quality_index
                from thegent.models.speed_values import get_model_best_speed_index

                q = get_model_quality_index(model_id)
                if 0 <= q <= 1:
                    quality_score = q
                s = get_model_best_speed_index(model_id)
                if 0 <= s <= 1:
                    speed_score = s
            except Exception:
                pass

        # Normalize Cost (Lower is better)
        total_cost = meta.cost_per_1k_input + meta.cost_per_1k_output
        cost_score = max(0, 1.0 - (total_cost / 0.1))

        weighted_score = (
            (quality_score * self.weights.quality)
            + (speed_score * self.weights.latency)
            + (cost_score * self.weights.cost)
        )
        return weighted_score


def get_objective_profile(profile_name: str) -> ObjectiveWeights:
    """Return a predefined objective profile."""
    profiles = {
        "balanced": ObjectiveWeights(quality=0.5, latency=0.25, cost=0.25),
        "fastest": ObjectiveWeights(quality=0.2, latency=0.7, cost=0.1),
        "cheapest": ObjectiveWeights(quality=0.1, latency=0.2, cost=0.7),
        "best": ObjectiveWeights(quality=0.8, latency=0.1, cost=0.1),
    }
    return profiles.get(profile_name, profiles["balanced"])
