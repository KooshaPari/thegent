"""Execution boundary shim -- WL-120 extraction hardening.

Re-exports the four canonical execution boundary functions so
downstream consumers (``thegent.dag`` Typer sub-app, MCP server
wrappers, WL-120 hardening tests) can resolve them without
circular-import risk.

Canonical homes:
- ``run_impl`` -> ``thegent.cli.commands.impl``
- ``bg_impl`` -> ``thegent.cli.commands.impl``
- ``resume_impl`` -> ``thegent.cli.commands.impl``
- ``loop_impl`` -> ``thegent.cli.services.run_post_surface_helpers``
"""

from __future__ import annotations

from thegent.cli.commands.impl import bg_impl, resume_impl, run_impl
from thegent.cli.services.run_post_surface_helpers import loop_impl

__all__ = ["run_impl", "bg_impl", "resume_impl", "loop_impl"]
