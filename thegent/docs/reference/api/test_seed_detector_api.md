# test_seed_detector API Reference

> **Source**: `src/thegent/memory/test_seed_detector.py`

Tests for seed detector pattern matching and classification.

---

## TestCaseInsensitiveDetection

Test case-insensitive pattern matching.

### Methods

#### TestCaseInsensitiveDetection.test_lowercase_what_if

```python
test_lowercase_what_if(self: Any)
```

Test lowercase 'what if' detection.

---

#### TestCaseInsensitiveDetection.test_mixed_case_we_should

```python
test_mixed_case_we_should(self: Any)
```

Test mixed case 'We Should' detection.

---

#### TestCaseInsensitiveDetection.test_uppercase_consider

```python
test_uppercase_consider(self: Any)
```

Test uppercase 'CONSIDER' detection.

---

---

## TestFlagExtraction

Test extraction of special flags from text.

### Methods

#### TestFlagExtraction.test_defer_flag_extraction

```python
test_defer_flag_extraction(self: Any)
```

Test extraction of $defer flag.

---

#### TestFlagExtraction.test_fixme_flag_extraction

```python
test_fixme_flag_extraction(self: Any)
```

Test extraction of FIXME flag.

---

#### TestFlagExtraction.test_idea_flag_extraction

```python
test_idea_flag_extraction(self: Any)
```

Test extraction of $idea flag.

---

#### TestFlagExtraction.test_multiple_flags

```python
test_multiple_flags(self: Any)
```

Test extraction of multiple flags.

---

#### TestFlagExtraction.test_no_flags

```python
test_no_flags(self: Any)
```

Test that text without flags returns all False.

---

#### TestFlagExtraction.test_pending_flag_extraction

```python
test_pending_flag_extraction(self: Any)
```

Test extraction of $pending flag.

---

#### TestFlagExtraction.test_todo_flag_extraction

```python
test_todo_flag_extraction(self: Any)
```

Test extraction of TODO flag.

---

---

## TestSeedDetectorPatternMatching

Test pattern matching for seed detection.

### Methods

#### TestSeedDetectorPatternMatching.test_code_quality_fixme_pattern

```python
test_code_quality_fixme_pattern(self: Any)
```

Test detection of FIXME comments.

---

#### TestSeedDetectorPatternMatching.test_code_quality_todo_pattern

```python
test_code_quality_todo_pattern(self: Any)
```

Test detection of TODO comments.

---

#### TestSeedDetectorPatternMatching.test_design_pattern_architecture

```python
test_design_pattern_architecture(self: Any)
```

Test detection of architecture keyword.

---

#### TestSeedDetectorPatternMatching.test_design_pattern_performance

```python
test_design_pattern_performance(self: Any)
```

Test detection of performance keyword.

---

#### TestSeedDetectorPatternMatching.test_design_pattern_refactor

```python
test_design_pattern_refactor(self: Any)
```

Test detection of refactor keyword.

---

#### TestSeedDetectorPatternMatching.test_explicit_consider_pattern

```python
test_explicit_consider_pattern(self: Any)
```

Test detection of 'Consider' pattern.

---

#### TestSeedDetectorPatternMatching.test_explicit_proposal_pattern

```python
test_explicit_proposal_pattern(self: Any)
```

Test detection of 'proposal' keyword.

---

#### TestSeedDetectorPatternMatching.test_explicit_we_should_pattern

```python
test_explicit_we_should_pattern(self: Any)
```

Test detection of 'We should' pattern.

---

#### TestSeedDetectorPatternMatching.test_explicit_what_if_pattern

```python
test_explicit_what_if_pattern(self: Any)
```

Test detection of 'What if' pattern.

---

#### TestSeedDetectorPatternMatching.test_multiple_seed_markers_in_text

```python
test_multiple_seed_markers_in_text(self: Any)
```

Test that only one seed is created per detection pass.

---

#### TestSeedDetectorPatternMatching.test_no_seed_detection_in_normal_text

```python
test_no_seed_detection_in_normal_text(self: Any)
```

Test that normal text doesn't trigger seed detection.

---

#### TestSeedDetectorPatternMatching.test_seed_source_preservation

```python
test_seed_source_preservation(self: Any)
```

Test that seed source is correctly preserved.

---

#### TestSeedDetectorPatternMatching.test_seed_text_truncation

```python
test_seed_text_truncation(self: Any)
```

Test that seed text is truncated to 500 chars.

---

---

## TestSeedMetadata

Test seed metadata generation.

### Methods

#### TestSeedMetadata.test_seed_default_status

```python
test_seed_default_status(self: Any)
```

Test that seed has default status 'new'.

---

#### TestSeedMetadata.test_seed_has_id

```python
test_seed_has_id(self: Any)
```

Test that seed has unique ID.

---

#### TestSeedMetadata.test_seed_has_timestamp

```python
test_seed_has_timestamp(self: Any)
```

Test that seed has ISO 8601 timestamp.

---

#### TestSeedMetadata.test_seed_to_dict_serialization

```python
test_seed_to_dict_serialization(self: Any)
```

Test that seed can be serialized to dict.

---

---

## TestTagExtraction

Test automatic tag extraction from seed text.

### Methods

#### TestTagExtraction.test_architecture_tag

```python
test_architecture_tag(self: Any)
```

Test extraction of architecture tag.

---

#### TestTagExtraction.test_multiple_tags

```python
test_multiple_tags(self: Any)
```

Test extraction of multiple tags.

---

#### TestTagExtraction.test_no_tags_for_simple_seed

```python
test_no_tags_for_simple_seed(self: Any)
```

Test that seeds without relevant keywords get empty tags.

---

#### TestTagExtraction.test_performance_tag

```python
test_performance_tag(self: Any)
```

Test extraction of performance tag.

---

#### TestTagExtraction.test_security_tag

```python
test_security_tag(self: Any)
```

Test extraction of security tag.

---

#### TestTagExtraction.test_tag_limit

```python
test_tag_limit(self: Any)
```

Test that tags are limited to 3.

---

---

## test_architecture_tag

```python
test_architecture_tag(self: Any)
```

Test extraction of architecture tag.

---

## test_code_quality_fixme_pattern

```python
test_code_quality_fixme_pattern(self: Any)
```

Test detection of FIXME comments.

---

## test_code_quality_todo_pattern

```python
test_code_quality_todo_pattern(self: Any)
```

Test detection of TODO comments.

---

## test_defer_flag_extraction

```python
test_defer_flag_extraction(self: Any)
```

Test extraction of $defer flag.

---

## test_design_pattern_architecture

```python
test_design_pattern_architecture(self: Any)
```

Test detection of architecture keyword.

---

## test_design_pattern_performance

```python
test_design_pattern_performance(self: Any)
```

Test detection of performance keyword.

---

## test_design_pattern_refactor

```python
test_design_pattern_refactor(self: Any)
```

Test detection of refactor keyword.

---

## test_explicit_consider_pattern

```python
test_explicit_consider_pattern(self: Any)
```

Test detection of 'Consider' pattern.

---

## test_explicit_proposal_pattern

```python
test_explicit_proposal_pattern(self: Any)
```

Test detection of 'proposal' keyword.

---

## test_explicit_we_should_pattern

```python
test_explicit_we_should_pattern(self: Any)
```

Test detection of 'We should' pattern.

---

## test_explicit_what_if_pattern

```python
test_explicit_what_if_pattern(self: Any)
```

Test detection of 'What if' pattern.

---

## test_fixme_flag_extraction

```python
test_fixme_flag_extraction(self: Any)
```

Test extraction of FIXME flag.

---

## test_idea_flag_extraction

```python
test_idea_flag_extraction(self: Any)
```

Test extraction of $idea flag.

---

## test_lowercase_what_if

```python
test_lowercase_what_if(self: Any)
```

Test lowercase 'what if' detection.

---

## test_mixed_case_we_should

```python
test_mixed_case_we_should(self: Any)
```

Test mixed case 'We Should' detection.

---

## test_multiple_flags

```python
test_multiple_flags(self: Any)
```

Test extraction of multiple flags.

---

## test_multiple_seed_markers_in_text

```python
test_multiple_seed_markers_in_text(self: Any)
```

Test that only one seed is created per detection pass.

---

## test_multiple_tags

```python
test_multiple_tags(self: Any)
```

Test extraction of multiple tags.

---

## test_no_flags

```python
test_no_flags(self: Any)
```

Test that text without flags returns all False.

---

## test_no_seed_detection_in_normal_text

```python
test_no_seed_detection_in_normal_text(self: Any)
```

Test that normal text doesn't trigger seed detection.

---

## test_no_tags_for_simple_seed

```python
test_no_tags_for_simple_seed(self: Any)
```

Test that seeds without relevant keywords get empty tags.

---

## test_pending_flag_extraction

```python
test_pending_flag_extraction(self: Any)
```

Test extraction of $pending flag.

---

## test_performance_tag

```python
test_performance_tag(self: Any)
```

Test extraction of performance tag.

---

## test_security_tag

```python
test_security_tag(self: Any)
```

Test extraction of security tag.

---

## test_seed_default_status

```python
test_seed_default_status(self: Any)
```

Test that seed has default status 'new'.

---

## test_seed_has_id

```python
test_seed_has_id(self: Any)
```

Test that seed has unique ID.

---

## test_seed_has_timestamp

```python
test_seed_has_timestamp(self: Any)
```

Test that seed has ISO 8601 timestamp.

---

## test_seed_source_preservation

```python
test_seed_source_preservation(self: Any)
```

Test that seed source is correctly preserved.

---

## test_seed_text_truncation

```python
test_seed_text_truncation(self: Any)
```

Test that seed text is truncated to 500 chars.

---

## test_seed_to_dict_serialization

```python
test_seed_to_dict_serialization(self: Any)
```

Test that seed can be serialized to dict.

---

## test_tag_limit

```python
test_tag_limit(self: Any)
```

Test that tags are limited to 3.

---

## test_todo_flag_extraction

```python
test_todo_flag_extraction(self: Any)
```

Test extraction of TODO flag.

---

## test_uppercase_consider

```python
test_uppercase_consider(self: Any)
```

Test uppercase 'CONSIDER' detection.

---
