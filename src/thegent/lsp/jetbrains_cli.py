"""JetBrains IDE CLI Integration."""

import shutil
import subprocess
from pathlib import Path
from typing import Any


class JetBrainsCLI:
    """Wrapper for JetBrains IDE CLI tools."""

    def __init__(self, ide_path: Path | None = None) -> None:
        """Initialize JetBrains CLI wrapper.

        Args:
            ide_path: Path to IntelliJ IDEA executable (e.g., /Applications/IntelliJ IDEA.app/Contents/MacOS/idea)
                     If None, tries to find in PATH or common locations.
        """
        self.ide_path = self._find_ide(ide_path)

    def _find_ide(self, provided_path: Path | None) -> Path | None:
        """Find IntelliJ IDEA executable."""
        if provided_path and provided_path.exists():
            return provided_path

        # Check PATH
        idea_cmd = shutil.which("idea")
        if idea_cmd:
            return Path(idea_cmd)

        # Check common macOS locations
        macos_paths = [
            Path("/Applications/IntelliJ IDEA.app/Contents/MacOS/idea"),
            Path.home() / "Applications" / "IntelliJ IDEA.app" / "Contents" / "MacOS" / "idea",
            # JetBrains Toolbox locations
            Path.home() / "Library" / "Application Support" / "JetBrains" / "Toolbox" / "scripts" / "idea",
            Path.home()
            / "Library"
            / "Application Support"
            / "JetBrains"
            / "Toolbox"
            / "apps"
            / "IDEA-U"
            / "ch-0"
            / "*"
            / "IntelliJ IDEA.app"
            / "Contents"
            / "MacOS"
            / "idea",
        ]
        for path in macos_paths:
            # Handle glob patterns
            if "*" in str(path):
                import glob

                matches = glob.glob(str(path))
                if matches:
                    return Path(matches[0])
            elif path.exists():
                return path

        # Check Linux locations
        linux_paths = [
            Path("/opt/idea/bin/idea.sh"),
            Path.home() / ".local" / "share" / "JetBrains" / "Toolbox" / "scripts" / "idea",
        ]
        for path in linux_paths:
            if path.exists():
                return path

        # Check for 'idea' command wrapper (created by Toolbox)
        idea_wrapper = Path.home() / ".local" / "bin" / "idea"
        if idea_wrapper.exists():
            return idea_wrapper

        return None

    def format(self, files: list[Path], project_root: Path | None = None) -> dict[str, Any]:
        """Format files using IntelliJ IDEA formatter.

        Args:
            files: List of files to format
            project_root: Project root directory (optional)

        Returns:
            Dict with 'success', 'stdout', 'stderr'
        """
        if not self.ide_path:
            return {"success": False, "error": "IntelliJ IDEA not found"}

        cmd = [str(self.ide_path), "format"]
        if project_root:
            cmd.extend(["--project", str(project_root)])
        cmd.extend([str(f) for f in files])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def inspect(self, project_root: Path, profile: str | None = None) -> dict[str, Any]:
        """Run code inspections using IntelliJ IDEA.

        Args:
            project_root: Project root directory
            profile: Inspection profile name (optional)

        Returns:
            Dict with inspection results
        """
        if not self.ide_path:
            return {"success": False, "error": "IntelliJ IDEA not found"}

        cmd = [str(self.ide_path), "inspect", str(project_root)]
        if profile:
            cmd.extend(["--profile", profile])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def diff(self, file1: Path, file2: Path) -> dict[str, Any]:
        """Show diff between two files.

        Args:
            file1: First file
            file2: Second file

        Returns:
            Dict with diff output
        """
        if not self.ide_path:
            return {"success": False, "error": "IntelliJ IDEA not found"}

        cmd = [str(self.ide_path), "diff", str(file1), str(file2)]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def merge(self, file1: Path, file2: Path, base: Path, output: Path) -> dict[str, Any]:
        """Merge two files with base.

        Args:
            file1: First file
            file2: Second file
            base: Base file
            output: Output file

        Returns:
            Dict with merge result
        """
        if not self.ide_path:
            return {"success": False, "error": "IntelliJ IDEA not found"}

        cmd = [
            str(self.ide_path),
            "merge",
            str(file1),
            str(file2),
            str(base),
            str(output),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
