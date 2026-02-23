"""WP-14002: Autonomous learning and model promotion."""

import orjson as json
import logging
from datetime import UTC, datetime

from thegent.infra import yaml_dump, yaml_load
from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


class ModelPromoter:
    """Manages autonomous model promotion based on performance metrics."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings

    def evaluate_promotion(self, model_id: str, success_rate: float, cost_efficiency: float):
        """Evaluate if a model should be promoted to a higher tier (e.g. from experimental to production)."""
        if success_rate > 0.95 and cost_efficiency > 0.8:
            _log.info("PROMOTING model %s to PRODUCTION tier", model_id)
            self._update_model_tier(model_id, "production")

    def _update_model_tier(self, model_id: str, new_tier: str):
        from thegent.models.catalog import _get_catalog, normalize_model_id

        normalized = normalize_model_id(model_id)
        catalog = _get_catalog()
        if normalized not in catalog:
            raise KeyError(f"Unknown model_id: {model_id}")

        custom_path = self.settings.custom_models_path
        custom_path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if custom_path.exists():
            loaded = yaml_load(custom_path) or {}
            if isinstance(loaded, dict):
                data = loaded

        routes = data.get(normalized)
        if not isinstance(routes, list):
            routes = []
            for route in catalog[normalized]:
                routes.append(
                    {
                        "provider": route.provider,
                        "backend_type": route.backend_type,
                        "model_alias": route.model_alias,
                        "priority": route.priority,
                        "cost_weight": route.cost_weight,
                        "tier": "experimental",
                    }
                )

        old_tier = str(routes[0].get("tier", "experimental")) if routes else "experimental"
        if old_tier == new_tier:
            return

        for route in routes:
            route["tier"] = new_tier
        data[normalized] = routes
        rendered = yaml_dump(data, default_flow_style=False, sort_keys=True) or ""
        custom_path.write_text(rendered, encoding="utf-8")

        audit_path = self.settings.session_dir / "model_promotion_audit.jsonl"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "model_id": normalized,
            "old_tier": old_tier,
            "new_tier": new_tier,
            "trigger_metrics": {
                "success_rate_threshold": 0.95,
                "cost_efficiency_threshold": 0.8,
            },
        }
        with audit_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event).decode().decode() + "\n")
