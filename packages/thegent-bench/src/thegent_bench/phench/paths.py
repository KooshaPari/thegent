from __future__ import annotations

import os
import re
from pathlib import Path

_TARGET_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def phenotype_root() -> Path:
    configured = os.environ.get("THGENT_PHENOTYPE_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / "CodeProjects" / "Phenotype").resolve()


def projects_root() -> Path:
    return phenotype_root() / "projects"


def home_mirror_root() -> Path:
    configured = os.environ.get("THGENT_PHENCH_HOME_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path.home() / "phench"


def validate_target_name(target: str) -> str:
    candidate = target.strip()
    if not candidate:
        raise ValueError("target name cannot be empty")
    if "/" in candidate or "\\" in candidate or ".." in candidate:
        raise ValueError(f"invalid target name: {target}")
    if not _TARGET_NAME_RE.fullmatch(candidate):
        raise ValueError(f"invalid target name: {target}")
    return candidate


def target_root(target: str) -> Path:
    return projects_root() / validate_target_name(target)


def target_repos_root(target: str) -> Path:
    return target_root(target) / "repos"


def target_state_root(target: str) -> Path:
    return target_root(target) / ".phench"


def mirror_target_state_root(target: str) -> Path:
    return home_mirror_root() / target / ".phench"
