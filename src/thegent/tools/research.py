"""Web research tools for thegent."""

import logging
import shutil
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


def ddg_search(query: str, num_results: int = 5) -> list[dict[str, str]]:
    """
    Search DuckDuckGo using ddgr CLI.
    Returns list of {title, url, abstract}.
    """
    ddgr_path = shutil.which("ddgr")
    if not ddgr_path:
        logger.warning("ddgr CLI not found. Please install it for web research.")
        return [{"error": "ddgr not installed. Run 'brew install ddgr' or equivalent."}]

    try:
        # Run ddgr in non-interactive mode, json output if supported,
        # but ddgr usually outputs text. We'll use --json if available or parse.
        # Actually ddgr has --json.
        result = subprocess.run(
            [
                "ddgr",
                "--json",
                "-n",
                str(num_results),
                query,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        import json

        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"ddgr failed: {e.stderr}")
        return [{"error": f"Search failed: {e.stderr}"}]
    except Exception as e:
        logger.error(f"Error during ddg search: {e}")
        return [{"error": str(e)}]
