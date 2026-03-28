# semantic_cache API Reference

> **Source**: `src/thegent/utils/routing_impl/semantic_cache.py`

GW-23: Semantic cache for LLM gateway using embedding similarity.

Caches LLM responses and retrieves them by semantic similarity of the
request prompt. Uses cosine similarity with a configurable threshold
(default: 0.95).

When the embedding model is unavailable, semantic cache degrades to
disabled (never hits) — the caller falls through to a live LLM call.

# @trace FR-CACHE-023

---

## EmbeddingProvider

Protocol for embedding providers.

**Inherits from**: `Protocol`

### Methods

#### EmbeddingProvider.embed

```python
embed(self: Any, text: str)
```

Return the embedding vector for text.

---

#### EmbeddingProvider.is_available

```python
is_available(self: Any)
```

Return True if this provider can produce embeddings.

---

---

## NumpyEmbeddingProvider

Deterministic embedding provider using numpy random unit vectors.

Seeds the RNG from the hash of the input text, producing a consistent
unit vector per unique string. Useful in tests when sentence_transformers
is not installed.

### Methods

#### NumpyEmbeddingProvider.__init__

```python
__init__(self: Any, dim: int)
```

---

#### NumpyEmbeddingProvider.embed

```python
embed(self: Any, text: str)
```

Return a deterministic unit vector for text.

---

#### NumpyEmbeddingProvider.is_available

```python
is_available(self: Any)
```

Return True if numpy is importable.

---

---

## SemanticCache

In-memory semantic cache keyed by namespace.

Stores LLM responses indexed by their prompt embedding. Lookup
computes cosine similarity and returns a hit when the nearest
neighbor exceeds the configured threshold.

Thread-safe via a single threading.Lock.

### Methods

#### SemanticCache.__init__

```python
__init__(self: Any, config: Any, provider: Any)
```

---

#### SemanticCache.clear

```python
clear(self: Any, namespace: Any)
```

Clear all entries from the given namespace (or all namespaces).

Returns the count of entries removed.

---

#### SemanticCache.delete_expired

```python
delete_expired(self: Any, namespace: Any)
```

Remove expired entries from the given namespace (or all namespaces).

Returns the count of entries removed.

---

#### SemanticCache.get

```python
get(self: Any, text: str, namespace: str)
```

Look up a semantically similar cached response.

Returns None on miss, on expired-only matches, or when the
embedding provider is unavailable.

---

#### SemanticCache.set

```python
set(self: Any, text: str, response: dict[(str, Any)], namespace: str)
```

Store a response in the semantic cache.

No-op when the embedding provider is unavailable.
Evicts the oldest entries when max_entries is exceeded.

---

---

## SemanticCacheConfig

Configuration for SemanticCache.

---

## SemanticCacheEntry

A single entry in the semantic cache.

### Methods

#### SemanticCacheEntry.is_expired

```python
is_expired(self: Any)
```

Return True if this entry has passed its TTL.

---

---

## SentenceTransformerProvider

Embedding provider backed by sentence-transformers.

Lazy-loads the sentence_transformers package. If the package is not
installed, is_available() returns False and embed() raises ImportError.

### Methods

#### SentenceTransformerProvider.__init__

```python
__init__(self: Any, model_name: str)
```

---

#### SentenceTransformerProvider.embed

```python
embed(self: Any, text: str)
```

Return the embedding vector for text as a list of floats.

---

#### SentenceTransformerProvider.is_available

```python
is_available(self: Any)
```

Return True if sentence_transformers is importable.

---

---

## clear

```python
clear(self: Any, namespace: Any)
```

Clear all entries from the given namespace (or all namespaces).

Returns the count of entries removed.

---

## cosine_similarity

```python
cosine_similarity(a: list[float], b: list[float])
```

Compute cosine similarity between two embedding vectors.

---

## delete_expired

```python
delete_expired(self: Any, namespace: Any)
```

Remove expired entries from the given namespace (or all namespaces).

Returns the count of entries removed.

---

## embed

```python
embed(self: Any, text: str)
```

Return a deterministic unit vector for text.

---

## extract_prompt_text

```python
extract_prompt_text(messages: list[dict])
```

Extract plain text from messages list for embedding.

---

## get

```python
get(self: Any, text: str, namespace: str)
```

Look up a semantically similar cached response.

Returns None on miss, on expired-only matches, or when the
embedding provider is unavailable.

---

## get_semantic_cache

```python
get_semantic_cache(config: Any)
```

Return the process-global SemanticCache singleton, creating it if needed.

---

## is_available

```python
is_available(self: Any)
```

Return True if numpy is importable.

---

## is_expired

```python
is_expired(self: Any)
```

Return True if this entry has passed its TTL.

---

## reset_semantic_cache

Reset the process-global singleton (for testing).

---

## semantic_cache_get

```python
semantic_cache_get(text: str, namespace: str)
```

Look up a semantically similar cached response. Returns None on miss.

---

## semantic_cache_set

```python
semantic_cache_set(text: str, response: dict[(str, Any)], namespace: str)
```

Store a response in the semantic cache.

---

## set

```python
set(self: Any, text: str, response: dict[(str, Any)], namespace: str)
```

Store a response in the semantic cache.

No-op when the embedding provider is unavailable.
Evicts the oldest entries when max_entries is exceeded.

---

