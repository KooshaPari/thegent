"""IDE and tool integrations for thegent."""

from thegent.integrations.ghostty import (
    GhosttyConfig,
    GhosttyError,
    GhosttyIntegration,
)
from thegent.integrations.jetbrains import (
    IdeType,
    JetBrainsConfig,
    JetBrainsIntegration,
)
from thegent.integrations.gh_project_sync import (
    GHProjectSyncConfig,
    GHProjectSyncResult,
)
from thegent.integrations.workstream_autosync import (
    LocalWorkItem,
    SyncCycleReport,
)

__all__ = [
    "GhosttyConfig",
    "GhosttyError",
    "GhosttyIntegration",
    "GHProjectSyncConfig",
    "GHProjectSyncResult",
    "LocalWorkItem",
    "SyncCycleReport",
    "IdeType",
    "JetBrainsConfig",
    "JetBrainsIntegration",
]
