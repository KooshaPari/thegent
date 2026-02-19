"""LSP command utilities for listing and managing servers."""

from thegent.lsp.auto_install import LSP_INSTALL_COMMANDS, check_command_available
from thegent.lsp.headless_manager import LSP_SERVERS


def list_all_lsp_servers() -> dict[str, dict[str, any]]:
    """List all available LSP servers with installation status.

    Returns:
        Dict mapping language to server info with 'installed' status
    """
    servers = {}
    for language, config in LSP_SERVERS.items():
        command = config["command"]
        install_info = LSP_INSTALL_COMMANDS.get(language, {})
        check_cmd = install_info.get("check", command)

        servers[language] = {
            "command": command,
            "installed": check_command_available(check_cmd),
            "description": install_info.get("description", f"{language} LSP"),
            "install": config.get("install", "N/A"),
        }

    return servers
