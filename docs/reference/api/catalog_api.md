# catalog API Reference

> **Source**: `src/thegent/models/catalog.py`

Model catalog and route resolution for distributed routing.

---

## CatalogView

View of the model catalog for discovery.

---

## ModelCatalog

Model catalog for route resolution. Merges static + scraped when use_scraped=True (Phase 7).

### Methods

#### ModelCatalog.routes_for

Return all routes that can serve the given model. Merges scraped data when use_scraped.

```python
routes_for(model_id, use_scraped)
```

#### ModelCatalog.to_catalog_view

Build CatalogView for discovery (by_provider, by_model). Uses scraped data when available.

```python
to_catalog_view(use_scraped)
```

#### ModelCatalog.to_contract_view

Return catalog with schema metadata and route details for structured consumers.

```python
to_contract_view(use_scraped, provider_filter, use_cache)
```

---

## ResolvedRoute

Resolved model routing decision with contract metadata.

---

## Route

A route to serve a model via a specific provider.

---

## filter_models_for_provider

Filter scraped models: remove blacklisted, keep unparseable (allow by default).

```python
filter_models_for_provider(provider, models)
```

---

## normalize_model_id

Normalize provider-agnostic model aliases to canonical IDs.

```python
normalize_model_id(model_id)
```

---

## normalize_route_policy

Validate and normalize routing policy. Raises ValueError on invalid policy.

```python
normalize_route_policy(policy)
```

---

## resolve_route

Resolve model to (provider, model_alias). Returns None if no route.

- provider_hint: Use this provider if it serves the model.
- policy: prefer_direct (default) | prefer_proxy | failover | round_robin | cheapest

```python
resolve_route(model_id, provider_hint, policy)
```

---

## resolve_route_contract

Resolve model and return contract-rich route metadata.

```python
resolve_route_contract(model_id, provider_hint, policy)
```

---

## route_contract

Return catalog contract metadata for auditing and compatibility checks.

---

## routes_for

Return all routes that can serve the given model. Merges scraped data when use_scraped.

```python
routes_for(model_id, use_scraped)
```

---

## to_catalog_view

Build CatalogView for discovery (by_provider, by_model). Uses scraped data when available.

```python
to_catalog_view(use_scraped)
```

---

## to_contract_view

Return catalog with schema metadata and route details for structured consumers.

```python
to_contract_view(use_scraped, provider_filter, use_cache)
```

---

