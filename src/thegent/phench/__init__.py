"""Package: thegent.phench - re-exports from local phench implementation."""

from __future__ import annotations

from . import service
from . import models
from . import runner
from . import store

# Re-export everything from service, models, runner, store
from .service import *
from .models import *
from .runner import *
from .store import *

__all__: list[str] = [
    "add_module_to_target",
    "add_repo",
    "audit_shared_modules",
    "audit_shared_modules_across_repos",
    "bootstrap_target",
    "build_catalog",
    "build_module_manifest_payload",
    "build_project_execution_matrix",
    "build_scan_candidates",
    "create_target_snapshot",
    "discover_repos",
    "get_env_profile",
    "import_repos",
    "init_target",
    "list_modules",
    "list_target_snapshots",
    "list_targets",
    "load_module_manifest",
    "load_module_repos",
    "load_target_lock",
    "lock_target",
    "materialize_module_candidate_manifest",
    "materialize_scan_candidate_manifest",
    "materialize_target",
    "run_env_doctor_for_target",
    "run_target",
    "scan_shared_modules_across_repos",
    "set_env_profile",
    "set_repo_ref",
    "show_target_snapshot",
    "sync_project_modules_from_repos",
    "sync_target",
    "target_status",
    "target_timeline",
]
