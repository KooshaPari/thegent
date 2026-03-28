"""Compatibility shim for historical phenotype_thegent_core infra imports."""

from collections.abc import Sequence
from subprocess import CompletedProcess


def run(cmd: str | Sequence[str], **kwargs: object) -> CompletedProcess[str]:
    """Delegate subprocess execution to the canonical implementation."""
    from thegent.infra.shim_subprocess import run as _run

    return _run(cmd, **kwargs)
