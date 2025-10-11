#!/usr/bin/env bash
set -euo pipefail

EXCEPTIONS_FILE="23_compliance/exceptions/root_level_exceptions.yaml"

# Ensure 24 modules
modules=$(ls -d [0-9][0-9]_* 2>/dev/null | wc -l | tr -d ' ')
if [ "$modules" != "24" ]; then
  echo "ERROR: Expected 24 root modules, got $modules"
  exit 24
fi

# Verify exceptions
if [ ! -f "$EXCEPTIONS_FILE" ]; then
  echo "ERROR: Missing $EXCEPTIONS_FILE"
  exit 24
fi

# Scan root unauthorized items
for item in * .*; do
  [ "$item" = "." ] && continue
  [ "$item" = ".." ] && continue
  [[ "$item" =~ ^[0-9]{2}_.+ ]] && continue
  # allow explicit exceptions
  if ! grep -qF "$item" "$EXCEPTIONS_FILE"; then
    echo "VIOLATION: Unauthorized root-level item '$item'"
    # Struktur-Verstoß → Review-First, kein Quarantine-Trigger
    mkdir -p 23_compliance/violations
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) root_violation: $item" >> 23_compliance/violations/structure_violations.log
    exit 24
  fi
done

echo "✅ structure_guard PASS"
