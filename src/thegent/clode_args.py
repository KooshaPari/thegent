"""Argument construction helpers for clode."""

from pathlib import Path


def clode_passthrough_args(
    *,
    cd: Path | None = None,
    debug: bool = False,
    add_dir: list[str] | None = None,
    output_format: str | None = None,
    continue_session: bool = False,
) -> list[str]:
    """Build extra args for claude from passthrough options."""
    args: list[str] = []
    if cd:
        args.extend(["--add-dir", str(cd.resolve())])
    if debug:
        args.append("--debug")
    if add_dir:
        for directory in add_dir:
            args.extend(["--add-dir", directory])
    if output_format:
        args.extend(["--output-format", output_format])
    if continue_session:
        args.append("--continue")
    return args


def free_extra_args(*, triggered_by_agent: bool, resume: str | None, prompt: str | None) -> list[str]:
    """Build free-mode extra args and preserve existing skip-permission behavior."""
    args: list[str] = []
    if not triggered_by_agent:
        args.append("--dangerously-skip-permissions")
    if resume:
        args.extend(["--resume", resume])
    if prompt:
        args.append(prompt)
    return args
