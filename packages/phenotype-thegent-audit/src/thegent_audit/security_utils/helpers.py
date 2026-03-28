"""Security helper utilities."""

import hashlib
import logging

logger = logging.getLogger(__name__)


class SecurityHelpers:
    """Security helper utilities."""

    @staticmethod
    def hash_password(password: str, salt: str = "") -> str:
        """Hash a password.

        Args:
            password: Password to hash
            salt: Optional salt

        Returns:
            Hashed password
        """
        combined = password + salt
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a random token.

        Args:
            length: Token length

        Returns:
            Random token
        """
        import secrets

        return secrets.token_urlsafe(length)
