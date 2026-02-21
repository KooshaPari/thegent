from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_instruction_architecture.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("instruction_architecture_check", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_instruction_doc_map_contains_links() -> None:
    mod = _load_module()
    links = mod.extract_instruction_doc_map_links((ROOT / "CLAUDE.md").read_text(encoding="utf-8"))
    assert links


def test_instruction_architecture_contracts_are_clean() -> None:
    mod = _load_module()
    findings = mod.run_checks()
    assert findings == []
    summary = mod.build_summary(findings)
    assert summary["ok"] is True
    assert summary["finding_count"] == 0
    checked = summary["checked"]
    assert "pre_work_gate_command_modules" in checked


def test_pre_work_gate_command_module_flags_literal_duplication(tmp_path: Path) -> None:
    mod = _load_module()
    module_path = tmp_path / "bad_module.py"
    module_path.write_text(
        "\n".join(
            [
                "from thegent.cli.services import pre_work_gate_helpers",
                "",
                "def _enforce_pre_work_hard_gate(project_dir):",
                "    return pre_work_gate_helpers.enforce_pre_work_hard_gate(project_dir)",
                "",
                "def note():",
                "    return 'WP-HG-05.pre_work_hard_gate'",
                "",
            ]
        ),
        encoding="utf-8",
    )

    findings = mod.validate_pre_work_gate_command_module(
        module_path=module_path,
        wrapper_contracts={"_enforce_pre_work_hard_gate": "enforce_pre_work_hard_gate"},
    )
    assert any(item.kind == "pre_work_gate_literal_duplicate" for item in findings)


def test_pre_work_gate_command_module_flags_wrapper_logic_leak(tmp_path: Path) -> None:
    mod = _load_module()
    module_path = tmp_path / "bad_wrapper.py"
    module_path.write_text(
        "\n".join(
            [
                "from thegent.cli.services import pre_work_gate_helpers",
                "",
                "def _enforce_pre_work_hard_gate(project_dir):",
                "    gate = pre_work_gate_helpers.enforce_pre_work_hard_gate(project_dir)",
                "    return gate",
                "",
            ]
        ),
        encoding="utf-8",
    )

    findings = mod.validate_pre_work_gate_command_module(
        module_path=module_path,
        wrapper_contracts={"_enforce_pre_work_hard_gate": "enforce_pre_work_hard_gate"},
    )
    assert any(item.kind == "pre_work_gate_wrapper_logic_leak" for item in findings)
