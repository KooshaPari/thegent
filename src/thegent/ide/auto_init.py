"""Auto-initialization hooks for IDE integrations."""

import logging

from thegent.config import ThegentSettings

logger = logging.getLogger(__name__)


def auto_init_on_startup() -> None:
    """Auto-initialize IDE integrations on thegent startup.

    This runs automatically when thegent starts to ensure all integrations
    are configured and ready to use.
    """
    settings = ThegentSettings()

    # Only auto-init if enabled
    if not settings.ide_integration_enabled:
        return

    logger.info("Auto-initializing IDE integrations...")

    # Auto-setup JetBrains integration
    try:
        from thegent.ide.auto_setup import auto_setup_jetbrains_integration

        auto_setup_jetbrains_integration()
    except Exception as e:
        logger.debug(f"JetBrains auto-setup failed: {e}")

    # Auto-detect Serena backend
    try:
        from thegent.lsp.serena_integration import detect_serena_backend

        backend = detect_serena_backend()
        logger.info(f"Serena backend detected: {backend}")
    except Exception as e:
        logger.debug(f"Serena backend detection failed: {e}")

    # Auto-setup Ghostty if enabled
    if settings.ghostty_enabled:
        try:
            from thegent.ide.auto_setup import auto_setup_ghostty_shell_integration

            result = auto_setup_ghostty_shell_integration()
            if not result["success"]:
                logger.debug(f"Ghostty shell integration not configured: {result.get('message')}")
        except Exception as e:
            logger.debug(f"Ghostty auto-setup failed: {e}")


def ensure_lsp_servers_ready(languages: list[str] | None = None) -> None:
    """Ensure LSP servers are installed and ready for specified languages.

    Args:
        languages: List of languages to ensure (None = all common languages)
    """
    if languages is None:
        languages = ["python", "typescript", "rust", "go"]

    for language in languages:
        _ensure_server(language)


def _ensure_server(language: str) -> None:
    """Helper to ensure a single LSP server is installed."""
    from thegent.lsp.auto_install import ensure_lsp_server_installed

    try:
        ensure_lsp_server_installed(language, auto_install=True)
    except Exception as e:
        logger.debug(f"Failed to ensure LSP server for {language}: {e}")
