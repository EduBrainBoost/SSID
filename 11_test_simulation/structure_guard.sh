#!/usr/bin/env bash
# =============================================================================
# Structure-Guard: CI-Blocker für Policy-Dateien außerhalb 23_compliance
# =============================================================================
# Prüft, dass keine Policy-Dateien außerhalb des zentralen Compliance-Ordners
# existieren oder hinzugefügt werden. Blockiert CI-Pipeline bei Verstößen.
#
# Exit Codes:
#   0 = Alle Checks erfolgreich
#   1 = Policy-Verletzungen gefunden (CI-Blocker)
#   2 = Konfigurationsfehler
# =============================================================================

set -euo pipefail

# --- KONFIGURATION ---
COMPLIANCE_ROOT="23_compliance"
MAX_DEPTH=2
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
LOG_FILE="${REPO_ROOT}/02_audit_logging/structure_guard.log"

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- LOGGING ---
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }

# --- HAUPTFUNKTIONEN ---

# Sucht nach Policy-Dateien
find_policy_files() {
    local search_root="${1:-.}"

    # Suche nach Dateien mit Policy-relevanten Namen oder Extensions
    find "${search_root}" -type f \( \
        -name "*policy*" -o \
        -name "*polic*" -o \
        -name "*.rego" -o \
        -name "*compliance*.yaml" -o \
        -name "*compliance*.yml" -o \
        -name "*regulation*.json" \
    \) 2>/dev/null || true
}

# Prüft, ob Pfad innerhalb 23_compliance liegt
is_in_compliance_root() {
    local file_path="$1"
    local normalized_path="${file_path#./}"  # Entfernt führendes ./

    [[ "${normalized_path}" == "${COMPLIANCE_ROOT}"/* ]] || \
    [[ "${normalized_path}" == "${COMPLIANCE_ROOT}" ]]
}

# Berechnet Verzeichnis-Tiefe relativ zu 23_compliance
calculate_depth() {
    local file_path="$1"
    local relative_path="${file_path#${COMPLIANCE_ROOT}/}"

    # Zähle Slashes im relativen Pfad
    local depth=$(echo "${relative_path}" | tr -cd '/' | wc -c)
    echo "${depth}"
}

# Prüft einzelne Datei
check_file() {
    local file="$1"
    local violations=0

    # Check 1: Zentralisierung
    if ! is_in_compliance_root "${file}"; then
        echo -e "${RED}❌ VIOLATION${NC}: Policy-Datei außerhalb ${COMPLIANCE_ROOT}/"
        echo -e "   ${BLUE}Datei:${NC} ${file}"
        log_error "Policy violation: ${file} outside ${COMPLIANCE_ROOT}/"
        violations=$((violations + 1))
    fi

    # Check 2: Tiefe (nur wenn in compliance_root)
    if is_in_compliance_root "${file}"; then
        local depth=$(calculate_depth "${file}")
        if [[ ${depth} -gt ${MAX_DEPTH} ]]; then
            echo -e "${RED}❌ DEPTH VIOLATION${NC}: Zu tief verschachtelt (${depth} > ${MAX_DEPTH})"
            echo -e "   ${BLUE}Datei:${NC} ${file}"
            log_error "Depth violation: ${file} at depth ${depth} (max: ${MAX_DEPTH})"
            violations=$((violations + 1))
        fi
    fi

    return ${violations}
}

# Hauptprüfung
main() {
    local exit_code=0
    local total_files=0
    local violation_count=0

    echo -e "${BLUE}=== Structure-Guard: Policy Centralization Check ===${NC}"
    log_info "Starting Structure-Guard check in ${REPO_ROOT}"

    # Prüfe, ob 23_compliance existiert
    if [[ ! -d "${REPO_ROOT}/${COMPLIANCE_ROOT}" ]]; then
        echo -e "${RED}❌ ERROR${NC}: Compliance-Root '${COMPLIANCE_ROOT}/' nicht gefunden!"
        log_error "Compliance root directory not found: ${COMPLIANCE_ROOT}"
        exit 2
    fi

    echo -e "${BLUE}Suche Policy-Dateien...${NC}"

    # Finde alle Policy-Dateien
    local policy_files=()
    while IFS= read -r file; do
        policy_files+=("${file}")
    done < <(find_policy_files "${REPO_ROOT}")

    total_files=${#policy_files[@]}

    if [[ ${total_files} -eq 0 ]]; then
        echo -e "${YELLOW}⚠️  WARNUNG${NC}: Keine Policy-Dateien gefunden"
        log_warn "No policy files found in repository"
        exit 0
    fi

    echo -e "${BLUE}Gefundene Policy-Dateien: ${total_files}${NC}"
    echo ""

    # Prüfe jede Datei
    for file in "${policy_files[@]}"; do
        # Relativer Pfad für Output
        local rel_path="${file#${REPO_ROOT}/}"

        if ! check_file "${rel_path}"; then
            violation_count=$((violation_count + 1))
            echo ""
        fi
    done

    # Zusammenfassung
    echo -e "${BLUE}=== Zusammenfassung ===${NC}"
    echo -e "Geprüfte Dateien: ${total_files}"
    echo -e "Verstöße:         ${violation_count}"
    echo ""

    if [[ ${violation_count} -gt 0 ]]; then
        echo -e "${RED}❌ STRUCTURE-GUARD FAILED${NC}"
        echo -e "${RED}CI-Pipeline wird blockiert!${NC}"
        echo ""
        echo -e "${YELLOW}Behebung:${NC}"
        echo -e "  1. Verschiebe alle Policy-Dateien nach ${COMPLIANCE_ROOT}/"
        echo -e "  2. Stelle sicher, dass max. Verschachtelungstiefe ${MAX_DEPTH} ist"
        echo -e "  3. Führe dieses Script erneut aus"
        echo ""
        log_error "Structure-Guard failed with ${violation_count} violations"
        exit_code=1
    else
        echo -e "${GREEN}✅ STRUCTURE-GUARD PASSED${NC}"
        echo -e "Alle Policy-Dateien sind korrekt in ${COMPLIANCE_ROOT}/ zentralisiert"
        log_success "Structure-Guard passed - all policies centralized correctly"
        exit_code=0
    fi

    exit ${exit_code}
}

# --- GIT-INTEGRATION (Optional für Pre-Commit Hook) ---

# Prüft nur geänderte Dateien in Git
check_git_changes() {
    echo -e "${BLUE}=== Git-Modus: Prüfe nur geänderte Dateien ===${NC}"
    log_info "Running in Git mode - checking staged changes only"

    local violations=0
    local changed_policies=()

    # Hole geänderte Dateien (staged und unstaged)
    while IFS= read -r file; do
        if [[ -f "${file}" ]]; then
            # Prüfe, ob es eine Policy-Datei ist
            if echo "${file}" | grep -qiE '(polic|\.rego$|compliance.*\.ya?ml$)'; then
                changed_policies+=("${file}")
            fi
        fi
    done < <(git diff --name-only HEAD 2>/dev/null || true)

    if [[ ${#changed_policies[@]} -eq 0 ]]; then
        echo -e "${GREEN}✅ Keine Policy-Dateien geändert${NC}"
        return 0
    fi

    echo -e "${BLUE}Geänderte Policy-Dateien: ${#changed_policies[@]}${NC}"

    for file in "${changed_policies[@]}"; do
        if ! check_file "${file}"; then
            violations=$((violations + 1))
            echo ""
        fi
    done

    return ${violations}
}

# --- ENTRY POINT ---

# Parse Argumente
if [[ $# -gt 0 ]] && [[ "$1" == "--git" ]]; then
    check_git_changes
else
    main "$@"
fi
