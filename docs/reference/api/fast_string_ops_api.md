# fast_string_ops API Reference

> **Source**: `src/thegent/infra/fast_string_ops.py`

Fast string operations with optimized backends.

This module provides optimized string operations:
- rapidfuzz for fuzzy matching (already installed!)
- regex for advanced regex patterns (already installed!)
- Optimized string operations

Performance improvements:
- rapidfuzz: 10-100x faster fuzzy matching
- regex: Faster complex regex patterns
- Optimized string operations

---

## FastStringOps

High-performance string operations with optimized backends.

### Methods

#### FastStringOps.fuzzy_match

Fuzzy string matching using rapidfuzz (10-100x faster).

Args:
    query: Query string
    choices: List of strings to match against
    limit: Maximum number of results
    score_cutoff: Minimum similarity score (0-100)

Returns:
    List of (match, score, index) tuples

Performance:
    - rapidfuzz: 10-100x faster than fuzzywuzzy
    - Uses optimized C++ implementation

```python
fuzzy_match(query, choices, limit, score_cutoff)
```

#### FastStringOps.fuzzy_ratio

Calculate fuzzy similarity ratio (0-100).

Args:
    str1: First string
    str2: Second string

Returns:
    Similarity ratio (0-100)

```python
fuzzy_ratio(str1, str2)
```

#### FastStringOps.regex_findall

Find all matches using regex library.

Args:
    pattern: Regex pattern
    text: Text to search
    **kwargs: Additional regex options

Returns:
    List of matches

```python
regex_findall(pattern, text)
```

#### FastStringOps.regex_search

Search using regex library (faster for complex patterns).

Args:
    pattern: Regex pattern
    text: Text to search
    **kwargs: Additional regex options

Returns:
    Match object or None

Performance:
    - regex library: Faster for complex patterns
    - Better Unicode support
    - More features than standard re

```python
regex_search(pattern, text)
```

---

## fuzzy_match

Fuzzy string matching using rapidfuzz (10-100x faster).

Args:
    query: Query string
    choices: List of strings to match against
    limit: Maximum number of results
    score_cutoff: Minimum similarity score (0-100)

Returns:
    List of (match, score, index) tuples

Performance:
    - rapidfuzz: 10-100x faster than fuzzywuzzy
    - Uses optimized C++ implementation

```python
fuzzy_match(query, choices, limit, score_cutoff)
```

---

## fuzzy_ratio

Calculate fuzzy similarity ratio (0-100).

Args:
    str1: First string
    str2: Second string

Returns:
    Similarity ratio (0-100)

```python
fuzzy_ratio(str1, str2)
```

---

## regex_findall

Find all matches using regex library.

Args:
    pattern: Regex pattern
    text: Text to search
    **kwargs: Additional regex options

Returns:
    List of matches

```python
regex_findall(pattern, text)
```

---

## regex_search

Search using regex library (faster for complex patterns).

Args:
    pattern: Regex pattern
    text: Text to search
    **kwargs: Additional regex options

Returns:
    Match object or None

Performance:
    - regex library: Faster for complex patterns
    - Better Unicode support
    - More features than standard re

```python
regex_search(pattern, text)
```

---

