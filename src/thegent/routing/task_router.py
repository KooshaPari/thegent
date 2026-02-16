import logging
from typing import TYPE_CHECKING, Any

from thegent.routing.models import TaskCategory, TaskMetadata

if TYPE_CHECKING:
    from thegent.config import ThegentSettings
    from thegent.execution import RunRegistry

logger = logging.getLogger(__name__)


class TaskClassifier:
    """Categorizes tasks based on prompt analysis and heuristics."""

    def __init__(self, config: "ThegentSettings") -> None:
        self.config = config

    def classify(self, prompt: str) -> TaskMetadata:
        """
        Classify task complexity based on prompt content.
        Heuristics:
        - Word count (token estimate proxy)
        - Keywords (architecture, design -> HIGH_COMPLEX)
        - Structure (bullets, code blocks -> COMPLEX)
        """
        prompt_lower = prompt.lower()
        word_count = len(prompt.split())
        estimated_tokens = int(word_count * 1.3)

        # Simple keyword-based complexity scoring
        high_complex_keywords = ["architecture", "design", "refactor", "optimize", "security", "database"]
        complex_keywords = ["implement", "test", "debug", "fix", "improve", "handle"]

        complexity_score = 0.0
        if any(kw in prompt_lower for kw in high_complex_keywords):
            complexity_score += 0.5
        if any(kw in prompt_lower for kw in complex_keywords):
            complexity_score += 0.2

        # Token count weight
        complexity_score += min(0.3, estimated_tokens / 5000)

        # Categorization
        if complexity_score >= 0.7 or estimated_tokens > 5000:
            category = TaskCategory.HIGH_COMPLEX
        elif complexity_score >= 0.4 or estimated_tokens > 1500:
            category = TaskCategory.COMPLEX
        elif complexity_score >= 0.15 or estimated_tokens > 300:
            category = TaskCategory.NORMAL
        else:
            category = TaskCategory.FAST

        # Estimate duration and cost (placeholders based on category)
        estimates = {
            TaskCategory.FAST: (1.0, 0.002),
            TaskCategory.NORMAL: (5.0, 0.03),
            TaskCategory.COMPLEX: (20.0, 0.15),
            TaskCategory.HIGH_COMPLEX: (60.0, 0.85),
        }
        duration, cost = estimates[category]

        return TaskMetadata(
            category=category,
            complexity_score=complexity_score,
            estimated_tokens=estimated_tokens,
            estimated_cost=cost,
            estimated_duration_s=duration,
            reasoning=f"Classified as {category} based on complexity score {complexity_score:.2f}",
            signals={
                "word_count": word_count,
                "token_estimate": estimated_tokens,
                "complexity_score": complexity_score,
            },
        )


class ConstraintValidator:
    """Validates task metadata against configured constraints."""

    def __init__(self, config: "ThegentSettings") -> None:
        self.config = config

    def validate(
        self,
        task_metadata: TaskMetadata,
        registry: "RunRegistry | None" = None,
        model: str | None = None,
    ) -> list[str]:
        """
        Validate task against hard constraints:
        - Instantaneous cost (per-call)
        - Cumulative cost (MTD per category)
        - Speed (SLA)
        """
        violations = []
        category = task_metadata.category

        # 1. Instantaneous cost check
        from thegent.governance.cost import CostEstimator

        estimator = CostEstimator()
        actual_est_cost = estimator.estimate(
            model=model,
            prompt_length=task_metadata.signals.get("word_count", 0) * 5,  # proxy for chars
        )

        max_cost = {
            TaskCategory.FAST: 0.01,
            TaskCategory.NORMAL: 0.20,
            TaskCategory.COMPLEX: 1.00,
            TaskCategory.HIGH_COMPLEX: 5.00,
        }.get(category, 1.0)

        if actual_est_cost > max_cost:
            violations.append(f"Cost: Estimated ${actual_est_cost:.3f} exceeds max ${max_cost:.3f} for {category}")

        # 2. Cumulative budget check (if registry provided)
        if registry:
            from thegent.governance.cost import CostAggregator

            agg = CostAggregator(registry.session_dir)
            mtd_total = agg.get_mtd_total()
            cost_budget = float(getattr(self.config, "cost_budget_mtd", 100.0))
            if mtd_total >= cost_budget:
                violations.append(f"Budget: Monthly total ${mtd_total:.2f} exceeds budget ${cost_budget:.2f}")

        # 3. Speed SLA check
        sla = {
            TaskCategory.FAST: 5.0,
            TaskCategory.NORMAL: 15.0,
            TaskCategory.COMPLEX: 45.0,
            TaskCategory.HIGH_COMPLEX: 180.0,
        }.get(category, 60.0)

        if task_metadata.estimated_duration_s > sla:
            violations.append(
                f"Speed: Estimated {task_metadata.estimated_duration_s}s exceeds {sla}s SLA for {category}"
            )

        return violations


class TaskRouter:
    """Orchestrates task classification and constraint validation."""

    def __init__(self, config: "ThegentSettings") -> None:
        self.config = config
        self.classifier = TaskClassifier(config)
        self.validator = ConstraintValidator(config)

    def classify(self, prompt: str) -> TaskMetadata:
        """Classify task."""
        return self.classifier.classify(prompt)

    def validate(
        self,
        task_metadata: TaskMetadata,
        registry: "RunRegistry | None" = None,
        model: str | None = None,
    ) -> list[str]:
        """Validate task against constraints."""
        return self.validator.validate(task_metadata, registry, model)

    def route(
        self,
        prompt: str,
        registry: "RunRegistry | None" = None,
        model: str | None = None,
    ) -> tuple[TaskMetadata, list[str]]:
        """
        Full routing: classify + validate.
        Returns (TaskMetadata, violations).
        """
        task = self.classify(prompt)
        violations = self.validate(task, registry, model)
        return task, violations

    def get_fallback_chain(self, category: TaskCategory) -> list[str]:
        """Get LiteLLM-style fallback chain for task category (WP-1001)."""
        if category == TaskCategory.FAST:
            return ["gemini-3-flash", "claude-haiku-4.5"]
        if category == TaskCategory.NORMAL:
            return ["gpt-5.3-codex-spark", "claude-haiku-4.5"]
        if category == TaskCategory.COMPLEX:
            return ["gpt-5.3-codex", "gemini-3-pro"]
        return ["claude-opus-4.6", "gpt-5.3-codex-max"]

    def route_dag_tasks(self, dag: Any) -> dict[str, list[str]]:
        """Route multiple tasks from a DAG, considering dependencies (WP-1001)."""
        routing_table = {}
        for task_id, task in getattr(dag, "tasks", {}).items():
            meta = self.classify(task.get("prompt", ""))
            routing_table[task_id] = self.get_fallback_chain(meta.category)
        return routing_table

    def route_by_capability(self, task_type: str) -> str:
        """Route to an agent based on task capability (WP-1007)."""
        mapping = {
            "coding": "codex",
            "research": "gemini",
            "orchestration": "claude",
            "review": "cursor-agent",
            "fast-fix": "copilot",
        }
        return mapping.get(task_type, "gemini")

    def should_delegate_to_reviewer(self, confidence: float) -> bool:
        """Determine if a task should be delegated to a reviewer based on confidence (WP-1007)."""
        # Threshold G-CA-02 B1: confidence < 0.7 triggers reviewer delegation
        return confidence < 0.7

    def find_active_terminal_for_path(self, path: str) -> str | None:
        """
        Find an active tmux pane matching the given project path.
        Returns pane_id if found.
        """
        from pathlib import Path

        from thegent.tools.terminal import is_claude_code_pane, list_tmux_panes

        target_path = Path(path).resolve()
        panes = list_tmux_panes()
        for p in panes:
            if Path(p.path).resolve() == target_path and is_claude_code_pane(p):
                return p.pane_id
        return None
