"""Unified Agent Registry routes for Control Plane."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from thegent.agents.unified_registry import (
    Agent,
    AgentCapability,
    AgentRegistryService,
    AgentStatus,
    CollaborationRule,
    ProjectAssignment,
)

# Global service instance for the control plane
_registry_service = AgentRegistryService()


async def list_agents(request: Request) -> JSONResponse:
    """GET /v1/agents — list agents."""
    status = request.query_params.get("status")
    project = request.query_params.get("project")
    capability = request.query_params.get("capability")

    agents = _registry_service.list_agents(
        status=AgentStatus(status) if status else None,
        project_id=project,
        capability=AgentCapability(capability) if capability else None,
    )

    return JSONResponse([a.model_dump(mode="json") for a in agents])


async def register_agent(request: Request) -> JSONResponse:
    """POST /v1/agents — register a new agent."""
    try:
        data = await request.json()
        agent = Agent(**data)
        registered = _registry_service.register_agent(agent)
        return JSONResponse(registered.model_dump(mode="json"), status_code=201)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=400)


async def get_agent(request: Request) -> JSONResponse:
    """GET /v1/agents/{agent_id} — get agent details."""
    agent_id = request.path_params.get("agent_id")
    agent = _registry_service.get_agent(agent_id)
    if agent:
        return JSONResponse(agent.model_dump(mode="json"))
    return JSONResponse({"detail": f"Agent {agent_id} not found"}, status_code=404)


async def update_agent(request: Request) -> JSONResponse:
    """PUT /v1/agents/{agent_id} — update agent."""
    agent_id = request.path_params.get("agent_id")
    try:
        data = await request.json()
        updated = _registry_service.update_agent(agent_id, data)
        if updated:
            return JSONResponse(updated.model_dump(mode="json"))
        return JSONResponse({"detail": f"Agent {agent_id} not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=400)


async def delete_agent(request: Request) -> Response:
    """DELETE /v1/agents/{agent_id} — delete agent."""
    agent_id = request.path_params.get("agent_id")
    if _registry_service.delete_agent(agent_id):
        return Response(status_code=204)
    return JSONResponse({"detail": f"Agent {agent_id} not found"}, status_code=404)


async def assign_project(request: Request) -> JSONResponse:
    """POST /v1/agents/{agent_id}/projects — assign agent to project."""
    agent_id = request.path_params.get("agent_id")
    try:
        data = await request.json()
        assignment = ProjectAssignment(**data)
        updated = _registry_service.assign_to_project(agent_id, assignment)
        if updated:
            return JSONResponse(updated.model_dump(mode="json"))
        return JSONResponse({"detail": f"Agent {agent_id} not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=400)


async def discover_best(request: Request) -> JSONResponse:
    """POST /v1/discover/best — discover best agent for task."""
    try:
        data = await request.json()
        description = data.get("task_description")
        capabilities = [AgentCapability(c) for c in data.get("required_capabilities", [])]
        project = data.get("project_id")

        agent = _registry_service.discover_best_agent(description, capabilities, project_id=project)
        if agent:
            return JSONResponse(agent.model_dump(mode="json"))
        return JSONResponse({"detail": "No suitable agent found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=400)


registry_routes = [
    Route("/v1/agents", list_agents, methods=["GET"]),
    Route("/v1/agents", register_agent, methods=["POST"]),
    Route("/v1/agents/{agent_id}", get_agent, methods=["GET"]),
    Route("/v1/agents/{agent_id}", update_agent, methods=["PUT"]),
    Route("/v1/agents/{agent_id}", delete_agent, methods=["DELETE"]),
    Route("/v1/agents/{agent_id}/projects", assign_project, methods=["POST"]),
    Route("/v1/discover/best", discover_best, methods=["POST"]),
]
