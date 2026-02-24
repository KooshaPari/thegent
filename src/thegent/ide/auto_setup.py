"""Auto-setup and auto-configuration for IDE integrations."""

import logging
import shutil
from pathlib import Path
from typing import Any

from thegent.lsp.jetbrains_cli import JetBrainsCLI

logger = logging.getLogger(__name__)

_GHOSTTY_BLOCK_BEGIN = "# >>> thegent managed: ghostty shell integration >>>"
_GHOSTTY_BLOCK_END = "# <<< thegent managed: ghostty shell integration <<<"
_GHOSTTY_BLOCK_BODY = """# Ghostty shell integration
if [[ "$TERM_PROGRAM" == "Ghostty" ]] || command -v ghostty >/dev/null 2>&1; then
    export GHOSTTY_SHELL_INTEGRATION=1
fi
"""


def _render_ghostty_managed_block() -> str:
    return f"{_GHOSTTY_BLOCK_BEGIN}\n{_GHOSTTY_BLOCK_BODY}{_GHOSTTY_BLOCK_END}\n"


def _upsert_managed_block(content: str, *, begin_marker: str, end_marker: str, replacement_block: str) -> str:
    start = content.find(begin_marker)
    if start == -1:
        base = content.rstrip("\n")
        if base:
            return f"{base}\n\n{replacement_block}"
        return replacement_block

    end = content.find(end_marker, start)
    if end == -1:
        raise ValueError(f"Managed block begin marker found without matching end marker: {begin_marker}")

    end_idx = end + len(end_marker)
    if end_idx < len(content) and content[end_idx] == "\n":
        end_idx += 1
    return f"{content[:start]}{replacement_block}{content[end_idx:]}"


def auto_setup_jetbrains_integration(auto_install: bool = True) -> dict[str, Any]:
    """Auto-setup JetBrains integration (detect IDE, verify CLI access, auto-install if needed).

    Args:
        auto_install: Automatically install IntelliJ IDEA if not found

    Returns:
        Dict with setup status and details
    """
    import platform

    cli = JetBrainsCLI()
    if cli.ide_path:
        logger.info(f"✅ JetBrains IDE detected: {cli.ide_path}")
        return {
            "success": True,
            "ide_path": str(cli.ide_path),
            "message": f"JetBrains IDE detected at {cli.ide_path}",
        }

    # Try to install if requested
    if auto_install:
        system = platform.system().lower()
        logger.info("Attempting to install IntelliJ IDEA...")

        try:
            if system == "darwin":
                # Install via Homebrew
                result = shim_run(
                    ["brew", "install", "--cask", "intellij-idea"],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    check=False,
                )
                if result.returncode == 0:
                    logger.info("✅ IntelliJ IDEA installed successfully")
                    # Re-check after installation
                    cli = JetBrainsCLI()
                    if cli.ide_path:
                        return {
                            "success": True,
                            "ide_path": str(cli.ide_path),
                            "message": "IntelliJ IDEA installed and detected",
                        }
                else:
                    logger.error(f"Installation failed: {result.stderr}")
            elif system == "linux":
                logger.warning("Linux installation not automated - please install manually")
            else:
                logger.warning(f"Unsupported platform: {system}")
        except Exception as e:
            logger.error(f"Failed to install IntelliJ IDEA: {e}")

    return {
        "success": False,
        "message": "JetBrains IDE not found",
        "instructions": [
            "Install IntelliJ IDEA:",
            "  macOS: brew install --cask intellij-idea",
            "  Linux: Download from https://www.jetbrains.com/idea/",
            "  Or use JetBrains Toolbox: https://www.jetbrains.com/toolbox/",
        ],
    }


def auto_setup_serena_jetbrains_plugin(auto_install: bool = True) -> dict[str, Any]:
    """Auto-detect and configure Serena JetBrains plugin.

    Args:
        auto_install: Attempt to install plugin if not detected

    Returns:
        Dict with setup status and instructions if needed
    """
    from thegent.config import ThegentSettings
    from thegent.lsp.serena_integration import detect_serena_backend

    settings = ThegentSettings()
    backend = detect_serena_backend()

    if backend == "jetbrains":
        return {
            "success": True,
            "backend": "jetbrains",
            "port": settings.serena_jetbrains_port,
            "message": "Serena JetBrains plugin detected and configured",
        }

    # Check if JetBrains IDE is available
    cli = JetBrainsCLI()
    if not cli.ide_path:
        return {
            "success": False,
            "backend": "lsp",
            "message": "JetBrains IDE not found - install IDE first",
            "instructions": [
                "1. Install IntelliJ IDEA: brew install --cask intellij-idea",
                "2. Then install Serena plugin",
            ],
        }

    # Try to install plugin if requested
    if auto_install:
        logger.info("Attempting to install Serena JetBrains plugin...")
        # Note: Plugin installation typically requires IDE to be running
        # We can provide instructions or use IDE's plugin manager CLI if available
        logger.warning("Serena plugin installation requires manual steps:")
        logger.info("1. Open IntelliJ IDEA")
        logger.info("2. Go to Settings > Plugins")
        logger.info("3. Search for 'Serena' and install")
        logger.info("4. Restart IDE")
        logger.info("5. Plugin will start MCP server automatically")

    return {
        "success": False,
        "backend": "lsp",
        "message": "Serena JetBrains plugin not detected",
        "instructions": [
            "1. Install plugin: https://plugins.jetbrains.com/plugin/28946/serena",
            '   Or in IDE: Settings > Plugins > Search "Serena" > Install',
            "2. Enable plugin in JetBrains IDE",
            "3. Restart IDE - plugin will start MCP server automatically",
            "4. Verify: thegent lsp serena-backend",
            "5. Plugin MCP server runs on port (default: 8765)",
        ],
    }


def auto_setup_ghostty_shell_integration(auto_configure: bool = True) -> dict[str, Any]:
    """Auto-setup Ghostty shell integration.

    Args:
        auto_configure: Automatically add shell integration if Ghostty is found

    Returns:
        Dict with setup status
    """
    import os

    ghostty_resources = os.environ.get("GHOSTTY_RESOURCES_DIR")
    if ghostty_resources:
        integration_script = Path(ghostty_resources) / "shell-integration" / "zsh" / "ghostty-integration"
        if integration_script.exists():
            return {
                "success": True,
                "message": "Ghostty shell integration detected",
                "resources_dir": ghostty_resources,
            }
        return {
            "success": False,
            "message": "Ghostty resources dir set but integration script not found",
            "resources_dir": ghostty_resources,
        }

    # Check if Ghostty is installed
    ghostty_path = shutil.which("ghostty")
    if not ghostty_path:
        return {
            "success": False,
            "message": "Ghostty not found in PATH",
            "instructions": ["Install Ghostty from https://ghostty.org/"],
        }

    # Auto-configure if requested
    shell_rc = Path.home() / ".zshrc"
    shell_integration_added = False

    if auto_configure and shell_rc.exists():
        try:
            content = shell_rc.read_text()
            desired_block = _render_ghostty_managed_block()
            updated = _upsert_managed_block(
                content,
                begin_marker=_GHOSTTY_BLOCK_BEGIN,
                end_marker=_GHOSTTY_BLOCK_END,
                replacement_block=desired_block,
            )
            if updated != content:
                shell_rc.write_text(updated)
                shell_integration_added = True
                logger.info("Updated managed Ghostty shell integration block in ~/.zshrc")
            else:
                return {
                    "success": True,
                    "message": "Ghostty shell integration already configured",
                }
        except Exception as e:
            logger.warning(f"Failed to auto-configure Ghostty: {e}")

    if shell_integration_added:
        return {
            "success": True,
            "message": "Ghostty shell integration auto-configured",
        }

    return {
        "success": False,
        "message": "Ghostty shell integration not configured",
        "instructions": [
            "Add to ~/.zshrc:",
            'if [ -n "${GHOSTTY_RESOURCES_DIR}" ]; then',
            '    source "${GHOSTTY_RESOURCES_DIR}/shell-integration/zsh/ghostty-integration"',
            "fi",
        ],
    }


def auto_setup_all(auto_configure: bool = True, auto_install: bool = True) -> dict[str, Any]:
    """Auto-setup all IDE integrations.

    Args:
        auto_configure: Automatically configure integrations when possible
        auto_install: Automatically install missing components (IDE, plugins)

    Returns:
        Dict with setup status for each integration
    """
    results = {
        "jetbrains": auto_setup_jetbrains_integration(auto_install=auto_install),
        "serena_jetbrains": auto_setup_serena_jetbrains_plugin(auto_install=auto_install),
        "ghostty": auto_setup_ghostty_shell_integration(auto_configure=auto_configure),
    }

    return results
