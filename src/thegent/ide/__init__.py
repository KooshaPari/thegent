"""IDE integration infrastructure for thegent."""

from thegent.ide.auto_init import (
    auto_init_on_startup,
    ensure_lsp_servers_ready,
)
from thegent.ide.auto_setup import (
    auto_setup_all,
    auto_setup_ghostty_shell_integration,
    auto_setup_jetbrains_integration,
    auto_setup_serena_jetbrains_plugin,
)

__all__ = [
    "auto_init_on_startup",
    "auto_setup_all",
    "auto_setup_ghostty_shell_integration",
    "auto_setup_jetbrains_integration",
    "auto_setup_serena_jetbrains_plugin",
    "ensure_lsp_servers_ready",
]
