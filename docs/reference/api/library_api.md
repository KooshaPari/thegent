# library API Reference

> **Source**: `src/thegent/prompts/library.py`

## PromptEntry

---

## PromptLibrary

Thread-safe in-memory versioned prompt store.

### Methods

#### PromptLibrary.__init__

```python
__init__(self: Any)
```

---

#### PromptLibrary.add

```python
add(self: Any, name: str, content: str)
```

Add or update a prompt. Returns the new PromptEntry with auto-assigned version.

---

#### PromptLibrary.delete

```python
delete(self: Any, name: str)
```

Remove all versions of a prompt. Returns True if existed.

---

#### PromptLibrary.get

```python
get(self: Any, name: str, version: Any)
```

Get prompt by name and optional version. Returns latest if version=None.

---

#### PromptLibrary.get_all_versions

```python
get_all_versions(self: Any, name: str)
```

Return all versions of a named prompt, oldest first.

---

#### PromptLibrary.list_names

```python
list_names(self: Any)
```

Return sorted list of all prompt names.

---

#### PromptLibrary.search

```python
search(self: Any, query: str)
```

Return latest version of all prompts whose name or content contains query (case-insensitive).

---

---

## add

```python
add(self: Any, name: str, content: str)
```

Add or update a prompt. Returns the new PromptEntry with auto-assigned version.

---

## delete

```python
delete(self: Any, name: str)
```

Remove all versions of a prompt. Returns True if existed.

---

## get

```python
get(self: Any, name: str, version: Any)
```

Get prompt by name and optional version. Returns latest if version=None.

---

## get_all_versions

```python
get_all_versions(self: Any, name: str)
```

Return all versions of a named prompt, oldest first.

---

## get_prompt_library

Return the module-level PromptLibrary singleton, creating it if needed.

---

## list_names

```python
list_names(self: Any)
```

Return sorted list of all prompt names.

---

## reset_prompt_library

Replace the singleton with a fresh PromptLibrary. Intended for tests.

---

## search

```python
search(self: Any, query: str)
```

Return latest version of all prompts whose name or content contains query (case-insensitive).

---

