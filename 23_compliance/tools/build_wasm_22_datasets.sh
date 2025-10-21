#!/usr/bin/env bash
# WASM Build Script - 22_datasets Policy
# Phase 7: HONEST COMPLIANCE v6.3 + Drift Control
# Purpose: Deterministic Rego → WASM compilation with reproducible hash

set -euo pipefail

# Configuration
POLICY="23_compliance/policies/22_datasets_policy_stub_v6_0.rego"
OUT_DIR="23_compliance/wasm"
ENTRYPOINT="ssid/22datasets/v6_0"
OUT_FILE="22_datasets_v6_0.wasm"

echo "=== Building WASM for 22_datasets Policy ==="

# Verify OPA is installed
if ! command -v opa &> /dev/null; then
    echo "[ERROR] OPA CLI not found. Install from https://www.openpolicyagent.org/docs/latest/#running-opa"
    exit 1
fi

echo "OPA Version:"
opa version

# Verify policy file exists
if [ ! -f "$POLICY" ]; then
    echo "[ERROR] Policy file not found: $POLICY"
    exit 1
fi

# Create output directory
mkdir -p "$OUT_DIR"

# Build WASM with explicit entrypoint
echo "Building WASM with entrypoint: data.$ENTRYPOINT"
opa build -t wasm -e "data.$ENTRYPOINT" "$POLICY"

# Extract WASM from bundle (OPA creates bundle.tar.gz by default)
if [ -f "bundle.tar.gz" ]; then
    tar -xzf bundle.tar.gz policy.wasm
    mv policy.wasm "$OUT_DIR/$OUT_FILE"
    rm bundle.tar.gz
else
    echo "[ERROR] OPA build did not produce bundle.tar.gz"
    exit 1
fi

# Generate SHA256 hash
echo "Generating SHA256 hash..."
if command -v sha256sum &> /dev/null; then
    sha256sum "$OUT_DIR/$OUT_FILE" | awk '{print $1}' > "$OUT_DIR/$OUT_FILE.sha256"
else
    # macOS fallback
    shasum -a 256 "$OUT_DIR/$OUT_FILE" | awk '{print $1}' > "$OUT_DIR/$OUT_FILE.sha256"
fi

# Display results
HASH=$(cat "$OUT_DIR/$OUT_FILE.sha256")
SIZE=$(stat -c%s "$OUT_DIR/$OUT_FILE" 2>/dev/null || stat -f%z "$OUT_DIR/$OUT_FILE" 2>/dev/null || echo "unknown")

echo "[OK] WASM build complete:"
echo "   File: $OUT_DIR/$OUT_FILE"
echo "   Size: $SIZE bytes"
echo "   SHA256: $HASH"

# Verify WASM is valid
if [ ! -s "$OUT_DIR/$OUT_FILE" ]; then
    echo "[ERROR] WASM file is empty or invalid"
    exit 1
fi

echo "[OK] 22_datasets WASM build successful"
