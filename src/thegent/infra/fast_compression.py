"""Fast compression/decompression with optimized backends.

This module provides optimized compression utilities:
- brotli for better compression ratios (if available)
- zstandard (zstd) for fast compression (if available)
- Standard gzip/zlib fallback

Performance improvements:
- brotli: Better compression ratios than gzip
- zstd: Faster compression/decompression
- Optimized for common use cases
"""

import gzip

try:
    import brotli

    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

try:
    import zstandard as zstd

    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False


class FastCompression:
    """High-performance compression with automatic backend selection."""

    @staticmethod
    def compress(data: bytes, method: str = "auto", level: int = 6) -> tuple[bytes, str]:
        """Compress data using fastest available method.

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
        """
        if method == "auto":
            # Auto-select best available
            if ZSTD_AVAILABLE:
                method = "zstd"
            elif BROTLI_AVAILABLE:
                method = "brotli"
            else:
                method = "gzip"

        if method == "zstd" and ZSTD_AVAILABLE:
            cctx = zstd.ZstdCompressor(level=level)
            return cctx.compress(data), "zstd"
        if method == "brotli" and BROTLI_AVAILABLE:
            return brotli.compress(data, quality=level), "brotli"
        # gzip fallback
        return gzip.compress(data, compresslevel=level), "gzip"

    @staticmethod
    def decompress(data: bytes, method: str | None = None) -> bytes:
        """Decompress data, auto-detecting method if not specified.

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
        """
        if method is None:
            # Auto-detect by trying methods
            # Check magic bytes
            if data.startswith(b"\x28\xb5\x2f\xfd"):  # zstd magic
                method = "zstd"
            elif data.startswith(b"\x1f\x8b"):  # gzip magic
                method = "gzip"
            elif data.startswith(b"\xce\xb2\xcf\x81"):  # brotli magic (approximate)
                method = "brotli"
            else:
                # Try zstd first (fastest), then brotli, then gzip
                for try_method in ["zstd", "brotli", "gzip"]:
                    try:
                        return FastCompression.decompress(data, try_method)
                    except Exception:
                        continue
                raise ValueError("Could not decompress data (unknown format)")

        if method == "zstd" and ZSTD_AVAILABLE:
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(data)
        if method == "brotli" and BROTLI_AVAILABLE:
            return brotli.decompress(data)
        if method == "gzip":
            return gzip.decompress(data)
        raise ValueError(f"Unsupported compression method: {method}")


# Convenience functions
def compress(data: bytes, method: str = "auto", level: int = 6) -> tuple[bytes, str]:
    """Compress data using fastest available method."""
    return FastCompression.compress(data, method, level)


def decompress(data: bytes, method: str | None = None) -> bytes:
    """Decompress data, auto-detecting method if not specified."""
    return FastCompression.decompress(data, method)
