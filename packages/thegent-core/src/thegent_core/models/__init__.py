"""Model catalog and distributed routing."""

from thegent_core.models.catalog import (
    CatalogView,
    ModelCatalog,
    ResolvedRoute,
    Route,
    filter_models_for_provider,
    normalize_model_id,
    normalize_route_policy,
    resolve_route,
    resolve_route_contract,
    route_contract,
)
from thegent_core.models.quality_values import invalidate_quality_index_cache
from thegent_core.models.scrapers import (
    SCRAPER_REGISTRY,
    ModelScraper,
    get_scraped_catalog,
    invalidate_models_cache,
    scrape_all,
)
from thegent_core.models.speed_values import invalidate_speed_index_cache
from thegent_core.models.task_io import TaskError, TaskInput, TaskOutput, TaskSpec

__all__ = [
    "SCRAPER_REGISTRY",
    "CatalogView",
    "ModelCatalog",
    "ModelScraper",
    "ResolvedRoute",
    "Route",
    "TaskError",
    "TaskInput",
    "TaskOutput",
    "TaskSpec",
    "filter_models_for_provider",
    "get_scraped_catalog",
    "invalidate_models_cache",
    "invalidate_quality_index_cache",
    "invalidate_speed_index_cache",
    "normalize_model_id",
    "normalize_route_policy",
    "resolve_route",
    "resolve_route_contract",
    "route_contract",
    "scrape_all",
]
