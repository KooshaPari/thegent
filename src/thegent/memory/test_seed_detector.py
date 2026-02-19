"""Tests for seed detector pattern matching and classification."""

from __future__ import annotations

import pytest

from .seed_detector import SeedDetector, SeedSource


class TestSeedDetectorPatternMatching:
    """Test pattern matching for seed detection."""

    def test_explicit_what_if_pattern(self):
        """Test detection of 'What if' pattern."""
        detector = SeedDetector()
        text = "What if we could optimize the database queries?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 1
        assert seeds[0].confidence == 0.9
        assert seeds[0].detected_by == "explicit_marker"

    def test_explicit_consider_pattern(self):
        """Test detection of 'Consider' pattern."""
        detector = SeedDetector()
        text = "Consider implementing a caching layer for performance."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 1
        assert seeds[0].confidence == 0.9

    def test_explicit_we_should_pattern(self):
        """Test detection of 'We should' pattern."""
        detector = SeedDetector()
        text = "We should refactor the authentication system."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 1
        assert seeds[0].confidence == 0.9

    def test_explicit_proposal_pattern(self):
        """Test detection of 'proposal' keyword."""
        detector = SeedDetector()
        text = "Proposal: Add real-time notifications to the dashboard."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 1
        assert seeds[0].confidence == 0.9

    def test_code_quality_todo_pattern(self):
        """Test detection of TODO comments."""
        detector = SeedDetector()
        text = "# TODO: Implement user authentication\ndef login():\n    pass"
        seeds = detector.detect_seeds(text, SeedSource.AGENT_OUTPUT)

        assert len(seeds) == 1
        assert seeds[0].confidence == 0.6
        assert seeds[0].detected_by == "code_quality_marker"

    def test_code_quality_fixme_pattern(self):
        """Test detection of FIXME comments."""
        detector = SeedDetector()
        text = "def process_data():\n    # FIXME: Handle edge cases\n    return data"
        seeds = detector.detect_seeds(text, SeedSource.AGENT_OUTPUT)

        assert len(seeds) == 1
        assert seeds[0].confidence == 0.6

    def test_design_pattern_architecture(self):
        """Test detection of architecture keyword."""
        detector = SeedDetector()
        text = "The current architecture doesn't scale. We need to rethink it."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 1
        assert seeds[0].detected_by == "design_marker"

    def test_design_pattern_refactor(self):
        """Test detection of refactor keyword."""
        detector = SeedDetector()
        text = "We should refactor the payment processing module."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) >= 1

    def test_design_pattern_performance(self):
        """Test detection of performance keyword."""
        detector = SeedDetector()
        text = "Performance is a key concern for this feature."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 1
        assert "performance" in seeds[0].tags

    def test_no_seed_detection_in_normal_text(self):
        """Test that normal text doesn't trigger seed detection."""
        detector = SeedDetector()
        text = "The user clicked the button and saw the result."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 0

    def test_seed_text_truncation(self):
        """Test that seed text is truncated to 500 chars."""
        detector = SeedDetector()
        long_text = "What if " + "x" * 1000
        seeds = detector.detect_seeds(long_text, SeedSource.USER_PROMPT)

        assert len(seeds[0].text) <= 500

    def test_seed_source_preservation(self):
        """Test that seed source is correctly preserved."""
        detector = SeedDetector()
        text = "Consider implementing a feature."

        seeds_from_prompt = detector.detect_seeds(text, SeedSource.USER_PROMPT)
        assert seeds_from_prompt[0].source == SeedSource.USER_PROMPT

        seeds_from_history = detector.detect_seeds(text, SeedSource.CLAUDE_HISTORY)
        assert seeds_from_history[0].source == SeedSource.CLAUDE_HISTORY

    def test_multiple_seed_markers_in_text(self):
        """Test that only one seed is created per detection pass."""
        detector = SeedDetector()
        text = "What if we could consider implementing a new feature?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        # Should only detect once (the first pattern match)
        assert len(seeds) == 1


class TestTagExtraction:
    """Test automatic tag extraction from seed text."""

    def test_architecture_tag(self):
        """Test extraction of architecture tag."""
        detector = SeedDetector()
        text = "What if we redesigned the system architecture?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert "architecture" in seeds[0].tags

    def test_performance_tag(self):
        """Test extraction of performance tag."""
        detector = SeedDetector()
        text = "What if we optimized performance across the app?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert "performance" in seeds[0].tags

    def test_security_tag(self):
        """Test extraction of security tag."""
        detector = SeedDetector()
        text = "Consider improving security in our authentication system."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert "security" in seeds[0].tags

    def test_multiple_tags(self):
        """Test extraction of multiple tags."""
        detector = SeedDetector()
        text = "What if we improved security and performance together?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert "security" in seeds[0].tags
        assert "performance" in seeds[0].tags

    def test_tag_limit(self):
        """Test that tags are limited to 3."""
        detector = SeedDetector()
        text = (
            "What if we refactored the architecture for better security, "
            "performance, testing, and documentation?"
        )
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds[0].tags) <= 3

    def test_no_tags_for_simple_seed(self):
        """Test that seeds without relevant keywords get empty tags."""
        detector = SeedDetector()
        text = "What if we changed the color scheme?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        # Should have empty or minimal tags
        assert len(seeds[0].tags) <= 1


class TestFlagExtraction:
    """Test extraction of special flags from text."""

    def test_idea_flag_extraction(self):
        """Test extraction of $idea flag."""
        flags = SeedDetector.extract_flags("$idea: Consider caching")
        assert flags["idea"] is True
        assert flags["defer"] is False

    def test_defer_flag_extraction(self):
        """Test extraction of $defer flag."""
        flags = SeedDetector.extract_flags("$defer: Handle later")
        assert flags["defer"] is True
        assert flags["idea"] is False

    def test_pending_flag_extraction(self):
        """Test extraction of $pending flag."""
        flags = SeedDetector.extract_flags("#pending: Waiting on input")
        assert flags["pending"] is True

    def test_todo_flag_extraction(self):
        """Test extraction of TODO flag."""
        flags = SeedDetector.extract_flags("# TODO: Implement this")
        assert flags["todo"] is True

    def test_fixme_flag_extraction(self):
        """Test extraction of FIXME flag."""
        flags = SeedDetector.extract_flags("FIXME: This is broken")
        assert flags["fixme"] is True

    def test_multiple_flags(self):
        """Test extraction of multiple flags."""
        flags = SeedDetector.extract_flags("$idea $pending TODO: Something")
        assert flags["idea"] is True
        assert flags["pending"] is True
        assert flags["todo"] is True

    def test_no_flags(self):
        """Test that text without flags returns all False."""
        flags = SeedDetector.extract_flags("This is normal text")
        assert all(not v for v in flags.values())


class TestSeedMetadata:
    """Test seed metadata generation."""

    def test_seed_has_timestamp(self):
        """Test that seed has ISO 8601 timestamp."""
        detector = SeedDetector()
        text = "What if we did something?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert seeds[0].timestamp
        assert "T" in seeds[0].timestamp  # ISO format has T
        assert "Z" in seeds[0].timestamp or "+" in seeds[0].timestamp

    def test_seed_has_id(self):
        """Test that seed has unique ID."""
        detector = SeedDetector()
        text1 = "What if we did A?"
        text2 = "What if we did B?"

        seeds1 = detector.detect_seeds(text1, SeedSource.USER_PROMPT)
        seeds2 = detector.detect_seeds(text2, SeedSource.USER_PROMPT)

        assert seeds1[0].id
        assert seeds2[0].id
        assert seeds1[0].id != seeds2[0].id

    def test_seed_default_status(self):
        """Test that seed has default status 'new'."""
        detector = SeedDetector()
        text = "What if we did something?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert seeds[0].status == "new"

    def test_seed_to_dict_serialization(self):
        """Test that seed can be serialized to dict."""
        detector = SeedDetector()
        text = "What if we did something?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        seed_dict = seeds[0].to_dict()

        assert seed_dict["id"]
        assert seed_dict["text"]
        assert seed_dict["source"]
        assert seed_dict["confidence"]
        assert seed_dict["timestamp"]
        assert seed_dict["tags"] is not None
        assert seed_dict["status"]


class TestCaseInsensitiveDetection:
    """Test case-insensitive pattern matching."""

    def test_lowercase_what_if(self):
        """Test lowercase 'what if' detection."""
        detector = SeedDetector()
        text = "what if we could do this?"
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 1

    def test_uppercase_consider(self):
        """Test uppercase 'CONSIDER' detection."""
        detector = SeedDetector()
        text = "CONSIDER implementing this feature."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 1

    def test_mixed_case_we_should(self):
        """Test mixed case 'We Should' detection."""
        detector = SeedDetector()
        text = "We Should refactor this code."
        seeds = detector.detect_seeds(text, SeedSource.USER_PROMPT)

        assert len(seeds) == 1
