# README

Source: docs/specs/README.md

---

# Specs/WBS/PRD Generation System

Quick reference guide for generating specifications, Work Breakdown Structures, and Product Requirements Documents from markdown files.

## Quick Start

```
# Generate specs for 10 projects (recommended for testing)
python3 thegent/specs/generate_all_specs.py --max-projects 10 --max-files 100

# Generate specs for 30 projects
python3 thegent/specs/generate_all_specs.py --max-projects 30 --max-files 150

# Full analysis (all projects, may take time)
python3 thegent/specs/generate_all_specs.py
```

## What Gets Generated

### Per Project

- **WBS** (`docs/specs/wbs/{project}_wbs.json`)
  - Hierarchical work breakdown structure
  - Estimated hours and dependencies
  
- **PRD** (`docs/specs/prds/{project}_prd.md` and `.json`)
  - Complete product requirements document
  - Features, requirements, architecture, timeline

### Unified

- **Unified Work Stream** (`docs/specs/UNIFIED_WORK_STREAM.md`)
  - Cross-project work streams
  - Shared features and dependencies
  
- **Analysis Results** (`docs/specs/ANALYSIS_RESULTS.json`)
  - Complete analysis summary
  - Project statistics

## Viewing Results

```
# View unified work stream
cat docs/specs/UNIFIED_WORK_STREAM.md

# View PRD for a project
cat docs/specs/prds/{project}_prd.md

# View WBS for a project
cat docs/specs/wbs/{project}_wbs.json | jq

# List all projects analyzed
python3 -c "import json; data=json.load(open('docs/specs/ANALYSIS_RESULTS.json')); print('\n'.join(data['project_specs_summary'].keys()))"
```

## How It Works

1. **Discovery**: Scans for project directories with markdown files
2. **Analysis**: Extracts features, tasks, WBS, and PRD content from markdown
3. **Cross-Analysis**: Finds relationships and shared features between projects
4. **Generation**: Creates WBS structures and PRDs for each project
5. **Unification**: Generates unified work streams across projects

## Content Extraction

The system extracts:

- **Features**: From feature lists, headings, and specifications
- **Tasks**: From checklists, task lists, and TODO items
- **WBS**: From hierarchical numbering (1.1.1, etc.)
- **PRD Sections**: From PRD documents and requirements files
- **Metadata**: Keywords, technologies, project references

## Output Structure

```
docs/specs/
├── ANALYSIS_RESULTS.json          # Summary of all analysis
├── UNIFIED_WORK_STREAM.json      # Unified work stream (JSON)
├── UNIFIED_WORK_STREAM.md        # Unified work stream (Markdown)
├── SPECS_GENERATION_SUMMARY.md   # Detailed summary
├── wbs/                          # Work Breakdown Structures
│   ├── project1_wbs.json
│   └── project2_wbs.json
└── prds/                         # Product Requirements Documents
    ├── project1_prd.md
    ├── project1_prd.json
    ├── project2_prd.md
    └── project2_prd.json
```

## Tips

1. **Start Small**: Use `--max-projects 10` to test first
2. **Adjust File Limits**: Use `--max-files` to control processing time
3. **Review Output**: Generated PRDs need human review and refinement
4. **Iterate**: Re-run with different limits to refine results

## Troubleshooting

**No projects found?**
- Check that project directories exist and contain markdown files
- Verify base path is correct

**Too many files?**
- Use `--max-files` to limit files per project
- Use `--max-projects` to limit number of projects

**Missing features?**
- Check markdown formatting (uses common patterns)
- Review extraction patterns in `markdown_analyzer.py`

## Next Steps

1. Review generated PRDs and refine as needed
2. Use unified work stream for planning
3. Integrate with project management tools
4. Set up automated generation on documentation updates

For detailed information, see `SPECS_GENERATION_SUMMARY.md`.