#!/bin/bash
# Test Self-Healing Engine - Fallback Mode
# =========================================
# Tests the self-healing suggestion generation using fallback rule-based mode

echo "=========================================="
echo "Self-Healing Engine Test - Fallback Mode"
echo "=========================================="
echo ""

# Test SOT-018 (yaml marker violation)
echo "Test 1: SOT-018 YAML Marker Validation"
echo "---------------------------------------"
cd /c/Users/bibel/Documents/Github/SSID/01_ai_layer/remediation
python self_healing_engine.py --rule-id SOT-018 --fallback-only

echo ""
echo ""

# Test SOT-025 (missing business_priority)
echo "Test 2: SOT-025 Business Priority Validation"
echo "---------------------------------------------"
python self_healing_engine.py --rule-id SOT-025 --fallback-only

echo ""
echo ""

# Test SOT-030 (deprecated business_priority)
echo "Test 3: SOT-030 Deprecated Business Priority"
echo "---------------------------------------------"
python self_healing_engine.py --rule-id SOT-030 --fallback-only

echo ""
echo "=========================================="
echo "All tests complete!"
echo "=========================================="
