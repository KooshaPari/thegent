"""Hexagonal architecture domain layer for thegent.

This module contains pure domain entities and value objects with no I/O or side effects.
The domain layer is the innermost layer and should have no dependencies on adapters,
infrastructure, or external frameworks (except Pydantic for serialization).
"""
