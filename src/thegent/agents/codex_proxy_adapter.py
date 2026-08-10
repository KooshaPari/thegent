"""CodexProxyAdapter — adapter wrapper for agent execution via codex_proxy."""

from thegent.adapters.ports import AdapterRegistry
from thegent.agents.codex_proxy_runner import CodexProxyRunner


class CodexProxyAdapter:
    """Codex proxy adapter for agent execution"""

    def __init__(self):
        self._runner = CodexProxyRunner

    def call(self, **kwargs) -> dict:
        """Execute via Codex proxy"""
        return {"status": "ready", "adapter": "codex_proxy"}


AdapterRegistry.register("codex_proxy", CodexProxyAdapter())
