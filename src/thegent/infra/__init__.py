"""Infrastructure modules for runtime resource management."""

from thegent.infra.process_registry import ProcessHandle, ProcessRegistry, get_registry
from thegent.infra.resource_limits import ResourceLimits, get_resource_limits
from thegent.infra.resource_monitor import ResourceMonitor, ResourceStats, get_resource_monitor
from thegent.infra.runtime_init import (
    get_resource_stats,
    initialize_runtime_infrastructure,
    is_initialized,
)
from thegent.infra.subprocess_manager import SubprocessManager, get_subprocess_manager

# Fast parsers and watchers (optional, with fallbacks)
try:
    from thegent.infra.fast_yaml_parser import (
        FastYAMLParser,
        get_yaml_parser,
        yaml_dump,
        yaml_dumps,
        yaml_load,
        yaml_loads,
    )

    _FAST_YAML_AVAILABLE = True
except ImportError:
    _FAST_YAML_AVAILABLE = False

try:
    from thegent.infra.fast_toml_parser import (
        FastTOMLParser,
        get_toml_parser,
        toml_dump,
        toml_dumps,
        toml_load,
        toml_loads,
    )

    _FAST_TOML_AVAILABLE = True
except ImportError:
    _FAST_TOML_AVAILABLE = False

try:
    from thegent.infra.fast_file_watcher import (
        FastFileWatcher,
        watch_files,
    )

    _FAST_WATCHER_AVAILABLE = True
except ImportError:
    _FAST_WATCHER_AVAILABLE = False

from thegent.infra.fast_process_monitor import (
    FastProcessMonitor,
    ProcessInfo,
    get_fast_monitor,
)

# Fast JSON schema validator
try:
    from thegent.infra.fast_json_schema import (
        FastJSONSchemaValidator,
        get_schema_validator,
        is_valid_json_schema,
        validate_json_schema,
    )

    _FAST_JSONSCHEMA_AVAILABLE = True
except ImportError:
    _FAST_JSONSCHEMA_AVAILABLE = False

# Fast file operations
try:
    from thegent.infra.fast_file_ops import (
        FastFileOps,
        copy_file,
        copy_tree,
        ensure_directory,
        get_path_size,
        move_file,
        remove_path,
    )

    _FAST_FILEOPS_AVAILABLE = True
except ImportError:
    _FAST_FILEOPS_AVAILABLE = False

# Fast HTTP client (optional)
try:
    from thegent.infra.fast_http_client import (
        FastHTTPClient,
        get_http_client,
        http_get,
        http_post,
        http_request,
    )

    _FAST_HTTP_AVAILABLE = True
except ImportError:
    _FAST_HTTP_AVAILABLE = False

__all__ = [
    # Fast process monitor
    "FastProcessMonitor",
    # Existing exports
    "ProcessHandle",
    "ProcessInfo",
    "ProcessRegistry",
    "ResourceLimits",
    "ResourceMonitor",
    "ResourceStats",
    "SubprocessManager",
    "get_fast_monitor",
    "get_registry",
    "get_resource_limits",
    "get_resource_monitor",
    "get_resource_stats",
    "get_subprocess_manager",
    "initialize_runtime_infrastructure",
    "is_initialized",
]

# Conditionally add fast parser exports
if _FAST_YAML_AVAILABLE:
    __all__.extend(
        [
            "FastYAMLParser",
            "get_yaml_parser",
            "yaml_dump",
            "yaml_dumps",
            "yaml_load",
            "yaml_loads",
        ]
    )

if _FAST_TOML_AVAILABLE:
    __all__.extend(
        [
            "FastTOMLParser",
            "get_toml_parser",
            "toml_dump",
            "toml_dumps",
            "toml_load",
            "toml_loads",
        ]
    )

if _FAST_WATCHER_AVAILABLE:
    __all__.extend(
        [
            "FastFileWatcher",
            "watch_files",
        ]
    )

if _FAST_JSONSCHEMA_AVAILABLE:
    __all__.extend(
        [
            "FastJSONSchemaValidator",
            "get_schema_validator",
            "is_valid_json_schema",
            "validate_json_schema",
        ]
    )

if _FAST_FILEOPS_AVAILABLE:
    __all__.extend(
        [
            "FastFileOps",
            "copy_file",
            "copy_tree",
            "ensure_directory",
            "get_path_size",
            "move_file",
            "remove_path",
        ]
    )

if _FAST_HTTP_AVAILABLE:
    __all__.extend(
        [
            "FastHTTPClient",
            "get_http_client",
            "http_get",
            "http_post",
            "http_request",
        ]
    )

# Fast subprocess execution
try:
    from thegent.infra.fast_subprocess import (
        FastSubprocess,
        run_subprocess_async,
        run_subprocess_optimized,
        run_subprocesses_concurrent,
    )

    _FAST_SUBPROCESS_AVAILABLE = True
except ImportError:
    _FAST_SUBPROCESS_AVAILABLE = False

# Multi-tier caching
try:
    from thegent.infra.fast_cache import (
        MultiTierCache,
        get_cache,
    )

    _FAST_CACHE_AVAILABLE = True
except ImportError:
    _FAST_CACHE_AVAILABLE = False

# Fast string operations
try:
    from thegent.infra.fast_string_ops import (
        FastStringOps,
        fuzzy_match,
        fuzzy_ratio,
        regex_findall,
        regex_search,
    )

    _FAST_STRING_AVAILABLE = True
except ImportError:
    _FAST_STRING_AVAILABLE = False

# Fast UUID generation
try:
    from thegent.infra.fast_uuid import (
        FastUUID,
        uuid1,
        uuid1_str,
        uuid4,
        uuid4_str,
    )

    _FAST_UUID_AVAILABLE = True
except ImportError:
    _FAST_UUID_AVAILABLE = False

if _FAST_SUBPROCESS_AVAILABLE:
    __all__.extend(
        [
            "FastSubprocess",
            "run_subprocess_async",
            "run_subprocess_optimized",
            "run_subprocesses_concurrent",
        ]
    )

if _FAST_CACHE_AVAILABLE:
    __all__.extend(
        [
            "MultiTierCache",
            "get_cache",
        ]
    )

if _FAST_STRING_AVAILABLE:
    __all__.extend(
        [
            "FastStringOps",
            "fuzzy_match",
            "fuzzy_ratio",
            "regex_findall",
            "regex_search",
        ]
    )

if _FAST_UUID_AVAILABLE:
    __all__.extend(
        [
            "FastUUID",
            "uuid1",
            "uuid1_str",
            "uuid4",
            "uuid4_str",
        ]
    )

# Fast WebSocket client
try:
    from thegent.infra.fast_websocket import (
        FastWebSocket,
        websocket_connect_async,
        websocket_connect_sync,
    )

    _FAST_WEBSOCKET_AVAILABLE = True
except ImportError:
    _FAST_WEBSOCKET_AVAILABLE = False

# Fast compression
try:
    from thegent.infra.fast_compression import (
        FastCompression,
        compress,
        decompress,
    )

    _FAST_COMPRESSION_AVAILABLE = True
except ImportError:
    _FAST_COMPRESSION_AVAILABLE = False

# Fast path operations
try:
    from thegent.infra.fast_path_ops import (
        FastPathOps,
        path_exists,
        path_is_dir,
        path_is_file,
        path_join,
        path_normalize,
    )

    _FAST_PATH_OPS_AVAILABLE = True
except ImportError:
    _FAST_PATH_OPS_AVAILABLE = False

if _FAST_WEBSOCKET_AVAILABLE:
    __all__.extend(
        [
            "FastWebSocket",
            "websocket_connect_async",
            "websocket_connect_sync",
        ]
    )

if _FAST_COMPRESSION_AVAILABLE:
    __all__.extend(
        [
            "FastCompression",
            "compress",
            "decompress",
        ]
    )

if _FAST_PATH_OPS_AVAILABLE:
    __all__.extend(
        [
            "FastPathOps",
            "path_exists",
            "path_is_dir",
            "path_is_file",
            "path_join",
            "path_normalize",
        ]
    )
