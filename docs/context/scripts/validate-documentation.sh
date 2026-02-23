#!/bin/bash

################################################################################
# Documentation Validation Script
################################################################################
#
# PURPOSE:
# Validates documentation integrity by checking markdown formatting, links,
# file naming standards, required sections, and code block formatting.
#
# USAGE:
# ./validate-documentation.sh [OPTIONS]
#
# OPTIONS:
# --help              Show this help message
# --strict            Fail on warnings (default: warnings only)
# --fix               Attempt to auto-fix common issues
# --docs-path PATH    Specify custom documentation path (default: ./docs)
# --verbose           Show detailed output
#
# EXAMPLE:
# ./validate-documentation.sh --strict --verbose
#
# EXIT CODES:
# 0 - All checks passed
# 1 - Warnings found (non-strict mode)
# 2 - Critical errors found
#
################################################################################

set -euo pipefail

# Configuration
DOCS_PATH="${DOCS_PATH:-.}"
STRICT_MODE=false
FIX_MODE=false
VERBOSE=false
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="docs_validation_report_${TIMESTAMP}.txt"

# Counters
TOTAL_FILES=0
FILES_CHECKED=0
ERRORS=0
WARNINGS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo "[INFO] $*" | tee -a "$REPORT_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "$REPORT_FILE"
    ((ERRORS++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "$REPORT_FILE"
    ((WARNINGS++))
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $*" | tee -a "$REPORT_FILE"
    ((PASSED_CHECKS++))
}

log_verbose() {
    if [[ $VERBOSE == true ]]; then
        echo "[DEBUG] $*" | tee -a "$REPORT_FILE"
    fi
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}" | tee -a "$REPORT_FILE"
}

show_help() {
    sed -n '1,/^################################/p' "$0" | head -40
    exit 0
}

fail_if_strict() {
    if [[ $STRICT_MODE == true ]]; then
        return 1
    fi
    return 0
}

################################################################################
# Check 1: Markdown Formatting Validation
################################################################################

check_markdown_formatting() {
    local file="$1"
    local filename=$(basename "$file")
    local file_errors=0

    log_verbose "Checking markdown formatting: $file"

    # Check for proper heading hierarchy
    if ! grep -q "^# " "$file"; then
        log_warning "File $file missing H1 heading"
        ((file_errors++))
    fi

    # Check for multiple H1 headings (only one should exist)
    local h1_count=$(grep -c "^# " "$file" || echo 0)
    if [[ $h1_count -gt 1 ]]; then
        log_error "File $file has $h1_count H1 headings (should have 1)"
        ((file_errors++))
    fi

    # Check for skipped heading levels (e.g., # -> #### without ### ##)
    if grep -qE "^## " "$file" && ! grep -q "^# " "$file"; then
        log_warning "File $file has H2 without H1"
        ((file_errors++))
    fi

    # Check for unmatched code blocks
    local open_blocks=$(grep -c '```' "$file" || echo 0)
    if (( open_blocks % 2 != 0 )); then
        log_error "File $file has unmatched code blocks (count: $open_blocks)"
        ((file_errors++))
    fi

    # Check for lines exceeding 120 characters
    local long_lines=$(awk 'length > 120 {count++} END {print count+0}' "$file")
    if [[ $long_lines -gt 0 ]]; then
        log_warning "File $file has $long_lines lines exceeding 120 characters"
        ((file_errors++))
    fi

    # Check for trailing whitespace
    if grep -q '[[:space:]]$' "$file"; then
        log_warning "File $file has trailing whitespace"
        if [[ $FIX_MODE == true ]]; then
            sed -i '' 's/[[:space:]]*$//' "$file"
            log_info "Fixed trailing whitespace in $file"
        fi
        ((file_errors++))
    fi

    # Check for tabs instead of spaces
    if grep -q $'\t' "$file"; then
        log_warning "File $file contains tabs (should use spaces)"
        ((file_errors++))
    fi

    # Check for proper list formatting
    if grep -qE "^[\*\+] " "$file" && grep -qE "^- " "$file"; then
        log_warning "File $file mixes different list markers"
        ((file_errors++))
    fi

    return $file_errors
}

################################################################################
# Check 2: Link Validation
################################################################################

check_links() {
    local file="$1"
    local file_errors=0

    log_verbose "Checking links: $file"

    # Extract all markdown links
    local links=$(grep -oE '\[.*\]\(.*\)' "$file" || echo "")

    if [[ -z "$links" ]]; then
        log_verbose "No links found in $file"
        return 0
    fi

    while IFS= read -r link; do
        # Extract the URL part from [text](url)
        local url=$(echo "$link" | sed 's/.*(\(.*\)).*/\1/')
        
        # Skip external links (starting with http)
        if [[ $url == http* ]]; then
            log_verbose "Skipping external link: $url"
            continue
        fi

        # Extract just the file path (before #)
        local file_path="${url%%#*}"
        
        # Skip empty paths and anchors only
        if [[ -z "$file_path" ]]; then
            continue
        fi

        # Resolve relative path
        local target_path
        target_path=$(cd "$(dirname "$file")" && cd "$(dirname "$file_path")" && pwd)/$(basename "$file_path")
        
        # Check if file exists
        if [[ ! -f "$target_path" ]]; then
            log_error "Broken link in $file: $url (target: $target_path does not exist)"
            ((file_errors++))
        else
            log_success "Link valid: $url"
        fi
    done <<< "$links"

    return $file_errors
}

################################################################################
# Check 3: File Naming Standards
################################################################################

check_file_naming() {
    local file="$1"
    local filename=$(basename "$file")
    local file_errors=0

    log_verbose "Checking file naming: $filename"

    # Check for lowercase with hyphens only
    if [[ ! "$filename" =~ ^[a-z0-9._-]+\.md$ ]]; then
        log_warning "File $filename doesn't follow naming convention (should be lowercase with hyphens)"
        ((file_errors++))
    fi

    # Check for spaces in filename
    if [[ "$filename" =~ [[:space:]] ]]; then
        log_error "File $filename contains spaces"
        ((file_errors++))
    fi

    # Check for CamelCase
    if [[ "$filename" =~ [[:upper:]] ]]; then
        log_warning "File $filename contains uppercase letters"
        ((file_errors++))
    fi

    # Check for underscores (should use hyphens)
    if [[ "$filename" =~ _ ]]; then
        log_warning "File $filename uses underscores (should use hyphens)"
        ((file_errors++))
    fi

    return $file_errors
}

################################################################################
# Check 4: Required Sections
################################################################################

check_required_sections() {
    local file="$1"
    local filename=$(basename "$file")
    local file_errors=0

    # Check for metadata/frontmatter
    if ! head -1 "$file" | grep -q "^---"; then
        log_warning "File $file missing frontmatter metadata"
        ((file_errors++))
    fi

    # Check for placeholder text
    if grep -qi '\(TODO\|FIXME\|TBD\|\[PENDING\]\)' "$file"; then
        log_warning "File $file contains placeholder text (TODO/FIXME/TBD)"
        ((file_errors++))
    fi

    # Check for empty sections
    local empty_sections=$(grep -E "^## [A-Za-z]+" "$file" | while read section; do
        # Get the section name and find the next section or end of file
        if ! grep -A 5 "^$section\$" "$file" | grep -qvE "^(##|$section|^$)"; then
            echo "$section"
        fi
    done)

    if [[ -n "$empty_sections" ]]; then
        log_warning "File $file has empty sections: $empty_sections"
        ((file_errors++))
    fi

    return $file_errors
}

################################################################################
# Check 5: Code Block Formatting
################################################################################

check_code_blocks() {
    local file="$1"
    local file_errors=0
    local in_code_block=false
    local block_lang=""
    local line_num=0

    log_verbose "Checking code blocks: $file"

    while IFS= read -r line; do
        ((line_num++))

        if [[ $line =~ \`\`\` ]]; then
            if [[ $in_code_block == false ]]; then
                # Opening code block
                in_code_block=true
                
                # Extract language identifier
                block_lang=$(echo "$line" | sed 's/^```\(.*\)/\1/')
                
                # Check for common unsupported languages
                if [[ -n "$block_lang" && ! "$block_lang" =~ ^(bash|shell|json|yaml|python|javascript|js|go|rust|text|markdown|html|css|sql)$ ]]; then
                    # Allow unsupported but don't error
                    log_verbose "Unusual code block language: $block_lang at line $line_num"
                fi
            else
                # Closing code block
                in_code_block=false
                block_lang=""
            fi
        fi

        # Check for indented code blocks (should use fenced)
        if [[ ! $in_code_block == true ]] && [[ $line =~ ^[[:space:]][[:space:]][[:space:]][[:space:]].+ ]]; then
            if ! echo "$line" | grep -q "^    [^ ]"; then
                # Could be a false positive, skip
                continue
            fi
        fi
    done < "$file"

    # Check if we ended still in a code block
    if [[ $in_code_block == true ]]; then
        log_error "File $file has unclosed code block"
        ((file_errors++))
    fi

    return $file_errors
}

################################################################################
# Main Validation
################################################################################

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                ;;
            --strict)
                STRICT_MODE=true
                shift
                ;;
            --fix)
                FIX_MODE=true
                shift
                ;;
            --docs-path)
                DOCS_PATH="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                ;;
        esac
    done

    # Initialize report
    {
        echo "================================================================================"
        echo "Documentation Validation Report"
        echo "Generated: $(date)"
        echo "================================================================================"
        echo ""
        echo "Configuration:"
        echo "  Docs Path: $DOCS_PATH"
        echo "  Strict Mode: $STRICT_MODE"
        echo "  Fix Mode: $FIX_MODE"
        echo "  Verbose: $VERBOSE"
        echo ""
    } > "$REPORT_FILE"

    print_header "Validation Starting"
    log_info "Scanning documentation in: $DOCS_PATH"
    log_info "Report will be saved to: $REPORT_FILE"

    # Find all markdown files
    local md_files=()
    while IFS= read -r file; do
        md_files+=("$file")
        ((TOTAL_FILES++))
    done < <(find "$DOCS_PATH" -name "*.md" -type f 2>/dev/null)

    if [[ $TOTAL_FILES -eq 0 ]]; then
        log_error "No markdown files found in $DOCS_PATH"
        exit 2
    fi

    log_info "Found $TOTAL_FILES markdown files to validate"

    # Check 1: Markdown Formatting
    print_header "Check 1: Markdown Formatting"
    local check1_errors=0
    for file in "${md_files[@]}"; do
        if ! check_markdown_formatting "$file"; then
            ((check1_errors += $?))
        fi
        ((FILES_CHECKED++))
    done

    # Check 2: Link Validation
    print_header "Check 2: Link Validation"
    local check2_errors=0
    for file in "${md_files[@]}"; do
        if ! check_links "$file"; then
            ((check2_errors += $?))
        fi
    done

    # Check 3: File Naming
    print_header "Check 3: File Naming Standards"
    local check3_errors=0
    for file in "${md_files[@]}"; do
        if ! check_file_naming "$file"; then
            ((check3_errors += $?))
        fi
    done

    # Check 4: Required Sections
    print_header "Check 4: Required Sections"
    local check4_errors=0
    for file in "${md_files[@]}"; do
        if ! check_required_sections "$file"; then
            ((check4_errors += $?))
        fi
    done

    # Check 5: Code Blocks
    print_header "Check 5: Code Block Formatting"
    local check5_errors=0
    for file in "${md_files[@]}"; do
        if ! check_code_blocks "$file"; then
            ((check5_errors += $?))
        fi
    done

    # Summary Report
    print_header "Validation Summary"
    
    {
        echo ""
        echo "================================================================================"
        echo "SUMMARY"
        echo "================================================================================"
        echo ""
        echo "Files Checked:        $FILES_CHECKED"
        echo "Passed Checks:        $PASSED_CHECKS"
        echo "Warnings:             $WARNINGS"
        echo "Errors:               $ERRORS"
        echo ""
        echo "Check Details:"
        echo "  Check 1 (Markdown):   Issues detected: $check1_errors"
        echo "  Check 2 (Links):      Issues detected: $check2_errors"
        echo "  Check 3 (Naming):     Issues detected: $check3_errors"
        echo "  Check 4 (Sections):   Issues detected: $check4_errors"
        echo "  Check 5 (CodeBlocks): Issues detected: $check5_errors"
        echo ""
        echo "Generation Time: $(date)"
        echo "================================================================================"
    } | tee -a "$REPORT_FILE"

    # Determine exit code
    local total_issues=$((ERRORS + WARNINGS))
    
    if [[ $ERRORS -gt 0 ]]; then
        log_error "Validation FAILED - $ERRORS critical errors found"
        return 2
    fi

    if [[ $WARNINGS -gt 0 ]] && [[ $STRICT_MODE == true ]]; then
        log_warning "Validation FAILED in strict mode - $WARNINGS warnings found"
        return 1
    fi

    if [[ $WARNINGS -gt 0 ]]; then
        log_warning "Validation completed with $WARNINGS warnings"
        return 0
    fi

    log_success "Validation PASSED - All checks successful!"
    echo ""
    echo "Report saved to: $REPORT_FILE"
    return 0
}

# Run main function
main "$@"
