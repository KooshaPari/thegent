"""Install package for thegent."""

from pathlib import Path

# Constants for install module
CLAUDE_MAPPING = {}
EXCLUDE_DIRS = set()
FACTORY_MAPPING = {}
ROOT_FILES = []


def create_symlink(*args, **kwargs):
    """Stub function for create_symlink."""


def get_home_dir(*args, **kwargs):
    """Stub function for get_home_dir."""
    return Path.home()


def get_source_dest_mapping(*args, **kwargs):
    """Stub function for get_source_dest_mapping."""
    return {}


def run_install(*args, **kwargs):
    """Stub function for run_install."""


def should_exclude(*args, **kwargs):
    """Stub function for should_exclude."""
    return False


def smart_copy_file(*args, **kwargs):
    """Stub function for smart_copy_file."""


def setup_hooks(*args, **kwargs):
    """Setup hooks for installation."""


def setup_harness(*args, **kwargs):
    """Setup harness for installation."""


def setup_skills(*args, **kwargs):
    """Setup skills for installation."""


def install_homebrew(*args, **kwargs):
    """Install Homebrew."""


def install_mise(*args, **kwargs):
    """Install Mise."""


class InstallManager:
    """Install manager stub."""

    def __init__(self, *args, **kwargs):
        pass


__all__ = [
    "setup_hooks",
    "setup_harness",
    "setup_skills",
    "install_homebrew",
    "install_mise",
    "run_install",
    "InstallManager",
    "CLAUDE_MAPPING",
    "EXCLUDE_DIRS",
    "FACTORY_MAPPING",
    "ROOT_FILES",
    "create_symlink",
    "get_home_dir",
    "get_source_dest_mapping",
    "should_exclude",
    "smart_copy_file",
]
