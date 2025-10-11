#!/usr/bin/env bash
# SSID Run-All Tests – Version 4.3 (Root-24-LOCK)
# Führt sämtliche automatisierten Prüfungen der SSID-Struktur aus.
# Kompatibel mit CI/CD und lokalem Audit-Betrieb.
# Autor: SSID Codex Engine  ©2025  MIT License

set -e
export PYTHONIOENCODING=utf-8

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Verify we're in the correct project
if [ ! -d "$ROOT/12_tooling" ]; then
  echo "❌ Error: Project root not found. Run this script from within SSID/."
  exit 1
fi

DATE_UTC="$(date -u +%Y-%m-%d)"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "🚀  SSID Root-24 Run-All-Tests  •  $TIMESTAMP"
echo "Repository root: $ROOT"
echo "─────────────────────────────────────────────"

# 0️⃣  Global File-Extension Scan + Hash-Ledger
echo "🧮  Scanning all file extensions and building hash ledger …"
ALLOWED_EXT="py|yaml|yml|json|md|sh|ini|toml|sol|sql|csv|pdf|svg|txt|tag|gitignore|rego|log|Makefile|LICENSE|gitkeep|zip"
EVIDENCE_DIR="$ROOT/23_compliance/evidence/structure_validator/$DATE_UTC"
EVIDENCE_HASH="$EVIDENCE_DIR/file_hashes.json"
mkdir -p "$EVIDENCE_DIR"

# Collect and hash all files properly (streamed)
echo "[" > "$EVIDENCE_HASH"
FIRST=1
find "$ROOT" -type f \
  ! -path "*/.git/*" \
  ! -path "*/.venv/*" \
  ! -path "*/.claude/*" \
  ! -path "*/.pytest_cache/*" \
  2>/dev/null |
while read -r file; do
  ext="${file##*.}"
  rel="${file#$ROOT/}"
  if ! echo "$ext" | grep -Eq "$ALLOWED_EXT"; then
    echo "⚠️  Unexpected file type detected: $rel"
  fi
  # Allow empty __init__.py and .gitkeep files (package markers)
  if [ ! -s "$file" ] && [[ ! "$file" =~ (__init__\.py|\.gitkeep)$ ]]; then
    echo "❌  Empty file detected: $rel"; exit 24
  fi
  h=$(sha256sum "$file" | awk '{print $1}')
  if [ "$FIRST" -eq 1 ]; then
    printf '  {"file": "%s", "sha256": "%s"}\n' "$rel" "$h" >> "$EVIDENCE_HASH"
    FIRST=0
  else
    printf ' ,{"file": "%s", "sha256": "%s"}\n' "$rel" "$h" >> "$EVIDENCE_HASH"
  fi
done
echo "]" >> "$EVIDENCE_HASH"
echo "🧾  Global hash evidence written to: ${EVIDENCE_HASH#"$ROOT/"}"
echo "✅  File-extension and integrity scan complete."
echo "─────────────────────────────────────────────"

# 1️⃣  Structure Tests
echo "🧩  Running Structure Guard …"
bash "$ROOT/12_tooling/scripts/structure_guard.sh" || exit 24

echo "🔒  Running Structure Lock L3 …"
python "$ROOT/24_meta_orchestration/triggers/ci/gates/structure_lock_l3.py" || exit 24

# 2️⃣  Policy & Exception Validation
echo "📜  Validating Policy & Exceptions …"
python - <<'PYCODE'
import yaml, pathlib, sys, hashlib, os

# use actual working directory (corrects wrong parent path)
root = pathlib.Path(os.getcwd())
files = [
    root/"23_compliance/policies/structure_policy.yaml",
    root/"23_compliance/exceptions/root_level_exceptions.yaml",
    root/"23_compliance/exceptions/structure_exceptions.yaml"
]

for f in files:
    if not f.exists():
        print(f"❌ Missing {f}")
        sys.exit(24)
    data = yaml.safe_load(f.read_text(encoding='utf-8')) or {}
    h = hashlib.sha256(f.read_bytes()).hexdigest()[:12]
    print(f"✅ {f.name:<40} version {data.get('version','?')}  hash {h}")
PYCODE
echo "─────────────────────────────────────────────"

# 3️⃣  Shard & Module Tests
echo "🧠  Running shard-level tests …"
pytest -q "$ROOT/11_test_simulation/tests" --maxfail=1 --disable-warnings -x || exit 24

# 4️⃣  Compliance & Audit Checks
echo "🔍  Checking compliance evidence …"
if [ -d "$ROOT/23_compliance/evidence/structure_lock" ]; then
  ls -1 "$ROOT/23_compliance/evidence/structure_lock/" | grep structure_lock_l3 | tail -n 1
else
  echo "❌  Missing Evidence folder"; exit 24
fi
echo "─────────────────────────────────────────────"

# 5️⃣  Conformance Tests
if [ -d "$ROOT/11_test_simulation/conformance" ]; then
  echo "🧪  Running conformance tests …"
  pytest -q "$ROOT/11_test_simulation/conformance" --maxfail=1 --disable-warnings -x || exit 24
fi

# 6️⃣  Integration / E2E Tests
if [ -d "$ROOT/11_test_simulation/e2e" ]; then
  echo "🌐  Running integration (E2E) tests …"
  pytest -q "$ROOT/11_test_simulation/e2e" --maxfail=1 --disable-warnings -x || exit 24
fi

# 6️⃣+ Deep Recursive Tests (all roots, all levels)
echo "🔭  Scanning all root modules for local test suites ..."
for rootdir in "$ROOT"/[0-9][0-9]_*/; do
  if [ -d "$rootdir/tests" ]; then
    echo "🧩  Running tests in ${rootdir#"$ROOT/"}tests"
    pytest -q "$rootdir/tests" --maxfail=1 --disable-warnings -x || exit 24
  fi
  if [ -d "$rootdir/conformance" ]; then
    echo "🧩  Running conformance in ${rootdir#"$ROOT/"}conformance"
    pytest -q "$rootdir/conformance" --maxfail=1 --disable-warnings -x || exit 24
  fi
  if [ -d "$rootdir/integration" ]; then
    echo "🌐  Running integration in ${rootdir#"$ROOT/"}integration"
    pytest -q "$rootdir/integration" --maxfail=1 --disable-warnings -x || exit 24
  fi
done
echo "✅  Recursive root-level test discovery complete."
echo "─────────────────────────────────────────────"

# 7️⃣  Summary + Evidence Mirror
SUMMARY_JSON="$ROOT/24_meta_orchestration/registry/generated/run_all_tests_summary.json"
mkdir -p "$(dirname "$SUMMARY_JSON")"
{
  echo "{"
  echo "  \"timestamp_utc\": \"$TIMESTAMP\","
  echo "  \"result\": \"PASS\","
  echo "  \"evidence_hashes\": \"${EVIDENCE_HASH#"$ROOT/"}\""
  echo "}"
} > "$SUMMARY_JSON"

echo "✅  All Root-24 structure, compliance and conformance tests PASSED!"
echo "🧾  Summary written to: ${SUMMARY_JSON#"$ROOT/"}"
exit 0
