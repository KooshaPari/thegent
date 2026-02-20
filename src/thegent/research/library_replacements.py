"""Library replacement implementations."""

import hashlib
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def replace_md5_with_sha256(data: bytes) -> str:
    """Replace MD5 with SHA256 for hashing.

    Args:
        data: Data to hash

    Returns:
        SHA256 hash hex string
    """
    return hashlib.sha256(data).hexdigest()


def check_tomlkit_available() -> bool:
    """Check if tomlkit is available.

    Returns:
        True if available
    """
    try:
        import tomlkit

        return True
    except ImportError:
        return False


def use_diskcache(cache_dir: Path) -> Any:
    """Use diskcache for caching.

    Args:
        cache_dir: Cache directory

    Returns:
        Cache instance
    """
    try:
        import diskcache

        return diskcache.Cache(str(cache_dir))
    except ImportError:
        logger.warning("diskcache not available")
        return None


def use_psutil_monitoring() -> dict[str, Any]:
    """Use psutil for resource monitoring.

    Returns:
        Resource metrics dictionary
    """
    try:
        import psutil

        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
        }
    except ImportError:
        logger.warning("psutil not available")
        return {}
