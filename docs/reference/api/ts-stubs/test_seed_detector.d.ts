// Auto-generated TypeScript declarations for test_seed_detector
// Source: generate-api-docs.py

export declare class TestCaseInsensitiveDetection {
  test_lowercase_what_if(): void;
  test_mixed_case_we_should(): void;
  test_uppercase_consider(): void;
}

export declare class TestFlagExtraction {
  test_defer_flag_extraction(): void;
  test_fixme_flag_extraction(): void;
  test_idea_flag_extraction(): void;
  test_multiple_flags(): void;
  test_no_flags(): void;
  test_pending_flag_extraction(): void;
  test_todo_flag_extraction(): void;
}

export declare class TestSeedDetectorPatternMatching {
  test_code_quality_fixme_pattern(): void;
  test_code_quality_todo_pattern(): void;
  test_design_pattern_architecture(): void;
  test_design_pattern_performance(): void;
  test_design_pattern_refactor(): void;
  test_explicit_consider_pattern(): void;
  test_explicit_proposal_pattern(): void;
  test_explicit_we_should_pattern(): void;
  test_explicit_what_if_pattern(): void;
  test_multiple_seed_markers_in_text(): void;
  test_no_seed_detection_in_normal_text(): void;
  test_seed_source_preservation(): void;
  test_seed_text_truncation(): void;
}

export declare class TestSeedMetadata {
  test_seed_default_status(): void;
  test_seed_has_id(): void;
  test_seed_has_timestamp(): void;
  test_seed_to_dict_serialization(): void;
}

export declare class TestTagExtraction {
  test_architecture_tag(): void;
  test_multiple_tags(): void;
  test_no_tags_for_simple_seed(): void;
  test_performance_tag(): void;
  test_security_tag(): void;
  test_tag_limit(): void;
}

export declare function test_architecture_tag(): void;
export declare function test_code_quality_fixme_pattern(): void;
export declare function test_code_quality_todo_pattern(): void;
export declare function test_defer_flag_extraction(): void;
export declare function test_design_pattern_architecture(): void;
export declare function test_design_pattern_performance(): void;
export declare function test_design_pattern_refactor(): void;
export declare function test_explicit_consider_pattern(): void;
export declare function test_explicit_proposal_pattern(): void;
export declare function test_explicit_we_should_pattern(): void;
export declare function test_explicit_what_if_pattern(): void;
export declare function test_fixme_flag_extraction(): void;
export declare function test_idea_flag_extraction(): void;
export declare function test_lowercase_what_if(): void;
export declare function test_mixed_case_we_should(): void;
export declare function test_multiple_flags(): void;
export declare function test_multiple_seed_markers_in_text(): void;
export declare function test_multiple_tags(): void;
export declare function test_no_flags(): void;
export declare function test_no_seed_detection_in_normal_text(): void;
export declare function test_no_tags_for_simple_seed(): void;
export declare function test_pending_flag_extraction(): void;
export declare function test_performance_tag(): void;
export declare function test_security_tag(): void;
export declare function test_seed_default_status(): void;
export declare function test_seed_has_id(): void;
export declare function test_seed_has_timestamp(): void;
export declare function test_seed_source_preservation(): void;
export declare function test_seed_text_truncation(): void;
export declare function test_seed_to_dict_serialization(): void;
export declare function test_tag_limit(): void;
export declare function test_todo_flag_extraction(): void;
export declare function test_uppercase_consider(): void;
