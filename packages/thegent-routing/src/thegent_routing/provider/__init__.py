"""Provider and model management.

This package contains:
- provider/crud.py: Provider CRUD operations
- provider/models.py: Model management
- provider/credentials.py: API key management
- provider/discovery.py: Model discovery and scoring

Import from here:
    from thegent.provider import list_providers, list_models
    from thegent.provider.crud import get_provider
"""

from .crud import (
    add_provider,
    delete_provider,
    get_provider,
    list_providers,
    update_provider,
    validate_provider,
)
from .credentials import add_api_key, list_credentials, remove_api_key
from .discovery import (
    calculate_composite_score,
    discover_models,
    get_model_modalities,
    list_models_with_scores,
)
from .models import (
    add_common_alias,
    add_model_alias,
    add_model_index,
    add_model_modality,
    fuzzy_search_models,
    list_model_indices,
    list_models,
    remove_common_alias,
    remove_model_alias,
    remove_model_index,
    search_by_modalities,
    search_models_by_capability,
)

__all__ = [
    # Credentials
    "add_api_key",
    # Models
    "add_common_alias",
    "add_model_alias",
    "add_model_index",
    "add_model_modality",
    # CRUD
    "add_provider",
    # Discovery
    "calculate_composite_score",
    "delete_provider",
    "discover_models",
    "fuzzy_search_models",
    "get_model_modalities",
    "get_provider",
    "list_credentials",
    "list_model_indices",
    "list_models",
    "list_models_with_scores",
    "list_providers",
    "remove_api_key",
    "remove_common_alias",
    "remove_model_alias",
    "remove_model_index",
    "search_by_modalities",
    "search_models_by_capability",
    "update_provider",
    "validate_provider",
]
