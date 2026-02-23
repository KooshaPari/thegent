# Wiki Navigation Examples

## Example 1: How do I set up Ante?

**Search Path**: Start at `/docs/context/wiki/`

1. **Initial exploration**: Check `README.md` for overview
2. **Setup guide**: Look in `guides/installation.md` or `getting-started.md`
3. **Configuration**: Reference `reference/configuration.md`
4. **Quick start**: See `guides/quickstart.md` for first steps

**Real search flow**:
```bash
# Browse wiki structure
ls docs/context/wiki/guides/

# Read the installation guide
cat docs/context/wiki/guides/installation.md

# Reference config options
grep -A5 "ANTE_" docs/context/wiki/reference/configuration.md
```

**Answer**: Setup typically involves:
- Installing with `ante install`
- Running `ante init` in your project
- Configuring `ante.config.yaml`
- Creating your first skill

See: `wiki/guides/installation.md`, `wiki/guides/quickstart.md`

---

## Example 2: What tools are available?

**Search**: `wiki/reference/tools-api.md`

**Quick Answer**:
- CLI Tools: Bash, Read, Write, Edit, Glob, Grep
- Integration Tools: WebFetch, TodoWrite
- Custom Tools: Can be added via skill system

See: `wiki/reference/tools-api.md` for full API documentation

**Finding details**:
```bash
# List all available tools
ls docs/context/wiki/reference/

# Search for specific tool documentation
grep -r "Tool.*Description" docs/context/wiki/
```

---

## Example 3: How do I create a custom skill?

**Search Path**:
1. Start: `wiki/guides/custom-skills.md` (main guide)
2. Templates: `wiki/reference/skill-templates/`
3. Examples: `wiki/examples/` (if available)

**Key sections to find**:
- Skill structure and anatomy
- Interface implementation
- Registration process
- Testing custom skills

**Implementation reference**:
```bash
# Look at skill template
cat docs/context/wiki/reference/skill-templates/basic-skill.py

# Check integration examples
grep -r "custom.*skill" docs/context/wiki/

# Review API documentation
cat docs/context/wiki/reference/skill-api.md
```

**Answer path**: 
1. Read `wiki/guides/custom-skills.md` for overview
2. Use template from `wiki/reference/skill-templates/`
3. Follow examples in `docs/examples/`
4. Test using `ante test`

---

## Example 4: How do I integrate with a new model provider?

**Search**: `wiki/guides/integration.md` or `wiki/guides/provider-integration.md`

**Navigation**:
1. Provider integration architecture: `wiki/guides/integration.md`
2. Specific provider examples: `wiki/guides/providers/`
3. API reference: `wiki/reference/provider-api.md`
4. Authentication: `wiki/reference/authentication.md`

**Key steps to find**:
```bash
# Find provider documentation
ls docs/context/wiki/guides/providers/

# Check specific provider (e.g., OpenAI)
cat docs/context/wiki/guides/providers/openai.md

# Find auth requirements
grep -r "authentication\|api.*key" docs/context/wiki/guides/providers/
```

**Answer navigation**:
1. Understand provider interface in `integration.md`
2. Review authentication requirements
3. Implement provider class
4. Register in configuration
5. Test integration

---

## Example 5: What are the best practices for performance?

**Search**: `wiki/guides/performance.md` or `wiki/reference/performance-tuning.md`

**Related documentation**:
- Optimization: `wiki/guides/optimization.md`
- Caching: `wiki/reference/caching.md`
- Benchmarking: `wiki/guides/benchmarking.md`

**Key areas**:
```bash
# Search for performance guidance
grep -r "performance\|optimization\|benchmark" docs/context/wiki/guides/ | head -20

# Find caching documentation
cat docs/context/wiki/reference/caching.md

# Check monitoring guide
cat docs/context/wiki/guides/monitoring.md
```

**Best practices include**:
- Tool reuse patterns (Example 5 in llms-txt-integration-examples.md)
- Caching strategies
- Batch operations
- Resource pooling
- Monitoring and metrics

---

## Wiki Structure Quick Reference

```
docs/context/wiki/
├── guides/              # How-to guides
│   ├── quickstart.md
│   ├── installation.md
│   ├── custom-skills.md
│   ├── integration.md
│   ├── performance.md
│   └── providers/       # Provider-specific guides
├── reference/           # Technical reference
│   ├── tools-api.md
│   ├── skill-api.md
│   ├── configuration.md
│   ├── caching.md
│   └── skill-templates/
├── examples/            # Code examples
├── architecture/        # Architecture docs
└── README.md           # Wiki overview
```

---

## Search Tips

1. **Use grep for quick searches**:
   ```bash
   grep -r "your-topic" docs/context/wiki/ --include="*.md"
   ```

2. **Browse by category**: Start with `guides/` for how-tos, `reference/` for technical details

3. **Check README files**: Each directory has a README explaining contents

4. **Look for examples**: Many guides include code examples

5. **Cross-reference**: Use links in documents to navigate related content

---

## Common Navigation Patterns

| Question | Start Here | Then See |
|----------|-----------|----------|
| "How do I...?" | `guides/` | `reference/` for details |
| "What is...?" | `README.md` | `architecture/` for details |
| "What are the options for...?" | `reference/` | `guides/` for examples |
| "How do I configure...?" | `reference/configuration.md` | Provider-specific guides |
| "Show me an example" | `examples/` | Related guide |
