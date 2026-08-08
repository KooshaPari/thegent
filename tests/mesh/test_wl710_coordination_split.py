"""WL710 decomposition tests for ``thegent.mesh.coordination``.

Pins the WL710 L1 split:

* The 327-LOC god-module ``thegent.mesh.coordination`` is now a
  5-submodule package: ``hlc``, ``occ``, ``leases``, ``intent`` and
  ``predict``.  Imports from the legacy flat path continue to work
  because the package ``__init__.py`` re-exports every public name.
* Each submodule is constrained to a strict LOC budget (CLAUDE.md).
* Each public class lives in its own canonical module and is importable
  from both the package root (back-compat) and the canonical module.
* ``isinstance`` / ``__module__`` checks confirm that the package
  re-exports are the *same* objects, not proxies.
* The split is purely structural — no behaviour change.

@trace FR-MESH-006, FR-MESH-007
"""

from __future__ import annotations

import inspect
import typing
from pathlib import Path

import pytest

from thegent.mesh import coordination as coordination_pkg
from thegent.mesh.coordination import (
    ConflictPrediction,
    EditIntent,
    FileClaimsRegistry,
    HLCTimestamp,
    IntentRegistry,
    OptimisticConcurrencyControl,
    _line_ranges_overlap,
    predict_merge_conflicts,
)
from thegent.mesh.coordination import hlc as hlc_module
from thegent.mesh.coordination import intent as intent_module
from thegent.mesh.coordination import leases as leases_module
from thegent.mesh.coordination import occ as occ_module
from thegent.mesh.coordination import predict as predict_module


# ---------------------------------------------------------------------------
# Package + submodule import surface
# ---------------------------------------------------------------------------


class TestPackageSurface:
    """Verify the package structure and re-exports."""

    def test_coordination_is_package_not_module(self):
        """``thegent.mesh.coordination`` is a package (has __path__)."""
        assert hasattr(coordination_pkg, "__path__"), "coordination should be a package after the WL710 split"
        assert coordination_pkg.__file__ is not None

    def test_submodules_exist(self):
        """All five WL710 submodules are importable."""
        assert hlc_module.__file__ is not None
        assert occ_module.__file__ is not None
        assert leases_module.__file__ is not None
        assert intent_module.__file__ is not None
        assert predict_module.__file__ is not None

    def test_submodule_names_are_correct(self):
        """Submodule ``__name__`` attributes match the canonical paths."""
        assert hlc_module.__name__ == "thegent.mesh.coordination.hlc"
        assert occ_module.__name__ == "thegent.mesh.coordination.occ"
        assert leases_module.__name__ == "thegent.mesh.coordination.leases"
        assert intent_module.__name__ == "thegent.mesh.coordination.intent"
        assert predict_module.__name__ == "thegent.mesh.coordination.predict"

    def test_submodule_files_are_distinct(self):
        """Each submodule has a distinct ``__file__`` path."""
        files = {
            hlc_module.__file__,
            occ_module.__file__,
            leases_module.__file__,
            intent_module.__file__,
            predict_module.__file__,
        }
        assert len(files) == 5, "submodule files must be distinct"


# ---------------------------------------------------------------------------
# Re-export identity (package is the canonical home)
# ---------------------------------------------------------------------------


class TestReexportIdentity:
    """``coordination`` re-exports must be the *same* objects as canonical modules."""

    def test_hlc_timestamp_identity(self):
        """``HLCTimestamp`` from package is the same as canonical module."""
        assert coordination_pkg.HLCTimestamp is hlc_module.HLCTimestamp
        assert HLCTimestamp is hlc_module.HLCTimestamp

    def test_occ_identity(self):
        """``OptimisticConcurrencyControl`` from package is the same as canonical."""
        assert coordination_pkg.OptimisticConcurrencyControl is occ_module.OptimisticConcurrencyControl
        assert OptimisticConcurrencyControl is occ_module.OptimisticConcurrencyControl

    def test_file_claims_registry_identity(self):
        """``FileClaimsRegistry`` from package is the same as canonical."""
        assert coordination_pkg.FileClaimsRegistry is leases_module.FileClaimsRegistry
        assert FileClaimsRegistry is leases_module.FileClaimsRegistry

    def test_edit_intent_identity(self):
        """``EditIntent`` from package is the same as canonical."""
        assert coordination_pkg.EditIntent is intent_module.EditIntent
        assert EditIntent is intent_module.EditIntent

    def test_conflict_prediction_identity(self):
        """``ConflictPrediction`` from package is the same as canonical."""
        assert coordination_pkg.ConflictPrediction is intent_module.ConflictPrediction
        assert ConflictPrediction is intent_module.ConflictPrediction

    def test_intent_registry_identity(self):
        """``IntentRegistry`` from package is the same as canonical."""
        assert coordination_pkg.IntentRegistry is intent_module.IntentRegistry
        assert IntentRegistry is intent_module.IntentRegistry

    def test_predict_functions_identity(self):
        """``predict_merge_conflicts`` + ``_line_ranges_overlap`` are the same."""
        assert coordination_pkg.predict_merge_conflicts is predict_module.predict_merge_conflicts
        assert predict_merge_conflicts is predict_module.predict_merge_conflicts
        assert coordination_pkg._line_ranges_overlap is predict_module._line_ranges_overlap
        assert _line_ranges_overlap is predict_module._line_ranges_overlap

    def test_class_module_strings(self):
        """Each class's ``__module__`` points to its canonical submodule."""
        assert HLCTimestamp.__module__ == "thegent.mesh.coordination.hlc"
        assert OptimisticConcurrencyControl.__module__ == "thegent.mesh.coordination.occ"
        assert FileClaimsRegistry.__module__ == "thegent.mesh.coordination.leases"
        assert EditIntent.__module__ == "thegent.mesh.coordination.intent"
        assert ConflictPrediction.__module__ == "thegent.mesh.coordination.intent"
        assert IntentRegistry.__module__ == "thegent.mesh.coordination.intent"
        assert predict_merge_conflicts.__module__ == "thegent.mesh.coordination.predict"


# ---------------------------------------------------------------------------
# Module shape (LOC + CC budgets per CLAUDE.md)
# ---------------------------------------------------------------------------


class TestModuleShapeRegression:
    """Pin the WL710 LOC budgets on each submodule."""

    def test_hlc_module_under_80_loc(self):
        """``hlc.py`` ≤ 80 LOC (HLCTimestamp class + helpers)."""
        src = Path(hlc_module.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 80, f"hlc.py is {loc} LOC, expected ≤ 80"

    def test_occ_module_under_100_loc(self):
        """``occ.py`` ≤ 100 LOC (OptimisticConcurrencyControl class)."""
        src = Path(occ_module.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 100, f"occ.py is {loc} LOC, expected ≤ 100"

    def test_leases_module_under_140_loc(self):
        """``leases.py`` ≤ 140 LOC (FileClaimsRegistry class)."""
        src = Path(leases_module.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 140, f"leases.py is {loc} LOC, expected ≤ 140"

    def test_intent_module_under_160_loc(self):
        """``intent.py`` ≤ 160 LOC (EditIntent + ConflictPrediction + IntentRegistry)."""
        src = Path(intent_module.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 160, f"intent.py is {loc} LOC, expected ≤ 160"

    def test_predict_module_under_120_loc(self):
        """``predict.py`` ≤ 120 LOC (_line_ranges_overlap + predict_merge_conflicts)."""
        src = Path(predict_module.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 120, f"predict.py is {loc} LOC, expected ≤ 120"

    def test_init_module_under_60_loc(self):
        """``__init__.py`` ≤ 60 LOC (pure re-exports)."""
        src = Path(coordination_pkg.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 60, f"__init__.py is {loc} LOC, expected ≤ 60"

    def test_total_split_is_smaller_per_module_than_original(self):
        """After the split, no single module exceeds the original 327 LOC."""
        # Pulled from the WL710 commit summary: original was 327 LOC.
        for module in (
            hlc_module,
            occ_module,
            leases_module,
            intent_module,
            predict_module,
        ):
            src = Path(module.__file__).read_text(encoding="utf-8")
            loc = len(src.splitlines())
            assert loc < 327, f"{module.__name__} is {loc} LOC, larger than the original 327"

    def _cognitive_complexity(self, func: object) -> int:
        """Rough CC estimate: count decision points + 1."""
        try:
            src_lines, _start = inspect.getsourcelines(func)
        except (OSError, TypeError):
            return 0
        text = "".join(src_lines)
        # Decision-point keywords (mirrors radon.cc_visit approximation)
        keywords = (
            "if ",
            "elif ",
            "else:",
            "for ",
            "while ",
            "and ",
            "or ",
            "except ",
            "with ",
        )
        cc = 1
        for kw in keywords:
            cc += text.count(kw)
        return cc

    def test_hlc_update_under_complexity_budget(self):
        """``HLCTimestamp.update`` has CC ≤ 15."""
        cc = self._cognitive_complexity(HLCTimestamp.update)
        assert cc <= 15, f"HLCTimestamp.update CC is {cc}, expected ≤ 15"

    def test_occ_claim_under_complexity_budget(self):
        """``OptimisticConcurrencyControl.claim_version`` has CC ≤ 15."""
        cc = self._cognitive_complexity(OptimisticConcurrencyControl.claim_version)
        assert cc <= 15, f"claim_version CC is {cc}, expected ≤ 15"

    def test_leases_acquire_under_complexity_budget(self):
        """``FileClaimsRegistry.acquire_lease`` has CC ≤ 15."""
        cc = self._cognitive_complexity(FileClaimsRegistry.acquire_lease)
        assert cc <= 15, f"acquire_lease CC is {cc}, expected ≤ 15"

    def test_intent_registry_register_under_complexity_budget(self):
        """``IntentRegistry.register_intent`` has CC ≤ 15."""
        cc = self._cognitive_complexity(IntentRegistry.register_intent)
        assert cc <= 15, f"register_intent CC is {cc}, expected ≤ 15"

    def test_predict_merge_under_complexity_budget(self):
        """``predict_merge_conflicts`` has CC ≤ 15."""
        cc = self._cognitive_complexity(predict_merge_conflicts)
        assert cc <= 15, f"predict_merge_conflicts CC is {cc}, expected ≤ 15"


# ---------------------------------------------------------------------------
# Public surface regression (back-compat pin)
# ---------------------------------------------------------------------------


class TestPublicSurfaceRegression:
    """Pin the complete public surface after the WL710 split."""

    REQUIRED_NAMES: typing.ClassVar[list[str]] = [
        "ConflictPrediction",
        "EditIntent",
        "FileClaimsRegistry",
        "HLCTimestamp",
        "IntentRegistry",
        "OptimisticConcurrencyControl",
        "_line_ranges_overlap",
        "predict_merge_conflicts",
    ]

    def test_all_names_present_at_package_root(self):
        """Every public name is reachable from ``thegent.mesh.coordination``."""
        for name in self.REQUIRED_NAMES:
            assert name in coordination_pkg.__dict__, f"{name} missing from thegent.mesh.coordination"

    def test_hlc_lives_in_hlc_submodule(self):
        """``HLCTimestamp`` is defined in the ``hlc`` submodule (not __init__)."""
        assert "HLCTimestamp" in hlc_module.__dict__
        src = Path(coordination_pkg.__file__).read_text(encoding="utf-8")
        assert "class HLCTimestamp" not in src

    def test_occ_lives_in_occ_submodule(self):
        """``OptimisticConcurrencyControl`` is defined in ``occ`` submodule."""
        src = Path(coordination_pkg.__file__).read_text(encoding="utf-8")
        assert "class OptimisticConcurrencyControl" not in src
        assert "class OptimisticConcurrencyControl" in Path(occ_module.__file__).read_text(encoding="utf-8")

    def test_leases_lives_in_leases_submodule(self):
        """``FileClaimsRegistry`` is defined in ``leases`` submodule."""
        src = Path(coordination_pkg.__file__).read_text(encoding="utf-8")
        assert "class FileClaimsRegistry" not in src
        assert "class FileClaimsRegistry" in Path(leases_module.__file__).read_text(encoding="utf-8")

    def test_intent_classes_live_in_intent_submodule(self):
        """``EditIntent`` + ``ConflictPrediction`` + ``IntentRegistry`` live in intent submodule."""
        src = Path(coordination_pkg.__file__).read_text(encoding="utf-8")
        intent_src = Path(intent_module.__file__).read_text(encoding="utf-8")
        for cls in ("EditIntent", "ConflictPrediction", "IntentRegistry"):
            assert f"class {cls}" in intent_src, f"class {cls} should live in intent.py"
            assert f"class {cls}" not in src, f"class {cls} should NOT live in __init__"

    def test_predict_lives_in_predict_submodule(self):
        """``predict_merge_conflicts`` + ``_line_ranges_overlap`` live in predict submodule."""
        src = Path(coordination_pkg.__file__).read_text(encoding="utf-8")
        predict_src = Path(predict_module.__file__).read_text(encoding="utf-8")
        assert "def predict_merge_conflicts" in predict_src
        assert "def predict_merge_conflicts" not in src
        assert "def _line_ranges_overlap" in predict_src
        assert "def _line_ranges_overlap" not in src


# ---------------------------------------------------------------------------
# Back-compat behavioural verification (no functional change)
# ---------------------------------------------------------------------------


class TestBackCompatBehaviour:
    """Verify the split is purely structural — all classes still work."""

    def test_hlc_timestamp_via_package_works(self):
        """``HLCTimestamp`` constructed via the package import works."""
        ts = HLCTimestamp()
        ts.update()
        s = str(ts)
        assert ":" in s
        parts = s.split(":")
        assert len(parts) == 2
        # Physical is integer ms, logical is hex (4 digits).
        assert parts[0].isdigit()
        assert len(parts[1]) >= 1

    def test_hlc_parse_via_package_works(self):
        """``HLCTimestamp.parse`` via the package import works."""
        ts = HLCTimestamp.parse("1234567890123:0005")
        assert ts.physical == 1234567890123
        assert ts.logical == 5

    def test_occ_claim_and_verify_via_package_works(self, tmp_path):
        """``OptimisticConcurrencyControl`` via package import works."""
        mesh_root = tmp_path / "mesh"
        mesh_root.mkdir()
        occ = OptimisticConcurrencyControl(mesh_root)
        file_path = tmp_path / "f.txt"
        file_path.write_text("abc\n")
        version = occ.claim_version(file_path, "wl710-agent")
        assert len(version) == 64  # sha256
        assert occ.verify_version(file_path, "wl710-agent") is True
        file_path.write_text("xyz\n")
        assert occ.verify_version(file_path, "wl710-agent") is False

    def test_file_claims_registry_via_package_works(self, tmp_path):
        """``FileClaimsRegistry`` via package import works."""
        mesh_root = tmp_path / "mesh"
        mesh_root.mkdir()
        registry = FileClaimsRegistry(mesh_root)
        f = tmp_path / "f.txt"
        f.write_text("hi")
        assert registry.acquire_lease(f, "agent-a", ttl=30) is True
        # Different agent blocked
        assert registry.acquire_lease(f, "agent-b", ttl=30) is False
        # Same agent can renew
        assert registry.acquire_lease(f, "agent-a", ttl=30) is True
        assert registry.release_lease(f, "agent-a") is True
        # Now agent-b can claim
        assert registry.acquire_lease(f, "agent-b", ttl=30) is True

    def test_edit_intent_via_package_works(self):
        """``EditIntent`` via package import works."""
        intent = EditIntent(
            agent_id="wl710",
            file_path="foo.py",
            operation="modify",
            line_ranges=[(10, 20)],
        )
        assert intent.agent_id == "wl710"
        assert intent.operation == "modify"
        assert intent.timestamp is not None  # auto-assigned in __post_init__

    def test_intent_registry_via_package_works(self, tmp_path):
        """``IntentRegistry`` via package import works."""
        mesh_root = tmp_path / "mesh"
        mesh_root.mkdir()
        registry = IntentRegistry(mesh_root)
        intent = EditIntent(
            agent_id="wl710",
            file_path="foo.py",
            operation="modify",
            line_ranges=[(1, 5)],
        )
        path = registry.register_intent(intent)
        assert path.exists()
        # Retrieve
        all_intents = registry.get_intents()
        assert len(all_intents) >= 1
        # Filtered retrieval
        filtered = registry.get_intents(agent_id="wl710")
        assert all(i.agent_id == "wl710" for i in filtered)
        # Clear
        cleared = registry.clear_intents("wl710")
        assert cleared >= 1
        assert registry.get_intents() == []

    def test_predict_merge_via_package_works(self):
        """``predict_merge_conflicts`` via package import works."""
        a = EditIntent("a", "f.py", "modify", [(1, 5)])
        b = EditIntent("b", "f.py", "modify", [(10, 20)])
        pred = predict_merge_conflicts(a, b)
        assert pred.has_conflict is False

        c = EditIntent("a", "f.py", "modify", [(1, 5)])
        d = EditIntent("b", "f.py", "modify", [(3, 7)])
        pred2 = predict_merge_conflicts(c, d)
        assert pred2.has_conflict is True


# ---------------------------------------------------------------------------
# Isolation: pkg import vs canonical submodule import
# ---------------------------------------------------------------------------


class TestImportIsolation:
    """Verify that submodule-level imports work as well as package-level imports."""

    def test_hlc_importable_from_hlc_module(self):
        """``from thegent.mesh.coordination.hlc import HLCTimestamp`` works."""
        from thegent.mesh.coordination.hlc import HLCTimestamp as HLCTimestampSub

        assert HLCTimestampSub is HLCTimestamp

    def test_occ_importable_from_occ_module(self):
        """``from thegent.mesh.coordination.occ import OptimisticConcurrencyControl`` works."""
        from thegent.mesh.coordination.occ import (
            OptimisticConcurrencyControl as OCCSub,
        )

        assert OCCSub is OptimisticConcurrencyControl

    def test_leases_importable_from_leases_module(self):
        """``from thegent.mesh.coordination.leases import FileClaimsRegistry`` works."""
        from thegent.mesh.coordination.leases import (
            FileClaimsRegistry as FCRSub,
        )

        assert FCRSub is FileClaimsRegistry

    def test_intent_classes_importable_from_intent_module(self):
        """All three intent classes importable from intent submodule."""
        from thegent.mesh.coordination.intent import (
            ConflictPrediction as CPSub,
            EditIntent as EISub,
            IntentRegistry as IRSub,
        )

        assert CPSub is ConflictPrediction
        assert EISub is EditIntent
        assert IRSub is IntentRegistry

    def test_predict_functions_importable_from_predict_module(self):
        """predict_merge_conflicts + _line_ranges_overlap importable from predict submodule."""
        from thegent.mesh.coordination.predict import (
            _line_ranges_overlap as _line_ranges_overlap_sub,
            predict_merge_conflicts as predict_merge_conflicts_sub,
        )

        assert predict_merge_conflicts_sub is predict_merge_conflicts
        assert _line_ranges_overlap_sub is _line_ranges_overlap


# ---------------------------------------------------------------------------
# Function-level budgets (CLAUDE.md: max function length 40 LOC)
# ---------------------------------------------------------------------------


class TestFunctionLengthRegression:
    """Wire-level pin: every public method is ≤ 40 LOC."""

    def _body_loc(self, func: object) -> int:
        """Return body LOC of a function (signature line + docstring excluded)."""
        try:
            src_lines, _start = inspect.getsourcelines(func)
        except (OSError, TypeError):
            return 0
        if not src_lines:
            return 0
        body_lines: list[str] = []
        in_docstring = False
        started = False
        for line in src_lines:
            if not started:
                if line.startswith((" ", "\t")):
                    started = True
                else:
                    continue
            stripped = line.strip()
            if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                in_docstring = True
                quote = stripped[:3]
                rest = stripped[3:]
                if rest.endswith(quote) and len(rest) > 3:
                    in_docstring = False
                continue
            if in_docstring:
                if '"""' in stripped or "'''" in stripped:
                    in_docstring = False
                continue
            body_lines.append(line)
        return len(body_lines)

    def test_hlc_update_under_40_loc(self):
        """``HLCTimestamp.update`` ≤ 40 LOC body."""
        loc = self._body_loc(HLCTimestamp.update)
        assert loc <= 40, f"update is {loc} LOC, expected ≤ 40"

    def test_hlc_parse_under_40_loc(self):
        """``HLCTimestamp.parse`` ≤ 40 LOC body."""
        loc = self._body_loc(HLCTimestamp.parse)
        assert loc <= 40, f"parse is {loc} LOC, expected ≤ 40"

    def test_occ_get_version_under_40_loc(self):
        """``OptimisticConcurrencyControl.get_version`` ≤ 40 LOC body."""
        loc = self._body_loc(OptimisticConcurrencyControl.get_version)
        assert loc <= 40, f"get_version is {loc} LOC, expected ≤ 40"

    def test_occ_claim_version_under_40_loc(self):
        """``OptimisticConcurrencyControl.claim_version`` ≤ 40 LOC body."""
        loc = self._body_loc(OptimisticConcurrencyControl.claim_version)
        assert loc <= 40, f"claim_version is {loc} LOC, expected ≤ 40"

    def test_occ_verify_version_under_40_loc(self):
        """``OptimisticConcurrencyControl.verify_version`` ≤ 40 LOC body."""
        loc = self._body_loc(OptimisticConcurrencyControl.verify_version)
        assert loc <= 40, f"verify_version is {loc} LOC, expected ≤ 40"

    def test_leases_acquire_lease_under_40_loc(self):
        """``FileClaimsRegistry.acquire_lease`` ≤ 40 LOC body."""
        loc = self._body_loc(FileClaimsRegistry.acquire_lease)
        assert loc <= 40, f"acquire_lease is {loc} LOC, expected ≤ 40"

    def test_leases_release_lease_under_40_loc(self):
        """``FileClaimsRegistry.release_lease`` ≤ 40 LOC body."""
        loc = self._body_loc(FileClaimsRegistry.release_lease)
        assert loc <= 40, f"release_lease is {loc} LOC, expected ≤ 40"

    def test_leases_cleanup_expired_under_40_loc(self):
        """``FileClaimsRegistry.cleanup_expired`` ≤ 40 LOC body."""
        loc = self._body_loc(FileClaimsRegistry.cleanup_expired)
        assert loc <= 40, f"cleanup_expired is {loc} LOC, expected ≤ 40"

    def test_intent_registry_register_intent_under_40_loc(self):
        """``IntentRegistry.register_intent`` ≤ 40 LOC body."""
        loc = self._body_loc(IntentRegistry.register_intent)
        assert loc <= 40, f"register_intent is {loc} LOC, expected ≤ 40"

    def test_intent_registry_get_intents_under_40_loc(self):
        """``IntentRegistry.get_intents`` ≤ 40 LOC body."""
        loc = self._body_loc(IntentRegistry.get_intents)
        assert loc <= 40, f"get_intents is {loc} LOC, expected ≤ 40"

    def test_intent_registry_clear_intents_under_40_loc(self):
        """``IntentRegistry.clear_intents`` ≤ 40 LOC body."""
        loc = self._body_loc(IntentRegistry.clear_intents)
        assert loc <= 40, f"clear_intents is {loc} LOC, expected ≤ 40"

    def test_predict_merge_conflicts_under_40_loc(self):
        """``predict_merge_conflicts`` ≤ 40 LOC body."""
        loc = self._body_loc(predict_merge_conflicts)
        assert loc <= 40, f"predict_merge_conflicts is {loc} LOC, expected ≤ 40"

    def test_line_ranges_overlap_under_40_loc(self):
        """``_line_ranges_overlap`` ≤ 40 LOC body."""
        loc = self._body_loc(_line_ranges_overlap)
        assert loc <= 40, f"_line_ranges_overlap is {loc} LOC, expected ≤ 40"


# ---------------------------------------------------------------------------
# Cross-class interaction: intent registry + predict + leases + occ
# ---------------------------------------------------------------------------


class TestCoordinationInteractions:
    """Verify the split preserves cross-class workflows."""

    def test_intent_registry_predict_round_trip(self, tmp_path):
        """Register two intents, then run predict_merge_conflicts on them."""
        mesh_root = tmp_path / "mesh"
        mesh_root.mkdir()
        registry = IntentRegistry(mesh_root)
        a = EditIntent("a", "shared.py", "modify", [(1, 5)])
        b = EditIntent("b", "shared.py", "modify", [(3, 8)])
        registry.register_intent(a)
        registry.register_intent(b)
        # Predict between them via the package import path
        pred = predict_merge_conflicts(a, b)
        assert pred.has_conflict is True

    def test_occ_then_lease_workflow(self, tmp_path):
        """OCC claim then lease acquire on same file should compose cleanly."""
        mesh_root = tmp_path / "mesh"
        mesh_root.mkdir()
        occ = OptimisticConcurrencyControl(mesh_root)
        leases = FileClaimsRegistry(mesh_root)
        f = tmp_path / "f.txt"
        f.write_text("data")
        version = occ.claim_version(f, "wl710")
        assert occ.verify_version(f, "wl710") is True
        assert leases.acquire_lease(f, "wl710", ttl=30) is True

    def test_dataclass_constructs_via_package(self):
        """All dataclasses construct cleanly via package imports."""
        intent = EditIntent("a", "x.py", "create")
        assert intent.line_ranges == []
        assert intent.timestamp is not None
        pred = ConflictPrediction(has_conflict=False)
        assert pred.has_conflict is False
        assert pred.conflicting_files == []
