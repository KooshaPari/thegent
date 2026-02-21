"""Automated link checking for documentation."""

import asyncio
import logging
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from thegent.utils.helpers import normalize_path, safe_read_file

logger = logging.getLogger(__name__)


class DocLinkChecker:
    """Check links in documentation files."""

    def __init__(
        self,
        base_dir: Path | None = None,
        ignore_patterns: list[str] | None = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize link checker.

        Args:
            base_dir: Base directory for documentation
            ignore_patterns: List of regex patterns to ignore
            timeout: HTTP request timeout
        """
        self.base_dir = base_dir or Path.cwd()
        self.ignore_patterns = [re.compile(p) for p in (ignore_patterns or [])]
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)

    async def __aenter__(self) -> "DocLinkChecker":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.client.aclose()

    def _is_ignored(self, url: str) -> bool:
        """Check if a URL should be ignored."""
        return any(pattern.search(url) for pattern in self.ignore_patterns)

    def find_links(self, file_path: Path) -> list[dict[str, Any]]:
        """Find all links in a markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            List of link dictionaries
        """
        content = safe_read_file(file_path)
        if not content:
            return []

        links = []
        lines = content.splitlines()

        # Markdown link patterns
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        for i, line in enumerate(lines, 1):
            for match in re.finditer(link_pattern, line):
                url = match.group(2)
                if not self._is_ignored(url):
                    links.append(
                        {
                            "url": url,
                            "line": i,
                            "text": match.group(1),
                            "file": str(file_path),
                        }
                    )
        return links

    async def check_external_link(self, url: str) -> dict[str, Any]:
        """Check if an external link is valid.

        Args:
            url: External URL

        Returns:
            Check result
        """
        try:
            response = await self.client.head(url)
            # Some servers block HEAD, try GET if HEAD fails
            if response.status_code >= 400:
                response = await self.client.get(url)

            return {
                "url": url,
                "status_code": response.status_code,
                "valid": response.status_code < 400,
                "type": "external",
            }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "valid": False,
                "type": "external",
            }

    def check_internal_link(self, url: str, base_path: Path) -> dict[str, Any]:
        """Check if an internal link is valid.

        Args:
            url: Internal URL
            base_path: Path of the file containing the link

        Returns:
            Check result
        """
        parsed = urlparse(url)

        # Anchor links
        if url.startswith("#"):
            return {
                "url": url,
                "type": "anchor",
                "valid": True,  # Complex to verify without full HTML render
            }

        # Relative file links
        target_path = (base_path.parent / parsed.path).resolve()

        # If it points to a directory, check for index.md
        if target_path.is_dir():
            target_path = target_path / "index.md"

        exists = target_path.exists()
        return {
            "url": url,
            "path": str(target_path),
            "valid": exists,
            "type": "internal",
        }

    async def check_link(self, url: str, base_path: Path) -> dict[str, Any]:
        """Check a single link."""
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https"):
            return await self.check_external_link(url)
        return self.check_internal_link(url, base_path)

    async def check_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Check all links in a file."""
        links = self.find_links(file_path)
        results = []

        # Check links concurrently
        tasks = [self.check_link(link["url"], file_path) for link in links]
        check_results = await asyncio.gather(*tasks)

        for link, result in zip(links, check_results, strict=True):
            combined = {**link, **result}
            results.append(combined)

        return results

    async def check_directory(self, dir_path: Path, pattern: str = "**/*.md") -> dict[str, Any]:
        """Check all links in a directory."""
        dir_path = Path(dir_path)
        md_files = list(dir_path.glob(pattern))

        all_results = []
        for md_file in md_files:
            file_results = await self.check_file(md_file)
            all_results.extend(file_results)

        broken_links = [r for r in all_results if not r["valid"]]

        return {
            "total_links": len(all_results),
            "broken_links_count": len(broken_links),
            "broken_links": broken_links,
            "results": all_results,
        }
