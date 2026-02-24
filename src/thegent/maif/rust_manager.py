"""MAIF Artifact Manager using Rust binary."""

import orjson as json
from thegent.infra.shim_subprocess import run as shim_run
from pathlib import Path
from typing import Any


class RustMAIFManager:
    """Manager that delegates MAIF operations to the Rust binary."""

    def __init__(self, binary_path: Path, private_key_path: Path, public_key_path: Path) -> None:
        self.binary_path = binary_path
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path

    def ensure_keys(self, bits: int = 2048) -> None:
        """Ensure RSA keys exist, generate if not."""
        if not self.private_key_path.exists() or not self.public_key_path.exists():
            self.private_key_path.parent.mkdir(parents=True, exist_ok=True)
            shim_run(
                [
                    str(self.binary_path),
                    "keygen",
                    "--bits",
                    str(bits),
                    "--private-key",
                    str(self.private_key_path),
                    "--public-key",
                    str(self.public_key_path),
                ],
                check=True,
                capture_output=True,
            )

    def create_artifact(
        self,
        action: str,
        payload: dict[str, Any],
        agent: str,
        session: str,
        output_path: Path,
    ) -> dict[str, Any]:
        """Create and sign a MAIF artifact using the Rust binary."""
        self.ensure_keys()

        payload_json = json.dumps(payload).decode()

        shim_run(
            [
                str(self.binary_path),
                "create",
                "--action",
                action,
                "--payload",
                payload_json,
                "--agent",
                agent,
                "--session",
                session,
                "--key",
                str(self.private_key_path),
                "--output",
                str(output_path),
            ],
            check=True,
            capture_output=True,
        )

        with open(output_path) as f:
            return json.load(f)

    def verify_artifact(self, artifact_path: Path) -> bool:
        """Verify a MAIF artifact using the Rust binary."""
        result = shim_run(
            [
                str(self.binary_path),
                "verify",
                "--artifact",
                str(artifact_path),
                "--key",
                str(self.public_key_path),
            ],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0
