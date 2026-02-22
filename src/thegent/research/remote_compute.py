"""Remote compute implementation for thegent run --remote."""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RemoteComputeClient:
    """Client for remote compute execution using SSH/rsync."""

    def __init__(self, remote_host: str, remote_port: int = 22) -> None:
        """Initialize remote compute client.

        Args:
            remote_host: Remote host address (e.g. user@host)
            remote_port: SSH port
        """
        self.remote_host = remote_host
        self.remote_port = remote_port

    def execute_remote(self, command: str, cwd: Path | None = None) -> dict[str, Any]:
        """Execute command on remote host.

        Args:
            command: Command to execute
            cwd: Working directory on remote host

        Returns:
            Execution result
        """
        ssh_cmd = ["ssh", "-p", str(self.remote_port), self.remote_host]

        full_command = f"cd {cwd} && {command}" if cwd else command

        ssh_cmd.append(full_command)

        logger.info(f"Executing remote command: {full_command} on {self.remote_host}")

        try:
            # We use check=False because we want to capture exit_code
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "status": "success" if result.returncode == 0 else "failed",
            }
        except Exception as e:
            logger.error(f"Remote execution failed: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "status": "error",
                "error": str(e),
            }

    def transfer_files(self, local_path: Path, remote_path: str) -> bool:
        """Transfer files to remote host using rsync.

        Args:
            local_path: Local file path or directory
            remote_path: Remote destination path (e.g. /tmp/thegent-run)

        Returns:
            True if successful
        """
        if not shutil.which("rsync"):
            logger.error("rsync not found, cannot transfer files.")
            return False

        # rsync -avz -e "ssh -p 22" local_path/ user@host:remote_path/
        rsync_cmd = [
            "rsync",
            "-avz",
            "-e",
            f"ssh -p {self.remote_port}",
            str(local_path) + "/",
            f"{self.remote_host}:{remote_path}/",
        ]

        logger.info(f"Transferring {local_path} to {self.remote_host}:{remote_path}")

        try:
            subprocess.run(rsync_cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"File transfer failed: {e.stderr.decode()}")
            return False
        except Exception as e:
            logger.error(f"File transfer failed: {e}")
            return False
