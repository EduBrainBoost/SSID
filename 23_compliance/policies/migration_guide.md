# Policy Migration Guide - Phase 2
**SSID Codex Engine - ROOT-24-LOCK Enforced**

## Overview

This guide provides the canonical migration path for centralizing policies into the `23_compliance/policies/` tree structure, ensuring compliance with Blueprint 4.1 and ROOT-24-LOCK governance.

## Target Structure

```
23_compliance/policies/
├── 01_ai_layer/
│   ├── S01_identity_personas/
│   │   └── policy.yaml
│   ├── S02_documents_proofs/
│   └── ...
├── 02_audit_logging/
│   ├── S01_identity_personas/
│   └── ...
├── ...
└── 24_meta_orchestration/
    ├── S01_identity_personas/
    └── ...
```

## Migration Steps

### Phase 1: Preparation

1. **Inventory Current Policies**
   ```bash
   # Find all policy files in current locations
   find . -name "policy.yaml" -o -name "*policy*.yaml" > policy_inventory.txt
   ```

2. **Review migration_map.yaml**
   - Open `23_compliance/policies/migration_map.yaml`
   - Verify source → target mappings
   - Add any missing mappings

3. **Run SoT Requirement Mapper (Baseline)**
   ```bash
   python 24_meta_orchestration/registry/tools/sot_requirement_mapper.py
   ```
   - Save baseline score for comparison

### Phase 2: Migration Execution

#### Step-by-Step Process

For each policy file:

1. **Create Target Directory**
   ```bash
   mkdir -p 23_compliance/policies/{ROOT}/{SHARD}/
   ```

2. **Copy Policy File**
   ```bash
   cp {SOURCE_PATH} 23_compliance/policies/{ROOT}/{SHARD}/policy.yaml
   ```

3. **Update chart.yaml References**
   - Open `{ROOT}/shards/{SHARD}/chart.yaml`
   - Update policy path:
     ```yaml
     policy:
       path: "../../../23_compliance/policies/{ROOT}/{SHARD}/policy.yaml"
     ```

4. **Verify Migration**
   ```bash
   # Check file exists
   test -f 23_compliance/policies/{ROOT}/{SHARD}/policy.yaml && echo "OK"

   # Validate YAML
   python -c "import yaml; yaml.safe_load(open('23_compliance/policies/{ROOT}/{SHARD}/policy.yaml'))"
   ```

5. **Commit Changes**
   ```bash
   git add 23_compliance/policies/{ROOT}/{SHARD}/policy.yaml
   git add {ROOT}/shards/{SHARD}/chart.yaml
   git commit -m "policy: centralize {SHARD} → {ROOT}/{SHARD}

   - Moved from {OLD_PATH}
   - Updated chart.yaml reference
   - Part of Phase-2 policy centralization

   Co-Authored-By: SSID Codex Engine <noreply@ssid.org>"
   ```

### Phase 3: Validation

After each migration group (e.g., all S01 shards):

1. **Run Placeholder Scan**
   ```bash
   python 23_compliance/anti_gaming/placeholder_removal_tool.py --dry-run
   ```

2. **Run SoT Mapper**
   ```bash
   python 24_meta_orchestration/registry/tools/sot_requirement_mapper.py
   ```

3. **Compare Scores**
   - Check if compliance score improved
   - Verify no new violations introduced

4. **Run Tests**
   ```bash
   pytest 11_test_simulation/tools/ -v
   ```

## Migration Batches

Recommended grouping for incremental migration:

### Batch 1: High-Priority Roots (Week 1)
- `01_ai_layer/*`
- `02_audit_logging/*`
- `23_compliance/*`

### Batch 2: Core Infrastructure (Week 2)
- `03_core/*`
- `20_foundation/*`
- `24_meta_orchestration/*`

### Batch 3: Identity & Auth (Week 3)
- `08_identity_score/*`
- `09_meta_identity/*`
- `14_zero_time_auth/*`

### Batch 4: Remaining Roots (Week 4)
- All other roots

## Commit Message Convention

```
policy: centralize {file} → {root}/{shard}

- Source: {old_path}
- Target: 23_compliance/policies/{root}/{shard}/policy.yaml
- Updated: {root}/shards/{shard}/chart.yaml
- Evidence: SoT score improved from {old}% to {new}%

Part of Phase-2 Policy Centralization (Blueprint 4.1)
ROOT-24-LOCK enforced - no new roots created

Co-Authored-By: SSID Codex Engine <noreply@ssid.org>
```

## Post-Migration Checklist

- [ ] All policies migrated to `23_compliance/policies/`
- [ ] All `chart.yaml` files updated with new paths
- [ ] SoT Requirement Mapper score ≥ baseline
- [ ] Placeholder scan shows reduced violations
- [ ] All unit tests passing
- [ ] CI pipeline green
- [ ] No broken references in codebase
- [ ] Registry manifests updated

## Troubleshooting

### Issue: Policy Not Found After Migration

**Solution:**
1. Check `chart.yaml` path is correct (relative from shard directory)
2. Verify file exists at target location
3. Check file permissions

### Issue: YAML Parse Error

**Solution:**
1. Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('file.yaml'))"`
2. Check for tabs (use spaces only)
3. Verify indentation consistency

### Issue: Tests Failing

**Solution:**
1. Run individual test: `pytest path/to/test.py::test_name -v`
2. Check if test hardcodes old policy path
3. Update test fixtures if needed

## Evidence Trail

All migration activities generate evidence:

- **Manifests**: `24_meta_orchestration/registry/manifests/`
- **Scores**: `02_audit_logging/scores/`
- **Reports**: `02_audit_logging/reports/`

## Rollback Procedure

If migration causes issues:

1. **Identify Problem Commit**
   ```bash
   git log --grep="policy: centralize"
   ```

2. **Revert Specific Migration**
   ```bash
   git revert <commit-hash>
   ```

3. **Re-run Validation**
   ```bash
   python 24_meta_orchestration/registry/tools/sot_requirement_mapper.py
   pytest -v
   ```

## Contact

For questions or issues:
- Review: `23_compliance/policies/migration_map.yaml`
- Check: `02_audit_logging/reports/sot_requirement_report.md`
- Reference: Blueprint 4.1 documentation

---
**Version**: 1.0.0
**Last Updated**: 2025-01-09
**Author**: SSID Codex Engine
**License**: MIT
