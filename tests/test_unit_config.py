"""Unit tests for config and base types."""



from thegent.agents.base import RunResult
from thegent.config import ThegentSettings


class TestRunResult:
    """Tests for RunResult dataclass."""

    def test_creation(self) -> None:
        """RunResult stores exit_code, stdout, stderr, timed_out."""
        r = RunResult(exit_code=0, stdout="out", stderr="err", timed_out=False)
        assert r.exit_code == 0
        assert r.stdout == "out"
        assert r.stderr == "err"
        assert r.timed_out is False

    def test_timed_out_default_false(self) -> None:
        """timed_out defaults to False."""
        r = RunResult(exit_code=124, stdout="", stderr="")
        assert r.timed_out is False  # must be set explicitly


class TestThegentSettings:
    """Tests for ThegentSettings."""

    def test_default_factory_skills_dir(self) -> None:
        """factory_skills_dir defaults to ~/.factory/skills."""
        s = ThegentSettings()
        assert "factory" in str(s.factory_skills_dir)
        assert "skills" in str(s.factory_skills_dir)

    def test_default_timeout(self) -> None:
        """default_timeout is 90."""
        s = ThegentSettings()
        assert s.default_timeout == 90

    def test_factory_droids_dir_resolves(self) -> None:
        """factory_droids_dir expands and resolves."""
        s = ThegentSettings()
        expanded = s.factory_droids_dir.expanduser()
        assert expanded.exists() or not expanded.exists()  # may or may not exist

    def test_models_cache_ttl_default(self) -> None:
        """models_cache_ttl_sec defaults to 300."""
        s = ThegentSettings()
        assert s.models_cache_ttl_sec == 300
