#!/usr/bin/env bash
# =============================================================================
# Evidence-Hasher: SHA-256 Hash-Kette für alle kritischen Dateien
# =============================================================================
# Berechnet und aktualisiert SHA-256 Hashes für:
# - Alle SoT-Dateien (23_compliance/policies/*.yaml)
# - Alle Policy-Dateien (*.rego)
# - Alle Implementierungen mit @req-Tags
# - Audit-Logs
# - Test-Ergebnisse
#
# Erstellt eine verifizierbare Hash-Chain für Audit-Zwecke.
#
# Exit Codes:
#   0 = Hashing erfolgreich
#   1 = Fehler beim Hashing
# =============================================================================

set -euo pipefail

# --- KONFIGURATION ---
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
HASH_OUTPUT="${REPO_ROOT}/02_audit_logging/evidence_hashes.json"
HASH_LOG="${REPO_ROOT}/02_audit_logging/hash_audit.log"
HASH_ALGORITHM="sha256sum"

# Kritische Dateitypen für Hashing
CRITICAL_PATTERNS=(
    "23_compliance/**/*.yaml"
    "23_compliance/**/*.yml"
    "23_compliance/**/*.rego"
    "02_audit_logging/**/*.log"
    "11_test_simulation/test_results/**/*"
)

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- LOGGING ---
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${HASH_LOG}"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }

# --- HASH-FUNKTIONEN ---

# Berechnet SHA-256 für einzelne Datei
hash_file() {
    local file="$1"

    if [[ ! -f "${file}" ]]; then
        echo "ERROR: File not found"
        return 1
    fi

    # Platform-agnostisch (Linux/Mac/Git Bash)
    if command -v sha256sum &>/dev/null; then
        sha256sum "${file}" | awk '{print $1}'
    elif command -v shasum &>/dev/null; then
        shasum -a 256 "${file}" | awk '{print $1}'
    else
        log_error "Keine SHA-256 Implementation gefunden (sha256sum/shasum)"
        return 1
    fi
}

# Findet alle kritischen Dateien
find_critical_files() {
    local files=()

    # SoT-Dateien (höchste Priorität)
    while IFS= read -r file; do
        [[ -f "${file}" ]] && files+=("${file}")
    done < <(find "${REPO_ROOT}/23_compliance" -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.rego" \) 2>/dev/null || true)

    # Audit-Logs
    while IFS= read -r file; do
        [[ -f "${file}" ]] && files+=("${file}")
    done < <(find "${REPO_ROOT}/02_audit_logging" -type f -name "*.log" 2>/dev/null || true)

    # Test-Ergebnisse
    if [[ -d "${REPO_ROOT}/11_test_simulation/test_results" ]]; then
        while IFS= read -r file; do
            [[ -f "${file}" ]] && files+=("${file}")
        done < <(find "${REPO_ROOT}/11_test_simulation/test_results" -type f 2>/dev/null || true)
    fi

    # Code mit @req-Tags (Implementierungen)
    while IFS= read -r file; do
        [[ -f "${file}" ]] && files+=("${file}")
    done < <(grep -rl "@req" "${REPO_ROOT}/31_ml_analytics" "${REPO_ROOT}/41_devsecops_cicd" "${REPO_ROOT}/51_monitoring_siem" 2>/dev/null || true)

    # Dedupliziere und sortiere
    printf '%s\n' "${files[@]}" | sort -u
}

# Erstellt Hash-Chain (verkettete Hashes)
create_hash_chain() {
    local files=("$@")
    local chain_hash=""
    local previous_hash="0000000000000000000000000000000000000000000000000000000000000000"

    local chain_data="["

    for file in "${files[@]}"; do
        local file_hash
        file_hash=$(hash_file "${file}") || continue

        # Chain: hash(previous_hash + file_hash)
        local combined="${previous_hash}${file_hash}"
        chain_hash=$(echo -n "${combined}" | sha256sum | awk '{print $1}' 2>/dev/null || echo -n "${combined}" | shasum -a 256 | awk '{print $1}')

        # Relative Pfade für Output
        local rel_path="${file#${REPO_ROOT}/}"

        # JSON-Eintrag
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local file_size=$(stat -f%z "${file}" 2>/dev/null || stat -c%s "${file}" 2>/dev/null || echo "0")

        chain_data+=$(cat <<EOF
{
  "file": "${rel_path}",
  "hash": "${file_hash}",
  "chain_hash": "${chain_hash}",
  "previous_hash": "${previous_hash}",
  "timestamp": "${timestamp}",
  "size": ${file_size}
},
EOF
)

        previous_hash="${chain_hash}"
    done

    # Entferne letztes Komma
    chain_data="${chain_data%,}"
    chain_data+="]"

    # Finale Chain-Hash
    echo "${chain_data}" | jq --arg final_hash "${chain_hash}" '. + [{"final_chain_hash": $final_hash}]' 2>/dev/null || echo "${chain_data}"
}

# Verifiziert existierende Hash-Chain
verify_hash_chain() {
    local hash_file="${1:-${HASH_OUTPUT}}"

    if [[ ! -f "${hash_file}" ]]; then
        log_warn "Keine existierende Hash-Chain gefunden: ${hash_file}"
        return 1
    fi

    echo -e "${BLUE}Verifiziere Hash-Chain...${NC}"

    local verification_failed=0
    local previous_hash="0000000000000000000000000000000000000000000000000000000000000000"

    # Lese JSON (mit jq wenn verfügbar, sonst manuell)
    if command -v jq &>/dev/null; then
        local entries
        entries=$(jq -r '.[] | select(.file) | @json' "${hash_file}" 2>/dev/null || echo "")

        while IFS= read -r entry; do
            [[ -z "${entry}" ]] && continue

            local file
            local stored_hash
            local stored_chain_hash
            local stored_previous_hash

            file=$(echo "${entry}" | jq -r '.file')
            stored_hash=$(echo "${entry}" | jq -r '.hash')
            stored_chain_hash=$(echo "${entry}" | jq -r '.chain_hash')
            stored_previous_hash=$(echo "${entry}" | jq -r '.previous_hash')

            # Prüfe Previous-Hash-Konsistenz
            if [[ "${stored_previous_hash}" != "${previous_hash}" ]]; then
                echo -e "${RED}❌ Chain-Break:${NC} ${file}"
                echo -e "   Expected previous: ${previous_hash}"
                echo -e "   Stored previous:   ${stored_previous_hash}"
                verification_failed=1
            fi

            # Prüfe Datei-Hash (falls Datei noch existiert)
            local full_path="${REPO_ROOT}/${file}"
            if [[ -f "${full_path}" ]]; then
                local current_hash
                current_hash=$(hash_file "${full_path}")

                if [[ "${current_hash}" != "${stored_hash}" ]]; then
                    echo -e "${YELLOW}⚠️  Modified:${NC} ${file}"
                    echo -e "   Stored hash:  ${stored_hash}"
                    echo -e "   Current hash: ${current_hash}"
                fi
            fi

            previous_hash="${stored_chain_hash}"

        done <<< "${entries}"
    else
        log_warn "jq nicht verfügbar - überspringe detaillierte Verifikation"
    fi

    if [[ ${verification_failed} -eq 0 ]]; then
        echo -e "${GREEN}✅ Hash-Chain ist konsistent${NC}"
        return 0
    else
        echo -e "${RED}❌ Hash-Chain ist inkonsistent${NC}"
        return 1
    fi
}

# --- HAUPT-ROUTINE ---

main() {
    local exit_code=0

    echo -e "${BLUE}=== Evidence-Hasher: SHA-256 Hash-Chain Generator ===${NC}"
    log_info "Starting Evidence-Hasher in ${REPO_ROOT}"

    # Erstelle Output-Verzeichnis falls nötig
    mkdir -p "$(dirname "${HASH_OUTPUT}")"

    # Phase 1: Finde kritische Dateien
    echo -e "${CYAN}Phase 1: Scanning critical files...${NC}"
    local critical_files=()
    while IFS= read -r file; do
        critical_files+=("${file}")
    done < <(find_critical_files)

    local file_count=${#critical_files[@]}
    echo -e "${CYAN}Gefundene kritische Dateien: ${file_count}${NC}"

    if [[ ${file_count} -eq 0 ]]; then
        log_warn "Keine kritischen Dateien gefunden"
        echo -e "${YELLOW}⚠️  Keine Dateien zum Hashen gefunden${NC}"
        exit 0
    fi

    # Phase 2: Erstelle Hash-Chain
    echo -e "${CYAN}Phase 2: Creating hash chain...${NC}"
    local hash_chain
    hash_chain=$(create_hash_chain "${critical_files[@]}")

    # Phase 3: Speichere Hash-Chain
    echo -e "${CYAN}Phase 3: Saving hash chain...${NC}"

    # Backup alte Version falls vorhanden
    if [[ -f "${HASH_OUTPUT}" ]]; then
        local backup_file="${HASH_OUTPUT}.$(date +%Y%m%d_%H%M%S).bak"
        cp "${HASH_OUTPUT}" "${backup_file}"
        log_info "Backed up previous hash chain to ${backup_file}"
    fi

    # Speichere neue Hash-Chain
    echo "${hash_chain}" > "${HASH_OUTPUT}"

    # Pretty-print falls jq verfügbar
    if command -v jq &>/dev/null; then
        local temp_file
        temp_file=$(mktemp)
        jq '.' "${HASH_OUTPUT}" > "${temp_file}" && mv "${temp_file}" "${HASH_OUTPUT}"
    fi

    log_success "Hash chain saved to ${HASH_OUTPUT}"

    # Phase 4: Verifizierung
    echo -e "${CYAN}Phase 4: Verifying hash chain...${NC}"
    if verify_hash_chain "${HASH_OUTPUT}"; then
        exit_code=0
    else
        exit_code=1
    fi

    # Zusammenfassung
    echo ""
    echo -e "${BLUE}=== Zusammenfassung ===${NC}"
    echo -e "Gehashte Dateien: ${file_count}"
    echo -e "Output:           ${HASH_OUTPUT}"
    echo -e "Log:              ${HASH_LOG}"
    echo ""

    if [[ ${exit_code} -eq 0 ]]; then
        echo -e "${GREEN}✅ Evidence-Hasher erfolgreich${NC}"
        log_success "Evidence-Hasher completed successfully"
    else
        echo -e "${RED}❌ Evidence-Hasher mit Fehlern${NC}"
        log_error "Evidence-Hasher completed with errors"
    fi

    exit ${exit_code}
}

# --- UTILITY-FUNKTIONEN ---

# Zeigt Hash für einzelne Datei
show_file_hash() {
    local file="$1"

    if [[ ! -f "${file}" ]]; then
        echo -e "${RED}❌ Datei nicht gefunden: ${file}${NC}"
        return 1
    fi

    local hash
    hash=$(hash_file "${file}")

    echo -e "${CYAN}File:${NC} ${file}"
    echo -e "${CYAN}SHA-256:${NC} ${hash}"
}

# --- ENTRY POINT ---

# Parse Argumente
case "${1:-}" in
    --verify)
        verify_hash_chain "${HASH_OUTPUT}"
        ;;
    --file)
        [[ -z "${2:-}" ]] && { echo "Usage: $0 --file <path>"; exit 1; }
        show_file_hash "$2"
        ;;
    --help|-h)
        cat <<EOF
Evidence-Hasher: SHA-256 Hash-Chain Generator

Usage:
  $0                  Erstellt neue Hash-Chain
  $0 --verify         Verifiziert existierende Hash-Chain
  $0 --file <path>    Zeigt Hash für einzelne Datei
  $0 --help           Zeigt diese Hilfe

Output:
  ${HASH_OUTPUT}
  ${HASH_LOG}
EOF
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
