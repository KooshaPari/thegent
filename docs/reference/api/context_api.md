# context API Reference

> **Source**: `src/thegent/orchestration/context.py`

Context management and semantic compression for thegent (WP-5001).

---

## ContextCompressor

WP-5001: Manages L1-L4 memory tiers and triggers semantic compression.

### Methods

#### ContextCompressor.__init__

```python
__init__(self, session_dir, threshold_pct)
```

#### ContextCompressor.generate_continuity_packet

Create a compressed essence of progress for handoffs.

```python
generate_continuity_packet(self, intent, decisions, risks, context_files)
```

#### ContextCompressor.prune_context

WP-5001: Priority-based pruning of conversation history.

```python
prune_context(self, conversation)
```

#### ContextCompressor.should_compress

True if current token usage exceeds threshold.

```python
should_compress(self, current_tokens, max_tokens)
```

---

## generate_continuity_packet

Create a compressed essence of progress for handoffs.

```python
generate_continuity_packet(self, intent, decisions, risks, context_files)
```

---

## prune_context

WP-5001: Priority-based pruning of conversation history.

```python
prune_context(self, conversation)
```

---

## should_compress

True if current token usage exceeds threshold.

```python
should_compress(self, current_tokens, max_tokens)
```

---

