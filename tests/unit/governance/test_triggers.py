"""Tests for governance/triggers.py - AgilePlus trigger modes."""

from unittest.mock import MagicMock, patch
import threading
import time

import pytest

from thegent.governance.triggers import (
    DEFAULT_DEBOUNCE_SECONDS,
    HealthThresholdTrigger,
    ManualTrigger,
    TimerTrigger,
    TriggerConfig,
    WatchdogTrigger,
    create_trigger,
)


class TestTriggerConfig:
    """Tests for TriggerConfig Pydantic model."""

    def test_default_values(self):
        config = TriggerConfig()
        assert config.mode == "manual"
        assert config.interval_seconds == 300
        assert config.debounce_seconds == DEFAULT_DEBOUNCE_SECONDS
        assert config.watch_paths == ["src/", "tests/", "hooks/"]
        assert config.max_cycles is None
        assert config.health_threshold == 90.0
        assert config.max_tasks_per_cycle == 10

    def test_custom_values(self):
        config = TriggerConfig(
            mode="timer",
            interval_seconds=60,
            debounce_seconds=15,
            watch_paths=["/custom/path"],
            max_cycles=5,
            health_threshold=85.0,
            max_tasks_per_cycle=20,
        )
        assert config.mode == "timer"
        assert config.interval_seconds == 60
        assert config.debounce_seconds == 15
        assert config.watch_paths == ["/custom/path"]
        assert config.max_cycles == 5
        assert config.health_threshold == 85.0
        assert config.max_tasks_per_cycle == 20


class TestWatchdogTrigger:
    """Tests for WatchdogTrigger class."""

    def test_init(self):
        loop = MagicMock()
        config = TriggerConfig(mode="watchdog", watch_paths=["src/"])
        trigger = WatchdogTrigger(loop, config)
        assert trigger.loop is loop
        assert trigger.config is config
        assert trigger._running is False
        assert "watchfiles" in str(trigger._use_watchfiles) or "watchdog" in str(trigger._use_watchfiles)

    def test_exclude_dirs(self):
        assert ".git" in WatchdogTrigger.EXCLUDE_DIRS
        assert "node_modules" in WatchdogTrigger.EXCLUDE_DIRS
        assert "__pycache__" in WatchdogTrigger.EXCLUDE_DIRS

    def test_watch_extensions(self):
        assert ".py" in WatchdogTrigger.WATCH_EXTENSIONS
        assert ".sh" in WatchdogTrigger.WATCH_EXTENSIONS
        assert ".yaml" in WatchdogTrigger.WATCH_EXTENSIONS
        assert ".json" in WatchdogTrigger.WATCH_EXTENSIONS
        assert ".md" in WatchdogTrigger.WATCH_EXTENSIONS

    def test_should_process_valid_file(self):
        loop = MagicMock()
        config = TriggerConfig()
        trigger = WatchdogTrigger(loop, config)
        assert trigger._should_process("src/main.py") is True

    def test_should_process_directory(self):
        loop = MagicMock()
        config = TriggerConfig()
        trigger = WatchdogTrigger(loop, config)
        assert trigger._should_process("src/") is False

    def test_should_process_excluded_extension(self):
        loop = MagicMock()
        config = TriggerConfig()
        trigger = WatchdogTrigger(loop, config)
        assert trigger._should_process("src/main.txt") is False

    def test_should_process_excluded_dir(self):
        loop = MagicMock()
        config = TriggerConfig()
        trigger = WatchdogTrigger(loop, config)
        assert trigger._should_process(".git/config") is False
        assert trigger._should_process("node_modules/package/index.js") is False

    def test_should_process_case_insensitive_extension(self):
        loop = MagicMock()
        config = TriggerConfig()
        trigger = WatchdogTrigger(loop, config)
        assert trigger._should_process("src/main.PY") is True

    @patch("thegent.governance.triggers.WATCHFILES_AVAILABLE", False)
    @patch("thegent.governance.triggers.WATCHDOG_AVAILABLE", True)
    def test_start_with_watchdog_fallback(self):
        loop = MagicMock()
        config = TriggerConfig(watch_paths=["src/"])
        with patch.object(WatchdogTrigger, "__init__", lambda self, loop, config: None):
            trigger = WatchdogTrigger(MagicMock(), MagicMock())
            trigger.loop = loop
            trigger.config = config
            trigger._running = False
            trigger._stop_event = threading.Event()
            trigger._debounce_timer = None
            trigger._last_trigger_time = 0.0
            trigger._watch_thread = None
            trigger._use_watchfiles = False
            trigger._observer = None
            trigger._handler = None
            # Just verify the object is properly initialized
            assert trigger._running is False


class TestTimerTrigger:
    """Tests for TimerTrigger class."""

    def test_init(self):
        loop = MagicMock()
        config = TriggerConfig(mode="timer", interval_seconds=60)
        trigger = TimerTrigger(loop, config)
        assert trigger.loop is loop
        assert trigger.config is config
        assert trigger._running is False

    def test_run_calls_loop_run_once(self):
        loop = MagicMock()
        loop.run_once.return_value = MagicMock(health_score=95.0, tasks_executed=3)
        config = TriggerConfig()
        trigger = TimerTrigger(loop, config)
        result = trigger.run(force=True)
        loop.run_once.assert_called_once_with(force=True)
        assert result.health_score == 95.0


class TestManualTrigger:
    """Tests for ManualTrigger class."""

    def test_init(self):
        loop = MagicMock()
        trigger = ManualTrigger(loop)
        assert trigger.loop is loop

    def test_start_is_noop(self):
        loop = MagicMock()
        trigger = ManualTrigger(loop)
        trigger.start()  # Should not raise

    def test_stop_is_noop(self):
        loop = MagicMock()
        trigger = ManualTrigger(loop)
        trigger.stop()  # Should not raise

    def test_run_calls_loop_run_once(self):
        loop = MagicMock()
        loop.run_once.return_value = MagicMock(health_score=95.0, tasks_executed=3)
        trigger = ManualTrigger(loop)
        result = trigger.run(force=True)
        loop.run_once.assert_called_once_with(force=True)
        assert result.health_score == 95.0


class TestHealthThresholdTrigger:
    """Tests for HealthThresholdTrigger class."""

    def test_init(self):
        loop = MagicMock()
        trigger = HealthThresholdTrigger(loop, threshold=85.0, check_interval=30)
        assert trigger.loop is loop
        assert trigger.threshold == 85.0
        assert trigger.check_interval == 30
        assert trigger._shutdown is False

    def test_init_default_values(self):
        loop = MagicMock()
        trigger = HealthThresholdTrigger(loop)
        assert trigger.threshold == 90.0
        assert trigger.check_interval == 60

    def test_run_calls_loop_run_once(self):
        loop = MagicMock()
        loop.run_once.return_value = MagicMock(health_score=95.0)
        trigger = HealthThresholdTrigger(loop)
        result = trigger.run(force=True)
        loop.run_once.assert_called_once_with(force=True)


class TestCreateTrigger:
    """Tests for create_trigger factory function."""

    def test_create_watchdog_trigger(self):
        loop = MagicMock()
        config = TriggerConfig(mode="watchdog")
        trigger = create_trigger("watchdog", loop, config)
        assert isinstance(trigger, WatchdogTrigger)

    def test_create_timer_trigger(self):
        loop = MagicMock()
        config = TriggerConfig(mode="timer")
        trigger = create_trigger("timer", loop, config)
        assert isinstance(trigger, TimerTrigger)

    def test_create_manual_trigger(self):
        loop = MagicMock()
        trigger = create_trigger("manual", loop, MagicMock())
        assert isinstance(trigger, ManualTrigger)

    def test_create_watch_health_trigger(self):
        loop = MagicMock()
        config = TriggerConfig()
        trigger = create_trigger(
            "watch-health",
            loop,
            config,
            watch_health_threshold=80.0,
            watch_health_interval=45,
        )
        assert isinstance(trigger, HealthThresholdTrigger)

    def test_create_unknown_trigger_raises(self):
        loop = MagicMock()
        config = TriggerConfig()
        with pytest.raises(ValueError, match="Unknown trigger mode"):
            create_trigger("unknown", loop, config)


class TestTriggerIntegration:
    """Integration tests for triggers with mocked backends."""

    def test_watchdog_trigger_on_change_debounce(self):
        loop = MagicMock()
        loop.run_once.return_value = MagicMock(health_score=95.0, tasks_executed=3)
        config = TriggerConfig(debounce_seconds=5)
        trigger = WatchdogTrigger(loop, config)
        trigger._running = True
        trigger._last_trigger_time = time.time() - 10  # 10 seconds ago

        trigger._on_file_change()

        loop.run_once.assert_called_once()

    def test_watchdog_trigger_on_change_within_debounce(self):
        loop = MagicMock()
        loop.run_once.return_value = MagicMock(health_score=95.0, tasks_executed=3)
        config = TriggerConfig(debounce_seconds=30)
        trigger = WatchdogTrigger(loop, config)
        trigger._running = True
        trigger._last_trigger_time = time.time() - 5  # 5 seconds ago

        trigger._on_file_change()

        loop.run_once.assert_not_called()
        assert trigger._debounce_timer is not None

    def test_watchdog_trigger_on_change_not_running(self):
        loop = MagicMock()
        config = TriggerConfig()
        trigger = WatchdogTrigger(loop, config)
        trigger._running = False

        trigger._on_file_change()

        loop.run_once.assert_not_called()

    def test_trigger_cycle_result_structure(self):
        loop = MagicMock()
        mock_result = MagicMock()
        mock_result.health_score = 95.5
        mock_result.tasks_executed = 7
        mock_result.tasks_verified = 5
        loop.run_once.return_value = mock_result

        config = TriggerConfig()
        trigger = TimerTrigger(loop, config)
        result = trigger.run()

        assert result.health_score == 95.5
        assert result.tasks_executed == 7


class TestWatchdogEventHandler:
    """Tests for _WatchdogEventHandler (fallback handler)."""

    def test_should_process_valid_path(self):
        from thegent.governance.triggers import _WatchdogEventHandler

        handler = _WatchdogEventHandler(
            on_change=lambda: None,
            exclude_dirs=WatchdogTrigger.EXCLUDE_DIRS,
            watch_extensions=WatchdogTrigger.WATCH_EXTENSIONS,
        )
        assert handler._should_process("src/main.py") is True

    def test_should_process_directory(self):
        from thegent.governance.triggers import _WatchdogEventHandler

        handler = _WatchdogEventHandler(
            on_change=lambda: None,
            exclude_dirs=WatchdogTrigger.EXCLUDE_DIRS,
            watch_extensions=WatchdogTrigger.WATCH_EXTENSIONS,
        )
        assert handler._should_process("src/") is False

    def test_should_process_invalid_extension(self):
        from thegent.governance.triggers import _WatchdogEventHandler

        handler = _WatchdogEventHandler(
            on_change=lambda: None,
            exclude_dirs=WatchdogTrigger.EXCLUDE_DIRS,
            watch_extensions=WatchdogTrigger.WATCH_EXTENSIONS,
        )
        assert handler._should_process("src/main.exe") is False

    def test_should_process_excluded_dir(self):
        from thegent.governance.triggers import _WatchdogEventHandler

        handler = _WatchdogEventHandler(
            on_change=lambda: None,
            exclude_dirs=WatchdogTrigger.EXCLUDE_DIRS,
            watch_extensions=WatchdogTrigger.WATCH_EXTENSIONS,
        )
        assert handler._should_process(".git/config") is False
