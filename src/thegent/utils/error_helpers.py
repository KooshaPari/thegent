"""Actionable error messages with suggested fixes."""

from typing import Any


class ActionableError(Exception):
    """Error with actionable suggestions for fixing it."""

    def __init__(
        self,
        message: str,
        suggestion: str | None = None,
        docs_url: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
        self.docs_url = docs_url
        self.context = context or {}

    def __str__(self) -> str:
        output = [f"❌ Error: {self.message}"]
        if self.suggestion:
            output.append(f"💡 Suggestion: {self.suggestion}")
        if self.docs_url:
            output.append(f"📖 Docs: {self.docs_url}")
        return "\n".join(output)


def handle_error_actionable(
    error: Exception,
    custom_message: str | None = None,
    suggestion: str | None = None,
    docs_url: str | None = None,
) -> ActionableError:
    """Wrap an error in an ActionableError.

    Args:
        error: Original exception
        custom_message: Optional custom message
        suggestion: Optional suggestion
        docs_url: Optional docs URL

    Returns:
        ActionableError instance
    """
    message = custom_message or str(error)
    return ActionableError(
        message=message,
        suggestion=suggestion,
        docs_url=docs_url,
        context={"original_error": str(error), "error_type": type(error).__name__},
    )
