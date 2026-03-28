"""Muxless agent session persistence via zmx.

Provides ZmxSessionManager and ZmxSessionConfig for managing agent sessions
without requiring tmux or screen multiplexers.

# @trace FR-SES-001
"""

from phenotype_thegent_execution.muxless.zmx_session import (
    ZmxSessionConfig,
    ZmxSessionManager,
    make_zmx_session_manager,
)

__all__ = [
    "ZmxSessionConfig",
    "ZmxSessionManager",
    "make_zmx_session_manager",
]
