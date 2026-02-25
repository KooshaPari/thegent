"""Catalog resource handlers for MCP server."""

from __future__ import annotations

import orjson as json
from typing import Any, Callable


def resource_dag_impl(
    *,
    dag_list_impl: Callable[..., Any],
) -> str:
    return json.dumps(dag_list_impl(cd=None))


def resource_agents_impl(
    *,
    list_agents_impl: Callable[..., Any],
) -> str:
    return json.dumps(list_agents_impl())


def resource_models_impl(
    *,
    provider: str | None,
    include_contract: bool,
    list_models_impl: Callable[..., Any],
) -> str:
    return json.dumps(list_models_impl(provider=provider, include_contract=include_contract))


def resource_models_contract_impl() -> str:
    from thegent.models import route_contract

    return json.dumps(route_contract())
