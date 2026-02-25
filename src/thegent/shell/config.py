"""
Shell Configuration

Configurable settings for shell execution.
"""

from dataclasses import dataclass


@dataclass
class ShellConfig:
    """Configuration for shell execution."""
    # Timeout settings
    default_timeout: float = 300.0  # 5 minutes (up from 150s)
    max_timeout: float = 1800.0  # 30 minutes max
    
    # Retry settings
    max_retries: int = 3
    retry_base_delay: float = 1.0  # seconds
    retry_max_delay: float = 30.0  # seconds
    retry_exponential_base: float = 2.0
    
    # Execution settings
    shell: str = "/bin/bash"
    capture_output: bool = True
    stream_output: bool = False
    
    def get_timeout(self, explicit_timeout: float = None) -> float:
        """Get timeout value, respecting max."""
        timeout = explicit_timeout or self.default_timeout
        return min(timeout, self.max_timeout)
    
    def get_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        delay = self.retry_base_delay * (self.retry_exponential_base ** attempt)
        return min(delay, self.retry_max_delay)
