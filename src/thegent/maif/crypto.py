"""MAIF Cryptographic Foundation - Signing and Verification.

Provides RSA-2048 signing and verification for MAIF artifacts.
"""

import hashlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class SigningKey:
    """RSA-2048 signing key for artifact creation.

    Uses RSA-2048 with SHA-256 for deterministic, reproducible signatures.
    """

    def __init__(self, private_key: rsa.RSAPrivateKey) -> None:
        """Initialize with a private key.

        Args:
            private_key: cryptography.hazmat RSAPrivateKey instance.
        """
        self.private_key = private_key
        self.public_key = private_key.public_key()

    @classmethod
    def generate(cls) -> "SigningKey":
        """Generate a new RSA-2048 key pair.

        Returns:
            SigningKey instance with freshly generated key pair.
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        return cls(private_key)

    @classmethod
    def from_pem(cls, pem_bytes: bytes) -> "SigningKey":
        """Load signing key from PEM format.

        Args:
            pem_bytes: PEM-encoded private key bytes.

        Returns:
            SigningKey instance.

        Raises:
            ValueError: If PEM format is invalid.
        """
        try:
            private_key = serialization.load_pem_private_key(pem_bytes, password=None, backend=default_backend())
            if not isinstance(private_key, rsa.RSAPrivateKey):
                raise ValueError("PEM key is not an RSA private key")
            return cls(private_key)
        except Exception as e:
            raise ValueError(f"Failed to load signing key: {e}")

    def sign(self, data: bytes) -> bytes:
        """Sign data with RSA-2048-SHA256.

        Args:
            data: Bytes to sign.

        Returns:
            RSA signature bytes (256 bytes for RSA-2048).
        """
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return signature

    def get_public_key(self) -> "VerifyingKey":
        """Get the public key for verification.

        Returns:
            VerifyingKey instance with the corresponding public key.
        """
        return VerifyingKey(self.public_key)

    def to_pem(self) -> bytes:
        """Export signing key to PEM format.

        Returns:
            PEM-encoded private key bytes.
        """
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )


class VerifyingKey:
    """RSA-2048 public key for artifact verification.

    Used to verify signatures on MAIF artifacts.
    """

    def __init__(self, public_key: rsa.RSAPublicKey) -> None:
        """Initialize with a public key.

        Args:
            public_key: cryptography.hazmat RSAPublicKey instance.
        """
        self.public_key = public_key

    @classmethod
    def from_pem(cls, pem_bytes: bytes) -> "VerifyingKey":
        """Load verifying key from PEM format.

        Args:
            pem_bytes: PEM-encoded public key bytes.

        Returns:
            VerifyingKey instance.

        Raises:
            ValueError: If PEM format is invalid.
        """
        try:
            public_key = serialization.load_pem_public_key(pem_bytes, backend=default_backend())
            if not isinstance(public_key, rsa.RSAPublicKey):
                raise ValueError("PEM key is not an RSA public key")
            return cls(public_key)
        except Exception as e:
            raise ValueError(f"Failed to load verifying key: {e}")

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify RSA-2048-SHA256 signature.

        Args:
            data: Original data bytes that were signed.
            signature: RSA signature bytes to verify.

        Returns:
            True if signature is valid, False otherwise.
        """
        try:
            self.public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    def to_pem(self) -> bytes:
        """Export verifying key to PEM format.

        Returns:
            PEM-encoded public key bytes.
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )


def hash_data(data: bytes) -> str:
    """Compute SHA-256 hash of data.

    Args:
        data: Bytes to hash.

    Returns:
        Hex-encoded SHA-256 hash.
    """
    return hashlib.sha256(data).hexdigest()
