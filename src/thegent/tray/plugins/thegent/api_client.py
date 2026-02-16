"""thegent API client for tray application plugin."""

from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class Project:
    """Represents a thegent project."""

    id: str
    name: str
    path: str
    language: str
    coverage: float
    last_run: str


@dataclass
class Agent:
    """Represents a thegent agent."""

    id: str
    name: str
    model: str
    context_limit: int
    rate_input: float
    rate_output: float
    status: str
    bounded_contexts: list[str] = field(default_factory=list)


@dataclass
class Run:
    """Represents a thegent agent run."""

    id: str
    project_id: str
    agent_id: str
    status: str
    duration: float
    cost: float
    xp: int
    started_at: str
    ended_at: str | None = None


@dataclass
class GardenerStatus:
    """Represents the gardener status."""

    running: bool
    active_agents: int
    max_agents: int
    uptime_seconds: int
    runs_today: int
    total_xp: int
    level: int
    hunger_states: dict[str, float] = field(default_factory=dict)


@dataclass
class CostSummary:
    """Represents cost summary information."""

    daily_spend: float
    daily_budget: float
    daily_percent: float
    monthly_spend: float
    monthly_budget: float
    by_project: dict[str, float] = field(default_factory=dict)
    by_agent: dict[str, float] = field(default_factory=dict)


@dataclass
class GamificationStats:
    """Represents gamification statistics."""

    total_xp: int
    level: int
    xp_to_next_level: int
    runs_today: int
    achievements_count: int
    streak_days: int


class ThegentAPIClient:
    """HTTP client for thegent MCP server API."""

    def __init__(self, host: str = "127.0.0.1", port: int = 3847) -> None:
        """Initialize the API client.

        Args:
            host: The host address of the MCP server.
            port: The port of the MCP server.
        """
        self._host = host
        self._port = port
        self._client = httpx.Client(timeout=30.0)

    def _get_url(self, path: str) -> str:
        """Build the full URL for an API endpoint.

        Args:
            path: The API path.

        Returns:
            The full URL.
        """
        return f"http://{self._host}:{self._port}{path}"

    # Projects
    def get_projects(self) -> list[Project]:
        """Get all projects.

        Returns:
            List of projects.
        """
        response = self._client.get(self._get_url("/api/projects"))
        response.raise_for_status()
        data = response.json()
        return [Project(**p) for p in data]

    def get_project(self, id: str) -> Project:
        """Get a project by ID.

        Args:
            id: The project ID.

        Returns:
            The project.
        """
        response = self._client.get(self._get_url(f"/api/projects/{id}"))
        response.raise_for_status()
        return Project(**response.json())

    def create_project(self, **kwargs: Any) -> Project:
        """Create a new project.

        Args:
            **kwargs: Project fields.

        Returns:
            The created project.
        """
        response = self._client.post(self._get_url("/api/projects"), json=kwargs)
        response.raise_for_status()
        return Project(**response.json())

    def update_project(self, id: str, **kwargs: Any) -> Project:
        """Update a project.

        Args:
            id: The project ID.
            **kwargs: Fields to update.

        Returns:
            The updated project.
        """
        response = self._client.patch(self._get_url(f"/api/projects/{id}"), json=kwargs)
        response.raise_for_status()
        return Project(**response.json())

    def delete_project(self, id: str) -> None:
        """Delete a project.

        Args:
            id: The project ID.
        """
        response = self._client.delete(self._get_url(f"/api/projects/{id}"))
        response.raise_for_status()

    # Agents
    def get_agents(self) -> list[Agent]:
        """Get all agents.

        Returns:
            List of agents.
        """
        response = self._client.get(self._get_url("/api/agents"))
        response.raise_for_status()
        data = response.json()
        return [Agent(**a) for a in data]

    def get_agent(self, id: str) -> Agent:
        """Get an agent by ID.

        Args:
            id: The agent ID.

        Returns:
            The agent.
        """
        response = self._client.get(self._get_url(f"/api/agents/{id}"))
        response.raise_for_status()
        return Agent(**response.json())

    def update_agent(self, id: str, **kwargs: Any) -> Agent:
        """Update an agent.

        Args:
            id: The agent ID.
            **kwargs: Fields to update.

        Returns:
            The updated agent.
        """
        response = self._client.patch(self._get_url(f"/api/agents/{id}"), json=kwargs)
        response.raise_for_status()
        return Agent(**response.json())

    # Runs
    def get_runs(self, project_id: str, status: str | None = None) -> list[Run]:
        """Get runs for a project.

        Args:
            project_id: The project ID.
            status: Optional status filter.

        Returns:
            List of runs.
        """
        params: dict[str, str] = {"project_id": project_id}
        if status:
            params["status"] = status
        response = self._client.get(self._get_url("/api/runs"), params=params)
        response.raise_for_status()
        data = response.json()
        return [Run(**r) for r in data]

    def get_run(self, id: str) -> Run:
        """Get a run by ID.

        Args:
            id: The run ID.

        Returns:
            The run.
        """
        response = self._client.get(self._get_url(f"/api/runs/{id}"))
        response.raise_for_status()
        return Run(**response.json())

    # Gardener
    def get_gardener_status(self) -> GardenerStatus:
        """Get gardener status.

        Returns:
            The gardener status.
        """
        response = self._client.get(self._get_url("/api/gardener/status"))
        response.raise_for_status()
        return GardenerStatus(**response.json())

    def start_gardener(self) -> GardenerStatus:
        """Start the gardener.

        Returns:
            The gardener status.
        """
        response = self._client.post(self._get_url("/api/gardener/start"))
        response.raise_for_status()
        return GardenerStatus(**response.json())

    def stop_gardener(self) -> GardenerStatus:
        """Stop the gardener.

        Returns:
            The gardener status.
        """
        response = self._client.post(self._get_url("/api/gardener/stop"))
        response.raise_for_status()
        return GardenerStatus(**response.json())

    def trigger_scan(self) -> dict[str, Any]:
        """Trigger a gardener scan.

        Returns:
            Scan result.
        """
        response = self._client.post(self._get_url("/api/gardener/scan"))
        response.raise_for_status()
        return response.json()

    def get_gardener_config(self) -> dict[str, Any]:
        """Get gardener configuration.

        Returns:
            The gardener configuration.
        """
        response = self._client.get(self._get_url("/api/gardener/config"))
        response.raise_for_status()
        return response.json()

    def update_gardener_config(self, **kwargs: Any) -> dict[str, Any]:
        """Update gardener configuration.

        Args:
            **kwargs: Configuration fields to update.

        Returns:
            The updated configuration.
        """
        response = self._client.patch(self._get_url("/api/gardener/config"), json=kwargs)
        response.raise_for_status()
        return response.json()

    # Costs
    def get_cost_daily(self) -> CostSummary:
        """Get daily cost summary.

        Returns:
            The daily cost summary.
        """
        response = self._client.get(self._get_url("/api/costs/daily"))
        response.raise_for_status()
        return CostSummary(**response.json())

    def get_cost_monthly(self) -> CostSummary:
        """Get monthly cost summary.

        Returns:
            The monthly cost summary.
        """
        response = self._client.get(self._get_url("/api/costs/monthly"))
        response.raise_for_status()
        return CostSummary(**response.json())

    def get_cost_alerts(self) -> list[dict[str, Any]]:
        """Get cost alerts.

        Returns:
            List of cost alerts.
        """
        response = self._client.get(self._get_url("/api/costs/alerts"))
        response.raise_for_status()
        return response.json()

    def create_cost_alert(self, **kwargs: Any) -> dict[str, Any]:
        """Create a cost alert.

        Args:
            **kwargs: Alert fields.

        Returns:
            The created alert.
        """
        response = self._client.post(self._get_url("/api/costs/alerts"), json=kwargs)
        response.raise_for_status()
        return response.json()

    # Gamification
    def get_gamification_stats(self) -> GamificationStats:
        """Get gamification statistics.

        Returns:
            The gamification stats.
        """
        response = self._client.get(self._get_url("/api/gamification/stats"))
        response.raise_for_status()
        return GamificationStats(**response.json())

    def get_achievements(self) -> list[dict[str, Any]]:
        """Get achievements.

        Returns:
            List of achievements.
        """
        response = self._client.get(self._get_url("/api/gamification/achievements"))
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
