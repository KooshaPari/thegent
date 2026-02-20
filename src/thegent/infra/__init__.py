"""Infrastructure modules for thegent.

This package contains infrastructure utilities including:
- Runtime dispatcher for multi-runtime support
- Performance optimizations
- Error handling
- Progress indicators
- Configuration management
- Multi-runtime diagnostics
"""

from thegent.infra.enhanced_errors import (
    ConfigurationError,
    DependencyError,
    EnhancedError,
    NetworkError,
    RuntimeError,
    create_config_error,
    create_dependency_error,
    create_network_error,
    create_runtime_error,
    error_report,
    format_error_with_context,
)
from thegent.infra.fast_file_ops import (
    copy_file,
    copy_tree,
    move_file,
)
from thegent.infra.fast_file_ops import (
    ensure_directory as ensure_dir,
)
from thegent.infra.fast_file_ops import (
    get_path_size as get_file_size,
)
from thegent.infra.fast_file_ops import (
    remove_path as remove_file,
)
from thegent.infra.fast_subprocess import run_subprocess_optimized
from thegent.infra.fast_cache import MultiTierCache, get_cache
from thegent.infra.fast_yaml_parser import yaml_dump, yaml_load, yaml_loads
from thegent.infra.mojo_bridge import (
    MojoBridge,
    MojoNotAvailableError,
    MojoTask,
    check_mojo_status,
    get_bridge,
)
from thegent.infra.progress import (
    measure_time,
    print_section,
    print_status,
    print_step,
    progress_context,
    spinner_context,
)

__all__ = [
    # Mojo bridge
    "MojoBridge",
    "MojoNotAvailableError",
    "MojoTask",
    "check_mojo_status",
    "get_bridge",
    # Enhanced errors
    "EnhancedError",
    "ConfigurationError",
    "RuntimeError",
    "DependencyError",
    "NetworkError",
    "create_config_error",
    "create_runtime_error",
    "create_dependency_error",
    "create_network_error",
    "format_error_with_context",
    "error_report",
    # File operations
    "copy_file",
    "copy_tree",
    # Subprocess
    "run_subprocess_optimized",
    # Cache
    "MultiTierCache",
    "get_cache",
    # YAML
    "yaml_dump",
    "yaml_load",
    "yaml_loads",
    # Progress indicators
    "progress_context",
    "spinner_context",
    "print_status",
    "print_step",
    "print_section",
    "measure_time",
]
