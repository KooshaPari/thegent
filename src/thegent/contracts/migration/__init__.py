"""Stub module."""


class MigrationController:
    """Controller for contract migrations."""

    def __init__(self) -> None:
        self.migrations: list[dict[str, object]] = []

    def run(self) -> None:
        """Run pending migrations."""

    def evaluate_version(self, contract_name: str, version: str) -> dict[str, object]:
        """Evaluate a contract version.

        Returns a compatibility status dict for the requested contract/version.
        """
        return {"compatible": True, "allowed": True, "contract": contract_name, "version": version}


__all__ = ["MigrationController"]
