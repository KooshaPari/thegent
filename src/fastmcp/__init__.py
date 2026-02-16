from typing import Any, Callable

class DummyApp:
    pass

class FastMCP:
    def __init__(self, name: str, lifespan: Any = None) -> None:
        self.name = name
        self.lifespan = lifespan

    def resource(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        def deco(f):
            return f

        return deco

    def prompt(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        def deco(f):
            return f

        return deco

    def tool(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        def deco(f):
            return f

        return deco

    def custom_route(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        def deco(f):
            return f

        return deco

    def add_middleware(self, middleware: Any) -> None:
        return None

    def add_transform(self, transform: Any) -> None:
        return None

    def http_app(self, **kwargs) -> DummyApp:
        return DummyApp()
