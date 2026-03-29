import re

RESUME_RE = re.compile(r"(?:claude|codex|cursor) resume ([\w-]+)")
TOKEN_USAGE_RE = re.compile(
    r"Token usage: total=([\d,]+) input=([\d,]+) \(\+ ([\d,]+) cached\) output=([\d,]+)(?: \(reasoning ([\d,]+)\))?"
)
MCP_ERROR_RE = re.compile(r"⚠ MCP startup incomplete \(failed: (.*?)\)")

text = """
⚠ MCP startup incomplete (failed: playwright)
Token usage: total=17,285,592 input=15,170,126 (+ 277,392,256 cached) output=2,115,466 (reasoning 974,681)
To continue this session, run codex resume 019c5c4a-773b-7cc3-b506-2da2b1586df3
"""

lines = text.splitlines()
for line in lines:
    m = MCP_ERROR_RE.search(line)
    if m:
        # found MCP error in line
        pass
    m = TOKEN_USAGE_RE.search(line)
    if m:
        # found token usage in line
        pass
    m = RESUME_RE.search(line)
    if m:
        # found resume match in line
        pass
