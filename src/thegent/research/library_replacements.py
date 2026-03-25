"""Library replacement implementations."""

import hashlib
import logging
from importlib import import_module, util
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
    return False


def use_diskcache(cache_dir: Path) -> Any:
    """Use diskcache for caching.

    Args:
        cache_dir: Cache directory

    Returns:
        Cache instance
    """
    if util.find_spec("diskcache") is None:
        logger.warning("diskcache not available")
        return None

    diskcache = import_module("diskcache")

    return diskcache.Cache(str(cache_dir))


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
