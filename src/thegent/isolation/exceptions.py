"""Isolation-related exceptions."""


class IsolationError(Exception):
    """Base exception for isolation-related errors."""



class TenantAllocationError(IsolationError):
    """Raised when tenant allocation fails."""



class LeaseConflictError(IsolationError):
    """Raised when a lease conflict is detected."""



class ExecutionContextError(IsolationError):
    """Raised when execution in isolated context fails."""

