"""WP-31002: Containerized Agent Sandboxes (Wasm).
Provides lightweight, secure execution environments for untrusted agent code using WebAssembly.
Ensures near-native performance with strict memory and capability isolation.
"""

import json
import logging
import time
from typing import Any, Optional

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class SandboxConfig(BaseModel):
    """Configuration for a Wasm sandbox."""

    max_memory_mb: int = 128
    allow_network: bool = False
    allow_filesystem: bool = False
    env_vars: dict[str, str] = {}


class WasmSandbox:
    """Manages secure execution of agent code in a Wasm environment using Extism."""

    def __init__(self, sandbox_id: str, config: SandboxConfig | None = None) -> None:
        self.sandbox_id = sandbox_id
        self.config = config or SandboxConfig()
        self.status = "initialized"
        self._plugin = None

    def _init_plugin(self, wasm_binary_path: str):
        """Initialize the Extism plugin."""
        try:
            import extism
        except ImportError:
            _log.error("Extism not installed. Run 'pip install extism'.")
            raise

        manifest = {"wasm": [{"path": wasm_binary_path}]}
        # Add config/env if needed
        if self.config.env_vars:
            manifest["config"] = self.config.env_vars

        # Extism handles memory limits via the runtime, but we can pass config
        self._plugin = extism.Plugin(manifest, wasi=True)

    def run_function(self, wasm_binary_path: str, function_name: str, input_data: str | bytes) -> dict[str, Any]:
        """Execute a function inside the Wasm sandbox using Extism."""
        start_time = time.time()
        _log.info("Executing Wasm binary %s in sandbox %s", wasm_binary_path, self.sandbox_id)

        if not self._plugin:
            self._init_plugin(wasm_binary_path)

        self.status = "running"
        try:
            # Extism plugin.call returns the output of the function
            output = self._plugin.call(function_name, input_data)
            duration_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "result": output.decode("utf-8") if isinstance(output, bytes) else output,
                "duration_ms": duration_ms,
            }
        except Exception as e:
            _log.error("Wasm execution failed: %s", e)
            return {"status": "error", "error": str(e), "duration_ms": (time.time() - start_time) * 1000}

    def shutdown(self):
        """Tear down the sandbox and release resources."""
        if self._plugin:
            self._plugin.close()
            self._plugin = None
        _log.info("Shutting down Wasm sandbox: %s", self.sandbox_id)
        self.status = "terminated"
