"""Resource access utilities for thegent."""

from pathlib import Path

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Fallback for Python < 3.9
    import importlib_resources as pkg_resources  # type: ignore


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to a resource file.

    In dev mode (THGENT_DEV=1 or running from git), looks in the project root.
    When installed, uses importlib.resources.
    """
    from thegent.utils import is_dev_mode

    if is_dev_mode():
        # In dev mode, resources are relative to the project root
        # .../src/thegent/resources.py -> project root is two levels up from src
        try:
            current_file = Path(__file__).resolve()
            if "src/thegent" in str(current_file):
                project_root = current_file.parents[2]
                path = project_root / relative_path
                if path.exists():
                    return path
        except Exception:
            pass

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
            except (ImportError, ModuleNotFoundError):
                pass

        # Default to main package
        with pkg_resources.path("thegent", relative_path) as p:
            return Path(p)
    except Exception:
        # Final fallback: assume it might be relative to current module
        return Path(__file__).parent / relative_path
