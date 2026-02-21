import logging
from pathlib import Path

from thegent.skills.terminal import capture_tmux_pane, is_claude_code_pane, list_tmux_panes

logger = logging.getLogger(__name__)


class SessionScraper:
    """MTSP-18: Session Scraper to extract user prompts and context.
    Focuses on terminal panes (tmux) and local history files.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def scrape_tmux_prompts(self) -> list[str]:
        """Scrape likely user prompts from active Claude Code tmux panes."""
        prompts = []
        panes = list_tmux_panes()

        for pane in panes:
            if is_claude_code_pane(pane):
                content = capture_tmux_pane(pane.pane_id, last_lines=100)
                # Heuristic: Find lines starting with '>' or common prompt markers in Claude Code
                # Claude Code often uses a specific icon or '>' for user input
                # Let's look for blocks of text that look like user intent
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    # Example heuristic for Claude Code prompt:
                    if line.startswith(">") and len(line) > 2:
                        prompts.append(line[1:].strip())
                    # Generic heuristic for user intent in session
                    elif "?" in line and len(line) > 10 and not line.startswith("Agent"):
                        # Only take it if it looks like a question/intent
                        prompts.append(line)

        return list(set(prompts))  # Unique only

    def scrape_claude_history(self) -> list[str]:
        """Scrape prompts from local Claude history files if they exist."""
        prompts = []
        history_dirs = [Path.home() / ".claude" / "history", self.project_root / ".claude" / "history"]

        for hdir in history_dirs:
            if hdir.exists():
                # Read most recent history files
                files = sorted(hdir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
                for f in files[:5]:  # Only look at last 5 sessions
                    try:
                        with open(f) as hfile:
                            # Heuristic: search for "prompt" or "user_input" keys
                            # Format depends on version, but usually contains JSON objects
                            import json

                            data = json.load(hfile)
                            if isinstance(data, list):
                                for entry in data:
                                    if "prompt" in entry:
                                        prompts.append(entry["prompt"])
                                    elif "user" in entry and isinstance(entry["user"], str):
                                        prompts.append(entry["user"])
                    except Exception as e:  # noqa: PERF203 - intentional per-item error handling
                        logger.error(f"Error reading history file {f}: {e}")

        return list(set(prompts))

    def scrape_ante_history(self) -> list[str]:
        """Scrape prompts from Ante user_input_history.jsonl."""
        import json

        prompts = []
        history_file = Path.home() / ".ante" / "user_input_history.jsonl"

        if not history_file.exists():
            return prompts

        try:
            with open(history_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if isinstance(data, dict) and "prompt" in data:
                            prompt = data["prompt"]
                            if isinstance(prompt, str) and prompt:
                                prompts.append(prompt)
                    except json.JSONDecodeError:
                        logger.debug(f"Failed to parse JSONL line: {line}")
        except Exception as e:
            logger.error(f"Error reading Ante history file {history_file}: {e}")

        return list(set(prompts))

    def collect_all_recent_prompts(self) -> list[str]:
        """Unified collection from all available scrapers."""
        all_prompts = []
        all_prompts.extend(self.scrape_tmux_prompts())
        all_prompts.extend(self.scrape_claude_history())
        all_prompts.extend(self.scrape_ante_history())
        return list(set(all_prompts))
