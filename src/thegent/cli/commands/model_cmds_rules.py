"""Model command rules layer — canonical home for cliproxy_ctl machine helpers.

WL-703 hardening: replaces the WL-124 stub semantics for
``cliproxy_login_cmd`` with a concrete-class extraction that mirrors the
WL-700 (L26 wildcard) and WL-702 (audit_verify_cmd) patterns. The
canonical home lives here so monkey-patches at
``thegent.cli.commands.model_cmds_rules.console`` and
``thegent.cli.commands.model_cmds_rules._run_cliproxyctl_machine_command``
resolve cleanly when called from
``thegent.cli.commands.model_cmds.cliproxy_login_cmd`` (the WL-124
stable-import alias used by ``thegent.cli.__init__``).

Contract:
    * ``console`` — module-level Rich ``Console`` instance. Patching it at
      its canonical location suppresses real output during tests.
    * ``_run_cliproxyctl_machine_command(provider, *, settings=None,
      prompt_func=None, force=False, login_timeout=None)`` — delegate to
      :func:`thegent.use_cases.manage_cliproxy_login.run_login`. Returns
      ``{"exit_code": <int>, "message": <str>}`` on success. Raises
      :class:`ValueError` on unknown provider (parity with the
      canonical ``_normalise_provider`` raise) and
      :class:`FileNotFoundError` when the cliproxy binary is missing
      (parity with the canonical ``_run_oauth_login`` raise).

The dispatcher in :func:`thegent.cli.commands.model_cmds.cliproxy_login_cmd`
imports ``_run_cliproxyctl_machine_command`` via local import so test
monkey-patches at the canonical surface (here) take effect at call time.
"""

from __future__ import annotations

from typing import Callable, TypedDict

from rich.console import Console

from thegent.config.settings import ThegentSettings

console: Console = Console()


class CliproxyLoginResult(TypedDict, total=True):
    """Canonical return shape for :func:`_run_cliproxyctl_machine_command`.

    The dispatcher in :mod:`thegent.cli.commands.model_cmds` consumes this
    shape verbatim. ``exit_code == 0`` indicates success; non-zero exit
    codes indicate user-skip (1), persist failure (2), or timeout (124).
    ``message`` is a human-readable summary suitable for the CLI console.

    L10 type-safety tightening (WL-704): this TypedDict replaces the prior
    ``dict[str, Any]`` annotation so the canonical contract is expressible
    in the type system instead of only at runtime. ``total=True`` enforces
    both keys at construction time.
    """

    exit_code: int
    message: str


def _run_cliproxyctl_machine_command(
    provider: str,
    *,
    settings: ThegentSettings | None = None,
    prompt_func: Callable[[str], str] | None = None,
    force: bool = False,
    login_timeout: int | None = None,
) -> CliproxyLoginResult:
    """Execute the canonical cliproxy ``-login`` machine path.

    WL-703 hardening: delegates to the use-case layer
    (``thegent.use_cases.manage_cliproxy_login.run_login``) instead of
    duplicating logic. Mirrors the WL-700 / WL-702 pattern of routing
    the rule through a dedicated module so the canonical surface is
    monkey-patchable from tests.

    Args:
        provider: Provider name (e.g., ``"claude"``, ``"codex"``,
            ``"gemini"``, ``"minimax"``, ``"qwen"``, ``"glm"``).
        settings: Optional :class:`ThegentSettings` instance. Defaults
            to ``ThegentSettings()`` when omitted.
        prompt_func: Optional override for the interactive ``input``
            function. Primarily used for tests.
        force: When ``True``, skip cached-credentials preflight.
        login_timeout: Optional override for the OAuth timeout
            (seconds). Defaults to ``THGENT_LOGIN_TIMEOUT`` env var or
            ``120``.

    Returns:
        ``{"exit_code": <int>, "message": <str>}`` — ``exit_code == 0``
        indicates success; non-zero indicates user-skip or persist
        failure. ``message`` is a human-readable summary suitable for
        the CLI console.

    Raises:
        ValueError: Provider is unknown / not in the canonical
            ``PROVIDER_LOGIN_CONFIG`` union with ``_LOGIN_FLAGS``.
        FileNotFoundError: cliproxy binary is not resolvable on the
            current ``PATH`` (re-raised from the canonical
            ``_run_oauth_login`` helper).
    """
    # Lazy import so test suites that monkey-patch
    # ``thegent.use_cases.manage_cliproxy_login.run_login`` resolve at
    # call time.
    from thegent.use_cases import manage_cliproxy_login

    if settings is None:
        settings = ThegentSettings()

    exit_code = manage_cliproxy_login.run_login(
        settings,
        provider=provider,
        prompt_func=prompt_func,
        force=force,
        login_timeout=login_timeout,
    )
    if exit_code == 0:
        return CliproxyLoginResult(
            exit_code=0,
            message=f"Login successful for provider={provider}",
        )
    if exit_code == 1:
        return CliproxyLoginResult(
            exit_code=1,
            message=f"Login skipped or failed for provider={provider}",
        )
    # exit_code == 2 (persist failure) or 124 (timeout) — surface as
    # failure for the caller to convert into a non-zero CLI exit.
    return CliproxyLoginResult(
        exit_code=int(exit_code),
        message=f"Login failed for provider={provider} (exit_code={exit_code})",
    )


__all__ = [
    "CliproxyLoginResult",
    "console",
    "_run_cliproxyctl_machine_command",
]
