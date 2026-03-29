"""BytePort synchronous client"""

from typing import Optional, Dict, List, Iterator
import httpx
from .types import (
    Deployment,
    DeployRequest,
    DeploymentList,
    DeploymentStatus,
    LogEntry,
    LogsResponse,
    Metrics,
    Project,
    ProjectList,
    CreateProjectRequest,
    DetectRequest,
    DetectResponse,
    EstimateCostRequest,
    EstimateCostResponse,
    HealthResponse,
)
from .exceptions import BytePortError, NotFoundError, BadRequestError, ServerError


class BytePortClient:
    """Synchronous BytePort API client"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.byteport.io/api/v1",
        timeout: float = 30.0,
    ):
        """
        Initialize BytePort client

        Args:
            api_key: BytePort API key
            base_url: API base URL (for self-hosted instances)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client"""
        self.client.close()

    def _handle_error(self, response: httpx.Response):
        """Handle HTTP errors"""
        if response.status_code == 404:
            try:
                error_data = response.json()
                raise NotFoundError(error_data.get("error", "Not found"), error_data.get("details", ""))
            except ValueError:
                raise NotFoundError(response.text)
        elif response.status_code == 400:
            try:
                error_data = response.json()
                raise BadRequestError(error_data.get("error", "Bad request"), error_data.get("details", ""))
            except ValueError:
                raise BadRequestError(response.text)
        elif response.status_code >= 500:
            try:
                error_data = response.json()
                raise ServerError(error_data.get("error", "Server error"), error_data.get("details", ""))
            except ValueError:
                raise ServerError(response.text)
        else:
            try:
                error_data = response.json()
                raise BytePortError(
                    error_data.get("error", "Unknown error"),
                    response.status_code,
                    error_data.get("details", "")
                )
            except ValueError:
                raise BytePortError(response.text, response.status_code)

    def health(self) -> HealthResponse:
        """Check API health"""
        response = self.client.get("/health")
        if not response.is_success:
            self._handle_error(response)
        return HealthResponse(**response.json())

    def deploy(self, request: Dict) -> Deployment:
        """Create a new deployment"""
        deploy_req = DeployRequest(**request)
        response = self.client.post("/deployments", json=deploy_req.model_dump(exclude_none=True))
        if not response.is_success:
            self._handle_error(response)
        return Deployment(**response.json())

    def get_deployment(self, deployment_id: str) -> Deployment:
        """Get deployment details"""
        response = self.client.get(f"/deployments/{deployment_id}")
        if not response.is_success:
            self._handle_error(response)
        return Deployment(**response.json())

    def list_deployments(self) -> List[Deployment]:
        """List all deployments"""
        response = self.client.get("/deployments")
        if not response.is_success:
            self._handle_error(response)
        data = DeploymentList(**response.json())
        return data.deployments

    def terminate(self, deployment_id: str) -> None:
        """Terminate a deployment"""
        response = self.client.delete(f"/deployments/{deployment_id}")
        if not response.is_success:
            self._handle_error(response)

    def get_status(self, deployment_id: str) -> DeploymentStatus:
        """Get deployment status"""
        response = self.client.get(f"/deployments/{deployment_id}/status")
        if not response.is_success:
            self._handle_error(response)
        return DeploymentStatus(**response.json())

    def get_logs(self, deployment_id: str, service: Optional[str] = None) -> List[LogEntry]:
        """Get deployment logs"""
        params = {"service": service} if service else {}
        response = self.client.get(f"/deployments/{deployment_id}/logs", params=params)
        if not response.is_success:
            self._handle_error(response)
        data = LogsResponse(**response.json())
        return data.logs

    def stream_logs(self, deployment_id: str) -> Iterator[LogEntry]:
        """Stream logs in real-time"""
        with self.client.stream("GET", f"/deployments/{deployment_id}/logs?stream=true") as response:
            if not response.is_success:
                self._handle_error(response)

            for line in response.iter_lines():
                if line:
                    try:
                        yield LogEntry.model_validate_json(line)
                    except Exception:
                        continue

    def get_metrics(self, deployment_id: str) -> Metrics:
        """Get deployment metrics"""
        response = self.client.get(f"/deployments/{deployment_id}/metrics")
        if not response.is_success:
            self._handle_error(response)
        return Metrics(**response.json())

    def create_project(self, request: Dict) -> Project:
        """Create a new project"""
        proj_req = CreateProjectRequest(**request)
        response = self.client.post("/projects", json=proj_req.model_dump(exclude_none=True))
        if not response.is_success:
            self._handle_error(response)
        return Project(**response.json())

    def get_project(self, project_id: str) -> Project:
        """Get project details"""
        response = self.client.get(f"/projects/{project_id}")
        if not response.is_success:
            self._handle_error(response)
        return Project(**response.json())

    def list_projects(self) -> List[Project]:
        """List all projects"""
        response = self.client.get("/projects")
        if not response.is_success:
            self._handle_error(response)
        data = ProjectList(**response.json())
        return data.projects

    def delete_project(self, project_id: str) -> None:
        """Delete a project"""
        response = self.client.delete(f"/projects/{project_id}")
        if not response.is_success:
            self._handle_error(response)

    def detect_app_type(self, files: List[str]) -> DetectResponse:
        """Auto-detect application type"""
        request = DetectRequest(files=files)
        response = self.client.post("/detect", json=request.model_dump())
        if not response.is_success:
            self._handle_error(response)
        return DetectResponse(**response.json())

    def estimate_cost(self, app_type: str, provider: str) -> EstimateCostResponse:
        """Estimate deployment cost"""
        request = EstimateCostRequest(type=app_type, provider=provider)
        response = self.client.post("/estimate-cost", json=request.model_dump())
        if not response.is_success:
            self._handle_error(response)
        return EstimateCostResponse(**response.json())
