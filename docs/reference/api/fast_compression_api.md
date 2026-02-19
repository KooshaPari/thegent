# fast_compression API Reference

> **Source**: `src/thegent/infra/fast_compression.py`

Fast compression/decompression with optimized backends.

This module provides optimized compression utilities:
- brotli for better compression ratios (if available)
- zstandard (zstd) for fast compression (if available)
- Standard gzip/zlib fallback

Performance improvements:
- brotli: Better compression ratios than gzip
- zstd: Faster compression/decompression
- Optimized for common use cases

---

## FastCompression

High-performance compression with automatic backend selection.

### Methods

#### FastCompression.compress

Compress data using fastest available method.

Args:
    data: Data to compress
    method: Compression method ("auto", "gzip", "brotli", "zstd")
    level: Compression level (1-9, higher = better compression)

Returns:
    Tuple of (compressed_data, method_used)

Performance:
    - zstd: Fastest compression/decompression
    - brotli: Best compression ratios
    - gzip: Standard fallback

```python
compress(data, method, level)
```

#### FastCompression.decompress

Decompress data, auto-detecting method if not specified.

Args:
    data: Compressed data
    method: Compression method (None = auto-detect)

Returns:
    Decompressed data

Performance:
    - Auto-detection tries fastest methods first
    - zstd: Fastest decompression
    - brotli: Fast decompression
    - gzip: Standard fallback

```python
decompress(data, method)
```

---

## compress

Compress data using fastest available method.

Args:
    data: Data to compress
    method: Compression method ("auto", "gzip", "brotli", "zstd")
    level: Compression level (1-9, higher = better compression)

Returns:
    Tuple of (compressed_data, method_used)

Performance:
    - zstd: Fastest compression/decompression
    - brotli: Best compression ratios
    - gzip: Standard fallback

```python
compress(data, method, level)
```

---

## decompress

Decompress data, auto-detecting method if not specified.

Args:
    data: Compressed data
    method: Compression method (None = auto-detect)

Returns:
    Decompressed data

Performance:
    - Auto-detection tries fastest methods first
    - zstd: Fastest decompression
    - brotli: Fast decompression
    - gzip: Standard fallback

```python
decompress(data, method)
```

---

