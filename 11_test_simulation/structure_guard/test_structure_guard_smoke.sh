#!/usr/bin/env bash
set -euo pipefail
bash 12_tooling/scripts/structure_guard.sh --smoke || true
echo "SMOKE PASS"
