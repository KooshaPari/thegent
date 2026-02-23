"""Common constants for thegent.

Centralized constants to avoid duplication across the codebase.
"""

from pathlib import Path

# Project paths
PROJECT_ROOT = Path.home() / ".thegent"
CACHE_DIR = PROJECT_ROOT / "cache"
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
CONFIG_DIR = PROJECT_ROOT / "config"

# Timeouts (seconds)
DEFAULT_TIMEOUT = 30
LONG_TIMEOUT = 300
SHORT_TIMEOUT = 5

# Retry settings
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000

# API limits
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
MAX_RESPONSE_SIZE = 50 * 1024 * 1024  # 50MB

# Cache settings
DEFAULT_CACHE_TTL = 3600  # 1 hour
MAX_CACHE_SIZE = 1000

# User agent
USER_AGENT = "thegent/1.0"

# HTTP methods
HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_DELETE = "DELETE"
HTTP_PATCH = "PATCH"

# Status codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_TIMEOUT = 2
EXIT_CANCELLED = 3

# Log levels
LOG_DEBUG = "DEBUG"
LOG_INFO = "INFO"
LOG_WARNING = "WARNING"
LOG_ERROR = "ERROR"
LOG_CRITICAL = "CRITICAL"

# Date formats
ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# File extensions
EXT_PY = ".py"
EXT_JSON = ".json"
EXT_YAML = ".yaml"
EXT_YML = ".yml"
EXT_TOML = ".toml"
EXT_MD = ".md"

# Environment names
ENV_DEV = "development"
ENV_STAGING = "staging"
ENV_PROD = "production"
ENV_TEST = "test"
