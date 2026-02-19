# scrapers API Reference

> **Source**: `src/thegent/models/scrapers.py`

Model scrapers for dynamic discovery.

---

## ModelScraper

Protocol for provider-specific model scrapers (Phase 12). Returns model IDs.

**Inherits from**: `Protocol`

### Methods

---

## get_models_cache_path

Return path to models cache file (for invalidation).

---

## get_scraped_catalog

Get scraped by_provider. Uses cache if use_cache and not refresh.
Returns {provider: [model_id, ...]}.

```python
get_scraped_catalog(use_cache, refresh, settings)
```

---

## invalidate_models_cache

Delete models cache file. Returns True if file existed and was removed.

---

## scrape_all

Scrape all providers. Returns by_provider: {provider: [model_id, ...]}.
Filters blacklisted models; unparseable allowed. Per-provider fallback on adapter failure.
SA2: gemini, SA3: claude, SA4: cursor/copilot, SA5: proxy (antigravity/minimax/glm).

```python
scrape_all(settings)
```

---

## scrape_claude

Scrape claude models: try 'claude models list', else --help for --model aliases.

---

## scrape_copilot

Scrape copilot --help for --model choices.

---

## scrape_cursor

Scrape cursor agent --list-models.

---

## scrape_cursor_api

Scrape cursor-api (wisdgod) GET /v1/models.

```python
scrape_cursor_api(settings)
```

---

## scrape_gemini

Scrape gemini models: try 'gemini models list' or 'gemini list-models', else --help.

---

## scrape_minimax_from_proxy

MiniMax models from proxy (minimax: block in config). Fallback to static.

---

## scrape_proxy

Scrape proxy models. Returns {provider: [model_id, ...]} for antigravity, minimax, glm.
Maps proxy model IDs to thegent providers by prefix/heuristic.

```python
scrape_proxy(settings)
```

---

