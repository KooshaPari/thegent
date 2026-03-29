"""Mesh audit-shadow tests for SCLI-P14.x."""

from pathlib import Path

from thegent.mesh.audit import AuditManager


def test_sync_to_shadow_backups_file_and_creates_shadow_repo(tmp_path: Path) -> None:
    """SCLI-P14.1 and SCLI-P14.2 backup a file path into the shadow repo."""
    project = tmp_path / "project"
    project.mkdir()
    target = project / "data.txt"
    target.write_text("hello")

    manager = AuditManager(project, project / ".mesh")
    manager.sync_to_shadow(target)

    assert (project / ".mesh" / "shadow-repo").exists()
    assert (project / ".mesh" / "shadow-repo" / "data.txt").exists()


def test_recover_file_restores_shadow_copy(tmp_path: Path) -> None:
    """SCLI-P14.3 restores a file from shadow storage when present."""
    project = tmp_path / "project"
    project.mkdir()

    manager = AuditManager(project, project / ".mesh")
    manager.shadow_root.mkdir(parents=True)
    source = manager.shadow_root / "recover.txt"
    source.write_text("restored")

    assert manager.recover_file("recover.txt", "123") is True
    assert (project / "recover.txt").read_text() == "restored"
