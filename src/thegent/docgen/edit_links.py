"""Generation of 'Edit on GitHub' links for documentation."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class EditLinkGenerator:
    """Generate 'Edit on GitHub' links for documentation files."""

    def __init__(
        self,
        repo_url: str,
        base_dir: Path,
        branch: str = "main",
        docs_subdir: str = "docs",
    ) -> None:
        """Initialize edit link generator.

        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/user/repo)
            base_dir: Root directory of the local repository
            branch: Default branch name
            docs_subdir: Subdirectory where docs are located
        """
        self.repo_url = repo_url.rstrip("/")
        self.base_dir = Path(base_dir).resolve()
        self.branch = branch
        self.docs_subdir = docs_subdir

    def get_edit_url(
        self,
        file_path: Path,
        line_number: int | None = None,
        branch: str | None = None,
    ) -> str:
        """Generate edit URL for a file.

        Args:
            file_path: Local path to the file
            line_number: Optional line number to link to
            branch: Optional branch override

        Returns:
            GitHub edit URL
        """
        file_path = Path(file_path).resolve()
        try:
            relative_path = file_path.relative_to(self.base_dir)
        except ValueError:
            logger.error(f"File {file_path} is not within base directory {self.base_dir}")
            return ""

        target_branch = branch or self.branch

        # GitHub edit URL format: {repo_url}/edit/{branch}/{path}
        url = f"{self.repo_url}/edit/{target_branch}/{relative_path}"

        if line_number:
            url = f"{url}#L{line_number}"

        return url

    def get_view_url(
        self,
        file_path: Path,
        line_number: int | None = None,
        branch: str | None = None,
    ) -> str:
        """Generate view URL for a file.

        Args:
            file_path: Local path to the file
            line_number: Optional line number
            branch: Optional branch override

        Returns:
            GitHub view URL
        """
        file_path = Path(file_path).resolve()
        try:
            relative_path = file_path.relative_to(self.base_dir)
        except ValueError:
            return ""

        target_branch = branch or self.branch
        url = f"{self.repo_url}/blob/{target_branch}/{relative_path}"

        if line_number:
            url = f"{url}#L{line_number}"

        return url

    def inject_edit_link(
        self,
        file_path: Path,
        label: str = "Edit this page on GitHub",
        position: str = "bottom",
    ) -> bool:
        """Inject an edit link into a markdown file.

        Args:
            file_path: Path to markdown file
            label: Link text
            position: 'top' or 'bottom'

        Returns:
            True if successful
        """
        url = self.get_edit_url(file_path)
        if not url:
            return False

        try:
            content = file_path.read_text()
            link_markdown = f"\n\n---\n\n[{label}]({url})\n"

            if position == "top":
                new_content = f"[{label}]({url})\n\n---\n\n" + content
            else:
                new_content = content.rstrip() + link_markdown

            file_path.write_text(new_content)
            return True
        except Exception as e:
            logger.error(f"Failed to inject edit link into {file_path}: {e}")
            return False
