"""Storage backends for results"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import json
import shutil


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def save(self, key: str, data: dict[str, Any]) -> None:
        """Save data"""
        ...
    
    @abstractmethod
    async def load(self, key: str) -> dict[str, Any] | None:
        """Load data"""
        ...
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete data"""
        ...
    
    @abstractmethod
    async def list(self, prefix: str = "") -> list[str]:
        """List keys with optional prefix"""
        ...


class LocalStorage(StorageBackend):
    """Local file system storage"""
    
    def __init__(self, base_path: Path | str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, key: str) -> Path:
        # Sanitize key to prevent directory traversal
        safe_key = key.replace("..", "").replace("/", "_")
        return self.base_path / f"{safe_key}.json"
    
    async def save(self, key: str, data: dict[str, Any]) -> None:
        path = self._get_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    async def load(self, key: str) -> dict[str, Any] | None:
        path = self._get_path(key)
        if not path.exists():
            return None
        with open(path) as f:
            return json.load(f)
    
    async def delete(self, key: str) -> bool:
        path = self._get_path(key)
        if path.exists():
            path.unlink()
            return True
        return False
    
    async def list(self, prefix: str = "") -> list[str]:
        pattern = f"{prefix}*.json" if prefix else "*.json"
        return [p.stem for p in self.base_path.glob(pattern)]


class ResultRegistry:
    """Registry for storing and retrieving benchmark results"""
    
    def __init__(self, storage: StorageBackend):
        self.storage = storage
    
    async def save_result(
        self,
        run_id: str,
        task_id: str,
        agent_name: str,
        metrics: dict[str, Any]
    ) -> None:
        """Save a task result"""
        key = f"{run_id}/{task_id}"
        await self.storage.save(key, {
            "run_id": run_id,
            "task_id": task_id,
            "agent_name": agent_name,
            "metrics": metrics,
        })
    
    async def get_result(self, run_id: str, task_id: str) -> dict[str, Any] | None:
        """Get a task result"""
        return await self.storage.load(f"{run_id}/{task_id}")
    
    async def list_runs(self) -> list[str]:
        """List all run IDs"""
        keys = await self.storage.list()
        runs = set()
        for key in keys:
            run_id = key.split("/")[0]
            runs.add(run_id)
        return sorted(runs)
    
    async def get_run_results(self, run_id: str) -> list[dict[str, Any]]:
        """Get all results for a run"""
        results = []
        prefix = f"{run_id}/"
        keys = await self.storage.list(prefix)
        for key in keys:
            result = await self.storage.load(key)
            if result:
                results.append(result)
        return results
    
    async def delete_run(self, run_id: str) -> None:
        """Delete all results for a run"""
        prefix = f"{run_id}/"
        keys = await self.storage.list(prefix)
        for key in keys:
            await self.storage.delete(key)
