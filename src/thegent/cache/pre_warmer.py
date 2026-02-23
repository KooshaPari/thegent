"""Predictive cache pre-warmer: proactively loads likely-needed data.

Usage pattern::

    cache = MultiLevelCache(l1_maxsize=500, l1_ttl=120)
    warmer = CachePreWarmer(cache)

    warmer.register_strategy(
        WarmingStrategy(
            name="my_strategy",
            predict_fn=lambda: ["key1", "key2", "key3"],
            load_fn=lambda key: fetch_expensive(key),
            schedule_seconds=300,
        )
    )

    # One-shot warm run
    results = warmer.warm_all()

    # Continuous background daemon
    warmer.start_background()
    ...
    warmer.stop_background()

FR traceability: FR-CACHE-003 (predictive pre-warming based on usage patterns)
"""

from __future__ import annotations

import contextlib
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from thegent.cache.multi_level import MultiLevelCache

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class WarmingStrategy:
    """Configuration for a single pre-warming strategy.

    Attributes:
        name:             Unique name for this strategy (used in stats/logs).
        predict_fn:       Callable returning a list of keys to pre-warm.
                          Called once per warming cycle.
        load_fn:          Callable accepting a single key and returning the value
                          to cache for that key.  Called once per predicted key.
        schedule_seconds: How often (in seconds) the background daemon should
                          run this strategy.  Defaults to 300 (5 minutes).
    """

    name: str
    predict_fn: Callable[[], list[str]]
    load_fn: Callable[[str], Any]
    schedule_seconds: float = 300.0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("WarmingStrategy.name must not be empty")
        if self.schedule_seconds <= 0:
            raise ValueError("WarmingStrategy.schedule_seconds must be positive")


@dataclass
class _StrategyState:
    """Runtime state tracked per strategy by the pre-warmer."""

    strategy: WarmingStrategy
    last_run: datetime | None = None
    warm_count: int = 0
    error_count: int = 0
    last_error: str | None = field(default=None, repr=False)


# ---------------------------------------------------------------------------
# CachePreWarmer
# ---------------------------------------------------------------------------


class CachePreWarmer:
    """Predictive pre-warmer that proactively loads likely-needed data into cache.

    Supports multiple :class:`WarmingStrategy` instances, each providing:
    - A *predict_fn* that returns a list of keys expected to be needed soon.
    - A *load_fn* that fetches the data for a given key.

    Warming can be triggered manually (:meth:`warm_all`) or automatically via
    a background daemon thread (:meth:`start_background` / :meth:`stop_background`).

    Args:
        cache: The :class:`~thegent.cache.MultiLevelCache` instance to warm.
    """

    def __init__(self, cache: MultiLevelCache) -> None:
        self._cache = cache
        self._strategies: dict[str, _StrategyState] = {}
        self._lock = threading.Lock()

        # Background daemon state
        self._bg_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._total_warm_count = 0
        self._last_run: datetime | None = None

    # ------------------------------------------------------------------
    # Strategy registration
    # ------------------------------------------------------------------

    def register_strategy(self, strategy: WarmingStrategy) -> None:
        """Register a :class:`WarmingStrategy` with the pre-warmer.

        Re-registering a strategy with the same name replaces the existing one.

        Args:
            strategy: The strategy to register.
        """
        with self._lock:
            self._strategies[strategy.name] = _StrategyState(strategy=strategy)
        logger.debug(
            "Registered warming strategy %r (schedule=%.1fs)",
            strategy.name,
            strategy.schedule_seconds,
        )

    def unregister_strategy(self, name: str) -> bool:
        """Remove a previously registered strategy by name.

        Args:
            name: Strategy name to remove.

        Returns:
            True if a strategy was removed, False if it was not found.
        """
        with self._lock:
            removed = self._strategies.pop(name, None)
        if removed is not None:
            logger.debug("Unregistered warming strategy %r", name)
            return True
        return False

    # ------------------------------------------------------------------
    # Manual warming
    # ------------------------------------------------------------------

    def warm_key(self, key: str, load_fn: Callable[[], Any]) -> bool:
        """Warm a single key by calling *load_fn* and storing the result in cache.

        Args:
            key:     Cache key to warm.
            load_fn: Zero-argument callable that returns the value for *key*.
                     Must not raise; exceptions are caught and logged.

        Returns:
            True if the key was successfully warmed (value fetched and stored),
            False if *load_fn* raised or returned None.
        """
        try:
            value = load_fn()
        except Exception as exc:
            logger.warning("warm_key(%r): load_fn raised: %s", key, exc)
            return False

        if value is None:
            logger.debug("warm_key(%r): load_fn returned None; skipping", key)
            return False

        self._cache.set(key, value)
        with self._lock:
            self._total_warm_count += 1
        logger.debug("warm_key(%r): warmed successfully", key)
        return True

    def warm_all(self) -> dict[str, bool]:
        """Run all registered strategies and warm every predicted key.

        Each strategy's *predict_fn* is called to obtain keys; then
        *load_fn* is called for each key.  Errors in individual keys are
        caught and recorded without aborting remaining keys.

        Returns:
            Mapping of ``key -> bool`` indicating whether each key was
            successfully warmed.  The dict preserves insertion order
            (strategies run in registration order).
        """
        results: dict[str, bool] = {}
        now = _utcnow()

        with self._lock:
            states = list(self._strategies.values())

        for state in states:
            self._warm_strategy(state, results, now)

        with self._lock:
            self._last_run = now

        return results

    # ------------------------------------------------------------------
    # Background daemon
    # ------------------------------------------------------------------

    def start_background(self) -> None:
        """Start a daemon thread that periodically warms the cache.

        The daemon respects each strategy's *schedule_seconds*: a strategy is
        only warmed when at least *schedule_seconds* have elapsed since its
        last run.  The thread polls every second for fine-grained scheduling.

        Calling this method when a daemon is already running has no effect.
        """
        with self._lock:
            if self._bg_thread is not None and self._bg_thread.is_alive():
                logger.debug("Background warmer already running; ignoring start_background()")
                return

            self._stop_event.clear()
            thread = threading.Thread(
                target=self._bg_loop,
                name="CachePreWarmer-daemon",
                daemon=True,
            )
            self._bg_thread = thread

        thread.start()
        logger.info("CachePreWarmer background daemon started")

    def stop_background(self, timeout: float = 5.0) -> bool:
        """Signal the background daemon to stop and wait for it to exit.

        Args:
            timeout: Maximum seconds to wait for the daemon thread to exit.

        Returns:
            True if the thread stopped within *timeout*, False if it timed out.
        """
        self._stop_event.set()

        with self._lock:
            thread = self._bg_thread

        if thread is None:
            return True

        thread.join(timeout=timeout)
        alive = thread.is_alive()
        if not alive:
            with self._lock:
                self._bg_thread = None
            logger.info("CachePreWarmer background daemon stopped")
        else:
            logger.warning(
                "CachePreWarmer background daemon did not stop within %.1fs",
                timeout,
            )
        return not alive

    @property
    def is_running(self) -> bool:
        """Return True if the background daemon thread is currently alive."""
        with self._lock:
            return self._bg_thread is not None and self._bg_thread.is_alive()

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        """Return a snapshot of pre-warmer statistics.

        Returns:
            Dict with keys:
            - ``strategies``: number of registered strategies
            - ``warm_count``: total successful warm operations across all strategies
            - ``last_run``: datetime of the last :meth:`warm_all` call, or None
            - ``background_running``: bool — whether the daemon is active
            - ``strategy_stats``: list of per-strategy dicts
        """
        with self._lock:
            strategy_stats = [
                {
                    "name": state.strategy.name,
                    "schedule_seconds": state.strategy.schedule_seconds,
                    "warm_count": state.warm_count,
                    "error_count": state.error_count,
                    "last_run": state.last_run,
                    "last_error": state.last_error,
                }
                for state in self._strategies.values()
            ]
            return {
                "strategies": len(self._strategies),
                "warm_count": self._total_warm_count,
                "last_run": self._last_run,
                "background_running": self._bg_thread is not None and self._bg_thread.is_alive(),
                "strategy_stats": strategy_stats,
            }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _bg_loop(self) -> None:
        """Main loop for the background daemon thread."""
        logger.debug("CachePreWarmer daemon loop starting")
        while not self._stop_event.is_set():
            now = _utcnow()

            with self._lock:
                states = list(self._strategies.values())

            for state in states:
                if self._stop_event.is_set():
                    break
                if _should_run(state, now):
                    self._warm_strategy_safe(state)

            # Poll at 1-second granularity so we can respond quickly to stop signals
            self._stop_event.wait(timeout=1.0)

        logger.debug("CachePreWarmer daemon loop exiting")

    def _warm_strategy(
        self,
        state: _StrategyState,
        results: dict[str, bool],
        now: datetime,
    ) -> None:
        """Run a strategy and accumulate results into *results*."""
        strategy = state.strategy
        try:
            keys = strategy.predict_fn()
        except Exception as exc:
            logger.warning("Strategy %r predict_fn raised: %s", strategy.name, exc)
            with self._lock:
                state.error_count += 1
                state.last_error = str(exc)
            return

        for key in keys:
            load_fn = strategy.load_fn
            success = self.warm_key(key, lambda k=key, fn=load_fn: fn(k))
            results[key] = success
            if success:
                with self._lock:
                    state.warm_count += 1
            else:
                with self._lock:
                    state.error_count += 1

        with self._lock:
            state.last_run = now

    def _warm_strategy_safe(self, state: _StrategyState) -> None:
        """Run a strategy's warming cycle catching all exceptions (used by daemon)."""
        now = _utcnow()
        with contextlib.suppress(Exception):
            self._warm_strategy(state, {}, now)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _utcnow() -> datetime:
    """Return current UTC datetime (extracted for testability)."""
    return datetime.now(UTC)


def _should_run(state: _StrategyState, now: datetime) -> bool:
    """Return True if the strategy is due for a warming run."""
    if state.last_run is None:
        return True
    elapsed = (now - state.last_run).total_seconds()
    return elapsed >= state.strategy.schedule_seconds


# ---------------------------------------------------------------------------
# Built-in strategies
# ---------------------------------------------------------------------------


def model_list_strategy(
    load_fn: Callable[[str], Any],
    model_keys: list[str] | None = None,
    schedule_seconds: float = 300.0,
) -> WarmingStrategy:
    """Return a strategy that pre-warms cached model-list metadata.

    Args:
        load_fn:          Function to load the value for a given model key.
        model_keys:       Explicit list of model cache keys to pre-warm.
                          Defaults to a standard set of common model identifiers.
        schedule_seconds: Warming interval in seconds (default: 300).

    Returns:
        A configured :class:`WarmingStrategy` named ``"model_list"``.
    """
    if model_keys is None:
        model_keys = [
            "models:list",
            "models:anthropic",
            "models:openai",
            "models:google",
            "models:available",
        ]

    frozen_keys = list(model_keys)

    return WarmingStrategy(
        name="model_list",
        predict_fn=lambda: frozen_keys,
        load_fn=load_fn,
        schedule_seconds=schedule_seconds,
    )


def session_list_strategy(
    load_fn: Callable[[str], Any],
    session_keys: list[str] | None = None,
    schedule_seconds: float = 300.0,
) -> WarmingStrategy:
    """Return a strategy that pre-warms cached session-list metadata.

    Args:
        load_fn:          Function to load the value for a given session key.
        session_keys:     Explicit list of session cache keys to pre-warm.
                          Defaults to a standard set of common session identifiers.
        schedule_seconds: Warming interval in seconds (default: 300).

    Returns:
        A configured :class:`WarmingStrategy` named ``"session_list"``.
    """
    if session_keys is None:
        session_keys = [
            "sessions:active",
            "sessions:recent",
            "sessions:all",
        ]

    frozen_keys = list(session_keys)

    return WarmingStrategy(
        name="session_list",
        predict_fn=lambda: frozen_keys,
        load_fn=load_fn,
        schedule_seconds=schedule_seconds,
    )
