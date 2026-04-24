# FR-GENT-015: Incremental XML Parser

## ID
- **FR-ID**: FR-GENT-015
- **Repository**: thegent
- **Domain**: CTR (Contracts)

## Description

The system SHALL parse streaming/partial XML from agent outputs using regex-based tag extraction (`<TAG>content</TAG>`), supporting allowed tag filtering, case-insensitive matching, partial state detection for unclosed tags, and error classification (PARSE_OK, PARSE_TRUNCATED, PARSE_INVALID_TAG, PARSE_MALFORMED).

## Acceptance Criteria

- [ ] Parses XML tags via regex
- [ ] Supports allowed tag filtering
- [ ] Case-insensitive tag matching
- [ ] Detects partial/unclosed tags

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/xml_tests.rs` | `test_xml_parser` | `// @trace FR-GENT-015` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/parser/xml.py` | `IncrementalXmlParser` | `@trace FR-GENT-015` |

## Related FRs

- FR-GENT-014: Canonical Structured Message Schema

## Status

- **Current**: implemented
- **Since**: 2026-01-20
