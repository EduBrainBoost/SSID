#!/bin/bash
################################################################################
# SSID Monitoring Dashboard - Cron Job Setup
################################################################################
# Purpose: Set up daily cron job for monitoring dashboard updates
# Version: 1.0.0
# Date: 2025-10-18
# Owner: SSID Compliance Team
#
# Usage: ./tools/setup_monitoring_cronjob.sh [--uninstall]
#
################################################################################

set -euo pipefail

# Configuration
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/update_monitoring_dashboard.py"
REPO_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRON_HOUR="${CRON_HOUR:-0}"  # Default: midnight
CRON_MINUTE="${CRON_MINUTE:-0}"
LOG_FILE="${HOME}/.ssid_monitoring.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

function log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
function log_success() { echo -e "${GREEN}✅ $1${NC}"; }
function log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
function log_error() { echo -e "${RED}❌ $1${NC}"; }

function print_usage() {
    cat <<EOF
Usage: $0 [options]

Set up daily cron job for monitoring dashboard updates.

Options:
  --uninstall      Remove cron job
  --help           Show this help

Environment Variables:
  CRON_HOUR        Hour to run (0-23, default: 0)
  CRON_MINUTE      Minute to run (0-59, default: 0)

Examples:
  # Install with default schedule (midnight)
  $0

  # Install at 2:30 AM
  CRON_HOUR=2 CRON_MINUTE=30 $0

  # Uninstall
  $0 --uninstall

EOF
}

function check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log_error "Python not installed"
        exit 1
    fi

    PYTHON_CMD=$(command -v python3 2>/dev/null || command -v python)
    log_success "Python: $PYTHON_CMD"

    # Check script exists
    if [ ! -f "$SCRIPT_PATH" ]; then
        log_error "Monitoring script not found: $SCRIPT_PATH"
        exit 1
    fi

    log_success "Monitoring script: $SCRIPT_PATH"

    # Check crontab availability
    if ! command -v crontab &> /dev/null; then
        log_error "crontab not available"
        log_info "This system may not support cron jobs"
        exit 1
    fi

    log_success "crontab available"
}

function install_cronjob() {
    echo ""
    log_info "Installing monitoring cron job..."

    # Create cron entry
    CRON_ENTRY="$CRON_MINUTE $CRON_HOUR * * * cd $REPO_PATH && python3 tools/update_monitoring_dashboard.py >> $LOG_FILE 2>&1"

    # Check if entry already exists
    if crontab -l 2>/dev/null | grep -qF "update_monitoring_dashboard.py"; then
        log_warning "Cron job already exists"
        log_info "Removing old entry..."

        # Remove old entry
        crontab -l 2>/dev/null | grep -vF "update_monitoring_dashboard.py" | crontab -
    fi

    # Add new entry
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

    log_success "Cron job installed"
    echo ""
    log_info "Schedule: Daily at $(printf "%02d:%02d" $CRON_HOUR $CRON_MINUTE) (server time)"
    log_info "Log file: $LOG_FILE"
    echo ""

    # Show current crontab
    log_info "Current crontab entries:"
    crontab -l | grep -E "(update_monitoring_dashboard|^#|^$)" || true
}

function uninstall_cronjob() {
    echo ""
    log_info "Uninstalling monitoring cron job..."

    if crontab -l 2>/dev/null | grep -qF "update_monitoring_dashboard.py"; then
        crontab -l 2>/dev/null | grep -vF "update_monitoring_dashboard.py" | crontab -
        log_success "Cron job removed"
    else
        log_warning "Cron job not found"
    fi

    # Ask about log file
    if [ -f "$LOG_FILE" ]; then
        log_info "Log file exists: $LOG_FILE"
        read -p "Delete log file? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm "$LOG_FILE"
            log_success "Log file deleted"
        fi
    fi
}

function test_cronjob() {
    echo ""
    log_info "Testing monitoring script..."

    if cd "$REPO_PATH" && python3 "$SCRIPT_PATH"; then
        log_success "Monitoring script executed successfully"

        if [ -f "02_audit_logging/archives/qa_master_suite/MONITORING.md" ]; then
            log_success "Dashboard updated"
            log_info "Preview:"
            head -20 "02_audit_logging/archives/qa_master_suite/MONITORING.md"
        fi
    else
        log_error "Monitoring script failed"
        log_info "Check errors above and fix before installing cron job"
        exit 1
    fi
}

function show_status() {
    echo ""
    log_info "Cron Job Status:"
    echo ""

    if crontab -l 2>/dev/null | grep -qF "update_monitoring_dashboard.py"; then
        log_success "Installed"
        echo ""
        echo "Entry:"
        crontab -l | grep "update_monitoring_dashboard.py"
        echo ""

        # Show next run time
        if command -v systemctl &> /dev/null && systemctl is-active --quiet cron; then
            log_info "Cron daemon: running"
        elif command -v service &> /dev/null && service cron status &> /dev/null; then
            log_info "Cron daemon: running"
        else
            log_warning "Cron daemon status: unknown"
        fi

        # Show recent log entries
        if [ -f "$LOG_FILE" ]; then
            LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
            log_info "Log file: $LOG_FILE ($LOG_SIZE)"

            if [ -s "$LOG_FILE" ]; then
                echo ""
                log_info "Recent log entries:"
                tail -10 "$LOG_FILE"
            fi
        else
            log_info "No log file yet (will be created on first run)"
        fi
    else
        log_warning "Not installed"
        log_info "Run: $0"
    fi
}

################################################################################
# MAIN
################################################################################

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📊 SSID Monitoring Dashboard - Cron Job Setup"
echo "═══════════════════════════════════════════════════════════════"

# Parse arguments
UNINSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

if [ "$UNINSTALL" = true ]; then
    uninstall_cronjob
    exit 0
fi

# Check prerequisites
check_prerequisites

# Test script first
test_cronjob

# Install cron job
install_cronjob

# Show status
show_status

echo ""
echo "═══════════════════════════════════════════════════════════════"
log_success "Setup complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
log_info "Next steps:"
echo "  1. Dashboard will update daily at $(printf "%02d:%02d" $CRON_HOUR $CRON_MINUTE)"
echo "  2. Check logs: tail -f $LOG_FILE"
echo "  3. Manual run: python3 tools/update_monitoring_dashboard.py"
echo "  4. Uninstall: $0 --uninstall"
echo ""
