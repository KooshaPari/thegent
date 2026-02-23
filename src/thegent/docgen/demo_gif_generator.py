"""Auto-generate demo GIFs from scripts."""

import logging
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
from pathlib import Path

logger = logging.getLogger(__name__)


class DemoGIFGenerator:
    """Generate demo GIFs from scripts using VHS or similar tools."""

    def __init__(self, vhs_path: str | None = None) -> None:
        """Initialize demo GIF generator.

        Args:
            vhs_path: Path to VHS binary
        """
        self.vhs_path = vhs_path or "vhs"

    def generate_from_script(self, script_path: Path, output_path: Path) -> bool:
        """Generate GIF from a script file.

        Args:
            script_path: Path to script file (.tape for VHS)
            output_path: Output GIF path

        Returns:
            True if successful
        """
        try:
            # VHS command: vhs script.tape -o output.gif
            cmd = [self.vhs_path, str(script_path), "-o", str(output_path)]
            result = shim_run(cmd, capture_output=True, text=True, timeout=60, check=False)

            if result.returncode == 0:
                logger.info(f"Generated GIF: {output_path}")
                return True
            logger.error(f"VHS error: {result.stderr}")
            return False
        except FileNotFoundError:
            logger.error(f"VHS not found at {self.vhs_path}")
            return False
        except Exception as e:
            logger.error(f"Error generating GIF: {e}")
            return False

    def generate_from_commands(self, commands: list[str], output_path: Path) -> bool:
        """Generate GIF from a list of commands.

        Args:
            commands: List of shell commands
            output_path: Output GIF path

        Returns:
            True if successful
        """
        # Create temporary .tape file
        tape_content = self._commands_to_tape(commands)
        temp_tape = output_path.with_suffix(".tape")
        temp_tape.write_text(tape_content)

        try:
            success = self.generate_from_script(temp_tape, output_path)
            # Clean up temp file
            if temp_tape.exists():
                temp_tape.unlink()
            return success
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

    def _commands_to_tape(self, commands: list[str]) -> str:
        """Convert commands to VHS tape format.

        Args:
            commands: List of commands

        Returns:
            VHS tape content
        """
        lines = ["Output demo.gif", "Set FontSize 14"]
        for cmd in commands:
            lines.append(f"Type '{cmd}'")
            lines.append("Enter")
            lines.append("Sleep 500ms")
        return "\n".join(lines)
