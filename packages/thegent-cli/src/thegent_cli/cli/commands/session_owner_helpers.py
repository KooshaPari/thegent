"""Session owner/tag and scope path helpers extracted from CLI impl."""

from __future__ import annotations

import getpass
import os
from pathlib import Path

from thegent.config import ThegentSettings


def scope_key(owner: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_.") else "_" for c in owner)


def compose_owner_tag(user: str, cwd: Path, scope: str = "") -> str:
    """Build deterministic owner tags with optional scope expansion."""
    base_name = cwd.name
    normalized_scope = scope or ""
    normalized_scope = os.path.expandvars(normalized_scope)
    normalized_scope = normalized_scope.format(
        user=user,
        uid=os.getuid(),
        pid=os.getpid(),
        ppid=os.getppid(),
        cwd=base_name,
    ).strip()
    if normalized_scope:
        return f"{user}:{base_name}:{normalized_scope}"
    return f"{user}:{base_name}"


def default_owner_tag(cwd: Path | None = None, *, include_process_id: bool = False) -> str:
    base = (cwd or Path.cwd()).expanduser().resolve()
    settings = ThegentSettings()
    explicit = settings.owner_tag
    if explicit:
        return explicit
    scope = settings.owner_scope.strip()
    if include_process_id and not scope:
        scope = "{pid}"
    user = getpass.getuser()
    return compose_owner_tag(user=user, cwd=base, scope=scope)


def session_dir(settings: ThegentSettings, owner: str) -> Path:
    d = settings.session_dir.expanduser().resolve() / scope_key(owner)
    d.mkdir(parents=True, exist_ok=True)
    return d


def session_scope_dirs(base: Path, owner: str) -> list[Path]:
    """Return session scope directories for an owner key, including pid-scoped variants."""
    owner_key = scope_key(owner)
    scopes: list[Path] = []
    for scope_dir in sorted(base.glob(f"{owner_key}*")):
        if scope_dir.name == owner_key or scope_dir.name.startswith(f"{owner_key}_"):
            scopes.append(scope_dir)
    if owner == "":
        return []
    if not scopes:
        fallback = base / owner_key
        if fallback.exists():
            scopes = [fallback]
    return scopes
