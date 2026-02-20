"""Virtual File System (VFS) adapter for efficient home directory management."""

import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class VfsAdapter:
    """
    Adapter for high-performance home directory creation.

    Supports:
    1. OverlayFS (Linux only) - Extremely fast, minimal disk usage.
    2. Reflink (macOS APFS / Btrfs) - Fast cloning without duplication.
    3. Fallback: Copy-on-Write (COW) or simple shutil.copytree.
    """

    def __init__(self, base_skel_dir: Path | None = None) -> None:
        """
        Initialize VfsAdapter.

        Args:
            base_skel_dir: Path to the 'skeleton' directory used as a base.
        """
        self.base_skel_dir = base_skel_dir
        if self.base_skel_dir:
            self.base_skel_dir.mkdir(parents=True, exist_ok=True)

        self.os_type = platform.system().lower()

    def create_home_dir(self, target_dir: Path, tenant_id: str) -> None:
        """
        Create a home directory for a tenant using the most efficient method.
        """
        if target_dir.exists():
            return

        target_dir.mkdir(parents=True, exist_ok=True)

        if not self.base_skel_dir or not any(self.base_skel_dir.iterdir()):
            logger.debug(f"Skeleton directory {self.base_skel_dir} is empty or missing. Creating empty home dir.")
            return

        # Optimization strategy based on OS and availability
        if self.os_type == "linux":
            # Try OverlayFS first (requires root/sudo, which sub-user system might not have yet)
            # For now, we'll implement the logic, but the actual execution might need elevation.
            try:
                self._try_overlay_mount(target_dir, tenant_id)
                return
            except Exception as e:
                logger.debug(f"OverlayFS failed: {e}. Falling back to copy/reflink.")

        # Fallback to reflink/copy
        self._copy_with_reflink(self.base_skel_dir, target_dir)

    def _copy_with_reflink(self, src: Path, dst: Path) -> None:
        """Copy using reflink if possible (APFS clonefile or Btrfs reflink)."""
        try:
            # On macOS (APFS) or Linux (Btrfs/XFS), cp --reflink=always is the standard
            # but on macOS we might need specific tool if 'cp' doesn't support it.
            if self.os_type == "darwin":
                # macOS 'cp' doesn't support --reflink, but APFS does it via clonefile(2)
                # For now, we'll just use shutil.copytree and rely on OS-level optimizations
                # unless we want to use a C-extension for clonefile.
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                # Linux: try cp --reflink=auto
                subprocess.run(
                    ["cp", "-a", "--reflink=auto", str(src) + "/.", str(dst)], check=True, capture_output=True
                )
        except Exception as e:
            logger.debug(f"Reflink copy failed: {e}. Falling back to simple copy.")
            shutil.copytree(src, dst, dirs_exist_ok=True)

    def _try_overlay_mount(self, target_dir: Path, tenant_id: str) -> None:
        """
        Attempt to mount an OverlayFS.

        Requires:
        - Linux kernel with overlay support.
        - Mount privileges (often root/sudo).
        - A writable upper layer.
        """
        if not self.base_skel_dir:
            return

        # We need a workdir and an upperdir for OverlayFS
        overlay_base = target_dir.parent / ".overlay"
        upper_dir = overlay_base / tenant_id / "upper"
        work_dir = overlay_base / tenant_id / "work"

        upper_dir.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=True, exist_ok=True)

        # Mount command: mount -t overlay overlay -o lowerdir=...,upperdir=...,workdir=... target_dir
        mount_opts = f"lowerdir={self.base_skel_dir},upperdir={upper_dir},workdir={work_dir}"

        # This will likely fail without sudo, but we include it for the "OS User (opt-in)" future.
        subprocess.run(
            ["mount", "-t", "overlay", "overlay", "-o", mount_opts, str(target_dir)], check=True, capture_output=True
        )
        logger.info(f"Mounted OverlayFS for tenant {tenant_id} at {target_dir}")

    def cleanup_home_dir(self, target_dir: Path, tenant_id: str) -> None:
        """Clean up the home directory, including unmounting if necessary."""
        if not target_dir.exists():
            return

        # Check if it's a mount point
        if self._is_mount(target_dir):
            try:
                subprocess.run(["umount", str(target_dir)], check=True, capture_output=True)
                # Also cleanup overlay metadata
                overlay_base = target_dir.parent / ".overlay"
                shutil.rmtree(overlay_base / tenant_id, ignore_errors=True)
            except Exception as e:
                logger.error(f"Failed to unmount {target_dir}: {e}")

        # Final cleanup of the directory itself
        shutil.rmtree(target_dir, ignore_errors=True)

    def _is_mount(self, path: Path) -> bool:
        """Check if a path is a mount point."""
        return os.path.ismount(str(path))
