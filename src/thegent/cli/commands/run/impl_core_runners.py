"""Re-export shim for ``thegent.cli.commands.run.impl_core_runners._apply_pareto_routing``.

The module name is referenced by
``src/thegent/cli/services/run_execution_core_helpers.py:114`` for the
pareto-routing path. Keeping the submodule distinct from the package
``__init__`` lets the test surface patch either side independently.
"""

from __future__ import annotations

from typing import Any

from thegent.cli.commands.run import _apply_pareto_routing as _impl_apply


def _apply_pareto_routing(
    agent: str | None,
    model: str | None,
    routing: str | None,
    include_contract: bool,
    route_contract: dict[str, Any] | None,
    route_request: dict[str, Any] | None,
) -> tuple[str | None, str | None, dict[str, Any] | None, dict[str, Any] | None]:
    return _impl_apply(agent, model, routing, include_contract, route_contract, route_request)


__all__ = ["_apply_pareto_routing"]
