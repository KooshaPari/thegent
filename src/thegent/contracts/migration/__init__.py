"""Stub module."""


class MigrationController:
    """Controller for contract migrations."""

    def __init__(self) -> None:
        self.migrations: list[dict[str, object]] = []

    def run(self) -> None:
        """Run pending migrations."""
        pass


__all__ = ["MigrationController"]
