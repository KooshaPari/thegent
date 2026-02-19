"""Performance optimizations for documentation."""

from pathlib import Path
from typing import Any


class PerformanceOptimizer:
    """Performance optimization utilities."""

    def optimize_code_splitting(self, entry_points: list[str]) -> dict[str, Any]:
        """Optimize code splitting for faster loads.
        
        Args:
            entry_points: List of entry point files
            
        Returns:
            Optimization configuration
        """
        return {
            "chunks": "all",
            "maxAsyncRequests": 5,
            "maxInitialRequests": 3,
            "cacheGroups": {
                "vendor": {
                    "test": "/node_modules/",
                    "priority": 10,
                },
                "common": {
                    "minChunks": 2,
                    "priority": 5,
                },
            },
        }

    def optimize_images(self, image_path: Path, output_format: str = "webp") -> dict[str, Any]:
        """Optimize images (WebP/AVIF, lazy loading).
        
        Args:
            image_path: Path to image
            output_format: Output format (webp, avif)
            
        Returns:
            Optimization configuration
        """
        return {
            "format": output_format,
            "quality": 85,
            "lazy": True,
            "srcset": True,
            "sizes": "(max-width: 768px) 100vw, 50vw",
        }

    def generate_image_html(self, src: str, alt: str, lazy: bool = True) -> str:
        """Generate optimized image HTML.
        
        Args:
            src: Image source
            alt: Alt text
            lazy: Enable lazy loading
            
        Returns:
            HTML string
        """
        loading = 'loading="lazy"' if lazy else ""
        return f'<img src="{src}" alt="{alt}" {loading} />'
