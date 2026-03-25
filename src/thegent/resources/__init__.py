"""Resource monitoring and coordination utilities for thegent."""

from thegent.resources.disk import DiskIoStats, DiskMonitor, DiskQueueSample
from thegent.resources.network import (
    BandwidthSample,
    NetworkMonitor,
    NetworkStats,
)

__all__ = [
    "BandwidthSample",
    "DiskIoStats",
    "DiskMonitor",
    "DiskQueueSample",
    "NetworkMonitor",
    "NetworkStats",
]

from thegent.resources.distributed import (
    DistributedResourceCoordinator,
    ResourceCoordinationError,
    ResourceLease,
)

__all__ += [
    "DistributedResourceCoordinator",
    "ResourceCoordinationError",
    "ResourceLease",
]

from thegent.resources.gpu import GpuInfo, GpuMonitor, GpuMonitorError

__all__ += [
    "GpuInfo",
    "GpuMonitor",
    "GpuMonitorError",
]

from pathlib import Path

import importlib.resources as pkg_resources
import logging

_LOG = logging.getLogger(__name__)


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to a resource file.

    In dev mode (THGENT_DEV=1 or running from git), looks in the project root.
    When installed, uses importlib.resources.
    """
    # Break circular dependency with thegent.utils by implementing dev check locally
    is_dev = False
    try:
        from thegent.config import ThegentSettings

        if ThegentSettings().dev:
            is_dev = True
        else:
            # Check if we are in a git repo and running from source
            current_file = Path(__file__).resolve()
            if "src/thegent" in str(current_file):
                project_root = current_file.parents[3]
                if (project_root / ".git").exists():
                    is_dev = True
    except (ImportError, ModuleNotFoundError) as exc:
        _LOG.warning(
            "resource_dev_mode_detection_failed",
            extra={
                "failure_type": "config_import_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc)[:180],
            },
        )
    except (OSError, RuntimeError, ValueError, IndexError) as exc:
        _LOG.warning(
            "resource_dev_mode_detection_failed",
            extra={
                "failure_type": "path_inspection_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc)[:180],
            },
        )

    if is_dev:
        # In dev mode, resources are relative to the project root.
        # .../src/thegent/resources/__init__.py -> project root is parents[3].
        try:
            current_file = Path(__file__).resolve()
            if "src/thegent" in str(current_file):
                project_root = current_file.parents[3]
                path = project_root / relative_path
                if path.exists():
                    return path
        except (OSError, RuntimeError, ValueError, IndexError) as exc:
            _LOG.warning(
                "resource_dev_mode_path_resolution_failed",
                extra={
                    "failure_type": "dev_path_error",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc)[:180],
                },
            )

    # When installed as a package
    try:
        # Split path into parts: e.g. "contracts/dag.json" -> ("contracts", "dag.json")
        parts = relative_path.split("/")
        if len(parts) > 1:
            package = "thegent." + ".".join(parts[:-1])
            resource = parts[-1]

            # Check if this subpackage exists, if not fallback to main package
            try:
                with pkg_resources.path(package, resource) as p:
                    return Path(p)
            except ImportError, ModuleNotFoundError:
                pass

        # Default to main package
        with pkg_resources.path("thegent", relative_path) as p:
            return Path(p)
    except FileNotFoundError, ImportError, ModuleNotFoundError, OSError, RuntimeError, ValueError:
        # Final fallback: assume it might be relative to current module
        return Path(__file__).parent.parent / relative_path


__all__ += ["get_resource_path"]
