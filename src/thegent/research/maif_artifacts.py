"""MAIF Action Artifacts (Signed Artifacts)."""

import hashlib
import logging
from datetime import UTC, datetime
from typing import Any
<<<<<<< HEAD
=======
from thegent.integrations.base import SerializableMixin
>>>>>>> fix/additional-improvements

from thegent.integrations.base import SerializableMixin

logger = logging.getLogger(__name__)


class MAIFArtifact(SerializableMixin):
    """MAIF (Model-Action Interface Format) signed artifact."""

    def __init__(self, action: dict[str, Any], signature: str | None = None) -> None:
        """Initialize MAIF artifact.

        Args:
            action: Action dictionary
            signature: Digital signature
        """
        self.action = action
        self.signature = signature
        self.timestamp = datetime.now(UTC).isoformat()

    def sign(self, private_key: str) -> str:
        """Sign the artifact.

        Args:
            private_key: Private key for signing

        Returns:
            Signature string
        """
        # Simplified signing - would use proper crypto in production
        content = str(self.action) + self.timestamp
        self.signature = hashlib.sha256(content.encode()).hexdigest()
        logger.info("Signed MAIF artifact")
        return self.signature

    def verify(self, public_key: str) -> bool:
        """Verify artifact signature.

        Args:
            public_key: Public key for verification

        Returns:
            True if signature is valid
        """
        if not self.signature:
            return False

        # Simplified verification
        content = str(self.action) + self.timestamp
        expected = hashlib.sha256(content.encode()).hexdigest()
        return self.signature == expected
