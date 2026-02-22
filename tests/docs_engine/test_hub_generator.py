"""Tests for VitePress federation hub generator.

# @trace FR-DOCS-013
"""
from docs_engine.hub.generator import HubGenerator


def test_hub_generator_creates_index(tmp_path):
    hub_dir = tmp_path / "docs-hub"
    gen = HubGenerator(hub_dir=hub_dir, projects={"thegent": "../thegent/docs"})
    gen.generate()
    assert (hub_dir / "index.md").exists()
    content = (hub_dir / "index.md").read_text()
    assert "thegent" in content


def test_hub_generator_creates_vitepress_config(tmp_path):
    hub_dir = tmp_path / "docs-hub"
    gen = HubGenerator(hub_dir=hub_dir, projects={"thegent": "../thegent/docs"})
    gen.generate()
    config = hub_dir / ".vitepress" / "config.ts"
    assert config.exists()
    content = config.read_text()
    assert "thegent" in content


def test_hub_generator_creates_package_json(tmp_path):
    hub_dir = tmp_path / "docs-hub"
    gen = HubGenerator(hub_dir=hub_dir, projects={"thegent": "../thegent/docs"})
    gen.generate()
    pkg = hub_dir / "package.json"
    assert pkg.exists()


def test_hub_generator_idempotent(tmp_path):
    hub_dir = tmp_path / "docs-hub"
    gen = HubGenerator(hub_dir=hub_dir, projects={"thegent": "../thegent/docs"})
    gen.generate()
    gen.generate()  # second call should not raise
    assert (hub_dir / "index.md").exists()
