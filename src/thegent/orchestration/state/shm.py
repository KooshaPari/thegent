import logging
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


class SHMSystem:
    """Wrapper for thegent_shm Rust extension."""

    _instance = None
    _interface = None

    def __new__(cls, session_dir: Path):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init(session_dir)
        return cls._instance

    def _init(self, session_dir: Path):
        from thegent.config import ThegentSettings

        self.session_dir = session_dir
        self.shm_path = session_dir / "state.shm"
        self.use_native = ThegentSettings().use_native_shm
        self._interface = None

        if self.use_native:
            try:
                import thegent_shm

                # BKM-05: Use global init_shm and also instantiate interface if needed for direct calls
                thegent_shm.init_shm(str(self.shm_path))
                self._interface = thegent_shm.SHMInterface(str(self.shm_path))
                _log.debug("Initialized native SHM at %s", self.shm_path)
            except ImportError:
                _log.debug("thegent_shm native extension not found. Falling back to legacy state.")
            except Exception as e:
                _log.error("Failed to initialize native SHM: %s", e)

    def is_native_active(self) -> bool:
        return self._interface is not None

    def record_failure(self, target: str, category: str = "agent"):
        if self._interface:
            cat_idx = 0 if category == "agent" else 1
            self._interface.record_failure(target, cat_idx)

    def is_open(
        self, target: str, category: str = "agent", threshold: int = 5, window_s: int = 300, recovery_s: int = 60
    ) -> bool:
        if self._interface:
            cat_idx = 0 if category == "agent" else 1
            return self._interface.is_open(target, cat_idx, threshold, window_s, recovery_s)
        return False

    def award_xp(self, amount: int):
        if self._interface:
            self._interface.award_xp(amount)

    def get_xp_state(self) -> dict[str, Any | None]:
        if self._interface:
            return self._interface.get_xp_state()
        return None

    def set_level(self, level: int):
        if self._interface:
            self._interface.set_level(level)


def get_shm_system(session_dir: Path) -> SHMSystem:
    return SHMSystem(session_dir)
