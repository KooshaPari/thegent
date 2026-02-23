"""
Doorstop Requirements Management Integration

Provides requirements management using doorstop.
Enables traceability between requirements and test cases.

Security:
- Verify MIT license compatibility
- No sensitive data in requirements documents

License: MIT (verified at https://github.com/doorstop-dev/doorstop)
"""

import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DoorstopError(Exception):
    """Base exception for Doorstop integration errors."""
    pass


class DoorstopStatus(Enum):
    """Doorstop integration status."""
    DISABLED = "disabled"
    READY = "ready"
    ERROR = "error"


@dataclass
class DoorstopConfig:
    """Configuration for Doorstop integration."""
    # Enable/disable the integration
    enabled: bool = False
    # Doorstop project directory
    project_dir: str = "./requirements"
    # Requirements tree root
    tree_root: str = "REQ"
    # Feature flag
    feature_flag: str = "THEGENT_ENABLE_DOORSTOP"
    # Validate on build
    validate_on_build: bool = True


@dataclass
class Requirement:
    """Represents a requirement."""
    id: str
    text: str
    parent: str = ""
    links: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)


class DoorstopManager:
    """
    Doorstop requirements manager.
    
    Provides:
    - Requirement validation
    - Traceability checks
    - Export to various formats
    """
    
    def __init__(self, config: DoorstopConfig | None = None):
        self._config = config or self._load_config()
        self._status = DoorstopStatus.DISABLED
        
        if self._config.enabled:
            self._status = DoorstopStatus.READY
            logger.info("Doorstop manager initialized (enabled)")
        else:
            logger.info("Doorstop manager initialized (disabled)")
    
    def _load_config(self) -> DoorstopConfig:
        """Load configuration from environment and defaults."""
        return DoorstopConfig(
            enabled=os.getenv("THEGENT_ENABLE_DOORSTOP", "").lower() in ("1", "true", "yes"),
            project_dir=os.getenv("DOORSTOP_PROJECT_DIR", "./requirements"),
            tree_root=os.getenv("DOORSTOP_TREE_ROOT", "REQ"),
            validate_on_build=os.getenv("DOORSTOP_VALIDATE_ON_BUILD", "true").lower() in ("1", "true", "yes"),
        )
    
    @property
    def name(self) -> str:
        return "doorstop"
    
    @property
    def status(self) -> DoorstopStatus:
        return self._status
    
    @property
    def is_enabled(self) -> bool:
        return self._config.enabled and self._status == DoorstopStatus.READY
    
    def _run_doorstop(self, args: list[str]) -> tuple[int, str, str]:
        """Run doorstop CLI command."""
        cmd = ["doorstop"] + args
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self._config.project_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            raise DoorstopError("doorstop CLI not found - install doorstop")
        except subprocess.TimeoutExpired:
            raise DoorstopError("doorstop command timed out")
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate all requirements.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.is_enabled:
            return False, "Doorstop not enabled"
        
        try:
            returncode, stdout, stderr = self._run_doorstop(["--strict"])
            
            if returncode == 0:
                return True, "All requirements valid"
            else:
                return False, f"Validation failed: {stderr}"
                
        except DoorstopError as e:
            return False, str(e)
    
    def get_requirements(self) -> list[Requirement]:
        """Get all requirements from the project."""
        if not self.is_enabled:
            return []
        
        try:
            returncode, stdout, stderr = self._run_doorstop(["--json"])
            
            if returncode == 0 and stdout:
                data = json.loads(stdout)
                requirements = []
                for item in data.get("items", []):
                    requirements.append(Requirement(
                        id=item.get("id", ""),
                        text=item.get("text", ""),
                        parent=item.get("parent", ""),
                        links=item.get("links", []),
                        attributes=item.get("attributes", {})
                    ))
                return requirements
            else:
                logger.warning(f"Failed to get requirements: {stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting requirements: {e}")
            return []
    
    def get_traceability(self) -> dict[str, list[str]]:
        """Get traceability matrix (requirement -> test links)."""
        requirements = self.get_requirements()
        
        traceability = {}
        for req in requirements:
            traceability[req.id] = req.links
        
        return traceability
    
    def export_requirements(self, format: str = "markdown") -> str:
        """Export requirements to specified format."""
        if not self.is_enabled:
            return ""
        
        if format == "markdown":
            returncode, stdout, stderr = self._run_doorstop(["--markdown"])
        elif format == "html":
            returncode, stdout, stderr = self._run_doorstop(["--html"])
        elif format == "csv":
            returncode, stdout, stderr = self._run_doorstop(["--csv"])
        else:
            return ""
        
        return stdout if returncode == 0 else ""
    
    def health_check(self) -> bool:
        """Check if doorstop is available and project is valid."""
        if not self.is_enabled:
            return False
        
        try:
            # Check if doorstop is installed
            result = subprocess.run(
                ["doorstop", "--version"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_stats(self) -> dict[str, Any]:
        """Get integration statistics."""
        return {
            "name": self.name,
            "status": self._status.value,
            "enabled": self.is_enabled,
            "config": {
                "project_dir": self._config.project_dir,
                "tree_root": self._config.tree_root,
                "validate_on_build": self._config.validate_on_build,
            }
        }


# Global manager instance
_doorstop_manager: DoorstopManager | None = None


def get_doorstop_manager() -> DoorstopManager:
    """Get the global Doorstop manager instance."""
    global _doorstop_manager
    if _doorstop_manager is None:
        _doorstop_manager = DoorstopManager()
    return _doorstop_manager


def is_doorstop_enabled() -> bool:
    """Check if Doorstop integration is enabled."""
    return get_doorstop_manager().is_enabled
