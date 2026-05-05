"""Stub module."""
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class TypeScriptAPIGenerator:
    """TypeScript API generator stub."""
    
    def generate(self, spec: dict[str, Any]) -> str:
        return "export interface Generated {}"


__all__ = ["TypeScriptAPIGenerator"]
