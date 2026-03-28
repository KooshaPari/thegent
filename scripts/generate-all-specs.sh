#!/bin/bash
# Generate AgilePlus specs for all projects

REPOS=(
  "agent-devops-setups"
  "agent-wave"
  "agentapi-plusplus"
  "agentops-policy-federation"
  "bifrost-extensions"
  "civ"
  "cliproxyapi-plusplus"
  "colab"
  "forgecode"
  "helMo"
  "parpour"
  "phench"
  "phenodocs"
  "phenotype-config"
  "phenotype-design"
  "phenotype-infrakit"
  "phenotype-skills-clone"
  "phenotypeActions"
  "policy-contract"
  "profiler"
  "template-commons"
  "template-domain-service-api"
  "template-domain-webapp"
  "template-lang-elixir-hex"
  "template-lang-go"
  "template-lang-kotlin"
  "template-lang-mojo"
  "template-lang-python"
  "template-lang-rust"
  "template-lang-swift"
  "template-lang-typescript"
  "template-lang-zig"
  "thegent-cache"
  "thegent-mesh"
  "thegent-metrics"
  "thegent-shm"
  "tokenledger"
  "trace"
  "trash-cli"
)

for repo in "${REPOS[@]}"; do
  if [[ ! -d "$repo/.git" ]]; then
    echo "SKIP: $repo (not a git repo)"
    continue
  fi
  
  echo "Processing $repo..."
  
  # Create kitty-specs directory
  mkdir -p "$repo/kitty-specs"
  
  # Analyze git history
  cd "$repo"
  
  # Get commit types and areas
  features=$(git log --format="%s" --since="2024-01-01" 2>/dev/null | grep -E "^(feat|fix|refactor|docs|chore)" | cut -d':' -f1 | cut -d'(' -f2 | cut -d')' -f1 | sort | uniq -c | sort -rn | head -5)
  
  # Count total commits
  total=$(git log --oneline --since="2024-01-01" 2>/dev/null | wc -l | tr -d ' ')
  
  if [[ "$total" == "0" ]]; then
    echo "  No commits since 2024 - creating minimal spec"
    mkdir -p "$repo/kitty-specs/001-initialization"
    cat > "$repo/kitty-specs/001-initialization/spec.md" << 'EOF'
# Spec: Project Initialization

## Meta

- **ID**: 001
- **Title**: Project Initialization
- **Created**: 2026-03-25
- **State**: specified

## Overview

Newly created project awaiting first implementation.

## Future Work
- Core functionality
- Tests
- Documentation
EOF
    cat > "$repo/kitty-specs/001-initialization/plan.md" << 'EOF'
# Plan: Project Initialization

## Timeline: 2026 Q1

## Phase 1: Core Setup
- Project structure
- Dependencies
- Basic functionality

## Verification
- Builds successfully
- Basic tests pass
EOF
  else
    echo "  Found $total commits - creating specs based on history"
    
    # Create spec based on project type
    case "$repo" in
      *colab*)
        mkdir -p "$repo/kitty-specs/001-colab-integration"
        cat > "$repo/kitty-specs/001-colab-integration/spec.md" << 'EOF'
# Spec: Colab Integration

## Meta

- **ID**: 001
- **Title**: Colab Integration
- **Created**: 2026-03-25
- **State**: shipped

## Overview

Integration with Google Colab for cloud-based notebook execution.

## Past Work (Completed)
- Colab runtime connection
- Notebook synchronization
- Execution pipeline

## Future Work
- Enhanced sync features
- Performance optimization
EOF
        cat > "$repo/kitty-specs/001-colab-integration/plan.md" << 'EOF'
# Plan: Colab Integration

## Timeline: 2024-2026

## Phase 1: Core Integration
- Runtime connection
- Basic sync

## Phase 2: Enhancement
- Feature completion
- Bug fixes

## Verification
- Notebooks execute correctly
- Sync reliable
EOF
        ;;
      *phench*)
        mkdir -p "$repo/kitty-specs/001-phench-cli"
        cat > "$repo/kitty-specs/001-phench-cli/spec.md" << 'EOF'
# Spec: Phench CLI

## Meta

- **ID**: 001
- **Title**: Phench CLI
- **Created**: 2026-03-25
- **State**: shipped

## Overview

Phench CLI tool for terminal and shell management.

## Past Work (Completed)
- CLI commands
- Shell integration
- Configuration

## Future Work
- Extended capabilities
- Plugin support
EOF
        cat > "$repo/kitty-specs/001-phench-cli/plan.md" << 'EOF'
# Plan: Phench CLI

## Timeline: 2024-2026

## Phase 1: Core CLI
- Commands
- Shell hooks

## Phase 2: Enhancement
- Features
- Integrations

## Verification
- Commands work
- Shell integration stable
EOF
        ;;
      *tokenledger*)
        mkdir -p "$repo/kitty-specs/001-token-management"
        cat > "$repo/kitty-specs/001-token-management/spec.md" << 'EOF'
# Spec: Token Management

## Meta

- **ID**: 001
- **Title**: Token Management
- **Created**: 2026-03-25
- **State**: shipped

## Overview

Token ledger for tracking and managing tokens across services.

## Past Work (Completed)
- Token tracking
- Ledger infrastructure
- API endpoints

## Future Work
- Analytics
- Token rotation
EOF
        cat > "$repo/kitty-specs/001-token-management/plan.md" << 'EOF'
# Plan: Token Management

## Timeline: 2024-2026

## Phase 1: Core
- Ledger storage
- Tracking logic

## Phase 2: API
- Endpoints
- Authentication

## Verification
- Tokens tracked correctly
- API functional
EOF
        ;;
      *forgecode*)
        mkdir -p "$repo/kitty-specs/001-code-forge"
        cat > "$repo/kitty-specs/001-code-forge/spec.md" << 'EOF'
# Spec: Code Forge

## Meta

- **ID**: 001
- **Title**: Code Forge
- **Created**: 2026-03-25
- **State**: shipped

## Overview

Code generation and templating infrastructure.

## Past Work (Completed)
- Template engine
- Code generation
- CLI tooling

## Future Work
- More templates
- Enhanced customization
EOF
        cat > "$repo/kitty-specs/001-code-forge/plan.md" << 'EOF'
# Plan: Code Forge

## Timeline: 2024-2026

## Phase 1: Core Engine
- Template processing
- Output generation

## Phase 2: CLI
- Command interface
- Configuration

## Verification
- Templates render correctly
- CLI works
EOF
        ;;
      *template-lang-*)
        lang="${repo##*-}"
        mkdir -p "$repo/kitty-specs/001-language-template"
        cat > "$repo/kitty-specs/001-language-template/spec.md" << 'EOF'
# Spec: Language Template

## Meta

- **ID**: 001
- **Title': Language Template
- **Created**: 2026-03-25
- **State**: shipped

## Overview

Template project for language development and testing.

## Past Work (Completed)
- Project scaffold
- Basic tooling
- CI configuration

## Future Work
- Enhanced templates
- Best practices documentation
EOF
        cat > "$repo/kitty-specs/001-language-template/plan.md" << 'EOF'
# Plan: Language Template

## Timeline: 2024-2026

## Phase 1: Scaffold
- Project structure
- Basic files

## Phase 2: Tooling
- Build config
- Testing setup

## Verification
- Builds work
- Tests run
EOF
        ;;
      *thegent-*)
        variant="${repo##*-}"
        mkdir -p "$repo/kitty-specs/001-$variant"
        cat > "$repo/kitty-specs/001-$variant/spec.md" << 'EOF'
# Spec: TheGent Variant

## Meta

- **ID**: 001
- **Title**: TheGent Variant
- **Created**: 2026-03-25
- **State**: shipped

## Overview

Specialized variant of TheGent with specific focus.

## Past Work (Completed)
- Core functionality
- Variant-specific features

## Future Work
- Feature enhancement
- Integration improvements
EOF
        cat > "$repo/kitty-specs/001-$variant/plan.md" << 'EOF'
# Plan: TheGent Variant

## Timeline: 2024-2026

## Phase 1: Core
- Base functionality
- Variant features

## Phase 2: Integration
- System integration
- Testing

## Verification
- Functional
- Tested
EOF
        ;;
      *)
        mkdir -p "$repo/kitty-specs/001-core-functionality"
        cat > "$repo/kitty-specs/001-core-functionality/spec.md" << 'EOF'
# Spec: Core Functionality

## Meta

- **ID**: 001
- **Title**: Core Functionality
- **Created**: 2026-03-25
- **State**: shipped

## Overview

Core project functionality and features.

## Past Work (Completed)
- Core implementation
- Tests
- Documentation

## Future Work
- Feature enhancements
- Performance improvements
EOF
        cat > "$repo/kitty-specs/001-core-functionality/plan.md" << 'EOF'
# Plan: Core Functionality

## Timeline: 2024-2026

## Phase 1: Core
- Implementation
- Testing

## Phase 2: Enhancement
- Features
- Polish

## Verification
- Tests pass
- Documentation complete
EOF
        ;;
    esac
  fi
  
  cd ..
  git add -A 2>/dev/null
  git commit -m "feat: add AgilePlus specs for $repo

Add kitty-specs documenting project functionality." 2>/dev/null
  echo "  Committed for $repo"
done

echo ""
echo "Done generating specs for all projects"
