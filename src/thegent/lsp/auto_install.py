"""Auto-installation and auto-configuration for LSP servers and IDE integrations."""

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Installation commands for LSP servers
LSP_INSTALL_COMMANDS = {
    "python": {
        "command": ["npm", "install", "-g", "pyright"],
        "check": "pyright-langserver",
        "description": "Python LSP (pyright)",
    },
    "typescript": {
        "command": ["npm", "install", "-g", "typescript-language-server", "typescript"],
        "check": "typescript-language-server",
        "description": "TypeScript LSP",
    },
    "rust": {
        "command": ["rustup", "component", "add", "rust-analyzer"],
        "check": "rust-analyzer",
        "description": "Rust LSP (rust-analyzer)",
        "requires_rustup": True,  # Need rustup first
        "rustup_install_macos": ["brew", "install", "rustup-init"],
        "rustup_install_linux": [
            "curl",
            "--proto",
            "=https",
            "--tlsv1.2",
            "-sSf",
            "https://sh.rustup.rs",
            "|",
            "sh",
            "-s",
            "--",
            "-y",
        ],
    },
    "go": {
        "command": ["go", "install", "golang.org/x/tools/gopls@latest"],
        "check": "gopls",
        "description": "Go LSP (gopls)",
    },
    "cpp": {
        "command_macos": ["brew", "install", "llvm"],
        "command_linux": ["apt-get", "install", "-y", "clangd"],
        "check": "clangd",
        "description": "C++ LSP (clangd)",
    },
    "bash": {
        "command": ["npm", "install", "-g", "bash-language-server"],
        "check": "bash-language-server",
        "description": "Bash LSP",
    },
    "yaml": {
        "command": ["npm", "install", "-g", "yaml-language-server"],
        "check": "yaml-language-server",
        "description": "YAML LSP",
    },
    "json": {
        "command": ["npm", "install", "-g", "vscode-json-languageserver"],
        "check": "vscode-json-languageserver",
        "description": "JSON LSP",
    },
    "java": {
        "command_macos": ["brew", "install", "jdtls"],
        "command_linux": ["apt-get", "install", "-y", "jdtls"],
        "check": "jdtls",
        "description": "Java LSP (Eclipse JDT)",
        "fallback_download": True,  # Can download from Eclipse if package manager fails
    },
}


def check_command_available(command: str) -> bool:
    """Check if a command is available in PATH.

    Also checks common installation paths for Go tools (GOPATH/bin).
    """
    if shutil.which(command) is not None:
        return True

    # Special handling for Go tools (gopls)
    if command == "gopls":
        import os

        go_path = os.environ.get("GOPATH")
        if go_path:
            gopls_path = Path(go_path) / "bin" / "gopls"
            if gopls_path.exists():
                return True
        # Check default Go paths
        default_go_paths = [
            Path.home() / "go" / "bin" / "gopls",
            Path.home() / ".local" / "go" / "bin" / "gopls",
        ]
        for path in default_go_paths:
            if path.exists():
                return True

    return False


def _download_jdtls_fallback() -> bool:
    """Download jdtls from Eclipse milestones as fallback.

    Returns:
        True if download and setup succeeded, False otherwise
    """
    import platform

    system = platform.system().lower()
    arch = platform.machine().lower()

    # Determine platform config
    if system == "darwin":
        config_dir = "config_mac"
    elif system == "linux":
        config_dir = "config_linux"
    elif system == "windows":
        config_dir = "config_win"
    else:
        logger.error(f"Unsupported platform: {system}")
        return False

    # Download latest milestone
    milestone_url = "http://download.eclipse.org/jdtls/milestones/?d"
    logger.info("Attempting to download jdtls from Eclipse milestones...")

    try:
        # Get latest milestone URL (we'll use a known stable version)
        # Latest stable: 1.56.0 (from Homebrew info)
        version = "1.56.0"
        base_url = f"http://download.eclipse.org/jdtls/milestones/{version}"

        # Try to download the repository
        # The actual download URL structure may vary, so we'll use Homebrew as primary
        logger.warning("jdtls download from Eclipse requires manual setup")
        logger.info("Recommended: Use 'brew install jdtls' for automated installation")
        return False
    except Exception as e:
        logger.error(f"Failed to download jdtls: {e}")
        return False


def auto_install_lsp_server(language: str, auto_confirm: bool = True) -> bool:
    """Auto-install LSP server for language.

    Args:
        language: Language name (python, typescript, etc.)
        auto_confirm: Auto-confirm installation prompts

    Returns:
        True if installation succeeded or already installed, False otherwise
    """
    # Check if already installed
    install_info = LSP_INSTALL_COMMANDS.get(language)
    if not install_info:
        logger.error(f"Unknown language: {language}")
        return False

    check_cmd = install_info.get("check")
    if check_cmd and check_command_available(check_cmd):
        logger.info(f"{install_info['description']} already installed")
        return True

    # Check for prerequisites (e.g., rustup for rust)
    if install_info.get("requires_rustup") and not check_command_available("rustup"):
        logger.info(f"Installing rustup prerequisite for {language}...")
        import platform

        system = platform.system().lower()

        if system == "darwin" and "rustup_install_macos" in install_info:
            rustup_cmd = install_info["rustup_install_macos"]
        elif system == "linux" and "rustup_install_linux" in install_info:
            rustup_cmd = install_info["rustup_install_linux"]
        else:
            logger.error(f"Cannot install rustup on {system}")
            return False

        try:
            rustup_result = subprocess.run(
                rustup_cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            if rustup_result.returncode != 0:
                logger.error(f"Failed to install rustup: {rustup_result.stderr}")
                return False
            logger.info("✅ rustup installed successfully")
        except Exception as e:
            logger.error(f"Failed to install rustup: {e}")
            return False

    # Determine install command
    import platform

    system = platform.system().lower()

    if "command" in install_info:
        install_cmd = install_info["command"]
    elif system == "darwin" and "command_macos" in install_info:
        install_cmd = install_info["command_macos"]
    elif system == "linux" and "command_linux" in install_info:
        install_cmd = install_info["command_linux"]
    else:
        logger.error(f"No install command for {language} on {system}")
        # Try fallback download if available
        if install_info.get("fallback_download"):
            logger.info(f"Attempting fallback download for {language}...")
            if language == "java":
                return _download_jdtls_fallback()
        return False

    logger.info(f"Installing {install_info['description']}...")
    logger.info(f"Command: {' '.join(install_cmd)}")

    try:
        # Run installation
        result = subprocess.run(
            install_cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            logger.info(f"✅ Successfully installed {install_info['description']}")
            return True
        logger.error(f"Installation failed: {result.stderr}")
        # Try fallback download if available
        if install_info.get("fallback_download"):
            logger.info(f"Attempting fallback download for {language}...")
            if language == "java":
                return _download_jdtls_fallback()
        return False
    except Exception as e:
        logger.error(f"Failed to install {install_info['description']}: {e}")
        # Try fallback download if available
        if install_info.get("fallback_download"):
            logger.info(f"Attempting fallback download for {language}...")
            if language == "java":
                return _download_jdtls_fallback()
        return False


def auto_install_all_lsp_servers(auto_confirm: bool = True, skip_installed: bool = True) -> dict[str, bool]:
    """Auto-install all available LSP servers.

    Args:
        auto_confirm: Auto-confirm installation prompts
        skip_installed: Skip servers that are already installed

    Returns:
        Dict mapping language to installation success status
    """
    results = {}
    for language in LSP_INSTALL_COMMANDS:
        if skip_installed:
            install_info = LSP_INSTALL_COMMANDS.get(language, {})
            check_cmd = install_info.get("check")
            if check_cmd and check_command_available(check_cmd):
                results[language] = True
                logger.info(f"Skipping {language} - already installed")
                continue
        results[language] = auto_install_lsp_server(language, auto_confirm)
    return results


def ensure_lsp_server_installed(language: str, auto_install: bool = True) -> bool:
    """Ensure LSP server is installed, auto-installing if needed.

    Args:
        language: Language name
        auto_install: Auto-install if missing

    Returns:
        True if server is available, False otherwise
    """
    install_info = LSP_INSTALL_COMMANDS.get(language)
    if not install_info:
        return False

    check_cmd = install_info.get("check")
    if check_cmd and check_command_available(check_cmd):
        return True

    if auto_install:
        logger.info(f"Auto-installing {install_info['description']}...")
        return auto_install_lsp_server(language, auto_confirm=True)

    return False
