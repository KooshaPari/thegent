"""Sandbox Seeding Utility for repeatable connector tests.

WL-316: Sandbox Seeding Utility
Generates, writes, and loads seed records for sandbox environment initialization.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import ClassVar


@dataclass
class SeedRecord:
    """A single seed record for sandbox initialization."""

    wl_id: str
    title: str
    status: str
    priority: str
    connector: str


class SandboxSeeder:
    """Utility for generating and managing sandbox seed records."""

    DEFAULT_SEEDS: ClassVar[list[dict]] = [
        {
            "wl_id": "SEED-DEFAULT-001",
            "title": "Initial sync task",
            "status": "TODO",
            "priority": "P1",
            "connector": "github",
        },
        {
            "wl_id": "SEED-DEFAULT-002",
            "title": "Second sync task",
            "status": "IN_PROGRESS",
            "priority": "P2",
            "connector": "jira",
        },
        {
            "wl_id": "SEED-DEFAULT-003",
            "title": "Completed sync task",
            "status": "DONE",
            "priority": "P3",
            "connector": "slack",
        },
    ]

    @staticmethod
    def generate_seeds(
        count: int,
        connector: str,
        status_pool: list[str] | None = None,
    ) -> list[SeedRecord]:
        """Generate seed records for sandbox initialization.

        Args:
            count: Number of seed records to generate.
            connector: Connector name for all seeds.
            status_pool: List of statuses to cycle through. Defaults to
                         ["TODO", "IN_PROGRESS", "DONE"].

        Returns:
            List of generated SeedRecord objects.
        """
        if status_pool is None:
            status_pool = ["TODO", "IN_PROGRESS", "DONE"]

        seeds = []
        for i in range(1, count + 1):
            wl_id = f"SEED-{i:03d}"
            title = f"Seeded sync task {i}"
            status = status_pool[(i - 1) % len(status_pool)]
            priority = f"P{((i - 1) % 3) + 1}"

            seed = SeedRecord(
                wl_id=wl_id,
                title=title,
                status=status,
                priority=priority,
                connector=connector,
            )
            seeds.append(seed)

        return seeds

    @staticmethod
    def write_seeds(seeds: list[SeedRecord], output_path: Path) -> None:
        """Write seed records to JSON file.

        Args:
            seeds: List of SeedRecord objects to write.
            output_path: Path to write JSON file to.

        Raises:
            ValueError: If output_path parent directory does not exist.
        """
        if not output_path.parent.exists():
            raise ValueError(f"Parent directory does not exist: {output_path.parent}")

        data = [asdict(seed) for seed in seeds]
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_seeds(input_path: Path) -> list[SeedRecord]:
        """Load seed records from JSON file.

        Args:
            input_path: Path to read JSON file from.

        Returns:
            List of loaded SeedRecord objects.

        Raises:
            FileNotFoundError: If input_path does not exist.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Seed file not found: {input_path}")

        with open(input_path) as f:
            data = json.load(f)

        return [SeedRecord(**record) for record in data]
