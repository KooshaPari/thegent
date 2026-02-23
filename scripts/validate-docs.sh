#!/bin/bash
#
# Documentation Quality Validation Script
# Validates all markdown files in the docs/ directory
# Run with: bash scripts/validate-docs.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCS_DIR="docs"
REPORT_FILE="${DOCS_DIR}/VALIDATION_REPORT.md"
ERRORS=0
WARNINGS=0
INFO=0

# Helper functions
log_error() {
    echo -e "${RED}✗ ERROR${NC}: $1"
    ((ERRORS++))
}

log_warning() {
    echo -e "${YELLOW}⚠ WARNING${NC}: $1"
    ((WARNINGS++))
}

log_info() {
    echo -e "${BLUE}ℹ INFO${NC}: $1"
    ((INFO++))
}

log_success() {
    echo -e "${GREEN}✓ OK${NC}: $1"
}

# Main validation functions

validate_markdown_files() {
    echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}Validating Markdown Files${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

    local md_files=$(find "${DOCS_DIR}" -name "*.md" -type f)
    local count=0
    local no_title=0

    for file in $md_files; do
        ((count++))
        
        # Check if file has a title (h1 heading)
        if ! head -1 "$file" | grep -q "^# "; then
            log_warning "Missing h1 title: $file"
            ((no_title++))
        else
            log_success "Title found: $(head -1 "$file" | sed 's/^# //')"
        fi
    done

    echo -e "\n${BLUE}Summary${NC}: Found $count markdown files, $no_title missing titles\n"
}

check_for_orphaned_docs() {
    echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}Checking for Orphaned Documents${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

    local orphaned=0
    local checked=0

    # Only check main docs, not archives/dumps/research
    local md_files=$(find "${DOCS_DIR}" -name "*.md" -type f \
        ! -path "${DOCS_DIR}/archives/*" \
        ! -path "${DOCS_DIR}/dumps/*" \
        ! -path "${DOCS_DIR}/research/*")

    for file in $md_files; do
        ((checked++))
        local basename=$(basename "$file" .md)
        
        # Check if document is referenced anywhere
        if grep -r -q "$(basename "$file")" "${DOCS_DIR}" --exclude-dir=archives --exclude-dir=dumps --exclude-dir=research > /dev/null 2>&1; then
            log_success "Referenced: $file"
        else
            # Skip index files and system files
            if [[ "$file" != *"README.md" ]] && [[ "$file" != *"INDEX.md" ]] && [[ "$file" != *"NAVIGATION"* ]]; then
                log_warning "Potentially orphaned: $file"
                ((orphaned++))
            fi
        fi
    done

    echo -e "\n${BLUE}Summary${NC}: Checked $checked documents, found $orphaned potentially orphaned\n"
}

list_docs_by_section() {
    echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}Documentation by Section${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

    for dir in "${DOCS_DIR}"/*; do
        if [ -d "$dir" ]; then
            local dirname=$(basename "$dir")
            local count=$(find "$dir" -maxdepth 2 -name "*.md" -type f | wc -l)
            if [ $count -gt 0 ]; then
                echo "  $dirname: $count files"
            fi
        fi
    done
    echo ""
}

check_link_validity() {
    echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}Checking Internal Link Validity${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

    local broken_links=0
    local valid_links=0
    
    # Extract all markdown link references
    local links=$(grep -r -h "\[.*\](.*)" "${DOCS_DIR}" --include="*.md" 2>/dev/null | grep -o "\./[^)]*" | sort | uniq)

    for link in $links; do
        # Remove anchors for file existence check
        local file=${link%%#*}
        
        # Skip external links (http, https, etc.)
        if [[ "$file" == http* ]]; then
            continue
        fi
        
        # Check if file exists
        if [ -f "$file" ]; then
            ((valid_links++))
        else
            log_warning "Broken link: $link"
            ((broken_links++))
        fi
    done

    echo -e "\nValid links: $valid_links, Broken links: $broken_links\n"
}

check_code_blocks() {
    echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}Validating Code Block Syntax${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

    local code_blocks=$(grep -r "^\`\`\`" "${DOCS_DIR}" --include="*.md" -c | grep -v ":0$" | wc -l)
    local unlabeled=0

    # Count unlabeled code blocks (```  with no language)
    unlabeled=$(grep -r "^\`\`\`$" "${DOCS_DIR}" --include="*.md" | wc -l)

    if [ $unlabeled -gt 0 ]; then
        log_warning "Found $unlabeled unlabeled code blocks (should specify language)"
    else
        log_success "All code blocks have language specified"
    fi

    echo -e "\nTotal code blocks: $code_blocks, Unlabeled: $unlabeled\n"
}

generate_statistics() {
    echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}Documentation Statistics${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

    local total_files=$(find "${DOCS_DIR}" -name "*.md" -type f | wc -l)
    local total_words=$(find "${DOCS_DIR}" -name "*.md" -type f -exec wc -w {} + | tail -1 | awk '{print $1}')
    local total_size=$(du -sh "${DOCS_DIR}" | awk '{print $1}')

    echo "Total markdown files: $total_files"
    echo "Total words: $total_words"
    echo "Total size: $total_size"
    echo ""

    # Count by category
    echo "Files by category:"
    find "${DOCS_DIR}" -maxdepth 1 -type d ! -name "docs" | while read dir; do
        local name=$(basename "$dir")
        local count=$(find "$dir" -name "*.md" | wc -l)
        [ $count -gt 0 ] && echo "  - $name: $count"
    done
    echo ""
}

generate_report() {
    echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}Validation Report${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

    echo "Total Errors: $ERRORS"
    echo "Total Warnings: $WARNINGS"
    echo "Total Info Messages: $INFO"
    echo ""

    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}✓ No critical errors found${NC}"
        return 0
    else
        echo -e "${RED}✗ Found $ERRORS critical errors${NC}"
        return 1
    fi
}

show_help() {
    cat << EOF
Documentation Quality Validator

Usage: bash scripts/validate-docs.sh [OPTIONS]

Options:
    -h, --help              Show this help message
    -q, --quick             Quick validation (files only, no links)
    -v, --verbose           Verbose output
    --fix                   Attempt to fix common issues (not implemented)

Examples:
    bash scripts/validate-docs.sh              # Full validation
    bash scripts/validate-docs.sh -q           # Quick check
    bash scripts/validate-docs.sh -v           # Verbose output

For more information, see: docs/NAVIGATION_MAP.md
EOF
}

# Main execution
main() {
    local quick_mode=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -q|--quick)
                quick_mode=true
                shift
                ;;
            -v|--verbose)
                # Already verbose by default
                shift
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Run validations
    echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   Documentation Quality Validation v1.0    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"

    if [ ! -d "$DOCS_DIR" ]; then
        log_error "Documentation directory not found: $DOCS_DIR"
        exit 1
    fi

    validate_markdown_files
    generate_statistics
    list_docs_by_section

    if [ "$quick_mode" = false ]; then
        check_for_orphaned_docs
        check_link_validity
        check_code_blocks
    fi

    # Generate final report
    generate_report
    local result=$?

    # Summary
    echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}Validation Complete${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

    exit $result
}

# Run main function
main "$@"
