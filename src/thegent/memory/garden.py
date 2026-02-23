"""WP-11002: Gardener Synthesis Phase 2 - Memory Garden implementation."""

import orjson as json
import logging
from dataclasses import dataclass
from pathlib import Path

from thegent.memory.seed_detector import Seed

logger = logging.getLogger(__name__)


@dataclass
class GardenCluster:
    id: str
    title: str
    seeds: list[str]  # seed IDs
    summary: str
    tags: list[str]


class MemoryGarden:
    """Manages clusters of idea seeds for long-term memory synthesis."""

    def __init__(self, garden_path: Path) -> None:
        self.garden_path = garden_path
        self.clusters: dict[str, GardenCluster] = {}
        self._load()

    def _load(self) -> None:
        if not self.garden_path.exists():
            return
        try:
            with open(self.garden_path) as f:
                data = json.load(f)
                for c_id, c_data in data.items():
                    self.clusters[c_id] = GardenCluster(**c_data)
        except Exception as e:
            logger.error(f"Failed to load garden: {e}")

    def save(self) -> None:
        self.garden_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.garden_path, "w") as f:
                data = {
                    c_id: {"id": c.id, "title": c.title, "seeds": c.seeds, "summary": c.summary, "tags": c.tags}
                    for c_id, c in self.clusters.items()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save garden: {e}")

    def add_to_cluster(self, cluster_id: str, seed: Seed) -> None:
        if cluster_id not in self.clusters:
            self.clusters[cluster_id] = GardenCluster(
                id=cluster_id, title=f"Cluster {cluster_id}", seeds=[], summary="Newly created cluster", tags=[]
            )

        if seed.id not in self.clusters[cluster_id].seeds:
            self.clusters[cluster_id].seeds.append(seed.id)
            self.save()

    def find_best_cluster(self, seed: Seed) -> str:
        """Find the best cluster for a seed based on keyword matching."""
        # Phase 2: Simple keyword matching. Phase 3: Semantic embedding.
        seed_keywords = set(seed.text.lower().split())

        best_cluster = "general"
        max_overlap = 0

        for c_id, cluster in self.clusters.items():
            cluster_keywords = set(cluster.title.lower().split()) | set(cluster.summary.lower().split())
            overlap = len(seed_keywords & cluster_keywords)
            if overlap > max_overlap:
                max_overlap = overlap
                best_cluster = c_id

        return best_cluster

    def synthesize(self) -> str:
        """Generate a markdown report of the current garden state."""
        lines = ["# Memory Garden Synthesis", ""]
        for cluster in self.clusters.values():
            lines.append(f"## {cluster.title} ({len(cluster.seeds)} seeds)")
            lines.append(cluster.summary)
            lines.append("")
            if cluster.tags:
                lines.append(f"Tags: {', '.join(cluster.tags)}")
                lines.append("")
        return "\n".join(lines)
