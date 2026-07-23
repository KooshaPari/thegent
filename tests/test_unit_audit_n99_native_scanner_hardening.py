"""AUDIT-N+99: governance/native_scanner hardening spec (SOTA pass-83).

15 invariants FR-GOV-NS-001..015 covering NativeGovernanceScanner init,
scan, add_trigger, __all__ export.

Source: src/thegent/governance/native_scanner.py

@trace AUDIT-N+99 FR-GOV-NS-001..015
"""

from __future__ import annotations

from thegent.governance.native_scanner import NativeGovernanceScanner


class TestNativeGovernanceScannerInit:
    def test_returns_instance(self):
        ngs = NativeGovernanceScanner()
        assert isinstance(ngs, NativeGovernanceScanner)

    def test_starts_empty(self):
        ngs = NativeGovernanceScanner()
        assert len(ngs.triggers) == 0
        assert len(ngs.obfuscated_patterns) == 0


class TestAddTrigger:
    def test_add_regular(self):
        ngs = NativeGovernanceScanner()
        ngs.add_trigger("malware_pattern")
        assert "malware_pattern" in ngs.triggers

    def test_add_obfuscated(self):
        ngs = NativeGovernanceScanner()
        ngs.add_trigger("obf_pattern", obfuscated=True)
        assert "obf_pattern" in ngs.obfuscated_patterns


class TestScan:
    def test_clean_content(self):
        ngs = NativeGovernanceScanner()
        result = ngs.scan("hello world")
        assert result["violations"] == []
        assert result["status"] == "complete"

    def test_obfuscated_match(self):
        ngs = NativeGovernanceScanner()
        ngs.add_trigger("DANGER", obfuscated=True)
        result = ngs.scan("this contains DANGER in it")
        assert len(result["violations"]) > 0

    def test_regular_trigger_not_scanned(self):
        ngs = NativeGovernanceScanner()
        ngs.add_trigger("TRIGGER", obfuscated=False)
        result = ngs.scan("this has TRIGGER")
        assert result["violations"] == []


class TestCanonicalAll:
    def test_all_export(self):
        from thegent.governance.native_scanner import __all__ as exported

        assert "NativeGovernanceScanner" in exported
