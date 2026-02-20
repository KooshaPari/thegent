import sys
from pathlib import Path

from thegent.cli_impl import _parse_work_stream_md

ws_path = Path("docs/reference/WORK_STREAM.md").resolve()
parsed = _parse_work_stream_md(ws_path)


if parsed["claimed"]:
    pass
