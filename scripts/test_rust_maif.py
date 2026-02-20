import json
import sys
from pathlib import Path

from thegent.maif.rust_manager import RustMAIFManager


def test_rust_maif():
    binary_path = Path("target-maif/release/thegent-maif")
    if not binary_path.exists():
        print(f"Binary not found at {binary_path}")
        sys.exit(1)

    private_key = Path("tests/data/maif_private.pem")
    public_key = Path("tests/data/maif_public.pem")
    output_path = Path("tests/data/test_artifact.json")

    private_key.parent.mkdir(parents=True, exist_ok=True)

    manager = RustMAIFManager(binary_path, private_key, public_key)

    print("Generating keys...")
    manager.ensure_keys()

    print("Creating artifact...")
    payload = {"test": "data", "nested": {"key": 123}}
    artifact = manager.create_artifact(
        action="test_action", payload=payload, agent="test_agent", session="test_session", output_path=output_path
    )

    print(f"Artifact created: {json.dumps(artifact, indent=2)}")

    print("Verifying artifact...")
    is_valid = manager.verify_artifact(output_path)
    print(f"Verification result: {is_valid}")

    if not is_valid:
        print("Verification failed!")
        sys.exit(1)

    print("All tests passed!")


if __name__ == "__main__":
    test_rust_maif()
