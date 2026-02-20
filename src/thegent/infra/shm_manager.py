import os
import time
from pathlib import Path
from typing import Any, Optional

try:
    import thegent_shm

    HAS_SHM = True
except ImportError:
    HAS_SHM = False


class SHMManager:
    """Python wrapper for the high-performance Rust SHM mesh."""

    def __init__(self, shm_path: Path | None = None):
        self.shm_path = shm_path or Path(os.environ.get("THEGENT_SHM_PATH", "/tmp/thegent-bridge/state.shm"))
        self._initialized = False
        if HAS_SHM:
            self._ensure_init()

    def _ensure_init(self):
        if not self._initialized:
            try:
                # Ensure directory exists
                self.shm_path.parent.mkdir(parents=True, exist_ok=True)
                thegent_shm.init_shm(str(self.shm_path))
                self._initialized = True
            except Exception as e:
                print(f"[SHM] Failed to initialize: {e}")

    def update_provider_metrics(self, provider: str, request_count: int, success_count: int, latency_ms: int):
        if not HAS_SHM:
            return
        self._ensure_init()
        try:
            thegent_shm.update_provider(provider, request_count, success_count, latency_ms)
        except Exception as e:
            print(f"[SHM] Failed to update provider {provider}: {e}")

    def get_provider_metrics(self, provider: str) -> dict[str, Any] | None:
        if not HAS_SHM:
            return None
        self._ensure_init()
        try:
            return thegent_shm.get_provider_metrics(provider)
        except Exception as e:
            print(f"[SHM] Failed to get metrics for {provider}: {e}")
            return None

    def record_resource_usage(self, pid: int, cpu_percent: float, memory_kb: int):
        if not HAS_SHM:
            return
        self._ensure_init()
        try:
            thegent_shm.record_resource_usage(pid, float(cpu_percent), int(memory_kb))
        except Exception as e:
            print(f"[SHM] Failed to record resource usage: {e}")

    def award_xp(self, amount: int):
        if not HAS_SHM:
            return
        self._ensure_init()
        try:
            thegent_shm.award_xp(amount)
        except Exception as e:
            print(f"[SHM] Failed to award XP: {e}")

    def get_xp_state(self) -> dict[str, Any] | None:
        if not HAS_SHM:
            return None
        self._ensure_init()
        try:
            return thegent_shm.get_xp_state()
        except Exception as e:
            print(f"[SHM] Failed to get XP state: {e}")
            return None

    def record_failure(self, target: str, category: int):
        if not HAS_SHM:
            return
        self._ensure_init()
        try:
            thegent_shm.record_failure(target, category)
        except Exception as e:
            print(f"[SHM] Failed to record failure for {target}: {e}")

    def set_health_score(self, score: float):
        if not HAS_SHM:
            return
        self._ensure_init()
        try:
            thegent_shm.set_health_score(score)
        except Exception as e:
            print(f"[SHM] Failed to set health score: {e}")

    def get_health_score(self) -> float:
        if not HAS_SHM:
            return 0.0
        self._ensure_init()
        try:
            return thegent_shm.get_health_score()
        except Exception as e:
            print(f"[SHM] Failed to get health score: {e}")
            return 0.0

    def update_router_metrics(
        self, lifecycle_inc: int = 0, thegent_inc: int = 0, changes_inc: int = 0, hysteresis_inc: int = 0
    ):
        if not HAS_SHM:
            return
        self._ensure_init()
        try:
            thegent_shm.update_router_metrics(lifecycle_inc, thegent_inc, changes_inc, hysteresis_inc)
        except Exception as e:
            print(f"[SHM] Failed to update router metrics: {e}")

    def get_router_metrics(self) -> dict[str, Any] | None:
        if not HAS_SHM:
            return None
        self._ensure_init()
        try:
            return thegent_shm.get_router_metrics()
        except Exception as e:
            print(f"[SHM] Failed to get router metrics: {e}")
            return None
