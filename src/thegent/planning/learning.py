"""WP-14002: Learning model registry and promotion with canary scoring."""

import orjson as json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class CanaryMetrics:
    success_count: int = 0
    failure_count: int = 0
    total_latency_ms: float = 0.0
    total_cost_usd: float = 0.0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    @property
    def avg_latency(self) -> float:
        total = self.success_count + self.failure_count
        return self.total_latency_ms / total if total > 0 else 0.0


@dataclass
class LearningModel:
    id: str
    status: str  # "canary", "candidate", "promoted", "rejected"
    started_at: str
    metrics: CanaryMetrics
    promoted_at: str | None = None
    approved_by: str | None = None


class LearningRegistry:
    """Registry for managing the lifecycle of candidate models (WP-14002)."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self._models: dict[str, LearningModel] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text())
                for mid, mdata in data.items():
                    mdata["metrics"] = CanaryMetrics(**mdata["metrics"])
                    self._models[mid] = LearningModel(**mdata)
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {mid: asdict(m) for mid, m in self._models.items()}
        self.storage_path.write_text(json.dumps(data, option=json.OPT_INDENT_2).decode())

    def add_canary(self, model_id: str) -> None:
        """Register a new model for canary testing."""
        if model_id in self._models:
            return
        self._models[model_id] = LearningModel(
            id=model_id, status="canary", started_at=datetime.now(UTC).isoformat(), metrics=CanaryMetrics()
        )
        self._save()

    def record_outcome(self, model_id: str, success: bool, latency_ms: float, cost_usd: float) -> None:
        """Record the outcome of a canary run."""
        model = self._models.get(model_id)
        if not model or model.status != "canary":
            return

        if success:
            model.metrics.success_count += 1
        else:
            model.metrics.failure_count += 1

        model.metrics.total_latency_ms += latency_ms
        model.metrics.total_cost_usd += cost_usd
        self._save()

    def promote_to_candidate(self, model_id: str) -> bool:
        """Promote a canary to a promotion candidate based on metrics."""
        model = self._models.get(model_id)
        if not model or model.status != "canary":
            return False

        # Simple promotion criteria: 50+ runs and 90%+ success rate
        total_runs = model.metrics.success_count + model.metrics.failure_count
        if total_runs >= 50 and model.metrics.success_rate >= 0.90:
            model.status = "candidate"
            self._save()
            return True
        return False

    def finalize_promotion(self, model_id: str, approver: str) -> bool:
        """WP-14003: Finalize promotion after human approval."""
        model = self._models.get(model_id)
        if not model or model.status != "candidate":
            return False

        model.status = "promoted"
        model.promoted_at = datetime.now(UTC).isoformat()
        model.approved_by = approver
        self._save()
        return True

    def list_models(self) -> list[LearningModel]:
        return list(self._models.values())
