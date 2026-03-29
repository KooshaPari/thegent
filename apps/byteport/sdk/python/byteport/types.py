"""BytePort type definitions"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class DeployRequest(BaseModel):
    """Request to create a deployment"""

    name: str
    type: str  # frontend, backend, database, cache
    provider: Optional[str] = None
    git_url: Optional[str] = None
    branch: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    env_vars: Optional[Dict[str, str]] = None


class CostInfo(BaseModel):
    """Cost information"""

    monthly: float
    currency: str = "USD"


class Deployment(BaseModel):
    """Deployment response"""

    id: str
    name: str
    type: str
    status: str
    url: str
    provider: str
    git_url: Optional[str] = None
    branch: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None
    created_at: datetime
    updated_at: datetime
    message: Optional[str] = None


class DeploymentList(BaseModel):
    """List of deployments"""

    deployments: List[Deployment]
    total: int


class DeploymentStatus(BaseModel):
    """Deployment status"""

    id: str
    status: str
    progress: int
    updated_at: datetime


class LogEntry(BaseModel):
    """Log entry"""

    timestamp: datetime
    level: str
    message: str


class LogsResponse(BaseModel):
    """Logs response"""

    deployment_id: str
    logs: List[LogEntry]


class Metrics(BaseModel):
    """Deployment metrics"""

    deployment_id: str
    uptime: str
    requests: int
    bandwidth: str
    response_time: str
    cost: CostInfo


class Project(BaseModel):
    """Project"""

    id: str
    name: str
    description: Optional[str] = None
    deployments: Optional[int] = None
    created_at: datetime


class ProjectList(BaseModel):
    """List of projects"""

    projects: List[Project]


class CreateProjectRequest(BaseModel):
    """Request to create a project"""

    name: str
    description: Optional[str] = None


class DetectRequest(BaseModel):
    """Request to detect app type"""

    files: List[str]


class DetectResponse(BaseModel):
    """App type detection response"""

    type: str
    framework: str
    confidence: float
    suggested_provider: str


class CostBreakdown(BaseModel):
    """Cost breakdown for a service"""

    service: str
    provider: str
    cost: float
    plan: str


class EstimateCostRequest(BaseModel):
    """Request to estimate cost"""

    type: str
    provider: str


class EstimateCostResponse(BaseModel):
    """Cost estimation response"""

    monthly: float
    currency: str = "USD"
    breakdown: List[CostBreakdown]
    message: str


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    service: str
    version: str
