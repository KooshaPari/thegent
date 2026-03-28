# tag_router API Reference

> **Source**: `src/thegent/utils/routing_impl/tag_router.py`

GW-58: Tag-based routing — route free_tier vs paid_tier to different deployments.

# @trace FR-AROUTE-058

---

## TagRoute

A tag-based routing rule.

A route matches when ALL of its tags are present in the request's tags.
Higher priority wins when multiple routes match.

---

## TagRouter

Routes requests based on tag matching.

Maintains a list of TagRoute instances and resolves a target model/deployment
based on which routes' tags are all present in the request's tags.

### Methods

#### TagRouter.__init__

```python
__init__(self: Any)
```

---

#### TagRouter.register

```python
register(self: Any, route: TagRoute)
```

Register a TagRoute with this router.

**Parameters**:

- `route`: The TagRoute to register.

---

#### TagRouter.resolve

```python
resolve(self: Any, request_tags: list[str])
```

Return the target of the highest-priority matching route.

A route matches if ALL of its tags are present in request_tags.
When multiple routes match, the one with the highest priority wins.
Ties are broken by registration order (first registered wins).

**Parameters**:

- `request_tags`: List of string tags present on the request.

**Returns**: The target model/deployment string, or None if no route matches.

---

---

## extract_request_tags

```python
extract_request_tags(body: dict)
```

Extract routing tags from a request body.

Reads the "tg_tags" field which must be a list of strings.

**Parameters**:

- `body`: The raw request body dict.

**Returns**: List of string tags, or empty list if not present.

---

## register

```python
register(self: Any, route: TagRoute)
```

Register a TagRoute with this router.

**Parameters**:

- `route`: The TagRoute to register.

---

## resolve

```python
resolve(self: Any, request_tags: list[str])
```

Return the target of the highest-priority matching route.

A route matches if ALL of its tags are present in request_tags.
When multiple routes match, the one with the highest priority wins.
Ties are broken by registration order (first registered wins).

**Parameters**:

- `request_tags`: List of string tags present on the request.

**Returns**: The target model/deployment string, or None if no route matches.

---

