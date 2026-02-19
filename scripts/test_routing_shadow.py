#!/usr/bin/env python3
"""Shadow mode testing for role-based routing.

Tests routing decisions across all categories and roles without enforcement.
Validates that correct models are selected for given prompts.
"""

import sys

from thegent.config import ThegentSettings
from thegent.routing.task_router import TaskClassifier

# Test prompts covering all categories and roles
TEST_PROMPTS = [
    # FAST + RESEARCHER
    ("what is 2+2", "FAST", "researcher", "gemini"),
    ("list files in current directory", "FAST", "researcher", "gemini"),
    ("explain how JWT works", "FAST", "researcher", "gemini"),
    # FAST + WORKHORSE
    ("fix typo in readme", "FAST", "workhorse", "minimax"),
    ("add semicolon to line 42", "FAST", "workhorse", "minimax"),
    # NORMAL + WRITER
    ("add error handling to cli.py", "NORMAL", "writer_fast", "codex"),
    ("implement basic JWT validation", "NORMAL", "writer_fast", "codex"),
    ("write unit test for TaskRouter", "NORMAL", "writer_fast", "codex"),
    # NORMAL + RESEARCHER
    ("find all uses of deprecated function", "NORMAL", "researcher", "gemini"),
    # COMPLEX + WRITER_HIGH
    ("design microservice architecture for auth", "COMPLEX", "writer_high", "codex"),
    ("refactor state machine for retry logic", "COMPLEX", "writer_high", "codex"),
    # COMPLEX + PLANNER
    ("evaluate tradeoffs between Redis and Memcached", "COMPLEX", "planner", "claude"),
    ("design schema for multi-tenant SaaS", "COMPLEX", "planner", "claude"),
    # HIGH_COMPLEX + PLANNER
    ("implement end-to-end OAuth flow with JWT tokens", "HIGH_COMPLEX", "planner", "claude"),
    ("design distributed transaction system", "HIGH_COMPLEX", "planner", "claude"),
    # HIGH_COMPLEX + WRITER_HIGH (mission-critical)
    ("implement payment processing with encryption", "HIGH_COMPLEX", "writer_high", "codex"),
    ("add authentication middleware with security audit", "HIGH_COMPLEX", "writer_high", "codex"),
    # LARGE_CONTEXT
    ("refactor all error handling across the entire codebase", "COMPLEX", "large_context", "claude"),
]


def main() -> None:
    """Run shadow mode routing tests."""

    print("=" * 80)
    print("ROUTING SHADOW MODE TEST")
    print("Testing role-based routing with subscription-optimized model selection")
    print("=" * 80)
    print()

    # Initialize classifier
    settings = ThegentSettings()
    classifier = TaskClassifier(settings)

    # Track results
    total = len(TEST_PROMPTS)
    passed = 0
    failed = 0

    for prompt, expected_category, expected_role, expected_model in TEST_PROMPTS:
        # Classify task
        metadata = classifier.classify(prompt)

        # Check results
        category_match = metadata.category.value == expected_category
        role_match = metadata.detected_role == expected_role
        model_match = metadata.selected_model == expected_model

        test_passed = category_match and role_match and model_match

        if test_passed:
            passed += 1
            status = "✓ PASS"
        else:
            failed += 1
            status = "✗ FAIL"

        # Print result
        print(f"{status}: {prompt[:60]:<60}")
        print(f"  Expected: {expected_category:12} | {expected_role:15} → {expected_model}")
        print(f"  Got:      {metadata.category.value:12} | {metadata.detected_role:15} → {metadata.selected_model}")

        if not test_passed:
            if not category_match:
                print("  ⚠ Category mismatch!")
            if not role_match:
                print("  ⚠ Role mismatch!")
            if not model_match:
                print("  ⚠ Model mismatch!")

        print(f"  Reason: {metadata.routing_reason}")
        print()

    # Summary
    print("=" * 80)
    print(f"RESULTS: {passed}/{total} passed, {failed}/{total} failed")
    print("=" * 80)

    if failed > 0:
        print("\n⚠ Some tests failed. Review routing logic.")
        sys.exit(1)
    else:
        print("\n✓ All tests passed! Routing is working correctly.")
        print("\nNext steps:")
        print("1. Enable routing in production: export THGENT_ROUTING_ENABLED=true")
        print("2. Monitor run_registry.jsonl for routing metadata")
        print("3. Track subscription quota usage (MiniMax: 300/5hrs, Gemini: 1500/day)")
        sys.exit(0)


if __name__ == "__main__":
    main()
