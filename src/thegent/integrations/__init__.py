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

__all__ = [
    "GhosttyConfig",
    "GhosttyError",
    "GhosttyIntegration",
    "IdeType",
    "JetBrainsConfig",
    "JetBrainsIntegration",
]
