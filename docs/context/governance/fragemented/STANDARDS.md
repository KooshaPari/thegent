# Ante LLM Context Documentation Standards

## 1. Markdown Formatting Standards

### 1.1 File Structure

**Document metadata (required):**
```markdown
---
title: Document Title
description: Brief description of content
version: 1.0.0
ante_version: ">=0.1.0"
last_updated: 2026-02-20
status: current
---

# Document Title

Content begins here...
```

**Metadata fields:**
- `title`: Descriptive document title
- `description`: 1-2 sentence summary
- `version`: Documentation version (X.Y.Z)
- `ante_version`: Ante compatibility range
- `last_updated`: ISO 8601 date format
- `status`: current|beta|deprecated|archived

### 1.2 Heading Hierarchy

**Rules:**
- Use H1 (#) only once per document for the main title
- Use H2 (##) for major sections
- Use H3 (###) for subsections
- Use H4 (####) for detailed sections
- Don't skip heading levels
- Keep heading text concise and descriptive

**Examples:**
```markdown
# Main Document Title

## Major Section
Content about major section

### Subsection
Related content

#### Detailed Subsection
More specific content
```

### 1.3 Text Formatting

**Emphasis:**
- Use `*italic*` for emphasis
- Use `**bold**` for strong emphasis
- Avoid excessive formatting
- Don't overuse ALL CAPS

**Code:**
- Inline code: `command` or `variable`
- Code blocks: Use triple backticks with language
- File paths: Use backticks `` `/path/to/file` ``
- Command options: Use backticks `` `--option` ``

**Lists:**
- Use `-` for unordered lists
- Use numbers (1., 2., 3.) for ordered lists
- Indent nested lists by 2 spaces
- Leave blank line before lists
- End list items with period if they're sentences

**Examples:**

Unordered list:
```markdown
- Item one
- Item two
  - Nested item
  - Another nested
- Item three
```

Ordered list:
```markdown
1. First step
2. Second step
   1. Substep a
   2. Substep b
3. Third step
```

### 1.4 Code Blocks

**Format:**
```markdown
\`\`\`[language]
code content
\`\`\`
```

**Supported languages:**
- `bash` - Shell commands
- `shell` - Shell scripts
- `json` - JSON data
- `yaml` - YAML configuration
- `markdown` - Markdown examples
- `text` - Plain text output
- `javascript` or `js` - JavaScript
- `python` - Python code
- `go` - Go code
- `rust` - Rust code

**Examples:**

Bash command:
```markdown
\`\`\`bash
ante run --context-size 32kb script.txt
\`\`\`
```

Output/Result:
```markdown
\`\`\`text
Output from command
Line 2 of output
\`\`\`
```

Configuration:
```markdown
\`\`\`yaml
context-size: 32kb
max-tokens: 8000
\`\`\`
```

### 1.5 Links

**Format:**
- Relative links: `[Text](../path/to/file.md)`
- Anchor links: `[Text](#section-heading)`
- External links: `[Text](https://example.com)`

**Rules:**
- Use descriptive link text, not "click here"
- Use relative paths for internal links
- Use HTTPS for external links
- Validate all links work
- Update links when documents move

**Examples:**
```markdown
See [Configuration Guide](./configuration.md) for details.

For more, see the [Advanced Options](#advanced) section below.

Read the [Ante Documentation](https://docs.antigma.ai).
```

### 1.6 Block Quotes

**Format:**
```markdown
> This is a quoted block
> that continues on multiple lines
```

**Use for:**
- Important notes
- Warnings or cautions
- Tips and tricks
- Highlighted information

**Examples:**

Note:
```markdown
> **Note:** This is an important note about the feature.
```

Warning:
```markdown
> ⚠️ **Warning:** This could impact performance.
```

Tip:
```markdown
> 💡 **Tip:** You can use this shortcut to save time.
```

### 1.7 Tables

**Format:**
```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

**Rules:**
- Header row required
- Use pipes (|) to separate columns
- Use dashes (-) for row separators
- Align content for readability
- Include 3+ rows for tables
- Use lists for 2-row content

**Example:**
```markdown
| Option | Type | Default |
|--------|------|---------|
| `--context-size` | string | 32kb |
| `--max-tokens` | integer | 8000 |
| `--model` | string | gpt-4 |
```

### 1.8 Horizontal Rules

Use for visual separation between major sections:
```markdown
---
```

Guidelines:
- Use sparingly
- Don't use at document start or end
- Use between major topic shifts
- Alternative to extra headings

## 2. Code Example Standards

### 2.1 Example Quality Requirements

**Completeness:**
- Includes all necessary setup/imports
- Shows realistic usage
- Includes expected output or result
- Includes error handling if relevant
- Is self-contained and runnable

**Clarity:**
- Comments explain non-obvious code
- Variable names are descriptive
- Following code style conventions
- Realistic data/values
- Not overly complex

**Accuracy:**
- Works with current Ante version
- Output matches documentation
- All options are correct
- Edge cases handled
- Error messages are accurate

### 2.2 Command Line Examples

**Format:**
```markdown
\`\`\`bash
ante [command] [options]
\`\`\`

Output:
\`\`\`text
Expected output here
\`\`\`
```

**Rules:**
- Show full command with all relevant options
- Include realistic data
- Show typical output
- Highlight important parts with comments
- Document assumptions

**Example:**
```markdown
Get context information:

\`\`\`bash
ante context --format json --limit 100
\`\`\`

Output:
\`\`\`json
{
  "items": [
    {"id": 1, "name": "item1", "size": 1024}
  ],
  "total": 1,
  "limit": 100
}
\`\`\`
```

### 2.3 Error Examples

**Format:**
```markdown
When [condition], you get:

\`\`\`bash
ante [command] --invalid-option
\`\`\`

This produces:
\`\`\`text
Error: Unknown option '--invalid-option'
Did you mean '--validate'?
\`\`\`

Solution: [Fix description]
```

### 2.4 Multi-Step Examples

**Format:**
```markdown
\`\`\`bash
# Step 1: Description
ante command --option1

# Step 2: Description
ante command --option2
\`\`\`
```

**Rules:**
- Use comments for step descriptions
- Show intermediate results if relevant
- Number steps in comments
- Explain what happens at each step
- Note any prerequisites

### 2.5 Pseudo-code and Conceptual Examples

**Use when:**
- Feature not yet released
- Cross-platform examples needed
- Conceptual clarity needed
- Avoiding language-specific details

**Format:**
```markdown
\`\`\`text
# Pseudocode example
INITIALIZE context
FOR EACH document IN collection
  CALCULATE relevance
  IF relevance > threshold
    ADD TO results
  END IF
END FOR
RETURN results
\`\`\`
```

### 2.6 Configuration Examples

**Format:**
```markdown
\`\`\`yaml
# Example configuration file
setting1: value1
setting2: value2
section:
  subsetting: value
\`\`\`
```

**Rules:**
- Show realistic values
- Comment non-obvious settings
- Include all required settings
- Show optional settings separately
- Validate syntax

**Example:**
```markdown
# Basic configuration:
\`\`\`yaml
ante:
  context-size: 32kb
  max-tokens: 8000
\`\`\`

# Advanced configuration:
\`\`\`yaml
ante:
  context-size: 64kb
  max-tokens: 16000
  performance:
    cache-enabled: true
    compression: gzip
\`\`\`
```

## 3. Link and Reference Standards

### 3.1 Internal Links

**Format:**
```markdown
[Link text](../path/to/file.md)
[Link text](#section-anchor)
[Link text](./file.md#section-anchor)
```

**Rules:**
- Use relative paths (start with `./` or `../`)
- Never use absolute paths
- Link text should be descriptive
- Verify links work before committing
- Update links when documents move

**Examples:**
```markdown
See the [CLI Reference](../reference/cli.md) for more options.

For advanced usage, see [Configuration](./config.md#advanced).

Related: [Performance Tips](../guides/performance.md#optimization)
```

### 3.2 External Links

**Format:**
```markdown
[Link text](https://example.com/path)
```

**Rules:**
- Always use HTTPS
- Use descriptive link text
- Don't link to URLs that might change
- Prefer official documentation
- Test links periodically

**Examples:**
```markdown
See the [Python documentation](https://docs.python.org/).

For more, visit [Ante GitHub](https://github.com/AntigmaLabs/ante).
```

### 3.3 Link Anchors

**Format:**
```markdown
# Section Title
Content here

[Link to section](#section-title)
```

**Rules:**
- Anchors are lowercase version of heading
- Replace spaces with hyphens
- Remove special characters
- Keep anchors consistent
- Use meaningful heading text

**Examples:**
```markdown
# Advanced Configuration
Content...

[Back to Advanced Configuration](#advanced-configuration)

# Performance Optimization Tips
Content...

[Skip to Performance Tips](#performance-optimization-tips)
```

### 3.4 See Also Sections

**Format:**
```markdown
## See Also
- [Related Topic](link)
- [Another Topic](link)
- [More Information](link)
```

**Rules:**
- Include at end of document
- List 2-5 related topics
- Use descriptive link text
- Organize by relevance
- Keep descriptions brief

**Example:**
```markdown
## See Also
- [Configuration Guide](./configuration.md) - How to configure Ante
- [CLI Reference](../reference/cli.md) - Full command reference
- [Performance Tuning](./performance.md) - Optimization tips
- [Troubleshooting](../guides/troubleshooting.md) - Common issues
```

### 3.5 Reference Format

**When referring to:**
- Commands: Use backticks and full syntax
- Options: Use backticks with leading dashes
- Functions: Use backticks
- Files: Use backticks with path
- Variables: Use backticks

**Examples:**
```markdown
Use the `ante run` command to execute scripts.

The `--context-size` option controls memory usage.

See the `calculate_score()` function for details.

Edit the `~/.ante/config.yaml` configuration file.

Set the `$ANTE_HOME` variable to customize paths.
```

## 4. Naming Conventions for Files

### 4.1 File Naming Rules

**Use lowercase with hyphens:**
```
good-file-name.md
AVOID CamelCase.md
AVOID file_with_underscores.md
AVOID spaces in filename.md
```

**Rules:**
- Use lowercase letters, numbers, and hyphens only
- Use hyphens to separate words
- No special characters
- No spaces in filenames
- Descriptive but concise
- No version numbers in filename

### 4.2 File Organization

```
docs/context/
├── governance/              # This framework
│   ├── GOVERNANCE.md
│   ├── PROCESSES.md
│   ├── MAINTENANCE.md
│   └── STANDARDS.md
├── llm-context/            # LLM-optimized documentation
│   ├── overview.md
│   ├── commands.md
│   └── workflows.md
├── wiki/                   # User-facing documentation
│   ├── getting-started.md
│   ├── guides/
│   │   ├── configuration.md
│   │   ├── performance.md
│   │   └── troubleshooting.md
│   ├── reference/
│   │   ├── cli.md
│   │   ├── api.md
│   │   └── options.md
│   ├── examples/
│   │   ├── basic-usage.md
│   │   ├── advanced-patterns.md
│   │   └── integration.md
│   └── faq.md
├── archive/                # Deprecated versions
│   ├── v0.1.0/
│   ├── v0.2.0/
│   └── README.md
└── llms.txt               # LLM context file
```

### 4.3 Naming Specific Document Types

**Guides:**
- `getting-started.md`
- `configuration.md`
- `installation.md`
- `advanced-usage.md`

**Reference:**
- `cli-reference.md` or `cli.md`
- `api-reference.md` or `api.md`
- `options-reference.md` or `options.md`

**Examples:**
- `basic-examples.md`
- `advanced-patterns.md`
- `integration-examples.md`

**Administration:**
- `governance.md`
- `processes.md`
- `standards.md`

### 4.4 Directory Naming

**Rules:**
- Use lowercase with hyphens
- Singular or plural consistently (use plural for collections)
- Descriptive but concise
- No version numbers

**Examples:**
```
guides/          (plural: collection of guides)
tutorials/       (plural: collection of tutorials)
examples/        (plural: collection of examples)
reference/       (singular: comprehensive reference)
governance/      (singular: the governance framework)
```

## 5. Content Structure Requirements

### 5.1 Standard Document Structure

**Recommended structure:**
```
---
title: ...
description: ...
version: ...
ante_version: ...
last_updated: ...
status: ...
---

# Main Title

## Overview
[What this document covers and why it matters]

## Prerequisites
[What users should know before reading]

## Core Concepts
[Important definitions and relationships]

## Main Content
[Organized into logical sections]

### Subsection 1
Details...

### Subsection 2
Details...

## Examples
[Practical examples]

## Common Issues
[Troubleshooting section]

## Advanced Topics
[Optional: for power users]

## Limitations
[What this feature cannot do]

## See Also
[Related documentation]
```

### 5.2 Section Guidelines

**Overview:**
- 1-3 sentences
- Explain purpose and audience
- Set expectations
- Indicate document scope

**Prerequisites:**
- List required knowledge
- Link to prerequisite documents
- List software/tools needed
- Indicate skill level

**Core Concepts:**
- Define important terms
- Explain relationships
- Show mental models
- Use diagrams if helpful

**Main Content:**
- Logical organization
- Progressive complexity
- Clear headings
- Helpful examples
- Related features cross-referenced

**Examples:**
- Realistic scenarios
- Working code/commands
- Expected output
- Variation examples
- Error examples

**Common Issues:**
- Frequently asked questions
- Common mistakes
- Troubleshooting steps
- Where to get help

**Advanced Topics:**
- Optional section
- For experienced users
- Less common patterns
- Performance considerations
- Edge cases

**See Also:**
- 2-5 related documents
- Brief description of each
- Organized by relevance

### 5.3 Completeness Checklist

Before marking document complete:

**Content**
- [ ] All features mentioned
- [ ] Examples are provided
- [ ] Edge cases documented
- [ ] Limitations listed
- [ ] Prerequisites stated
- [ ] Related features linked

**Quality**
- [ ] No placeholder text (TODO, TBD)
- [ ] Spelling and grammar correct
- [ ] Formatting consistent
- [ ] Code examples tested
- [ ] Links validated
- [ ] Metadata complete

**Standards Compliance**
- [ ] Metadata present
- [ ] Follows style guide
- [ ] Proper heading hierarchy
- [ ] Tables/lists formatted correctly
- [ ] File name follows convention
- [ ] No broken links

**LLM Optimization**
- [ ] Clear section headers
- [ ] Concise explanations
- [ ] Practical examples
- [ ] Consistent terminology
- [ ] Version information clear

## 6. Code Style and Formatting Standards

### 6.1 Bash/Shell Examples

**Style:**
```bash
#!/bin/bash
# Clear comment explaining what this does

# Use meaningful variable names
context_size="32kb"

# Use quotes around variables
echo "Context size: $context_size"

# Use full command names (not aliases)
ls -la /path/to/directory
```

**Rules:**
- Use full command names (not aliases)
- Use meaningful variable names
- Quote variables
- Add comments for non-obvious lines
- Use `#!/bin/bash` for scripts
- Handle errors appropriately

### 6.2 JSON Examples

**Style:**
```json
{
  "name": "example",
  "version": "1.0.0",
  "settings": {
    "context-size": "32kb",
    "max-tokens": 8000
  }
}
```

**Rules:**
- Consistent indentation (2 spaces)
- Quotes around all strings
- Trailing comma in last item (check JSON spec)
- Descriptive key names
- Realistic values

### 6.3 YAML Examples

**Style:**
```yaml
# Configuration file
application:
  name: ante
  version: 1.0.0
settings:
  context-size: 32kb
  max-tokens: 8000
```

**Rules:**
- Use 2-space indentation
- Clear comments
- Consistent key naming (lowercase with hyphens)
- Realistic values
- Show nested structure clearly

## 7. Document Versioning and Status

### 7.1 Version Numbering

**Format:** X.Y.Z (semantic versioning)

- X (Major): Breaking changes to documentation structure
- Y (Minor): New sections, significant additions
- Z (Patch): Corrections, clarifications, minor updates

**Examples:**
- Initial release: 1.0.0
- Add new section: 1.1.0
- Fix typo: 1.0.1
- Reorganize structure: 2.0.0

### 7.2 Status Field

**Allowed values:**

- `current` - Current, maintained documentation
- `beta` - Experimental, subject to change
- `deprecated` - Will be archived soon
- `archived` - Older version, reference only

### 7.3 Ante Compatibility

**Format:** Specify Ante version compatibility

```yaml
ante_version: ">=0.1.0"
ante_version: ">=0.2.0, <0.3.0"
ante_version: "0.2.x"
```

## 8. Accessibility and LLM Optimization

### 8.1 LLM-Friendly Formatting

**Principles:**
1. Clear section hierarchy
2. Descriptive headings
3. Concise, technical language
4. Practical examples
5. Complete context
6. Explicit assumptions

**Example - Not optimized:**
```markdown
Ante can do stuff with files and things. You just run it and it works.
See the guide for more info.
```

**Example - LLM-optimized:**
```markdown
## Processing Files with Ante

The `ante process` command handles file analysis:

\`\`\`bash
ante process --input file.txt --output result.json
\`\`\`

This command:
- Reads the input file
- Analyzes content
- Outputs structured results as JSON
- Returns exit code 0 on success, non-zero on error
```

### 8.2 Explicit Context

**Always include:**
- Command full name and syntax
- Expected inputs/outputs
- Exit codes and errors
- Version limitations
- Related commands/features

### 8.3 Consistency for LLM Parsing

**Use consistent patterns:**

For commands:
```markdown
## Command: [name]

Syntax:
\`\`\`
[full syntax]
\`\`\`

Description: [What it does]

Options:
- \`--option1\`: Description
- \`--option2\`: Description

Example:
\`\`\`bash
[example]
\`\`\`
```

For features:
```markdown
## Feature: [name]

Overview: [Brief description]

When to use: [Common scenarios]

Example:
\`\`\`
[example]
\`\`\`

Limitations: [What it can't do]
```

## 9. Quality Assurance Checklist

Before submitting any documentation for review:

**Content Quality**
- [ ] No placeholder text (TODO, TBD, [PENDING])
- [ ] All information is accurate
- [ ] Examples work with current version
- [ ] Edge cases are documented
- [ ] Limitations are noted
- [ ] Prerequisites are stated

**Format and Standards**
- [ ] Metadata is complete
- [ ] Heading hierarchy is correct
- [ ] No lines exceed 120 characters
- [ ] Code blocks have language specified
- [ ] Lists are formatted correctly
- [ ] Tables are aligned properly

**Links and References**
- [ ] All links are valid relative paths
- [ ] No broken anchors
- [ ] External links use HTTPS
- [ ] Cross-references are accurate
- [ ] See Also section present (if applicable)

**Writing Quality**
- [ ] No spelling errors
- [ ] No grammar errors
- [ ] Clear, concise language
- [ ] Technical terms defined
- [ ] Consistent terminology
- [ ] Good paragraph structure

**LLM Optimization**
- [ ] Clear section headers
- [ ] Descriptive headings
- [ ] Explicit command syntax
- [ ] Complete examples
- [ ] Assumptions stated
- [ ] Version information clear

**Standards Compliance**
- [ ] Follows STANDARDS.md
- [ ] File name follows convention
- [ ] Version number appropriate
- [ ] Status field correct
- [ ] All required metadata present

## 10. Common Mistakes to Avoid

**Don't:**
- Use CamelCase in file names
- Create orphaned documents (not linked from index)
- Write vague section headings
- Use `click here` as link text
- Include placeholder content
- Forget to test examples
- Use outdated Ante syntax
- Create overly long documents (>3000 words)
- Write for search engines instead of users
- Break internal links when reorganizing

**Do:**
- Use lowercase with hyphens
- Link all documents from index
- Use descriptive, specific headings
- Write meaningful link text
- Complete all sections before publishing
- Test all code examples
- Keep examples current
- Break long content into multiple files
- Write for human and LLM readers
- Update cross-references when moving documents
