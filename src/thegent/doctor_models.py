"""Shared models for doctor checks."""


class CheckResult:
    def __init__(self, name: str, category: str) -> None:
        self.name = name
        self.category = category
        self.status: str = "pending"  # ok, warn, fail
        self.severity: str = "info"  # info, warning, error, critical
        self.message: str = ""
        self.details: str | None = None
        self.fix_hint: str | None = None
