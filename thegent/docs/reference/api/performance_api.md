# performance API Reference

> **Source**: `src/thegent/docgen/performance.py`

Performance optimizations for documentation.

---

## PerformanceOptimizer

Performance optimization utilities.

### Methods

#### PerformanceOptimizer.generate_image_html

```python
generate_image_html(self: Any, src: str, alt: str, lazy: bool)
```

Generate optimized image HTML.

**Parameters**:

- `src`: Image source
- `alt`: Alt text
- `lazy`: Enable lazy loading

**Returns**: HTML string

---

#### PerformanceOptimizer.optimize_code_splitting

```python
optimize_code_splitting(self: Any, entry_points: list[str])
```

Optimize code splitting for faster loads.

**Parameters**:

- `entry_points`: List of entry point files

**Returns**: Optimization configuration

---

#### PerformanceOptimizer.optimize_images

```python
optimize_images(self: Any, image_path: Path, output_format: str)
```

Optimize images (WebP/AVIF, lazy loading).

**Parameters**:

- `image_path`: Path to image
- `output_format`: Output format (webp, avif)

**Returns**: Optimization configuration

---

---

## generate_image_html

```python
generate_image_html(self: Any, src: str, alt: str, lazy: bool)
```

Generate optimized image HTML.

**Parameters**:

- `src`: Image source
- `alt`: Alt text
- `lazy`: Enable lazy loading

**Returns**: HTML string

---

## optimize_code_splitting

```python
optimize_code_splitting(self: Any, entry_points: list[str])
```

Optimize code splitting for faster loads.

**Parameters**:

- `entry_points`: List of entry point files

**Returns**: Optimization configuration

---

## optimize_images

```python
optimize_images(self: Any, image_path: Path, output_format: str)
```

Optimize images (WebP/AVIF, lazy loading).

**Parameters**:

- `image_path`: Path to image
- `output_format`: Output format (webp, avif)

**Returns**: Optimization configuration

---
