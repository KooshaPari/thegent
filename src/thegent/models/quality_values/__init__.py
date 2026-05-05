"""Stub module."""


class ModelQuality:
    """Model quality value."""

    def __init__(self, quality: float = 1.0) -> None:
        self.quality = quality


def get_model_quality_for_role(role: str) -> ModelQuality:
    """Get model quality for a given role."""
    return ModelQuality(quality=1.0)


__all__ = ["ModelQuality", "get_model_quality_for_role", "get_model_quality_index"]


def get_model_quality_index(model_id: str) -> float:
    """Get the quality index for a model."""
    return 1.0
