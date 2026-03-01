import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from thegent.integrations.base import SerializableMixin

_log = logging.getLogger(__name__)


class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SyncResult(SerializableMixin):
    component: str
    status: SyncStatus
    message: str = ""
    duration: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    changes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())



class SyncComponent(ABC):
    def __init__(self, name: str, description: str, depends_on: list[str] | None = None) -> None:
        self.name = name
        self.description = description
        self.depends_on = depends_on or []

    @abstractmethod
    async def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        pass

    @abstractmethod
    async def update(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        pass


class RulesSyncComponent(SyncComponent):
    def __init__(self) -> None:
        super().__init__("rules", "Sync CLAUDE.md to other platform-specific rule files.")

    async def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        from thegent.cli.commands.impl import rules_sync_impl

        try:
            rules_sync_impl(force=force, check=dry_run)
            return SyncResult(self.name, SyncStatus.SUCCESS, "Rules synchronized successfully.")
        except Exception as e:
            return SyncResult(self.name, SyncStatus.FAILED, f"Failed: {e}", errors=[str(e)])

    async def update(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        return await self.sync(dry_run=dry_run, force=force)


class DagSyncComponent(SyncComponent):
    def __init__(self) -> None:
        super().__init__("dag", "Synchronize DAG state from session meta files.")

    async def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        from thegent.cli import dag_sync_cmd

        try:
            dag_sync_cmd()
            return SyncResult(self.name, SyncStatus.SUCCESS, "DAG state synchronized.")
        except Exception as e:
            return SyncResult(self.name, SyncStatus.FAILED, f"Failed: {e}", errors=[str(e)])

    async def update(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        from thegent.cli import dag_sync_cmd

        try:
            dag_sync_cmd()
            return SyncResult(self.name, SyncStatus.SUCCESS, "DAG state updated.")
        except Exception as e:
            return SyncResult(self.name, SyncStatus.FAILED, f"Failed: {e}", errors=[str(e)])


class WorkStreamSyncComponent(SyncComponent):
    def __init__(self) -> None:
        super().__init__("work-stream", "Incorporate new work items into WORK_STREAM.md.")

    async def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        from thegent.cli import plan_incorporate_cmd

        try:
            plan_incorporate_cmd(dry_run=dry_run)
            return SyncResult(self.name, SyncStatus.SUCCESS, "Work stream incorporated.")
        except Exception as e:
            return SyncResult(self.name, SyncStatus.FAILED, f"Failed: {e}", errors=[str(e)])

    async def update(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        return await self.sync(dry_run=dry_run, force=force)


class CatalogSyncComponent(SyncComponent):
    def __init__(self) -> None:
        super().__init__("catalog", "Update the model catalog by scraping providers.")

    async def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        if dry_run:
            return SyncResult(self.name, SyncStatus.SUCCESS, "Would scrape all providers.")
        from thegent.models.scrapers import scrape_all

        try:
            by_provider = scrape_all()
            count = sum(len(m) for m in by_provider.values())
            return SyncResult(
                self.name, SyncStatus.SUCCESS, f"Scraped {count} models from {len(by_provider)} providers."
            )
        except Exception as e:
            return SyncResult(self.name, SyncStatus.FAILED, f"Failed: {e}", errors=[str(e)])

    async def update(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        return await self.sync(dry_run=dry_run, force=force)


class SyncRegistry:
    def __init__(self) -> None:
        self.components: dict[str, SyncComponent] = {}

    def register(self, component: SyncComponent):
        self.components[component.name] = component

    def get_component(self, name: str) -> SyncComponent | None:
        return self.components.get(name)

    def get_all_components(self) -> list[SyncComponent]:
        return list(self.components.values())


class SyncOrchestrator:
    def __init__(self, registry: SyncRegistry | None = None) -> None:
        self.registry = registry or global_registry

    async def sync_all(
        self, names: list[str] | None = None, dry_run: bool = False, force: bool = False
    ) -> list[SyncResult]:
        components_to_sync = []
        if not names:
            components_to_sync = self.registry.get_all_components()
        else:
            for name in names:
                comp = self.registry.get_component(name)
                if comp:
                    components_to_sync.append(comp)

        sorted_components = self._resolve_dependencies(components_to_sync)
        results = []
        for comp in sorted_components:
            start_time = time.time()
            try:
                result = await comp.sync(dry_run=dry_run, force=force)
                result.duration = time.time() - start_time
                results.append(result)
            except Exception as e:
                results.append(
                    SyncResult(
                        component=comp.name, status=SyncStatus.FAILED, message=str(e), duration=time.time() - start_time
                    )
                )
        return results

    async def update_all(
        self, names: list[str] | None = None, dry_run: bool = False, force: bool = False
    ) -> list[SyncResult]:
        components_to_update = []
        if not names:
            components_to_update = self.registry.get_all_components()
        else:
            for name in names:
                comp = self.registry.get_component(name)
                if comp:
                    components_to_update.append(comp)

        sorted_components = self._resolve_dependencies(components_to_update)
        results = []
        for comp in sorted_components:
            start_time = time.time()
            try:
                result = await comp.update(dry_run=dry_run, force=force)
                result.duration = time.time() - start_time
                results.append(result)
            except Exception as e:
                results.append(
                    SyncResult(
                        component=comp.name, status=SyncStatus.FAILED, message=str(e), duration=time.time() - start_time
                    )
                )
        return results

    def _resolve_dependencies(self, components: list[SyncComponent]) -> list[SyncComponent]:
        resolved = []
        seen = set()

        def resolve(comp: SyncComponent):
            if comp.name in seen:
                return
            for dep_name in comp.depends_on:
                dep = self.registry.get_component(dep_name)
                if dep:
                    resolve(dep)
            resolved.append(comp)
            seen.add(comp.name)

        for comp in components:
            resolve(comp)
        return resolved


# Global registry
global_registry = SyncRegistry()
global_registry.register(RulesSyncComponent())
global_registry.register(DagSyncComponent())
global_registry.register(WorkStreamSyncComponent())
global_registry.register(CatalogSyncComponent())
