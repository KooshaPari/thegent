# Utils - Reusable Helper Library

This directory contains reusable helper libraries and utilities for common patterns used throughout thegent.

## Available Helpers

### Core Helpers (`helpers.py`)
- `batch_file_operations` - Batch file operations with error handling
- `normalize_path` - Cross-platform path normalization
- `safe_read_file` - Safe file reading with encoding handling
- `safe_write_file` - Safe file writing with atomic writes

### Reusable Patterns (`reusable_helpers.py`)
The `ReusableHelpers` class provides common patterns:

| Method | Description |
|--------|-------------|
| `error_handler` | Decorator that logs exceptions and returns safe defaults |
| `safe_execute` | Execute function with error handling, returns (result, error) |
| `retry_on_failure` | Retry function on failure using tenacity |
| `ensure_directory` | Ensure directory exists (mkdir -p) |
| `find_files` | Find files matching pattern recursively |
| `read_json_safe` | Safely read JSON files |
| `read_file_efficiency` | Read file with offset/limit support |
| `write_json_safe` | Safely write JSON files |

### Path Utilities (`path_utils.py`)
- Cross-platform path operations
- Path normalization and validation

### Batch Operations (`batch_file_ops.py`, `batch_operations.py`, `batch_ops.py`)
- Efficient batch file operations
- 3-5x fewer tool calls optimization

### Shell Utilities (`shell.py`, `shell_config.py`)
- Shell command execution helpers
- Shell configuration management

### Terminal (`holdpty.py`, `terminal_capture.py`)
- PTY holding for interactive processes
- Terminal capture utilities

### Workstream (`workstream_ops.py`, `workstream.py`)
- Workstream operation helpers

### Other Utilities
- `linting_accelerator.py` - Linting acceleration
- `xml_repair.py` - XML repair utilities
- `cache.py` - Caching utilities
- `borrow.py` - Borrowing patterns

## Usage

```python
from thegent.utils import batch_file_operations, normalize_path, safe_read_file
from thegent.utils.reusable_helpers import ReusableHelpers

# Using ReusableHelpers
helpers = ReusableHelpers()
result, error = helpers.safe_execute(my_function, arg1, arg2)

# Using retry
result = ReusableHelpers.retry_on_failure(
    flaky_function,
    max_retries=3,
    delay=1.0,
)

# Find files
files = ReusableHelpers.find_files(Path("./src"), "*.py")
```

## Design Principles

- **Library-first**: Use existing libraries (tenacity, pathlib) over custom implementations
- **Fail fast**: Functions should fail clearly, not silently
- **Type hints**: All functions have type annotations
- **Error handling**: Consistent error handling patterns
