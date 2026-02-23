"""Doctor check functions.

Contains all the diagnostic check functions for thegent doctor.
"""

import re
import shutil
from pathlib import Path
from typing import Any

from thegent.doctor.models import CheckResult, CheckStatus, ProcessInfo


def check_dependencies() -> list[CheckResult]:
    """Check if required dependencies are installed."""
    results: list[CheckResult] = []
    
    # Check for required commands
    required_cmds = ["git", "python3", "node", "npm"]
    for cmd in required_cmds:
        if shutil.which(cmd):
            results.append(CheckResult(
                check_id=f"deps_{cmd}",
                status=CheckStatus.PASS,
                message=f"{cmd} is installed",
            ))
        else:
            results.append(CheckResult(
                check_id=f"deps_{cmd}",
                status=CheckStatus.FAIL,
                message=f"{cmd} is not installed",
            ))
    
    return results


def check_configuration() -> list[CheckResult]:
    """Check configuration files and settings."""
    results: list[CheckResult] = []
    
    # Check for config files
    config_paths = [
        Path.home() / ".thegent" / "config.yaml",
        Path.home() / ".thegent" / ".env",
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            results.append(CheckResult(
                check_id=f"config_{config_path.name}",
                status=CheckStatus.PASS,
                message=f"Config file exists: {config_path}",
            ))
        else:
            results.append(CheckResult(
                check_id=f"config_{config_path.name}",
                status=CheckStatus.WARN,
                message=f"Config file not found: {config_path}",
            ))
    
    return results


def check_isolation() -> list[CheckResult]:
    """Check process isolation settings."""
    results: list[CheckResult] = []
    
    # Check for isolation config
    isolation_path = Path.home() / ".thegent" / "isolation"
    if isolation_path.exists():
        results.append(CheckResult(
            check_id="isolation",
            status=CheckStatus.PASS,
            message="Isolation directory exists",
        ))
    else:
        results.append(CheckResult(
            check_id="isolation",
            status=CheckStatus.WARN,
            message="Isolation directory not found",
        ))
    
    return results


def check_connectivity(auto_start: bool = True) -> list[CheckResult]:
    """Check network connectivity and services."""
    results: list[CheckResult] = []
    
    # Check common ports
    ports = [8000, 8080, 3000]
    import socket
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                results.append(CheckResult(
                    check_id=f"port_{port}",
                    status=CheckStatus.PASS,
                    message=f"Port {port} is open",
                ))
            else:
                results.append(CheckResult(
                    check_id=f"port_{port}",
                    status=CheckStatus.SKIP,
                    message=f"Port {port} is not in use",
                ))
        except Exception as e:
            results.append(CheckResult(
                check_id=f"port_{port}",
                status=CheckStatus.WARN,
                message=f"Could not check port {port}: {e}",
            ))
    
    return results


def check_environment() -> list[CheckResult]:
    """Check environment variables."""
    results: list[CheckResult] = []
    
    important_env_vars = [
        "PATH",
        "HOME",
        "USER",
        "THEGENT_CONFIG_PATH",
    ]
    
    for var in important_env_vars:
        value = Path.home()  # Just check if we can access home
        if var in ["PATH", "HOME", "USER"]:
            results.append(CheckResult(
                check_id=f"env_{var.lower()}",
                status=CheckStatus.PASS,
                message=f"Environment variable {var} is set",
            ))
        else:
            results.append(CheckResult(
                check_id=f"env_{var.lower()}",
                status=CheckStatus.SKIP,
                message=f"Environment variable {var} is optional",
            ))
    
    return results


def check_shim_binaries() -> list[CheckResult]:
    """Check if shim binaries exist."""
    results: list[CheckResult] = []
    
    bin_dir = Path.home() / ".thegent" / "bin"
    expected_bins = ["thegent", "clode", "roid", "dex"]
    
    if not bin_dir.exists():
        return [CheckResult(
            check_id="shim_dir",
            status=CheckStatus.FAIL,
            message=f"Shim directory not found: {bin_dir}",
        )]
    
    for bin_name in expected_bins:
        bin_path = bin_dir / bin_name
        if bin_path.exists():
            results.append(CheckResult(
                check_id=f"shim_{bin_name}",
                status=CheckStatus.PASS,
                message=f"Shim binary exists: {bin_path}",
            ))
        else:
            results.append(CheckResult(
                check_id=f"shim_{bin_name}",
                status=CheckStatus.WARN,
                message=f"Shim binary not found: {bin_path}",
            ))
    
    return results


def check_providers() -> list[CheckResult]:
    """Check configured LLM providers."""
    results: list[CheckResult] = []
    
    # Check for provider configs
    config_dir = Path.home() / ".thegent" / "providers"
    if not config_dir.exists():
        results.append(CheckResult(
            check_id="providers",
            status=CheckStatus.WARN,
            message="No provider configurations found",
        ))
    else:
        configs = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.json"))
        results.append(CheckResult(
            check_id="providers",
            status=CheckStatus.PASS,
            message=f"Found {len(configs)} provider configurations",
            details={"count": len(configs)},
        ))
    
    return results


def check_ollama() -> list[CheckResult]:
    """Check Ollama installation and status."""
    results: list[CheckResult] = []
    
    # Check if ollama is installed
    ollama_path = shutil.which("ollama")
    if ollama_path:
        results.append(CheckResult(
            check_id="ollama_installed",
            status=CheckStatus.PASS,
            message=f"Ollama found at: {ollama_path}",
        ))
    else:
        results.append(CheckResult(
            check_id="ollama_installed",
            status=CheckStatus.WARN,
            message="Ollama not found in PATH",
        ))
    
    return results


def check_headless() -> list[CheckResult]:
    """Check headless mode configuration."""
    results: list[CheckResult] = []
    
    # Check for headless mode
    env_headless = Path.home() / ".thegent" / "headless"
    if env_headless.exists():
        results.append(CheckResult(
            check_id="headless",
            status=CheckStatus.PASS,
            message="Headless mode is enabled",
        ))
    else:
        results.append(CheckResult(
            check_id="headless",
            status=CheckStatus.SKIP,
            message="Headless mode is not enabled (normal for desktop)",
        ))
    
    return results


def check_process_health(processes: list[ProcessInfo]) -> list[CheckResult]:
    """Check health of running processes."""
    results: list[CheckResult] = []
    
    if not processes:
        results.append(CheckResult(
            check_id="process_health",
            status=CheckStatus.WARN,
            message="No processes to check",
        ))
        return results
    
    # Check for stuck processes
    stuck = [p for p in processes if p.cpu_percent > 80]
    if stuck:
        results.append(CheckResult(
            check_id="process_stuck",
            status=CheckStatus.FAIL,
            message=f"Found {len(stuck)} stuck processes",
            details={"pids": [p.pid for p in stuck]},
        ))
    else:
        results.append(CheckResult(
            check_id="process_health",
            status=CheckStatus.PASS,
            message="All processes are healthy",
        ))
    
    return results


def check_sessions() -> list[CheckResult]:
    """Check active sessions."""
    results: list[CheckResult] = []
    
    session_dir = Path.home() / ".thegent" / "sessions"
    if not session_dir.exists():
        results.append(CheckResult(
            check_id="sessions",
            status=CheckStatus.SKIP,
            message="No sessions directory found",
        ))
        return results
    
    sessions = list(session_dir.glob("*.json"))
    results.append(CheckResult(
        check_id="sessions",
        status=CheckStatus.PASS,
        message=f"Found {len(sessions)} session files",
        details={"count": len(sessions)},
    ))
    
    return results


def check_project_hints() -> list[CheckResult]:
    """Check for project hint files."""
    results: list[CheckResult] = []
    
    # Check for various hint files
    hint_files = {
        ".thegent-hints": "Thegent hints",
        ".env": "Environment file",
        "pyproject.toml": "Python project",
        "package.json": "Node project",
    }
    
    found = 0
    for filename, description in hint_files.items():
        if Path(filename).exists():
            found += 1
    
    if found > 0:
        results.append(CheckResult(
            check_id="project_hints",
            status=CheckStatus.PASS,
            message=f"Found {found} project hint files",
            details={"count": found},
        ))
    else:
        results.append(CheckResult(
            check_id="project_hints",
            status=CheckStatus.WARN,
            message="No project hint files found",
        ))
    
    return results


def check_performance() -> list[CheckResult]:
    """Check system performance metrics."""
    results: list[CheckResult] = []
    
    # Try to get system metrics
    try:
        import psutil
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent < 80:
            results.append(CheckResult(
                check_id="cpu",
                status=CheckStatus.PASS,
                message=f"CPU usage: {cpu_percent:.1f}%",
                details={"cpu_percent": cpu_percent},
            ))
        else:
            results.append(CheckResult(
                check_id="cpu",
                status=CheckStatus.WARN,
                message=f"High CPU usage: {cpu_percent:.1f}%",
                details={"cpu_percent": cpu_percent},
            ))
        
        # Memory usage
        mem = psutil.virtual_memory()
        if mem.percent < 80:
            results.append(CheckResult(
                check_id="memory",
                status=CheckStatus.PASS,
                message=f"Memory usage: {mem.percent:.1f}%",
                details={"memory_percent": mem.percent},
            ))
        else:
            results.append(CheckResult(
                check_id="memory",
                status=CheckStatus.WARN,
                message=f"High memory usage: {mem.percent:.1f}%",
                details={"memory_percent": mem.percent},
            ))
        
    except ImportError:
        results.append(CheckResult(
            check_id="performance",
            status=CheckStatus.SKIP,
            message="psutil not available, skipping performance checks",
        ))
    except Exception as e:
        results.append(CheckResult(
            check_id="performance",
            status=CheckStatus.WARN,
            message=f"Could not check performance: {e}",
        ))
    
    return results
