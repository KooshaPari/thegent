"""Claude config isolation helpers for clode."""

import contextlib
import shutil
from pathlib import Path


def ensure_claude_config_isolation(config_dir: Path) -> None:
    """Ensure isolated config dir links to global state and onboarding/session data."""
    global_dir = Path.home() / ".claude"
    global_json = Path.home() / ".claude.json"

    target_json = config_dir / ".claude.json"
    if global_json.exists() and not target_json.exists():
        with contextlib.suppress(OSError):
            target_json.symlink_to(global_json)

    if global_dir.exists():
        target_settings = config_dir / "settings.json"
        if not target_settings.exists():
            global_settings = global_dir / "settings.json"
            if global_settings.exists():
                try:
                    import json

                    data = json.loads(global_settings.read_text())
                    target_settings.write_text(json.dumps(data, indent=2))
                except Exception:
                    pass

        for item in global_dir.iterdir():
            if item.name == "settings.json":
                continue
            target = config_dir / item.name
            if target.exists() and not target.is_symlink():
                try:
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                except OSError:
                    pass

            if not target.exists():
                with contextlib.suppress(OSError):
                    target.symlink_to(item, target_is_directory=item.is_dir())
