# Self-Healing Engine v1.0 - AI-Powered Remediation Suggestions

**Status:** ✅ OPERATIONAL
**Version:** 1.0.0
**Date:** 2025-10-17
**Team:** SSID AI/ML Team

---

## Overview

The Self-Healing Engine provides AI-powered and rule-based remediation suggestions for failed SoT (Single Source of Truth) validation rules. It generates:

- **JSON Patch** (RFC 6902) for programmatic fixes
- **CLI commands** (yq/jq/sed) for manual application
- **Human-readable explanations** with confidence scoring
- **Effort estimates** for applying fixes

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SoT Validator CLI                        │
│              (12_tooling/cli/sot_validator.py)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ --suggest-fixes flag
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               Self-Healing Engine (Stage 2)                 │
│         (01_ai_layer/remediation/self_healing_engine.py)    │
│                                                             │
│  ┌─────────────┐         ┌─────────────┐                   │
│  │   LLM API   │  ◄──────┤   Prompt    │                   │
│  │  (Claude/   │         │  Template   │                   │
│  │   GPT-4)    │         │   (YAML)    │                   │
│  └──────┬──────┘         └─────────────┘                   │
│         │                                                    │
│         │ Fallback                                          │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │ Rule-Based  │                                            │
│  │ Suggestions │                                            │
│  │ (Hardcoded) │                                            │
│  └─────────────┘                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ JSON Patch
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   jsonpatch Library                         │
│              Apply fixes to YAML/JSON files                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### ✅ LLM-Powered Suggestions

- **Claude 3.5 Sonnet** (primary)
- **GPT-4** (fallback)
- Structured output with JSON Patch generation
- Context-aware explanations
- Confidence scoring (0.0-1.0)

### ✅ Rule-Based Fallback

- Hardcoded suggestions for common rules:
  - **SOT-018**: YAML block marker (```yml → ```yaml)
  - **SOT-019**: Version badge format
  - **SOT-025**: Missing business_priority in instances
  - **SOT-030**: Missing business_priority in deprecated_list

### ✅ Priority-Based Filtering

- **MUST rules**: Skipped (require manual review for safety)
- **SHOULD rules**: Suggestions generated (warnings only)
- **HAVE rules**: Suggestions generated (informational)

### ✅ Interactive Fix Application

- User-prompted patch application (y/N)
- Automatic revalidation after applying fixes
- Tracks applied vs. skipped fixes

### ✅ Caching

- SHA256-based cache keys
- Avoids redundant LLM calls
- Cache persists during session

---

## Usage

### CLI Integration

```bash
# Generate AI-powered suggestions for failed rules
python sot_validator.py --scorecard --input config.yaml --suggest-fixes

# Example output:
# ⚠️ SOT-018 [SHOULD]
# ---------------------------------------------------------------------
# Method: FALLBACK
# Confidence: 95%
# Effort: 10 seconds
#
# Explanation:
#   YAML block markers should use '```yaml' not '```yml' for consistency.
#
# CLI Command:
#   yq -i '.yaml_block_marker = "```yaml"' config.yaml
#
# JSON Patch:
#   [{"op": "replace", "path": "/yaml_block_marker", "value": "```yaml"}]
#
# Apply this fix? [y/N]: y
# ✅ Applied fix for SOT-018
# Revalidating...
# ✅ SOT-018 now passing!
```

### Python API

```python
from remediation.self_healing_engine import SelfHealingEngine

# Initialize engine
engine = SelfHealingEngine(
    llm_provider="claude",  # or "gpt4"
    api_key="your-api-key",  # or use env var
    use_fallback=True
)

# Generate suggestion
suggestion = engine.generate_suggestion(
    rule_id="SOT-018",
    rule_name="YAML Block Marker Validation",
    priority="should",
    scientific_foundation="IEEE 829-2008 Documentation Standards",
    current_data={"yaml_block_marker": "```yml"},
    failure_message="[SOT-018] FAIL: Invalid YAML marker",
    expected_behavior="Use ```yaml not ```yml"
)

# Output:
# {
#   "patch": [{"op": "replace", "path": "/yaml_block_marker", "value": "```yaml"}],
#   "cli_command": "yq -i '.yaml_block_marker = \"```yaml\"' config.yaml",
#   "explanation": "YAML block markers should use '```yaml' not '```yml'...",
#   "effort": "10 seconds",
#   "confidence": 0.95,
#   "method": "fallback"
# }

# Apply patch
engine.apply_patch(
    file_path="config.yaml",
    patch=suggestion["patch"],
    dry_run=False
)
```

---

## Configuration

### Environment Variables

```bash
# For Claude API (primary)
export CLAUDE_API_KEY="your-claude-api-key"
# or
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For OpenAI GPT-4 (fallback)
export OPENAI_API_KEY="your-openai-api-key"
```

### Prompt Template

Located at: `16_codex/prompts/ai_remediation_suggestion_example.yaml`

Key sections:
- `system_prompt`: LLM instructions
- `user_prompt_template`: Request format with placeholders
- `llm_config`: Model settings (temperature, max_tokens)
- `fallback`: Hardcoded suggestions configuration
- `qa_checks`: Validation rules
- `security`: Safety constraints

---

## Dependencies

```bash
# Required
pip install pyyaml

# Optional (for LLM features)
pip install requests

# Optional (for patch application)
pip install jsonpatch
```

---

## Testing

### Standalone Engine Test

```bash
# Test fallback mode
cd 01_ai_layer/remediation
python self_healing_engine.py --rule-id SOT-018 --fallback-only

# Test with LLM (requires API key)
python self_healing_engine.py --rule-id SOT-018 --provider claude --api-key your-key
```

### Integration Test

```bash
# Run all self-healing tests
cd 12_tooling/cli
bash test_self_healing.sh

# Output:
# Test 1: SOT-018 YAML Marker Validation
# Test 2: SOT-025 Business Priority Validation
# Test 3: SOT-030 Deprecated Business Priority
```

---

## Fallback Suggestions

### SOT-018: YAML Block Marker

**Problem:** Uses `\`\`\`yml` instead of `\`\`\`yaml`
**Fix:** Replace with `\`\`\`yaml`
**Confidence:** 95%
**Effort:** 10 seconds

```json
{
  "patch": [{"op": "replace", "path": "/yaml_block_marker", "value": "```yaml"}],
  "cli_command": "yq -i '.yaml_block_marker = \"```yaml\"' config.yaml"
}
```

### SOT-025: Missing business_priority

**Problem:** Instance missing `business_priority` field
**Fix:** Add with default `medium` value
**Confidence:** 85%
**Effort:** 30 seconds

```json
{
  "patch": [{"op": "add", "path": "/instances/0/business_priority", "value": "medium"}],
  "cli_command": "yq -i '.instances[0].business_priority = \"medium\"' config.yaml"
}
```

### SOT-030: Deprecated business_priority

**Problem:** Deprecated item missing `business_priority`
**Fix:** Add with default `low` value
**Confidence:** 80%
**Effort:** 30 seconds

```json
{
  "patch": [{"op": "add", "path": "/deprecated_list/0/business_priority", "value": "low"}],
  "cli_command": "yq -i '.deprecated_list[0].business_priority = \"low\"' config.yaml"
}
```

---

## File Structure

```
01_ai_layer/
├── remediation/
│   ├── __init__.py                   # Module exports
│   ├── self_healing_engine.py        # Core engine (400 lines)
│   └── README.md                     # This file
│
16_codex/
└── prompts/
    └── ai_remediation_suggestion_example.yaml  # LLM prompt template (250 lines)

12_tooling/
└── cli/
    ├── sot_validator.py              # CLI with --suggest-fixes flag
    └── test_self_healing.sh          # Test script
```

---

## Integration Points

### 1. SoT Validator CLI

**File:** `12_tooling/cli/sot_validator.py`
**Function:** `suggest_fixes(results, input_file, interactive=True)`

```python
# Called after scorecard generation
if args.suggest_fixes:
    fix_summary = suggest_fixes(results, args.input, interactive=True)
```

### 2. MoSCoW Priority Model

**Priority-based filtering:**
- MUST (48 rules): Skipped - too critical for auto-fix
- SHOULD (15 rules): Suggestions generated
- HAVE (6 rules): Suggestions generated

### 3. Validation Core

**File:** `03_core/validators/sot/sot_validator_core.py`
**Function:** `validate_all_sot_rules(data, rule_ids=None)`

Provides validation results to self-healing engine.

---

## Security

### Safety Constraints

1. **MUST rules never auto-applied**
   - Require manual review
   - Too critical for automation

2. **LLM output sanitization**
   - Strip markdown code blocks
   - Validate JSON structure
   - Check for code injection

3. **Patch safety validation**
   - Verify JSON Pointer paths
   - Check for critical field deletion
   - Validate against schema

4. **Interactive mode required**
   - User approval before applying fixes
   - Revalidation after each fix
   - Undo not supported (backup recommended)

---

## Cost Management

### LLM API Costs (Estimated)

- **Claude 3.5 Sonnet:** ~$0.003 per suggestion
- **GPT-4:** ~$0.01 per suggestion
- **Fallback mode:** Free (no API calls)

### Rate Limiting

- Max 10 requests/minute (configurable)
- Cache TTL: 1 hour
- Daily budget: $10 (alert threshold)

---

## Roadmap

### Future Enhancements (v2.0)

1. **Batch Fix Application**
   - Apply multiple fixes at once
   - Transaction rollback on failure

2. **Advanced Confidence Scoring**
   - Multi-model consensus
   - Historical success rate tracking

3. **Custom Rule Suggestions**
   - User-defined fallback rules
   - Domain-specific templates

4. **Git Integration**
   - Auto-commit after successful fixes
   - Branch creation for bulk fixes

5. **Web UI**
   - Visual diff preview
   - One-click fix application

---

## Compliance

### Standards

- **JSON Patch:** RFC 6902
- **Documentation:** IEEE 829-2008
- **AI Governance:** NIST AI RMF 1.0

### Audit Trail

- All suggestions logged to `02_audit_logging/logs/`
- Includes: rule_id, method, confidence, applied status
- SHA-256 hashing for evidence chain

---

## Troubleshooting

### Issue: LLM API calls failing

**Solution:**
1. Check API key is set: `echo $CLAUDE_API_KEY`
2. Verify network connectivity
3. Use fallback mode: `--fallback-only` flag

### Issue: Patch application fails

**Solution:**
1. Verify JSON Pointer path is correct
2. Check file is valid YAML/JSON
3. Ensure write permissions

### Issue: Confidence scores too low

**Solution:**
1. Improve prompt template specificity
2. Add more examples to fallback rules
3. Use LLM mode instead of fallback

---

## Contributing

### Adding New Fallback Rules

Edit `01_ai_layer/remediation/self_healing_engine.py`:

```python
FALLBACK_SUGGESTIONS = {
    "SOT-XXX": {
        "patch": [{"op": "replace", "path": "/field", "value": "new_value"}],
        "cli_command": 'yq -i \'.field = "new_value"\' config.yaml',
        "explanation": "Brief explanation of the fix",
        "effort": "30 seconds",
        "confidence": 0.90
    }
}
```

### Improving Prompt Template

Edit `16_codex/prompts/ai_remediation_suggestion_example.yaml`:

- Update `system_prompt` for better LLM instructions
- Add examples to `examples` section
- Adjust `llm_config.temperature` for determinism

---

## References

- **JSON Patch Specification:** https://jsonrfc.org/rfc6902
- **MoSCoW Priority Model:** `03_core/validators/sot/sot_validator_core.py`
- **SoT Contract:** `16_codex/contracts/sot/sot_contract.yaml`
- **CI MoSCoW Gate:** `.github/workflows/ci_moscow_gate.yml`

---

## Support

- **Team:** SSID AI/ML Team
- **Contact:** ssid-core@example.com
- **Documentation:** `05_documentation/design/roadmap_adaptive_compliance_v4.md`
- **Issues:** GitHub Issues (for bug reports)

---

**Version:** 1.0.0
**Last Updated:** 2025-10-17
**Status:** ✅ PRODUCTION READY
