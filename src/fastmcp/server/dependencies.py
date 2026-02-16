from collections.abc import Callable
from ..server.context import Context

def current_context() -> Context:
    # simple callable returning a default context for dependency injection
    return Context()

# Backwards compatibility
CurrentContext = current_context
