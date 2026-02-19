# scoring API Reference

> **Source**: `src/thegent/routing/scoring.py`

WP-Y8-rel: Provider scoring with learning.

---

## ProviderScorer

Scores providers based on historical performance and learning.

### Methods

#### ProviderScorer.__init__

```python
__init__(self, settings)
```

#### ProviderScorer.get_score

Get the current score for a provider (0.0 to 1.0).

```python
get_score(self, provider_id)
```

#### ProviderScorer.update_score

Update provider score based on a new result.

```python
update_score(self, provider_id, latency_s, success)
```

---

## get_score

Get the current score for a provider (0.0 to 1.0).

```python
get_score(self, provider_id)
```

---

## update_score

Update provider score based on a new result.

```python
update_score(self, provider_id, latency_s, success)
```

---

