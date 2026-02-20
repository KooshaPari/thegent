"""Mojo Bridge - Python to Mojo Interoperability.

This module provides a bridge for calling compiled Mojo modules from Python.
It supports subprocess-based execution of compiled Mojo binaries with JSON I/O.

Note: Mojo ecosystem is still maturing. This bridge uses subprocess to call
compiled Mojo binaries, with future support for C-ABI integration when stable.
"""

import asyncio
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from thegent.infra.cache_v2 import CacheV2


# Try to import the IPC module if available
try:
    from thegent.infra.ipc import IPCMesh
    IPC_AVAILABLE = True
except ImportError:
    IPC_AVAILABLE = False


# Try to import the shell module if available
try:
    from thegent.infra.shell_injection import run_untrusted_shell_command
    SHELL_AVAILABLE = True
except ImportError:
    SHELL_AVAILABLE = False


class MojoNotAvailableError(Exception):
    """Raised when Mojo is not installed or not accessible."""
    pass


@dataclass
class MojoModule:
    """Represents a compiled Mojo module."""
    name: str
    path: Path
    compiled: bool = False


@dataclass
class MojoTask:
    """Task to be executed in Mojo."""
    task_id: str
    module: str
    function: str
    args: dict[str, Any]
    timeout: float = 30.0


class MojoBridge:
    """Bridge for calling Mojo modules from Python.
    
    Supports:
    - Subprocess-based execution of compiled Mojo binaries
    - Graceful fallback when Mojo is not available
    - JSON-based I/O for data exchange
    - Async execution for better integration
    
    Future:
    - C-ABI integration when Mojo's foreign function interface stabilizes
    - Direct memory sharing for high-performance scenarios
    """
    
    def __init__(
        self,
        mojo_root: Path | None = None,
        cache_root: Path | None = None,
    ) -> None:
        """Initialize the Mojo bridge.
        
        Args:
            mojo_root: Root directory for Mojo modules (default: ~/.thegent/mojo)
            cache_root: Root directory for cache (default: /tmp/thegent-mojo-cache)
        """
        self.mojo_root = mojo_root or Path.home() / ".thegent" / "mojo"
        self.cache_root = cache_root or Path("/tmp/thegent-mojo-cache")
        
        # Ensure directories exist
        self.mojo_root.mkdir(parents=True, exist_ok=True)
        self.cache_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize cache
        self._cache = CacheV2(self.cache_root, namespace="mojo_bridge")
        
        # Track Mojo availability
        self._mojo_path: Path | None = None
        self._is_available: bool | None = None
        
        # Platform-specific settings
        is_mac = platform.system() == "Darwin"
        self.default_timeout = 60.0 if is_mac else 30.0
        
    @property
    def is_available(self) -> bool:
        """Check if Mojo is installed and available."""
        if self._is_available is not None:
            return self._is_available
        
        self._is_available = self._check_mojo()
        return self._is_available
    
    def _check_mojo(self) -> bool:
        """Check if Mojo is installed on the system.
        
        Checks:
        1. Direct `mojo` command in PATH
        2. Modular CLI in common locations
        3. Mojo SDK in standard installation paths
        """
        # Check for mojo command
        mojo_cmd = shutil.which("mojo")
        if mojo_cmd:
            self._mojo_path = Path(mojo_cmd)
            return True
        
        # Check for modular CLI (Mojo's package manager)
        modular_cmd = shutil.which("modular")
        if modular_cmd:
            # Try to get mojo version through modular
            try:
                result = subprocess.run(
                    ["modular", "auth"],
                    capture_output=True,
                    timeout=5,
                )
                # If modular is set up, mojo should be available
                return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        # Check common installation paths on macOS
        if platform.system() == "Darwin":
            common_paths = [
                Path.home() / ".modular" / "pkg" / "mojo-nightly" / "bin" / "mojo",
                Path.home() / ".modular" / "pkg" / "mojo" / "bin" / "mojo",
            ]
            for path in common_paths:
                if path.exists():
                    self._mojo_path = path
                    return True
        
        # Check common installation paths on Linux
        if platform.system() == "Linux":
            common_paths = [
                Path.home() / ".modular" / "pkg" / "mojo-nightly" / "bin" / "mojo",
                Path.home() / ".modular" / "pkg" / "mojo" / "bin" / "mojo",
                Path("/opt/mojo/bin/mojo"),
            ]
            for path in common_paths:
                if path.exists():
                    self._mojo_path = path
                    return True
        
        return False
    
    async def get_version(self) -> str | None:
        """Get the Mojo version if available.
        
        Returns:
            Version string or None if not available
        """
        if not self.is_available:
            return None
        
        try:
            cmd = "mojo" if self._mojo_path is None else str(self._mojo_path)
            process = await asyncio.create_subprocess_exec(
                cmd, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=10.0
            )
            if process.returncode == 0:
                return stdout.decode().strip()
        except (asyncio.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        return None
    
    async def run_mojo_script(
        self,
        script: str,
        args: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Run a Mojo script with JSON input/output.
        
        Args:
            script: Mojo source code or path to .mojo file
            args: Arguments to pass to the Mojo script
            timeout: Timeout in seconds
            
        Returns:
            JSON response from the Mojo script
        """
        if not self.is_available:
            raise MojoNotAvailableError(
                "Mojo is not installed. "
                "Install via: brew install mojo (macOS) or see https://docs.modular.com/mojo"
            )
        
        timeout = timeout or self.default_timeout
        args = args or {}
        
        # Create temporary file for the script if it's inline code
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.mojo', 
            delete=False
        ) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Run mojo with JSON args
            cmd = "mojo" if self._mojo_path is None else str(self._mojo_path)
            
            # Pass args as JSON environment variable
            env = os.environ.copy()
            env["THEGENT_MOJO_ARGS"] = json.dumps(args)
            
            process = await asyncio.create_subprocess_exec(
                cmd, script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Mojo script failed: {error_msg}")
            
            output = stdout.decode().strip()
            if output:
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {"output": output}
            return {}
            
        finally:
            # Clean up temp file
            try:
                os.unlink(script_path)
            except OSError:
                pass
    
    async def run_compiled(
        self,
        binary_path: Path,
        input_data: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Run a compiled Mojo binary.
        
        Args:
            binary_path: Path to the compiled Mojo binary
            input_data: JSON input to pass to the binary
            timeout: Timeout in seconds
            
        Returns:
            JSON response from the binary
        """
        if not self.is_available:
            raise MojoNotAvailableError("Mojo is not installed")
        
        timeout = timeout or self.default_timeout
        input_data = input_data or {}
        
        # Write input to temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
        ) as f:
            json.dump(input_data, f)
            input_path = f.name
        
        try:
            process = await asyncio.create_subprocess_exec(
                str(binary_path),
                input_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Mojo binary failed: {error_msg}")
            
            output = stdout.decode().strip()
            if output:
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {"output": output}
            return {}
            
        finally:
            try:
                os.unlink(input_path)
            except OSError:
                pass
    
    def install_instructions(self) -> str:
        """Get installation instructions for Mojo.
        
        Returns:
            Installation instructions as a string
        """
        if platform.system() == "Darwin":
            return """# Install Mojo on macOS

Using Homebrew:
    brew install mojo

Or manually:
    1. Visit https://docs.modular.com/mojo/manual/install/
    2. Download the Mojo SDK for your platform
    3. Run the installer and follow the instructions
"""
        elif platform.system() == "Linux":
            return """# Install Mojo on Linux

    1. Visit https://docs.modular.com/mojo/manual/install/
    2. Download the Mojo SDK for Linux
    3. Run the installer and follow the instructions
"""
        else:
            return """# Install Mojo

Visit https://docs.modular.com/mojo/manual/install/ for platform-specific instructions.
"""
    
    async def dispatch(self, task: MojoTask) -> dict[str, Any]:
        """Dispatch a task to Mojo for execution.
        
        Args:
            task: The Mojo task to execute
            
        Returns:
            Result from the Mojo execution
        """
        # For now, we execute via subprocess
        # Future: use C-ABI when stable
        
        # Check cache first
        cache_key = f"mojo_task:{task.module}:{task.function}:{json.dumps(task.args, sort_keys=True)}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached
        
        # Build a simple Mojo script to execute the function
        mojo_code = f"""
from python import Python

fn main():
    # This is a placeholder - actual implementation would call the module
    let args = Python.import_module("os").environ.get("THEGENT_MOJO_ARGS", "{{}}")
    print(args)
"""
        
        try:
            result = await self.run_mojo_script(mojo_code, task.args, task.timeout)
            
            # Cache the result
            await self._cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except MojoNotAvailableError:
            # Return gracefully when mojo is not available
            return {
                "error": "mojo_not_available",
                "message": "Mojo is not installed. " + self.install_instructions(),
                "task_id": task.task_id,
            }
    
    async def compile_module(
        self,
        source_path: Path,
        output_path: Path | None = None,
    ) -> Path | None:
        """Compile a Mojo source file to a binary.
        
        Note: This requires the full Mojo SDK to be installed.
        
        Args:
            source_path: Path to .mojo source file
            output_path: Path for the compiled binary (default: same name without .mojo)
            
        Returns:
            Path to the compiled binary, or None if compilation failed
        """
        if not self.is_available:
            return None
        
        output_path = output_path or source_path.with_name(source_path.stem)
        
        try:
            cmd = "mojo" if self._mojo_path is None else str(self._mojo_path)
            process = await asyncio.create_subprocess_exec(
                cmd, "compile", str(source_path), str(output_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120.0,
            )
            
            if process.returncode == 0:
                return output_path
            else:
                print(f"Compilation failed: {stderr.decode()}")
                return None
                
        except asyncio.TimeoutExpired:
            print("Compilation timed out")
            return None
        except Exception as e:
            print(f"Compilation error: {e}")
            return None
    
    async def shutdown(self) -> None:
        """Clean up resources."""
        # Clear cache if needed
        await self._cache.clear_expired()
        print("[MojoBridge] Shutdown complete.")


# Global bridge instance
_bridge: MojoBridge | None = None


def get_bridge() -> MojoBridge:
    """Get the global Mojo bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = MojoBridge()
    return _bridge


async def check_mojo_status() -> dict[str, Any]:
    """Check Mojo installation status.
    
    Returns:
        Dictionary with availability and version info
    """
    bridge = get_bridge()
    
    result = {
        "available": bridge.is_available,
        "version": None,
        "install_instructions": None,
    }
    
    if bridge.is_available:
        result["version"] = await bridge.get_version()
    else:
        result["install_instructions"] = bridge.install_instructions()
    
    return result


# Example usage when run directly
if __name__ == "__main__":
    async def main():
        import sys
        
        bridge = get_bridge()
        status = await check_mojo_status()
        
        print("=== Mojo Bridge Status ===")
        print(f"Available: {status['available']}")
        print(f"Version: {status['version'] or 'N/A'}")
        
        if not status['available']:
            print("\n=== Installation Instructions ===")
            print(status['install_instructions'])
        
        # Try a simple test if available
        if status['available']:
            print("\n=== Running Test ===")
            test_task = MojoTask(
                task_id="test_001",
                module="test",
                function="hello",
                args={"name": "thegent"},
            )
            result = await bridge.dispatch(test_task)
            print(f"Result: {result}")
    
    asyncio.run(main())
