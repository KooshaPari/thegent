# beartype — O(1) runtime type checking for Python
# Add to conftest.py or project __init__.py to enable project-wide
# Install: pip install beartype
#
# Usage: All function signatures with type hints are validated at runtime
# with O(1) time complexity (constant-time, not linear in collection size).
#
# Configuration options:
#   beartype_this_package() — enable for entire package
#   @beartype — decorate individual functions
#   BeartypeConf(violation_type=...) — customize violation behavior

from beartype.claw import beartype_this_package

# Enable beartype for the entire package at import time
# Place this in your package's __init__.py
beartype_this_package()

# Alternative: per-function decoration
# from beartype import beartype
# @beartype
# def my_function(x: int, y: str) -> bool:
#     ...

# Alternative: custom configuration
# from beartype import BeartypeConf
# beartype_this_package(conf=BeartypeConf(
#     violation_type=UserWarning,  # Warn instead of raise
# ))
