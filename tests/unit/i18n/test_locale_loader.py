"""Unit tests for :mod:`thegent.i18n.locale_loader`.

These tests pin the public surface of the locale loader so the cockpit
can rely on ``locale_loader.register_all()`` for cold-start
internationalization.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from thegent import i18n
from thegent.i18n import locale_loader


@pytest.fixture(autouse=True)
def reset_i18n_state() -> Iterator[None]:
    """Keep process-global locale and catalog state isolated per test."""
    i18n.set_locale("en")
    i18n.reset_catalogs()
    yield
    i18n.set_locale("en")
    i18n.reset_catalogs()


def test_locales_dir_exists_and_is_under_i18n_package() -> None:
    base = locale_loader.locales_dir()

    assert base.is_dir()
    assert base.name == "locales"
    assert base.parent.name == "i18n"


def test_shipped_locales_include_english_and_french() -> None:
    codes = locale_loader.discover_locales()

    assert "en" in codes
    assert "fr" in codes


def test_discover_locales_is_sorted_and_deduped(tmp_path: Path) -> None:
    (tmp_path / "de.yaml").write_text("a: A\n", encoding="utf-8")
    (tmp_path / "ar.yaml").write_text("a: A\n", encoding="utf-8")
    (tmp_path / "ja.yaml").write_text("a: A\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")

    codes = locale_loader.discover_locales(tmp_path)

    assert codes == ("ar", "de", "ja")


def test_discover_locales_returns_empty_for_missing_directory(tmp_path: Path) -> None:
    assert locale_loader.discover_locales(tmp_path / "nope") == ()


def test_load_catalog_returns_locale_file_for_en() -> None:
    locale_file = locale_loader.load_catalog("en")

    assert locale_file.locale == "en"
    assert locale_file.path.exists()
    assert locale_file.path.suffix == ".yaml"
    assert locale_file.catalog["cockpit.title"] == "TheGent Cockpit"


def test_load_catalog_raises_not_found_for_unknown_locale(tmp_path: Path) -> None:
    with pytest.raises(locale_loader.LocaleNotFoundError):
        locale_loader.load_catalog("xx", tmp_path)


def test_load_catalog_raises_parse_error_for_non_mapping_yaml(tmp_path: Path) -> None:
    (tmp_path / "en.yaml").write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(locale_loader.LocaleParseError):
        locale_loader.load_catalog("en", tmp_path)


def test_load_catalog_raises_parse_error_for_non_string_values(tmp_path: Path) -> None:
    (tmp_path / "en.yaml").write_text("cockpit.title: 42\n", encoding="utf-8")

    with pytest.raises(locale_loader.LocaleParseError):
        locale_loader.load_catalog("en", tmp_path)


def test_load_all_returns_every_shipped_locale() -> None:
    files = locale_loader.load_all()

    locales = {file.locale for file in files}
    assert {"en", "fr"}.issubset(locales)
    assert all(file.catalog for file in files)


def test_register_all_populates_translations_for_every_locale() -> None:
    totals = locale_loader.register_all()

    assert totals.get("en", 0) > 0
    assert totals.get("fr", 0) > 0

    i18n.set_locale("fr")
    assert i18n._("cockpit.title") == "Cockpit TheGent"
    assert i18n._("cockpit.lane.L2") == "Boucle de dev"


def test_register_all_is_idempotent_across_repeated_calls() -> None:
    first = locale_loader.register_all()
    second = locale_loader.register_all()

    # First call seeded every message-id; second call is a no-op
    # because every key is already in the catalog.
    assert sum(first.values()) > 0
    assert second == dict.fromkeys(first, 0)


def test_bundle_message_ids_contains_canonical_keys() -> None:
    bundle = locale_loader.bundle_message_ids()

    assert "cockpit.title" in bundle
    assert "cockpit.lane.L17" in bundle
    assert "cockpit.dag.tick" in bundle


def test_coverage_reports_full_for_a_locale_that_has_every_key() -> None:
    translated, total = locale_loader.coverage("en")

    assert total > 0
    assert translated == total


def test_coverage_reports_zero_for_an_unknown_locale() -> None:
    translated, total = locale_loader.coverage("xx", message_ids=["a", "b", "c"])

    assert (translated, total) == (0, 3)


def test_coverage_accepts_explicit_message_ids(tmp_path: Path) -> None:
    (tmp_path / "fr.yaml").write_text(
        "cockpit.title: Cockpit\ncockpit.lane.L1: Archi\n",
        encoding="utf-8",
    )

    translated, total = locale_loader.coverage(
        "fr",
        directory=tmp_path,
        message_ids=["cockpit.title", "cockpit.lane.L1", "cockpit.lane.L2"],
    )

    assert (translated, total) == (2, 3)
