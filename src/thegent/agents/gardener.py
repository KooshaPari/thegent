"""WP-15004: Memory-to-Doc Synthesis Agent (Gardener).
MTSP-17/18: Synthesize session memory and source code into human-readable documentation.
"""

import logging
from datetime import UTC, datetime

from thegent.orchestration.memory import DualMemory
from thegent.orchestration.session_scraper import SessionHistoryScraper

_log = logging.getLogger(__name__)


class GardenerAgent:
    """Agent that synthesizes session memory and codebase state into documentation."""

    def __init__(self, run_id: str, memory_store: DualMemory) -> None:
        self.run_id = run_id
        self.memory = memory_store
        self.scraper = SessionHistoryScraper()

    def synthesize(self, session_dir: str) -> str:
        """Analyze session logs and synthesize documentation."""
        _log.info("Gardener synthesis started for session: %s", session_dir)

        # 1. Scrape session logs
        logs = self.scraper.scrape(session_dir)

        # 2. Extract key decisions (simulated logic)
        decisions = []
        for log in logs:
            if "decision" in log.get("content", "").lower():
                decisions.append(log.get("content"))

        # 3. Format synthesized report
        report = [
            "# 🌿 Gardener Session Synthesis",
            f"**Session ID**: {self.run_id}",
            f"**Generated At**: {datetime.now(UTC).isoformat()}",
            "\n## Key Decisions",
        ]

        if not decisions:
            report.append("- No explicit decisions captured in session logs.")
        else:
            for i, d in enumerate(decisions, 1):
                report.append(f"{i}. {d}")

        report.append("\n## Memory Artifacts")
        for artifact in self.memory.list_artifacts():
            report.append(f"- {artifact.get('id')} ({artifact.get('type')})")

        _log.info("Gardener synthesis complete.")
        return "\n".join(report)

    def write_to_docset(self, synthesized_doc: str, output_path: str):
        """Write synthesized doc to the project's documentation set."""
        with open(output_path, "w") as f:
            f.write(synthesized_doc)
        _log.info("Gardener documentation written to: %s", output_path)
