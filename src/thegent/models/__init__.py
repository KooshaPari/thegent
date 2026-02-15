"""Model catalog and distributed routing."""

from thegent.models.catalog import (
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
from thegent.models.scrapers import (
    SCRAPER_REGISTRY,
    ModelScraper,
    get_scraped_catalog,
    invalidate_models_cache,
    scrape_all,
)

__all__ = [
    "SCRAPER_REGISTRY",
    "CatalogView",
    "ModelCatalog",
    "ModelScraper",
    "ResolvedRoute",
    "Route",
    "filter_models_for_provider",
    "get_scraped_catalog",
    "invalidate_models_cache",
    "normalize_model_id",
    "normalize_route_policy",
    "resolve_route",
    "resolve_route_contract",
    "route_contract",
    "scrape_all",
]
