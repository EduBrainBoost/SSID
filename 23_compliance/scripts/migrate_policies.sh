#!/bin/bash
################################################################################
# Policy Consolidation Migration Script
# Version: 1.0.0
# Purpose: Migrate 404+ distributed policies to central 23_compliance/policies/
# Estimated Runtime: 2-4 hours
# Author: SSID Compliance Team
# Date: 2025-10-07
################################################################################

set -e  # Exit on error
set -o pipefail  # Catch errors in pipelines

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TARGET_BASE="23_compliance/policies"
LOG_DIR="23_compliance/logs"
LOG_FILE="${LOG_DIR}/policy_migration_$(date +%Y%m%d_%H%M%S).log"
BACKUP_DIR="23_compliance/backups/policies_backup_$(date +%Y%m%d_%H%M%S)"
DRY_RUN=${DRY_RUN:-false}  # Set DRY_RUN=true to test without actually moving files

# Counters
TOTAL_FILES=0
MIGRATED_FILES=0
SKIPPED_FILES=0
ERROR_FILES=0

################################################################################
# Logging Functions
################################################################################

log() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
    ((ERROR_FILES++))
}

################################################################################
# Pre-Flight Checks
################################################################################

preflight_checks() {
    log "Starting pre-flight checks..."

    # Check if running from repo root
    if [[ ! -d "23_compliance" ]]; then
        log_error "Must run from repository root directory"
        exit 1
    fi

    # Check required tools
    for tool in find sha256sum python3 awk grep; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            exit 1
        fi
    done

    # Create necessary directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$TARGET_BASE/global"

    # Count existing policies
    TOTAL_FILES=$(find . -type f \( -name "*policy*.yaml" -o -name "*.rego" \) \
        ! -path "*/node_modules/*" \
        ! -path "*/.git/*" \
        ! -path "*/23_compliance/policies/*" \
        ! -path "*/.claude/*" 2>/dev/null | wc -l)

    log "Found $TOTAL_FILES policy files to migrate"

    if [[ $TOTAL_FILES -eq 0 ]]; then
        log_warning "No policy files found to migrate"
        exit 0
    fi

    log_success "Pre-flight checks passed"
}

################################################################################
# Backup Current State
################################################################################

backup_current_state() {
    log "Creating backup of current policy files..."

    if [[ -d "$TARGET_BASE" ]]; then
        cp -r "$TARGET_BASE" "$BACKUP_DIR/23_compliance_policies"
        log_success "Backed up existing 23_compliance/policies/ to $BACKUP_DIR"
    fi

    # Create manifest of all policy files
    find . -type f \( -name "*policy*.yaml" -o -name "*.rego" \) \
        ! -path "*/node_modules/*" \
        ! -path "*/.git/*" \
        ! -path "*/.claude/*" 2>/dev/null > "${BACKUP_DIR}/policy_manifest.txt"

    log_success "Created policy manifest: ${BACKUP_DIR}/policy_manifest.txt"
}

################################################################################
# Create Target Directory Structure
################################################################################

create_directory_structure() {
    log "Creating target directory structure..."

    # Define all 24 root modules
    local roots=(
        "01_ai_layer"
        "02_audit_logging"
        "03_core"
        "04_deployment"
        "05_documentation"
        "06_data_pipeline"
        "07_governance_legal"
        "08_identity_score"
        "09_meta_identity"
        "10_interoperability"
        "11_test_simulation"
        "12_tooling"
        "13_ui_layer"
        "14_zero_time_auth"
        "15_infra"
        "16_codex"
        "17_observability"
        "18_data_layer"
        "19_adapters"
        "20_foundation"
        "21_post_quantum_crypto"
        "22_datasets"
        "23_compliance"
        "24_meta_orchestration"
    )

    # Create root directories
    for root in "${roots[@]}"; do
        mkdir -p "$TARGET_BASE/$root"
        log "Created: $TARGET_BASE/$root"
    done

    # Create shard subdirectories for roots that have shards
    local shard_names=(
        "01_identitaet_personen"
        "02_dokumente_nachweise"
        "03_zugang_berechtigungen"
        "04_kommunikation_daten"
        "05_gesundheit_medizin"
        "06_bildung_qualifikationen"
        "07_familie_soziales"
        "08_mobilitaet_fahrzeuge"
        "09_arbeit_karriere"
        "10_finanzen_banking"
        "11_versicherungen_risiken"
        "12_immobilien_grundstuecke"
        "13_unternehmen_gewerbe"
        "14_vertraege_vereinbarungen"
        "15_handel_transaktionen"
        "16_behoerden_verwaltung"
    )

    for root in "01_ai_layer" "02_audit_logging" "03_core" "23_compliance"; do
        for shard in "${shard_names[@]}"; do
            mkdir -p "$TARGET_BASE/$root/$shard"
        done
        log "Created shard structure for $root (16 shards)"
    done

    log_success "Directory structure created"
}

################################################################################
# Calculate SHA-256 Hash
################################################################################

calculate_hash() {
    local file="$1"
    # Calculate hash excluding any existing hash line
    grep -v "^# sha256:" "$file" 2>/dev/null | sha256sum | awk '{print $1}'
}

################################################################################
# Append Hash to Policy File
################################################################################

append_hash() {
    local file="$1"

    # Check if hash already exists
    if grep -q "^# sha256:" "$file" 2>/dev/null; then
        log_warning "Hash already exists in $file, skipping"
        return 0
    fi

    # Calculate hash
    local hash
    hash=$(calculate_hash "$file")

    # Append hash annotation
    if [[ "$DRY_RUN" == "false" ]]; then
        echo "" >> "$file"
        echo "# sha256:$hash" >> "$file"
    fi

    log "Added hash ${hash:0:8}... to $(basename "$file")"
}

################################################################################
# Create Policy Reference File
################################################################################

create_policy_reference() {
    local original_file="$1"
    local target_file="$2"
    local hash="$3"

    # Determine reference file path
    local ref_file="${original_file%.yaml}.policy_ref"
    ref_file="${ref_file%.rego}.policy_ref"

    if [[ "$DRY_RUN" == "false" ]]; then
        cat > "$ref_file" << EOF
# Policy Reference File
# This file indicates the policy has been migrated to central location
central_policy: "$target_file"
migrated: "$(date +%Y-%m-%d)"
original_sha256: "$hash"
migration_log: "$LOG_FILE"
EOF
    fi

    log "Created reference: $(basename "$ref_file")"
}

################################################################################
# Migrate Single Policy File
################################################################################

migrate_policy_file() {
    local src="$1"

    # Skip if already in target location
    if [[ "$src" == *"$TARGET_BASE"* ]]; then
        log_warning "Skipping (already in target): $src"
        ((SKIPPED_FILES++))
        return 0
    fi

    # Extract root module from path
    local root
    root=$(echo "$src" | awk -F'/' '{print $2}')

    # Check if path contains shards
    local target_dir
    if echo "$src" | grep -q "shards"; then
        # Extract shard name
        local shard
        shard=$(echo "$src" | grep -oP 'shards/\K[^/]+' | head -1)

        if [[ -n "$shard" ]]; then
            target_dir="$TARGET_BASE/$root/$shard"
        else
            target_dir="$TARGET_BASE/$root"
        fi
    else
        target_dir="$TARGET_BASE/$root"
    fi

    # Handle global policies
    if [[ "$src" == *"/global/"* ]] || [[ "$(basename "$src")" == "master_"* ]]; then
        target_dir="$TARGET_BASE/global"
    fi

    # Create target directory if it doesn't exist
    mkdir -p "$target_dir"

    # Determine target filename
    local filename
    filename=$(basename "$src")
    local target="$target_dir/$filename"

    # Check if target already exists
    if [[ -f "$target" ]] && [[ "$src" != "$target" ]]; then
        log_warning "Target already exists: $target (source: $src)"
        # Create numbered copy
        local counter=1
        local base="${filename%.*}"
        local ext="${filename##*.}"
        while [[ -f "${target_dir}/${base}_${counter}.${ext}" ]]; do
            ((counter++))
        done
        target="${target_dir}/${base}_${counter}.${ext}"
        log "Using alternate name: $(basename "$target")"
    fi

    # Copy file
    if [[ "$DRY_RUN" == "false" ]]; then
        if ! cp "$src" "$target"; then
            log_error "Failed to copy: $src -> $target"
            return 1
        fi
    fi

    # Calculate and append hash
    if [[ "$DRY_RUN" == "false" ]]; then
        local hash
        hash=$(calculate_hash "$target")
        append_hash "$target"
    else
        local hash="dryrun_hash"
    fi

    # Create reference file in original location
    create_policy_reference "$src" "$target" "$hash"

    # Log migration
    log_success "Migrated: $src -> $target (hash: ${hash:0:8}...)"
    ((MIGRATED_FILES++))

    return 0
}

################################################################################
# Main Migration Process
################################################################################

migrate_all_policies() {
    log "Starting policy migration..."

    # Find all policy files
    local policy_files
    mapfile -t policy_files < <(find . -type f \( -name "*policy*.yaml" -o -name "*.rego" \) \
        ! -path "*/node_modules/*" \
        ! -path "*/.git/*" \
        ! -path "*/23_compliance/policies/*" \
        ! -path "*/.claude/*" 2>/dev/null)

    local total=${#policy_files[@]}
    local current=0

    log "Processing $total policy files..."

    for src in "${policy_files[@]}"; do
        ((current++))
        log "[$current/$total] Processing: $src"

        if ! migrate_policy_file "$src"; then
            log_error "Failed to migrate: $src"
        fi

        # Progress indicator every 50 files
        if ((current % 50 == 0)); then
            log_success "Progress: $current/$total files processed"
        fi
    done

    log_success "Migration processing complete"
}

################################################################################
# Generate Policy Index
################################################################################

generate_policy_index() {
    log "Generating policy index..."

    local index_file="$TARGET_BASE/index.yaml"

    if [[ "$DRY_RUN" == "false" ]]; then
        python3 23_compliance/tools/generate_policy_index.py \
            --input "$TARGET_BASE" \
            --output "$index_file" 2>&1 | tee -a "$LOG_FILE"

        if [[ -f "$index_file" ]]; then
            log_success "Generated policy index: $index_file"
        else
            log_warning "Policy index generator not available or failed"
            # Create basic index manually
            cat > "$index_file" << EOF
---
version: "1.0.0"
generated: "$(date +%Y-%m-%d)"
total_policies: $(find "$TARGET_BASE" -type f \( -name "*.yaml" -o -name "*.rego" \) 2>/dev/null | wc -l)
migration_log: "$LOG_FILE"
backup_location: "$BACKUP_DIR"

notes:
  - "Migrated from distributed locations"
  - "All policies include SHA-256 hash annotations"
  - "Original locations have .policy_ref files"
EOF
            log "Created basic index file"
        fi
    fi
}

################################################################################
# Verification
################################################################################

verify_migration() {
    log "Verifying migration..."

    # Count migrated policies
    local migrated_count
    migrated_count=$(find "$TARGET_BASE" -type f \( -name "*.yaml" -o -name "*.rego" \) ! -name "index.yaml" 2>/dev/null | wc -l)

    log "Total policies in target location: $migrated_count"

    # Verify hashes
    local files_without_hash=0
    while IFS= read -r file; do
        if ! grep -q "^# sha256:" "$file" 2>/dev/null; then
            log_warning "Missing hash: $file"
            ((files_without_hash++))
        fi
    done < <(find "$TARGET_BASE" -type f \( -name "*.yaml" -o -name "*.rego" \) ! -name "index.yaml" 2>/dev/null)

    if [[ $files_without_hash -gt 0 ]]; then
        log_warning "$files_without_hash files are missing hash annotations"
    else
        log_success "All files have SHA-256 hash annotations"
    fi

    # Check for policy references
    local ref_count
    ref_count=$(find . -type f -name "*.policy_ref" ! -path "*/23_compliance/policies/*" 2>/dev/null | wc -l)
    log "Created $ref_count policy reference files"
}

################################################################################
# Generate Migration Report
################################################################################

generate_report() {
    local report_file="${LOG_DIR}/migration_report_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# Policy Migration Report
**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Dry Run:** $DRY_RUN

## Summary

- **Total Files Found:** $TOTAL_FILES
- **Successfully Migrated:** $MIGRATED_FILES
- **Skipped:** $SKIPPED_FILES
- **Errors:** $ERROR_FILES
- **Success Rate:** $(awk "BEGIN {printf \"%.1f\", ($MIGRATED_FILES/$TOTAL_FILES)*100}")%

## Files

### Target Location
\`$TARGET_BASE\`

### Backup Location
\`$BACKUP_DIR\`

### Log File
\`$LOG_FILE\`

## Post-Migration Status

\`\`\`bash
# Policies in central location
$(find "$TARGET_BASE" -type f \( -name "*.yaml" -o -name "*.rego" \) 2>/dev/null | wc -l) files

# Policy reference files created
$(find . -type f -name "*.policy_ref" 2>/dev/null | wc -l) references

# Total disk space used
$(du -sh "$TARGET_BASE" 2>/dev/null | awk '{print $1}')
\`\`\`

## Next Steps

1. [ ] Review migration log: \`$LOG_FILE\`
2. [ ] Verify hash integrity: \`bash 23_compliance/scripts/verify_hash_annotations.sh\`
3. [ ] Test CI/CD gates: \`./run_ci_checks.sh\`
4. [ ] Update policy imports in code
5. [ ] Deploy to staging environment
6. [ ] Monitor for 24 hours
7. [ ] Remove .policy_ref files after validation (optional)

## Rollback Instructions

If issues are encountered:

\`\`\`bash
# Restore from backup
rm -rf $TARGET_BASE
cp -r $BACKUP_DIR/23_compliance_policies $TARGET_BASE

# Remove policy reference files
find . -type f -name "*.policy_ref" -delete
\`\`\`

---
**Generated by:** migrate_policies.sh v1.0.0
EOF

    log_success "Generated migration report: $report_file"
    echo ""
    cat "$report_file"
}

################################################################################
# Main Execution
################################################################################

main() {
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║          SSID Policy Consolidation Migration Script           ║"
    echo "║                       Version 1.0.0                            ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN MODE - No files will be modified"
    fi

    # Execute migration phases
    preflight_checks
    backup_current_state
    create_directory_structure
    migrate_all_policies
    generate_policy_index
    verify_migration
    generate_report

    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                   Migration Complete!                          ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    log_success "Total: $TOTAL_FILES | Migrated: $MIGRATED_FILES | Skipped: $SKIPPED_FILES | Errors: $ERROR_FILES"
    echo ""
    log "Review the full log at: $LOG_FILE"
    echo ""

    if [[ $ERROR_FILES -gt 0 ]]; then
        log_warning "Migration completed with $ERROR_FILES errors. Review log for details."
        exit 1
    fi

    exit 0
}

# Run main function
main "$@"
