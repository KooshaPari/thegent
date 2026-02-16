from collections.abc import Callable

def lifespan(fn: Callable) -> Callable:
    # passthrough decorator used in tests and stub runtime
    return fn
