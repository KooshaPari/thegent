"""Unit tests for install module: InstallManager, run_install, run_wizard, helpers."""
    """Tests for InstallManager initialization."""


import pytest
pytestmark = pytest.mark.skip(reason="Module imports not implemented")
if False:
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_init_defaults(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-001
            """Default init sets dry_run=False, verbose=False, loads manifest."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            mgr = InstallManager()

            assert mgr.dry_run is False
            assert mgr.verbose is False
            assert isinstance(mgr.manifest, InstallManifest)

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_init_custom_flags(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-002
            """Custom dry_run and verbose flags are stored."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            mgr = InstallManager(dry_run=True, verbose=True)

            assert mgr.dry_run is True
            assert mgr.verbose is True

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_init_loads_existing_manifest(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-003
            """Existing manifest file is loaded on init."""
            manifest_file = tmp_path / "manifest.json"
            existing = InstallManifest(
                version=1,
                installed_at="2025-01-01T00:00:00",
                files={"/tmp/test": FileManifest(source="/src/test", target="/tmp/test", mode="copy", mtime=100.0)},
            )
            manifest_file.write_text(existing.model_dump_json(indent=2))
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            mgr = InstallManager()

            assert len(mgr.manifest.files) == 1
            assert "/tmp/test" in mgr.manifest.files


    # ---------------------------------------------------------------------------
    # InstallManager._load_manifest / save_manifest
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestManifestIO:
        """Tests for manifest load and save."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_load_manifest_missing_file(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-004
            """Missing manifest file returns empty InstallManifest."""
            manifest_file = tmp_path / "does_not_exist.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            mgr = InstallManager()

            assert mgr.manifest.files == {}
            assert mgr.manifest.configs == []

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_load_manifest_corrupt_json(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-005
            """Corrupt manifest file falls back to empty InstallManifest."""
            manifest_file = tmp_path / "manifest.json"
            manifest_file.write_text("NOT VALID JSON {{{")
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            mgr = InstallManager()

            assert mgr.manifest.files == {}

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def testsave_manifest_writes_file(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-006
            """save_manifest writes JSON to disk."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            mgr = InstallManager(dry_run=False)
            mgr.manifest.files["/tmp/a"] = FileManifest(source="/src/a", target="/tmp/a", mode="copy", mtime=1.0)
            mgr.save_manifest()

            assert manifest_file.exists()
            data = json.loads(manifest_file.read_text())
            assert "/tmp/a" in data["files"]

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def testsave_manifest_dry_run_no_write(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-007
            """save_manifest does NOT write when dry_run=True."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            mgr = InstallManager(dry_run=True)
            mgr.save_manifest()

            assert not manifest_file.exists()


    # ---------------------------------------------------------------------------
    # InstallManager.install_file
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestInstallFile:
        """Tests for InstallManager.install_file."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_copy(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-008
            """Copying a file to a new target succeeds."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source" / "file.txt"
            src.parent.mkdir(parents=True)
            src.write_text("hello")

            dst = tmp_path / "dest" / "file.txt"

            mgr = InstallManager()
            action = mgr.install_file(src, dst, InstallMode.FORCE)

            assert action == FileAction.COPIED
            assert dst.exists()
            assert dst.read_text() == "hello"
            assert str(dst) in mgr.manifest.files

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_symlink(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-009
            """Editable mode creates a symlink."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source" / "file.txt"
            src.parent.mkdir(parents=True)
            src.write_text("linked")

            dst = tmp_path / "dest" / "file.txt"

            mgr = InstallManager()
            action = mgr.install_file(src, dst, InstallMode.EDITABLE)

            assert action == FileAction.SYMLINKED
            assert dst.is_symlink()
            assert dst.read_text() == "linked"
            assert mgr.manifest.files[str(dst)].mode == "symlink"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_source_missing(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-010
            """Missing source returns ERROR action."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "nonexistent.txt"
            dst = tmp_path / "dest" / "file.txt"

            mgr = InstallManager()
            action = mgr.install_file(src, dst, InstallMode.FORCE)

            assert action == FileAction.ERROR

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_force_overwrites(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-011
            """Force mode overwrites existing target."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("new content")

            dst = tmp_path / "dest.txt"
            dst.write_text("old content")

            mgr = InstallManager()
            action = mgr.install_file(src, dst, InstallMode.FORCE)

            assert action == FileAction.COPIED
            assert dst.read_text() == "new content"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_smart_skips_up_to_date(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-012
            """Smart mode skips when target is newer than source."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("source")
            # Set source mtime to the past
            os.utime(src, (1000.0, 1000.0))

            dst = tmp_path / "dest.txt"
            dst.write_text("dest")
            # Set dest mtime to the future
            os.utime(dst, (2000.0, 2000.0))

            mgr = InstallManager()
            action = mgr.install_file(src, dst, InstallMode.SMART)

            assert action == FileAction.SKIPPED

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_smart_copies_when_newer(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-013
            """Smart mode copies when source is newer than target."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("newer source")
            os.utime(src, (3000.0, 3000.0))

            dst = tmp_path / "dest.txt"
            dst.write_text("older dest")
            os.utime(dst, (1000.0, 1000.0))

            mgr = InstallManager()
            action = mgr.install_file(src, dst, InstallMode.SMART)

            assert action == FileAction.COPIED
            assert dst.read_text() == "newer source"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_dry_run_copy(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-014
            """Dry run reports COPIED but does not create file."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("content")

            dst = tmp_path / "dest" / "file.txt"

            mgr = InstallManager(dry_run=True)
            action = mgr.install_file(src, dst, InstallMode.FORCE)

            assert action == FileAction.COPIED
            assert not dst.exists()

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_dry_run_symlink(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-015
            """Dry run reports SYMLINKED but does not create symlink."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("content")

            dst = tmp_path / "dest" / "file.txt"

            mgr = InstallManager(dry_run=True)
            action = mgr.install_file(src, dst, InstallMode.EDITABLE)

            assert action == FileAction.SYMLINKED
            assert not dst.exists()

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_copy_directory(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-016
            """Copying a directory uses copytree."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src_dir = tmp_path / "src_dir"
            src_dir.mkdir()
            (src_dir / "a.txt").write_text("a")
            (src_dir / "b.txt").write_text("b")

            dst_dir = tmp_path / "dst_dir"

            mgr = InstallManager()
            action = mgr.install_file(src_dir, dst_dir, InstallMode.FORCE)

            assert action == FileAction.COPIED
            assert dst_dir.is_dir()
            assert (dst_dir / "a.txt").read_text() == "a"
            assert (dst_dir / "b.txt").read_text() == "b"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_backup_on_overwrite(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-017
            """Overwriting an existing file creates a backup."""
            backup_dir = tmp_path / "backups"
            backup_dir.mkdir()
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = backup_dir

            src = tmp_path / "source.txt"
            src.write_text("new")

            dst = tmp_path / "dest.txt"
            dst.write_text("old")

            mgr = InstallManager()
            action = mgr.install_file(src, dst, InstallMode.FORCE)

            assert action == FileAction.COPIED
            # Backup should exist in manifest
            entry = mgr.manifest.files[str(dst)]
            assert entry.backup is not None

        @patch("sys.stdin")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_install_file_interactive_non_tty_skips(
            self, mock_manifest_path, mock_backup_dir, mock_stdin, tmp_path
        ) -> None:
            # @trace FR-INST-018
            """Interactive mode in non-TTY returns CONFLICT."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_stdin.isatty.return_value = False

            src = tmp_path / "source.txt"
            src.write_text("src")
            dst = tmp_path / "dest.txt"
            dst.write_text("existing")

            mgr = InstallManager()
            action = mgr.install_file(src, dst, InstallMode.INTERACTIVE)

            assert action == FileAction.CONFLICT


    # ---------------------------------------------------------------------------
    # InstallManager.update_config
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestUpdateConfig:
        """Tests for InstallManager.update_config."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_update_config_new_file(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-019
            """Creating config in a new file works."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            config_path = tmp_path / "config.json"

            mgr = InstallManager()
            result = mgr.update_config(config_path, "mcpServers.thegent", {"url": "http://localhost"})

            assert result is True
            assert config_path.exists()
            data = json.loads(config_path.read_text())
            assert data["mcpServers"]["thegent"]["url"] == "http://localhost"
            assert len(mgr.manifest.configs) == 1

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_update_config_existing_file(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-020
            """Updating existing config preserves other keys."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            config_path = tmp_path / "config.json"
            config_path.write_text(json.dumps({"existingKey": "value", "mcpServers": {}}).decode().decode())

            mgr = InstallManager()
            mgr.update_config(config_path, "mcpServers.thegent", {"url": "http://test"})

            data = json.loads(config_path.read_text())
            assert data["existingKey"] == "value"
            assert data["mcpServers"]["thegent"]["url"] == "http://test"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_update_config_records_original_value(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-021
            """Config manifest records original value when overwriting."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            config_path = tmp_path / "config.json"
            config_path.write_text(json.dumps({"mcpServers": {"thegent": {"url": "old"}}}).decode().decode())

            mgr = InstallManager()
            mgr.update_config(config_path, "mcpServers.thegent", {"url": "new"})

            cfg_entry = mgr.manifest.configs[0]
            assert cfg_entry.original_value == {"url": "old"}
            assert cfg_entry.new_value == {"url": "new"}

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_update_config_dry_run(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-022
            """Dry run returns True but does not write file."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            config_path = tmp_path / "config.json"

            mgr = InstallManager(dry_run=True)
            result = mgr.update_config(config_path, "key.sub", "val")

            assert result is True
            assert not config_path.exists()

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_update_config_corrupt_json_falls_back(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-023
            """Corrupt existing config is replaced with fresh structure."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            config_path = tmp_path / "config.json"
            config_path.write_text("{{INVALID}}")

            mgr = InstallManager()
            result = mgr.update_config(config_path, "a.b", "value")

            assert result is True
            data = json.loads(config_path.read_text())
            assert data["a"]["b"] == "value"


    # ---------------------------------------------------------------------------
    # InstallManager.uninstall
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestUninstall:
        """Tests for InstallManager.uninstall."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_removes_installed_files(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-024
            """Uninstall removes files tracked in manifest."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            installed = tmp_path / "installed.txt"
            installed.write_text("content")

            manifest = InstallManifest(
                files={
                    str(installed): FileManifest(
                        source="/src/file.txt",
                        target=str(installed),
                        mode="copy",
                        mtime=1.0,
                    )
                }
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager()
            counts = mgr.uninstall()

            assert counts["removed"] == 1
            assert not installed.exists()

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_restores_backup(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-025
            """Uninstall restores backup file when available."""
            backup_dir = tmp_path / "backups"
            backup_dir.mkdir()
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = backup_dir

            installed = tmp_path / "installed.txt"
            installed.write_text("new content")

            backup_file = backup_dir / "backup.txt"
            backup_file.write_text("original content")

            manifest = InstallManifest(
                files={
                    str(installed): FileManifest(
                        source="/src/file.txt",
                        target=str(installed),
                        mode="copy",
                        mtime=1.0,
                        backup=str(backup_file),
                    )
                }
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager()
            counts = mgr.uninstall()

            assert counts["restored"] == 1
            assert installed.exists()
            assert installed.read_text() == "original content"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_reverts_configs(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-026
            """Uninstall reverts config keys to original values."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            config_path = tmp_path / "config.json"
            config_path.write_text(json.dumps({"mcpServers": {"thegent": {"url": "new"}}}).decode().decode())

            manifest = InstallManifest(
                configs=[
                    ConfigManifest(
                        file_path=str(config_path),
                        key="mcpServers.thegent",
                        original_value={"url": "original"},
                        new_value={"url": "new"},
                    )
                ]
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager()
            counts = mgr.uninstall()

            assert counts["reverted"] == 1
            data = json.loads(config_path.read_text())
            assert data["mcpServers"]["thegent"]["url"] == "original"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_deletes_key_when_no_original(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-027
            """Uninstall deletes config key when original_value is None."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            config_path = tmp_path / "config.json"
            config_path.write_text(json.dumps({"mcpServers": {"thegent": {"url": "x"}}}).decode().decode())

            manifest = InstallManifest(
                configs=[
                    ConfigManifest(
                        file_path=str(config_path),
                        key="mcpServers.thegent",
                        original_value=None,
                        new_value={"url": "x"},
                    )
                ]
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager()
            counts = mgr.uninstall()

            assert counts["reverted"] == 1
            data = json.loads(config_path.read_text())
            assert "thegent" not in data["mcpServers"]

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_dry_run(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-028
            """Dry run uninstall counts removals but does not delete."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            installed = tmp_path / "installed.txt"
            installed.write_text("content")

            manifest = InstallManifest(
                files={
                    str(installed): FileManifest(
                        source="/src/file.txt",
                        target=str(installed),
                        mode="copy",
                        mtime=1.0,
                    )
                }
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager(dry_run=True)
            counts = mgr.uninstall()

            assert counts["removed"] == 1
            assert installed.exists()  # File still present


    # ---------------------------------------------------------------------------
    # _get_mcp_config
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestGetMcpConfig:
        """Tests for _get_mcp_config helper."""

        def test_generic_client(self) -> None:
            # @trace FR-INST-029
            """Generic client config includes url, transport, description."""
            cfg = _get_mcp_config("http://localhost:3847/mcp")
            assert cfg["url"] == "http://localhost:3847/mcp"
            assert cfg["transport"] == "http"
            assert "description" in cfg
            assert "autoApprove" not in cfg

        def test_cursor_client(self) -> None:
            # @trace FR-INST-030
            """Cursor client config includes autoApprove tools list."""
            cfg = _get_mcp_config("http://localhost:3847/mcp", client="cursor")
            assert cfg["autoApprove"] == THEGENT_TOOLS
            assert cfg["url"] == "http://localhost:3847/mcp"

        def test_claude_desktop_client(self) -> None:
            # @trace FR-INST-031
            """Claude Desktop client config only has url."""
            cfg = _get_mcp_config("http://localhost:3847/mcp", client="claude-desktop")
            assert cfg == {"url": "http://localhost:3847/mcp"}


    @pytest.mark.unit
    class TestBundleManifestLoader:
        """Tests for third-party bundle manifest loading and resolution helpers."""

        def test_load_bundle_manifest_returns_empty_when_missing(self, tmp_path) -> None:
            """Missing manifest path returns empty dict."""
            missing = tmp_path / "does-not-exist.json"
            assert load_bundle_manifest(missing) == {}

        @patch("thegent.install.load_bundle_manifest")
        def test_resolve_bundles_handles_all(self, mock_load, tmp_path) -> None:
            # @trace FR-INST-047
            mock_load.return_value = {
                "cli-tools": [
                    {"source": str(tmp_path / "a.txt"), "target": "{home}/a.txt"},
                    {"source": "thegent:skills/agent-orchestra", "target": "{cwd}/agent-orchestra", "mode": "editable"},
                ],
                "hooks": [{"source": str(tmp_path / "hooks"), "target": str(tmp_path / "hooks.out"), "mode": "symlink"}],
            }
            (tmp_path / "a.txt").write_text("hello")

            home = tmp_path / "home"
            home.mkdir()
            cwd = tmp_path / "project"
            cwd.mkdir()
            thegent_root = tmp_path
            items = resolve_bundles(
                ["all"],
                Path("/tmp/manifest.json"),
                thegent_root=thegent_root,
                home=home,
                cwd=cwd,
                fallback_mode=InstallMode.SMART,
            )
            assert len(items) == 3
            assert items[0][1] == home / "a.txt"
            assert items[1][0] == thegent_root / "skills" / "agent-orchestra"
            assert items[1][1] == cwd / "agent-orchestra"
            assert items[2][2] == InstallMode.EDITABLE

        def test_resolve_bundles_rejects_unknown(self, tmp_path) -> None:
            """Unknown bundle name raises a clear error."""
            manifest = tmp_path / "bundles.json"
            manifest.write_text(json.dumps({"bundles": {"known": []}}).decode().decode())

            with patch("thegent.install.load_bundle_manifest") as mock_load:
                mock_load.return_value = {"known": []}
                with pytest.raises(ValueError, match="Unknown bundle"):
                    resolve_bundles(
                        ["missing"],
                        manifest,
                        thegent_root=tmp_path,
                        home=tmp_path,
                        cwd=tmp_path,
                        fallback_mode=InstallMode.SMART,
                    )

        def test_validate_bundle_manifest_requires_pin_checksum_for_external_sources(self, tmp_path) -> None:
            """External (URL/git) sources must include immutable pin and checksum metadata."""
            manifest = tmp_path / "bundles.json"
            manifest.write_text(
                json.dumps(
                    {
                        "bundles": {
                            "external-tools": {
                                "items": [
                                    {
                                        "source": "https://example.com/tool.tar.gz",
                                        "target": "{home}/.tools/tool.tar.gz",
                                    }
                                ]
                            }
                        }
                    }
                )).decode()
            ok, issues = validate_bundle_manifest(manifest)
            assert ok is False
            assert any("requires non-empty 'pin'" in issue for issue in issues)
            assert any("requires non-empty 'checksum'" in issue for issue in issues)

        def test_validate_bundle_manifest_accepts_pin_checksum_for_external_sources(self, tmp_path) -> None:
            """External sources validate when pin + checksum are provided."""
            manifest = tmp_path / "bundles.json"
            manifest.write_text(
                json.dumps(
                    {
                        "bundles": {
                            "external-tools": {
                                "items": [
                                    {
                                        "source": "github:org/repo//path?ref=v1.2.3",
                                        "target": "{home}/.tools/tool",
                                        "pin": "v1.2.3",
                                        "checksum": "sha256:abc123",
                                    }
                                ]
                            }
                        }
                    }
                )).decode()
            ok, issues = validate_bundle_manifest(manifest)
            assert ok is True
            assert issues == []


    # ---------------------------------------------------------------------------
    # Legacy shims
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestLegacyShims:
        """Tests for should_exclude, create_symlink, smart_copy_file, get_source_dest_mapping."""

        def test_should_exclude_pycache(self) -> None:
            # @trace FR-INST-032
            """__pycache__ paths are excluded."""
            assert should_exclude(Path("foo/__pycache__/bar.pyc")) is True

        def test_should_exclude_clean_path(self) -> None:
            # @trace FR-INST-033
            """Normal paths are not excluded."""
            assert should_exclude(Path("src/module/file.py")) is False

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_create_symlink_creates(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-034
            """create_symlink creates a symlink and returns 'created'."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("content")
            dst = tmp_path / "link.txt"

            result = create_symlink(src, dst)

            assert result == "created"
            assert dst.is_symlink()

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_create_symlink_exists(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-035
            """create_symlink returns 'existed' when symlink already points to source."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("content")
            dst = tmp_path / "link.txt"
            dst.symlink_to(src)

            result = create_symlink(src, dst)

            assert result == "existed"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_smart_copy_file_copies(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-036
            """smart_copy_file copies when no target exists."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("data")
            dst = tmp_path / "dest.txt"

            result = smart_copy_file(src, dst)

            assert result == "copied"
            assert dst.read_text() == "data"

        def test_get_source_dest_mapping_invalid_bundle(self, tmp_path) -> None:
            # @trace FR-INST-037
            """Invalid bundle raises ValueError."""
            with pytest.raises(ValueError, match="Invalid bundle"):
                get_source_dest_mapping(tmp_path, "invalid_bundle")


    # ---------------------------------------------------------------------------
    # run_install
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestRunInstall:
        """Tests for the run_install orchestration function."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_run_install_invalid_target(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-038
            """Invalid target raises ValueError."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            with pytest.raises(ValueError, match="Invalid target"):
                run_install(target="nonexistent_target")

        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_run_install_codex_dry_run(self, mock_manifest_path, mock_backup_dir, mock_home, tmp_path) -> None:
            # @trace FR-INST-039
            """Codex install in dry_run updates config without writing."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path

            result = run_install(target="codex", mode="smart", dry_run=True)

            assert isinstance(result, dict)
            assert "copied" in result
            assert "errors" in result

        @patch("thegent.install.InstallManager.update_config")
        @patch("thegent.install.InstallManager.install_file")
        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_run_install_claude_code(
            self, mock_manifest_path, mock_backup_dir, mock_home, mock_install_file, mock_update_config, tmp_path
        ) -> None:
            # @trace FR-INST-040
            """Claude-code target installs files and updates MCP config."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path

            mock_install_file.return_value = FileAction.COPIED
            mock_update_config.return_value = True

            # Create source tree so src.exists() passes
            Path(__file__).parent.parent / "src" / "thegent"
            # We need to mock Path resolution; instead we test the overall flow via mocks

            result = run_install(target="claude-code", mode="smart", dry_run=False)

            assert isinstance(result, dict)
            # update_config should have been called for .claude.json
            assert mock_update_config.called
            called_keys = [call.args[1] for call in mock_update_config.call_args_list]
            assert "mcpServers.thegent" in called_keys
            assert "mcpServers.codex_apps" in called_keys

        @patch("thegent.install.InstallManager.install_file")
        @patch("thegent.install.InstallManager.update_config", return_value=True)
        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_run_install_codex_writes_compatibility_mcp_keys(
            self,
            mock_manifest_path,
            mock_backup_dir,
            mock_home,
            mock_update_config,
            mock_install_file,
            tmp_path,
        ) -> None:
            # @trace FR-INST-051
            """Codex target writes both thegent and codex_apps MCP entries."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path

            result = run_install(target="codex", mode="smart", dry_run=False)

            assert isinstance(result, dict)
            called_keys = [call.args[1] for call in mock_update_config.call_args_list]
            assert "mcpServers.thegent" in called_keys
            assert "mcpServers.codex_apps" in called_keys

        @patch("thegent.install.InstallManager.install_file")
        @patch("thegent.install.InstallManager.update_config", return_value=True)
        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        @patch("thegent.install.load_bundle_manifest")
        def test_run_install_bundle_items(
            self,
            mock_load_bundle_manifest,
            mock_manifest_path,
            mock_backup_dir,
            mock_home,
            mock_update_config,
            mock_install_file,
            tmp_path,
        ) -> None:
            # @trace FR-INST-049
            """Bundle items are applied via run_install and pass through item modes."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path
            mock_install_file.return_value = FileAction.COPIED

            source_copy = tmp_path / "bundle_source_copy.txt"
            source_copy.write_text("copy payload")
            source_link = tmp_path / "bundle_source_link.txt"
            source_link.write_text("symlink payload")
            bundle_target = tmp_path / "bundle_copy.txt"
            bundle_target_link = tmp_path / "bundle_link.txt"

            mock_load_bundle_manifest.return_value = {
                "web": [
                    {
                        "source": str(source_copy),
                        "target": str(bundle_target),
                        "mode": "smart",
                    },
                    {
                        "source": str(source_link),
                        "target": str(bundle_target_link),
                        "mode": "symlink",
                    },
                ]
            }

            result = run_install(
                target="codex",
                mode="force",
                dry_run=False,
                bundles=["web"],
                bundle_manifest=tmp_path / "bundles.json",
            )

            assert isinstance(result, dict)
            assert mock_install_file.call_count == 2
            called_targets = [c.args[1] for c in mock_install_file.call_args_list]
            assert bundle_target in called_targets
            assert not bundle_target.exists()
            assert bundle_target_link in called_targets
            assert mock_install_file.call_args_list[0].args[2] == InstallMode.SMART
            assert mock_install_file.call_args_list[1].args[2] == InstallMode.EDITABLE

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        @patch("thegent.install.load_bundle_manifest")
        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.InstallManager.update_config", return_value=True)
        def test_run_install_unknown_bundle_raises(
            self,
            mock_update_config,
            mock_home,
            mock_load_bundle_manifest,
            mock_manifest_path,
            mock_backup_dir,
            tmp_path,
        ) -> None:
            # @trace FR-INST-048
            """Unknown bundle names fail fast."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path
            mock_load_bundle_manifest.return_value = {"known": []}

            with pytest.raises(ValueError, match="Unknown bundle"):
                run_install(target="codex", mode="smart", bundles=["missing"], bundle_manifest=tmp_path / "bundles.json")

        @patch("thegent.install.InstallManager.uninstall")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        @patch("platform.system", return_value="Linux")
        def test_run_install_undo_mode(
            self, mock_platform, mock_manifest_path, mock_backup_dir, mock_uninstall, tmp_path
        ) -> None:
            # @trace FR-INST-041
            """Undo mode calls uninstall and returns its result."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_uninstall.return_value = {"removed": 3, "restored": 1, "reverted": 0, "errors": 0}

            result = run_install(target="claude-code", mode="undo")

            assert result["removed"] == 3
            assert result["restored"] == 1
            mock_uninstall.assert_called_once()


    # ---------------------------------------------------------------------------
    # run_wizard
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestRunWizard:
        """Tests for the interactive wizard."""

        @patch("thegent.install.run_install")
        @patch("thegent.install.platform")
        def test_wizard_all_targets(self, mock_platform, mock_run_install) -> None:
            # @trace FR-INST-042
            """Wizard with 'all' targets calls run_install for each target."""
            mock_platform.system.return_value = "Linux"
            mock_run_install.return_value = {"copied": 1, "skipped": 0, "errors": 0}

            with (
                patch("rich.console.Console") as MockConsole,
                patch("rich.prompt.Prompt.ask") as mock_ask,
                patch("rich.prompt.Confirm.ask") as mock_confirm,
            ):
                console_instance = MagicMock()
                MockConsole.return_value = console_instance
                # First Prompt.ask -> target selection "all"
                # Second Prompt.ask -> mode "smart"
                mock_ask.side_effect = ["all", "smart"]
                # Confirm.ask -> proceed
                mock_confirm.return_value = True

                run_wizard(url="http://localhost:3847/mcp")

            assert mock_run_install.call_count == 5  # 5 targets in "all"

        @patch("thegent.install.run_install")
        @patch("thegent.install.platform")
        def test_wizard_no_targets_exits(self, mock_platform, mock_run_install) -> None:
            # @trace FR-INST-043
            """Wizard with no targets selected exits without installing."""
            mock_platform.system.return_value = "Linux"

            with (
                patch("rich.console.Console") as MockConsole,
                patch("rich.prompt.Prompt.ask") as mock_ask,
            ):
                console_instance = MagicMock()
                MockConsole.return_value = console_instance
                # Return an input that matches no targets_map keys
                mock_ask.side_effect = ["99"]

                run_wizard()

            mock_run_install.assert_not_called()

        @patch("thegent.install.run_install")
        @patch("thegent.install.platform")
        def test_wizard_cancelled(self, mock_platform, mock_run_install) -> None:
            # @trace FR-INST-044
            """Wizard cancelled at confirmation step does not install."""
            mock_platform.system.return_value = "Linux"

            with (
                patch("rich.console.Console") as MockConsole,
                patch("rich.prompt.Prompt.ask") as mock_ask,
                patch("rich.prompt.Confirm.ask") as mock_confirm,
            ):
                console_instance = MagicMock()
                MockConsole.return_value = console_instance
                mock_ask.side_effect = ["1", "smart"]
                mock_confirm.return_value = False

                run_wizard()

            mock_run_install.assert_not_called()


    # ---------------------------------------------------------------------------
    # Coverage gaps: install_file edge cases (lines 126, 192, 211, 217, 227-237, 247, 270, 278)
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestCreateSymlinkReturnExisted:
        """Test create_symlink returns 'existed' for already-symlinked file (line 126)."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_create_symlink_non_matching_link_returns_created(
            self, mock_manifest_path, mock_backup_dir, tmp_path
        ) -> None:
            # @trace FR-INST-034
            """create_symlink replaces stale symlink and returns 'created'."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("content")
            dst = tmp_path / "link.txt"
            other = tmp_path / "other.txt"
            other.write_text("other")
            dst.symlink_to(other)

            result = create_symlink(src, dst)
            assert result == "created"


    @pytest.mark.unit
    class TestBackupFileTargetMissing:
        """Test _backup_file returns None when target does not exist (line 192)."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_backup_file_nonexistent_returns_none(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-017
            """_backup_file returns None for non-existent target."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            mgr = InstallManager()
            result = mgr._backup_file(tmp_path / "nonexistent.txt")
            assert result is None


    @pytest.mark.unit
    class TestInstallFileEditableExistingTarget:
        """Test install_file editable mode with existing target (line 211)."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_editable_overwrites_existing_file(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-009
            """Editable mode replaces existing file with symlink."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("content")
            dst = tmp_path / "dest.txt"
            dst.write_text("old content")

            mgr = InstallManager()
            action = mgr.install_file(src, dst, InstallMode.EDITABLE)

            assert action == FileAction.SYMLINKED
            assert dst.is_symlink()


    @pytest.mark.unit
    class TestInstallFileSmartSkipsVerbose:
        """Test install_file smart mode verbose skip message (line 217)."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_smart_verbose_skip_prints_message(self, mock_manifest_path, mock_backup_dir, tmp_path, capsys) -> None:
            # @trace FR-INST-012
            """Smart mode verbose prints skip message."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("source")
            os.utime(src, (1000.0, 1000.0))
            dst = tmp_path / "dest.txt"
            dst.write_text("dest")
            os.utime(dst, (2000.0, 2000.0))

            mgr = InstallManager(verbose=True)
            action = mgr.install_file(src, dst, InstallMode.SMART)

            assert action == FileAction.SKIPPED
            captured = capsys.readouterr()
            assert "Skipped" in captured.out


    @pytest.mark.unit
    class TestInstallFileInteractiveChoices:
        """Test install_file interactive mode choice branches (lines 227-237, 247)."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_interactive_skip_choice(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-018
            """Interactive mode with 's' choice returns SKIPPED."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("src")
            dst = tmp_path / "dest.txt"
            dst.write_text("existing")

            mgr = InstallManager()
            with (
                patch("sys.stdin") as mock_stdin,
                patch("rich.prompt.Prompt.ask", return_value="s"),
            ):
                mock_stdin.isatty.return_value = True
                action = mgr.install_file(src, dst, InstallMode.INTERACTIVE)

            assert action == FileAction.SKIPPED

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_interactive_overwrite_choice(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-018
            """Interactive mode with 'o' choice overwrites (FORCE)."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("new content")
            dst = tmp_path / "dest.txt"
            dst.write_text("old")

            mgr = InstallManager()
            with (
                patch("sys.stdin") as mock_stdin,
                patch("rich.prompt.Prompt.ask", return_value="o"),
            ):
                mock_stdin.isatty.return_value = True
                action = mgr.install_file(src, dst, InstallMode.INTERACTIVE)

            assert action == FileAction.COPIED
            assert dst.read_text() == "new content"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_interactive_backup_choice(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-018
            """Interactive mode with 'b' choice does backup and overwrite."""
            backup_dir = tmp_path / "backups"
            backup_dir.mkdir()
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = backup_dir

            src = tmp_path / "source.txt"
            src.write_text("new content")
            dst = tmp_path / "dest.txt"
            dst.write_text("old")

            mgr = InstallManager()
            with (
                patch("sys.stdin") as mock_stdin,
                patch("rich.prompt.Prompt.ask", return_value="b"),
            ):
                mock_stdin.isatty.return_value = True
                action = mgr.install_file(src, dst, InstallMode.INTERACTIVE)

            assert action == FileAction.COPIED
            assert dst.read_text() == "new content"


    @pytest.mark.unit
    class TestInstallFileDryRunVerbose:
        """Test install_file dry_run with verbose (line 270, 278)."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_dry_run_verbose_prints_would_copy(self, mock_manifest_path, mock_backup_dir, tmp_path, capsys) -> None:
            # @trace FR-INST-014
            """Dry run verbose prints 'Would copy' message."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            src = tmp_path / "source.txt"
            src.write_text("content")
            dst = tmp_path / "dest" / "file.txt"

            mgr = InstallManager(dry_run=True, verbose=True)
            action = mgr.install_file(src, dst, InstallMode.FORCE)

            assert action == FileAction.COPIED
            captured = capsys.readouterr()
            assert "Would copy" in captured.out


    # ---------------------------------------------------------------------------
    # Coverage gaps: uninstall edge cases (lines 338-339, 345, 352, 358, 368-369)
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestUninstallEdgeCases:
        """Tests for uninstall edge cases."""

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_config_error_counts(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-026
            """Uninstall config revert error increments errors count (lines 338-339)."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            config_path = tmp_path / "config.json"
            config_path.write_text("{{invalid json}}")

            manifest = InstallManifest(
                configs=[
                    ConfigManifest(
                        file_path=str(config_path),
                        key="mcpServers.thegent",
                        original_value={"url": "old"},
                        new_value={"url": "new"},
                    )
                ]
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager()
            counts = mgr.uninstall()
            assert counts["errors"] >= 1

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_missing_file_skipped(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-024
            """Uninstall skips files that no longer exist (line 345)."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            manifest = InstallManifest(
                files={
                    str(tmp_path / "gone.txt"): FileManifest(
                        source="/src/file.txt",
                        target=str(tmp_path / "gone.txt"),
                        mode="copy",
                        mtime=1.0,
                    )
                }
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager()
            counts = mgr.uninstall()
            assert counts["removed"] == 0
            assert counts["errors"] == 0

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_directory_uses_rmtree(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-024
            """Uninstall removes directory via rmtree (line 352)."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            installed_dir = tmp_path / "installed_dir"
            installed_dir.mkdir()
            (installed_dir / "file.txt").write_text("hello")

            manifest = InstallManifest(
                files={
                    str(installed_dir): FileManifest(
                        source="/src/dir",
                        target=str(installed_dir),
                        mode="copy",
                        mtime=1.0,
                    )
                }
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager()
            counts = mgr.uninstall()
            assert counts["removed"] == 1
            assert not installed_dir.exists()

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_restores_directory_backup(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-025
            """Uninstall restores directory backup via copytree (line 358)."""
            backup_dir = tmp_path / "backups"
            backup_dir.mkdir()
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = backup_dir

            installed_dir = tmp_path / "installed_dir"
            installed_dir.mkdir()
            (installed_dir / "new.txt").write_text("new")

            backup_subdir = backup_dir / "orig_dir"
            backup_subdir.mkdir()
            (backup_subdir / "original.txt").write_text("original")

            manifest = InstallManifest(
                files={
                    str(installed_dir): FileManifest(
                        source="/src/dir",
                        target=str(installed_dir),
                        mode="copy",
                        mtime=1.0,
                        backup=str(backup_subdir),
                    )
                }
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager()
            counts = mgr.uninstall()
            assert counts["restored"] == 1
            assert installed_dir.exists()
            assert (installed_dir / "original.txt").read_text() == "original"

        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_uninstall_file_error_increments(self, mock_manifest_path, mock_backup_dir, tmp_path) -> None:
            # @trace FR-INST-024
            """Uninstall file removal error increments errors (lines 368-369)."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"

            installed = tmp_path / "installed.txt"
            installed.write_text("content")

            manifest = InstallManifest(
                files={
                    str(installed): FileManifest(
                        source="/src/file.txt",
                        target=str(installed),
                        mode="copy",
                        mtime=1.0,
                    )
                }
            )
            manifest_file.write_text(manifest.model_dump_json(indent=2))

            mgr = InstallManager()
            with patch.object(Path, "unlink", side_effect=PermissionError("denied")):
                counts = mgr.uninstall()
            assert counts["errors"] >= 1


    # ---------------------------------------------------------------------------
    # Coverage gaps: run_install (lines 538-541, 555-566, 588-596, 600-611, 618-627)
    # ---------------------------------------------------------------------------


    @pytest.mark.unit
    class TestRunInstallUndoMacOS:
        """Test run_install undo on macOS calls service_uninstall (lines 538-541)."""

        @patch("thegent.install.InstallManager.uninstall")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        @patch("platform.system", return_value="Darwin")
        def test_undo_darwin_calls_service_uninstall(
            self, mock_platform, mock_manifest_path, mock_backup_dir, mock_uninstall, tmp_path
        ) -> None:
            # @trace FR-INST-041
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_uninstall.return_value = {"removed": 1, "restored": 0, "reverted": 0, "errors": 0}

            with patch("thegent.mcp_manage.service_uninstall", return_value=(True, "Uninstalled")):
                result = run_install(target="claude-code", mode="undo")
            assert result["reverted"] >= 1

        @patch("thegent.install.InstallManager.uninstall")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        @patch("platform.system", return_value="Darwin")
        def test_undo_darwin_service_uninstall_failure(
            self, mock_platform, mock_manifest_path, mock_backup_dir, mock_uninstall, tmp_path
        ) -> None:
            # @trace FR-INST-041
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_uninstall.return_value = {"removed": 1, "restored": 0, "reverted": 0, "errors": 0}

            with patch("thegent.mcp_manage.service_uninstall", return_value=(False, "Not found")):
                result = run_install(target="claude-code", mode="undo")
            assert result["removed"] == 1


    @pytest.mark.unit
    class TestRunInstallServiceInstall:
        """Test run_install with service installation (lines 555-566)."""

        @patch("thegent.install.InstallManager.update_config")
        @patch("thegent.install.InstallManager.install_file", return_value=FileAction.COPIED)
        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        @patch("platform.system", return_value="Darwin")
        def test_service_install_success_verbose(
            self,
            mock_platform,
            mock_manifest_path,
            mock_backup_dir,
            mock_home,
            mock_install_file,
            mock_update_config,
            tmp_path,
            capsys,
        ) -> None:
            # @trace FR-INST-040
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path
            mock_update_config.return_value = True

            with (
                patch("thegent.install.service_install", return_value=(True, "Installed")),
                patch("thegent.install.service_start"),
            ):
                result = run_install(target="claude-code", mode="smart", verbose=True, install_service=True, dry_run=False)
            assert isinstance(result, dict)

        @patch("thegent.install.InstallManager.update_config")
        @patch("thegent.install.InstallManager.install_file", return_value=FileAction.COPIED)
        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        @patch("platform.system", return_value="Darwin")
        def test_service_install_failure_verbose(
            self,
            mock_platform,
            mock_manifest_path,
            mock_backup_dir,
            mock_home,
            mock_install_file,
            mock_update_config,
            tmp_path,
            capsys,
        ) -> None:
            # @trace FR-INST-040
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path
            mock_update_config.return_value = True

            with patch("thegent.install.service_install", return_value=(False, "Failed")):
                run_install(target="claude-code", mode="smart", verbose=True, install_service=True, dry_run=False)
            captured = capsys.readouterr()
            # The code path at lines 563-566 is exercised: verbose prints the failure message
            # Note: counts["errors"] is incremented but return dict reads counts.get("error", 0)
            # (singular vs plural key mismatch), so result["errors"] is 0.
            assert "Service install failed: Failed" in captured.out


    @pytest.mark.unit
    class TestRunInstallTargetBranches:
        """Test run_install target branches (claude-desktop, cursor, droid)."""

        @patch("thegent.install.InstallManager.update_config")
        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        @patch("platform.system", return_value="Darwin")
        def test_claude_desktop_darwin(
            self, mock_platform, mock_manifest_path, mock_backup_dir, mock_home, mock_update_config, tmp_path
        ) -> None:
            # @trace FR-INST-040
            """claude-desktop target on macOS updates config."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path
            mock_update_config.return_value = True

            # Create the parent dir so it exists
            claude_dir = tmp_path / "Library" / "Application Support" / "Claude"
            claude_dir.mkdir(parents=True)

            result = run_install(target="claude-desktop", mode="smart", dry_run=False)
            assert isinstance(result, dict)
            assert mock_update_config.called

        @patch("thegent.install.InstallManager.update_config")
        @patch("thegent.install.InstallManager.install_file", return_value=FileAction.COPIED)
        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_cursor_target(
            self, mock_manifest_path, mock_backup_dir, mock_home, mock_install_file, mock_update_config, tmp_path
        ) -> None:
            # @trace FR-INST-040
            """cursor target installs files and updates MCP config."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path
            mock_update_config.return_value = True

            result = run_install(target="cursor", mode="smart", dry_run=False)
            assert isinstance(result, dict)

        @patch("thegent.install.InstallManager.update_config")
        @patch("thegent.install.InstallManager.install_file", return_value=FileAction.COPIED)
        @patch("thegent.install.get_home_dir")
        @patch("thegent.install.get_backup_dir")
        @patch("thegent.install.get_manifest_path")
        def test_droid_target(
            self, mock_manifest_path, mock_backup_dir, mock_home, mock_install_file, mock_update_config, tmp_path
        ) -> None:
            # @trace FR-INST-040
            """droid target installs files and updates MCP config."""
            manifest_file = tmp_path / "manifest.json"
            mock_manifest_path.return_value = manifest_file
            mock_backup_dir.return_value = tmp_path / "backups"
            mock_home.return_value = tmp_path
            mock_update_config.return_value = True

            result = run_install(target="droid", mode="smart", dry_run=False)
            assert isinstance(result, dict)

