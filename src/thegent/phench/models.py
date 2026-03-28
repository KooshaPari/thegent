from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


TargetMode = Literal["repo", "stack"]


@dataclass(slots=True)
class RepoSelection:
    repo_id: str
    repo_path: str
    selected_ref: str | None = None
    module_name: str | None = None
    selected_runner: str | None = None
    selected_command: str | None = None
    selected_env_profile: str | None = None
    source_worktree_path: str | None = None
    resolved_sha: str | None = None
    preferred_runner: str | None = None
    preferred_command: str | None = None
    preferred_ref: str | None = None

    def __post_init__(self) -> None:
        if self.selected_ref is None:
            self.selected_ref = self.preferred_ref
        if not self.selected_ref:
            raise ValueError("selected_ref cannot be empty")

        if self.selected_runner is None and self.preferred_runner is not None:
            self.selected_runner = self.preferred_runner
        elif self.selected_runner is not None and self.preferred_runner is None:
            self.preferred_runner = self.selected_runner

        if self.selected_command is None and self.preferred_command is not None:
            self.selected_command = self.preferred_command
        elif self.selected_command is not None and self.preferred_command is None:
            self.preferred_command = self.selected_command

        if self.preferred_ref is None:
            self.preferred_ref = self.selected_ref


@dataclass(slots=True)
class TargetLock:
    schema_version: int
    target_name: str
    mode: TargetMode
    repos: list[RepoSelection] = field(default_factory=list)
    lock_hash: str = ""
    created_at_utc: str = ""


@dataclass(slots=True)
class RuntimeRepo:
    repo_id: str
    checkout_path: str
    resolved_sha: str
    head_branch: str | None = None


@dataclass(slots=True)
class RuntimeState:
    target_name: str
    materialized_root: str
    repo_materializations: list[RuntimeRepo] = field(default_factory=list)
    materialized_at_utc: str = ""


@dataclass(slots=True)
class RunnerCommand:
    runner: str
    name: str
    description: str
    source_file: str


@dataclass(slots=True)
class RunnerCatalog:
    target_name: str
    runners_detected: list[str] = field(default_factory=list)
    commands: list[RunnerCommand] = field(default_factory=list)
    default_command: str = ""


@dataclass(slots=True)
class EnvDoctorReport:
    target_name: str
    doctor_status: Literal["pass", "fail"]
    missing_requirements: list[str] = field(default_factory=list)
    resolved_versions: dict[str, str] = field(default_factory=dict)
    detected_files: list[str] = field(default_factory=list)
