"""ACP client adapter for spawning external ACP agents."""

<<<<<<< HEAD
<<<<<<< HEAD
import orjson as json
=======
from thegent.utils.json_utils import json_dumps, json_loads
>>>>>>> fix/ci-remove-macos
import subprocess
=======
import orjson as jsonimport subprocess
>>>>>>> main
from collections.abc import Callable
from pathlib import Path

from thegent.agents.base import AgentRunner, RunResult


class ACPClientAdapter(AgentRunner):
    """AgentRunner implementation that spawns external ACP agents."""

    def __init__(self, acp_command: list[str], agent_name: str = "acp-agent") -> None:
        """Initialize ACP client adapter.

        Args:
            acp_command: Command to spawn ACP agent (e.g., ["npx", "-y", "@zed-industries/claude-agent-acp"])
            agent_name: Name of the agent (for logging/identification)
        """
        self.acp_command = acp_command
        self.agent_name = agent_name
        self.process: subprocess.Popen[str] | None = None

    def run(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        *,
        use_stream: bool = True,
        live_output: bool = False,
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
    ) -> RunResult:
        """Run ACP agent via subprocess.

        Args:
            prompt: User prompt/request
            cwd: Working directory
            mode: Agent mode (unused for ACP)
            timeout: Timeout in seconds
            use_stream: Whether to stream responses (unused for ACP)
            live_output: Whether to show live output (unused for ACP)
            on_stdout: Callback for stdout (unused for ACP)
            on_stderr: Callback for stderr (unused for ACP)

        Returns:
            RunResult with stdout, stderr, exit_code
        """
        # Spawn ACP agent process
        self.process = subprocess.Popen(
            self.acp_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(cwd) if cwd else None,
        )

        if not self.process.stdin or not self.process.stdout:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr="Failed to open stdin/stdout",
                timed_out=False,
            )

        try:
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "capabilities": {},
                },
            }
<<<<<<< HEAD
<<<<<<< HEAD
            self.process.stdin.write(json.dumps(init_request).decode().decode() + "\n")
=======
            self.process.stdin.write(json_dumps(init_request) + "\n")
>>>>>>> fix/ci-remove-macos
            self.process.stdin.flush()
=======
            self.process.stdin.write(json.dumps(init_request).decode().decode() + "\n")            self.process.stdin.flush()
>>>>>>> main

            # Read initialize response
            init_response_line = self.process.stdout.readline()
            if init_response_line:
                init_response = json_loads(init_response_line.strip())
                if "error" in init_response:
                    return RunResult(
                        exit_code=1,
                        stdout="",
                        stderr=f"ACP initialize error: {init_response['error']}",
                        timed_out=False,
                    )

            # Send spawn request
            spawn_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "agent/spawn",
                "params": {
                    "prompt": prompt,
                    "cwd": str(cwd) if cwd else None,
                },
            }
<<<<<<< HEAD
<<<<<<< HEAD
            self.process.stdin.write(json.dumps(spawn_request).decode().decode() + "\n")
=======
            self.process.stdin.write(json_dumps(spawn_request) + "\n")
>>>>>>> fix/ci-remove-macos
            self.process.stdin.flush()
=======
            self.process.stdin.write(json.dumps(spawn_request).decode().decode() + "\n")            self.process.stdin.flush()
>>>>>>> main

            # Read responses
            stdout_lines = []
            stderr_lines = []

            # Read stdout (ACP responses)
            for line in self.process.stdout:
                if not line.strip():
                    continue
                try:
                    response = json_loads(line.strip())
                    if "result" in response:
                        result = response["result"]
                        if "stdout" in result:
                            stdout_lines.append(result["stdout"])
                        if "stderr" in result:
                            stderr_lines.append(result["stderr"])
                    elif "error" in response:
                        stderr_lines.append(f"ACP error: {response['error']}")
                except json.JSONDecodeError:
                    # Non-JSON output (may be agent stdout)
                    stdout_lines.append(line)

            # Wait for process
            try:
                exit_code = self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.process.kill()
                exit_code = 1
                timed_out = True
            else:
                timed_out = False

            return RunResult(
                exit_code=exit_code,
                stdout="\n".join(stdout_lines),
                stderr="\n".join(stderr_lines),
                timed_out=timed_out,
            )

        except Exception as e:
            if self.process:
                self.process.kill()
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=f"ACP client error: {e}",
                timed_out=False,
            )
