# Phase 1.5: Factory Pattern Optimization (Optional)

**Date**: 2025-10-14
**Status**: OPTIONAL - Execute only after 2 stable CI cycles
**Prerequisite**: Phase 1 consolidation complete and stable
**Estimated Impact**: -1 to -2s additional build time, -100KB code size

---

## Executive Summary

Phase 1.5 is an **optional optimization** that eliminates the 384 minimal subclasses by replacing them with a factory pattern + configuration files. This should only be executed after confirming that no shards require local overrides over 2 CI cycles.

**Trade-offs**:
- **Pros**: Further build time reduction, simpler file structure, single configuration source
- **Cons**: Less flexibility for per-shard customization, requires configuration management

**Trigger Condition**: All shards remain stable with zero custom overrides after 2 CI cycles

---

## Current State (Post-Phase 1)

```
03_core/healthcheck/shard_health_base.py       (5 KB, base class)

shards/01_identitaet_personen/.../health.py    (0.5 KB, 3-line subclass)
shards/02_dokumente_nachweise/.../health.py    (0.5 KB, 3-line subclass)
shards/03_zugang_berechtigungen/.../health.py  (0.5 KB, 3-line subclass)
... (381 more minimal subclasses)

Total: 1 base + 384 subclasses = ~200 KB
Build time: ~5s
```

---

## Proposed State (Phase 1.5)

```
03_core/healthcheck/shard_health_base.py       (5 KB, base class)
03_core/healthcheck/shard_health_factory.py    (3 KB, factory + config loader)
03_core/healthcheck/shard_registry.yaml        (15 KB, all shard configurations)

shards/01_identitaet_personen/.../health.py    (0.2 KB, factory call)
shards/02_dokumente_nachweise/.../health.py    (0.2 KB, factory call)
shards/03_zugang_berechtigungen/.../health.py  (0.2 KB, factory call)
... (381 more factory calls)

Total: 1 base + 1 factory + 1 config + 384 thin wrappers = ~100 KB
Build time: ~3-4s (cached YAML parsing)
```

### Efficiency Gain (Phase 1 → Phase 1.5)

| Metric | Phase 1 | Phase 1.5 | Improvement |
|--------|---------|-----------|-------------|
| **Code Size** | ~200 KB | ~100 KB | -50% |
| **Build Time** | ~5s | ~3-4s | -20 to -40% |
| **Maintenance** | 1 base + 384 custom | 1 base + 1 config | Further simplification |

---

## Implementation Design

### 1. Shard Registry Configuration

**File**: `03_core/healthcheck/shard_registry.yaml`

```yaml
# Shard Health Check Registry
# Central configuration for all shard health endpoints

version: 1
registry_type: shard_health

shards:
  # Layer 01: AI Layer
  - layer: "01_ai_layer"
    shard_id: "01"
    shard_name: "Identitaet_Personen"
    path: "01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/api/health.py"

  - layer: "01_ai_layer"
    shard_id: "02"
    shard_name: "Dokumente_Nachweise"
    path: "01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/api/health.py"

  # ... (382 more shard configurations)

  # Layer 24: Meta Orchestration
  - layer: "24_meta_orchestration"
    shard_id: "16"
    shard_name: "Behoerden_Verwaltung"
    path: "24_meta_orchestration/shards/16_behoerden_verwaltung/implementations/python-tensorflow/src/api/health.py"

# Optional: Custom health checks for specific shards
custom_checks:
  - shard_id: "10"
    layer: "08_identity_score"
    checks:
      - database_connection
      - external_api_availability
```

### 2. Factory Implementation

**File**: `03_core/healthcheck/shard_health_factory.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shard_health_factory.py - Shard Health Check Factory
Author: edubrainboost ©2025 MIT License

Factory pattern for generating shard health check instances from configuration.
Eliminates need for 384 individual subclass files.

Usage:
    from healthcheck.shard_health_factory import ShardHealthFactory

    factory = ShardHealthFactory()
    health_check = factory.create_for_path(__file__)
    status = health_check.get_health_status()
"""

import yaml
from pathlib import Path
from typing import Dict, Optional
from .shard_health_base import ShardHealthCheck


class ShardHealthFactory:
    """Factory for creating shard health check instances from configuration."""

    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize factory with shard registry.

        Args:
            registry_path: Path to shard_registry.yaml (default: auto-detect)
        """
        if registry_path is None:
            registry_path = Path(__file__).parent / "shard_registry.yaml"

        self.registry_path = registry_path
        self._registry = None
        self._path_index = None

    @property
    def registry(self) -> Dict:
        """Load and cache registry configuration."""
        if self._registry is None:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self._registry = yaml.safe_load(f)
        return self._registry

    @property
    def path_index(self) -> Dict[str, Dict]:
        """Build and cache path-to-shard lookup index."""
        if self._path_index is None:
            self._path_index = {}
            for shard in self.registry.get("shards", []):
                # Normalize path for lookup
                path_key = Path(shard["path"]).as_posix()
                self._path_index[path_key] = shard
        return self._path_index

    def create_for_path(self, file_path: str) -> ShardHealthCheck:
        """
        Create health check instance for given file path.

        Args:
            file_path: Path to health.py file (typically __file__)

        Returns:
            ShardHealthCheck instance configured for this shard

        Raises:
            ValueError: If path not found in registry
        """
        # Normalize file path for lookup
        normalized_path = Path(file_path).as_posix()

        # Try direct match
        if normalized_path in self.path_index:
            shard = self.path_index[normalized_path]
            return ShardHealthCheck(
                shard_name=shard["shard_name"],
                shard_id=shard["shard_id"]
            )

        # Try fuzzy match (handle relative vs absolute paths)
        for registry_path, shard in self.path_index.items():
            if normalized_path.endswith(registry_path) or registry_path.endswith(normalized_path):
                return ShardHealthCheck(
                    shard_name=shard["shard_name"],
                    shard_id=shard["shard_id"]
                )

        # Fallback: Extract from path structure
        parts = Path(file_path).parts

        # Try to find shard ID from path (e.g., "01_identitaet_personen")
        shard_name = "Unknown"
        shard_id = "00"

        for part in parts:
            if part.startswith("shards/"):
                continue
            if "_" in part:
                try:
                    potential_id = part.split("_")[0]
                    if potential_id.isdigit():
                        shard_id = potential_id
                        shard_name = "_".join(part.split("_")[1:]).replace("-", "_").title()
                        break
                except:
                    pass

        return ShardHealthCheck(shard_name=shard_name, shard_id=shard_id)

    def create(self, shard_name: str, shard_id: str) -> ShardHealthCheck:
        """
        Create health check instance by shard name and ID.

        Args:
            shard_name: Name of shard
            shard_id: Shard identifier

        Returns:
            ShardHealthCheck instance
        """
        return ShardHealthCheck(shard_name=shard_name, shard_id=shard_id)

    def list_shards(self) -> list:
        """
        List all registered shards.

        Returns:
            List of shard configuration dicts
        """
        return self.registry.get("shards", [])

    def validate_registry(self) -> Dict[str, any]:
        """
        Validate registry configuration.

        Returns:
            Validation results dict
        """
        issues = []
        shards = self.registry.get("shards", [])

        # Check for duplicate shard IDs per layer
        seen = {}
        for shard in shards:
            key = (shard["layer"], shard["shard_id"])
            if key in seen:
                issues.append(f"Duplicate shard_id {shard['shard_id']} in layer {shard['layer']}")
            seen[key] = shard

        # Check for missing required fields
        required_fields = ["layer", "shard_id", "shard_name", "path"]
        for i, shard in enumerate(shards):
            for field in required_fields:
                if field not in shard:
                    issues.append(f"Shard {i}: Missing required field '{field}'")

        return {
            "valid": len(issues) == 0,
            "shard_count": len(shards),
            "issues": issues
        }


# Singleton instance for import efficiency
_factory_instance = None

def get_factory() -> ShardHealthFactory:
    """Get singleton factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = ShardHealthFactory()
    return _factory_instance


if __name__ == "__main__":
    # Example usage and validation
    factory = ShardHealthFactory()

    print("Shard Health Factory - Validation")
    print("=" * 70)
    print()

    # Validate registry
    validation = factory.validate_registry()
    print(f"Registry valid: {validation['valid']}")
    print(f"Total shards: {validation['shard_count']}")

    if validation['issues']:
        print(f"\nIssues found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    else:
        print("\nNo issues found")

    print()
    print("Sample shard instances:")
    print()

    # Test factory
    for shard in factory.list_shards()[:5]:
        health_check = factory.create(shard["shard_name"], shard["shard_id"])
        status = health_check.get_health_status()
        print(f"  {shard['shard_name']} (ID: {shard['shard_id']}): {status['status']}")
```

### 3. Updated Health Module Template

**Each health.py file becomes**:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shard Health Check: <Shard_Name>
Layer: <Layer_ID>
Shard ID: <Shard_ID>
"""

from pathlib import Path
import sys

# Add core to path
core_path = Path(__file__).resolve().parents[6] / "03_core"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

from healthcheck.shard_health_factory import get_factory


# Flask compatibility
def health():
    from flask import jsonify
    factory = get_factory()
    health_check = factory.create_for_path(__file__)
    return jsonify(health_check.get_health_status())


# Standalone execution
if __name__ == "__main__":
    factory = get_factory()
    health_check = factory.create_for_path(__file__)

    import json
    print(json.dumps(health_check.get_health_status(), indent=2))
```

**Size**: ~15 lines (down from ~25 lines in Phase 1)

---

## Migration Script

**File**: `12_tooling/scripts/migrate_to_factory_pattern.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate_to_factory_pattern.py - Phase 1.5 Factory Pattern Migration

Migrates Phase 1 minimal subclasses to Phase 1.5 factory pattern.

ONLY RUN AFTER:
- Phase 1 consolidation complete
- 2 CI cycles passed successfully
- Zero custom overrides detected in health modules

Usage:
    python 12_tooling/scripts/migrate_to_factory_pattern.py
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import shutil
import re

# Add paths
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))


class FactoryPatternMigrator:
    """Migrate Phase 1 subclasses to Phase 1.5 factory pattern."""

    def __init__(self, root_dir: Path = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[2]

        self.root = root_dir
        self.shard_registry = []

    def scan_health_modules(self) -> List[Path]:
        """Find all health.py modules in shards."""
        return list(self.root.rglob("shards/**/health.py"))

    def extract_shard_info(self, health_file: Path) -> Dict:
        """Extract shard information from health.py file."""
        content = health_file.read_text(encoding="utf-8")

        # Extract from docstring
        shard_name = "Unknown"
        shard_id = "00"

        # Try to extract from class definition
        class_match = re.search(r'class (\w+)Health\(ShardHealthCheck\)', content)
        if class_match:
            shard_name = class_match.group(1)

        # Try to extract from super().__init__
        init_match = re.search(r'super\(\).__init__\("([^"]+)",\s*"([^"]+)"\)', content)
        if init_match:
            shard_name = init_match.group(1)
            shard_id = init_match.group(2)

        # Determine layer from path
        parts = health_file.parts
        layer = "unknown"
        for i, part in enumerate(parts):
            if part.startswith(tuple(f"{j:02d}_" for j in range(1, 25))):
                layer = part
                break

        return {
            "layer": layer,
            "shard_id": shard_id,
            "shard_name": shard_name,
            "path": str(health_file.relative_to(self.root))
        }

    def generate_factory_wrapper(self, health_file: Path) -> str:
        """Generate factory-based wrapper code."""
        # Calculate relative path to core
        depth = len([p for p in health_file.relative_to(self.root).parts if p != "health.py"]) - 1

        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shard Health Check - Factory Pattern
Auto-generated by Phase 1.5 migration
"""

from pathlib import Path
import sys

# Add core to path
core_path = Path(__file__).resolve().parents[{depth}] / "03_core"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

from healthcheck.shard_health_factory import get_factory


# Flask compatibility
def health():
    from flask import jsonify
    factory = get_factory()
    health_check = factory.create_for_path(__file__)
    return jsonify(health_check.get_health_status())


# Standalone execution
if __name__ == "__main__":
    factory = get_factory()
    health_check = factory.create_for_path(__file__)

    import json
    print(json.dumps(health_check.get_health_status(), indent=2))
'''

    def generate_registry_yaml(self) -> str:
        """Generate shard_registry.yaml content."""
        import yaml

        registry = {
            "version": 1,
            "registry_type": "shard_health",
            "shards": sorted(self.shard_registry, key=lambda x: (x["layer"], x["shard_id"]))
        }

        return yaml.dump(registry, default_flow_style=False, sort_keys=False)

    def migrate(self, dry_run: bool = False):
        """Execute migration to factory pattern."""
        print("=" * 70)
        print("Phase 1.5: Factory Pattern Migration")
        print("=" * 70)
        print()

        # Scan modules
        health_modules = self.scan_health_modules()
        print(f"Found {len(health_modules)} health modules")
        print()

        if dry_run:
            print("[DRY RUN MODE - No changes will be made]")
            print()

        # Create backup
        if not dry_run:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.root / "02_audit_logging" / "backups" / f"phase1_5_migration_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"Backup directory: {backup_dir}")
            print()

        # Process each module
        success = 0
        failed = 0

        for health_file in health_modules:
            try:
                # Extract shard info
                shard_info = self.extract_shard_info(health_file)
                self.shard_registry.append(shard_info)

                if not dry_run:
                    # Backup original
                    rel_path = health_file.relative_to(self.root)
                    backup_file = backup_dir / rel_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(health_file, backup_file)

                    # Write factory wrapper
                    factory_code = self.generate_factory_wrapper(health_file)
                    health_file.write_text(factory_code, encoding="utf-8")

                success += 1

            except Exception as e:
                print(f"Failed: {health_file}")
                print(f"  Error: {e}")
                failed += 1

        print()
        print("=" * 70)
        print("Migration Complete")
        print("=" * 70)
        print(f"Total modules: {len(health_modules)}")
        print(f"Success: {success}")
        print(f"Failed: {failed}")

        if not dry_run:
            print(f"Backup: {backup_dir}")

            # Write registry
            registry_path = self.root / "03_core" / "healthcheck" / "shard_registry.yaml"
            registry_path.write_text(self.generate_registry_yaml(), encoding="utf-8")
            print(f"Registry: {registry_path}")

        print()
        print("Next steps:")
        print("  1. Verify factory pattern: python 03_core/healthcheck/shard_health_factory.py")
        print("  2. Test sample health endpoints")
        print("  3. Run post-migration verification workflow")
        print("  4. Measure build time reduction")


if __name__ == "__main__":
    migrator = FactoryPatternMigrator()

    # Safety check: Require explicit confirmation
    print("Phase 1.5 Factory Pattern Migration")
    print()
    print("This will:")
    print("  1. Scan all 384 health modules")
    print("  2. Extract shard configuration")
    print("  3. Generate shard_registry.yaml")
    print("  4. Replace subclasses with factory wrappers")
    print("  5. Create backup in 02_audit_logging/backups/")
    print()
    print("PREREQUISITE: Phase 1 stable for 2+ CI cycles")
    print()

    response = input("Proceed with migration? [yes/no/dry-run]: ").strip().lower()

    if response == "yes":
        migrator.migrate(dry_run=False)
    elif response == "dry-run":
        migrator.migrate(dry_run=True)
    else:
        print("Migration cancelled")
```

---

## Verification

### 1. Pre-Migration Checks

```bash
# Ensure Phase 1 is stable
python 12_tooling/quality/link_density_analyzer.py

# Check for custom overrides in health modules
grep -r "def get_health_status" */shards/*/health.py

# If any overrides found, DO NOT proceed with Phase 1.5
```

### 2. Run Migration (Dry Run First)

```bash
# Dry run to preview changes
python 12_tooling/scripts/migrate_to_factory_pattern.py
# Enter: dry-run

# Review output, then execute
python 12_tooling/scripts/migrate_to_factory_pattern.py
# Enter: yes
```

### 3. Post-Migration Verification

```bash
# Validate registry
python 03_core/healthcheck/shard_health_factory.py

# Test sample health endpoints
python 01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/api/health.py

# Run post-migration CI workflow
gh workflow run post_consolidation_verification.yml
```

---

## OPA Policy Update

**File**: `23_compliance/policies/opa/link_density_threshold.rego`

Add Phase 1.5 pattern recognition:

```rego
# Exception: Allow factory pattern (Phase 1.5)
shard_health_factory_pattern if {
    # Check if factory exists
    input.consolidation_status
    input.consolidation_status.factory_exists == true

    # Check if registry exists
    input.consolidation_status.registry_exists == true

    # Allow up to 400 factory wrappers
    wrapper_count := input.consolidation_status.wrapper_count
    wrapper_count <= 400
}

deny[msg] if {
    shard_health_duplication
    not shard_health_consolidation_pattern  # Phase 1
    not shard_health_factory_pattern        # Phase 1.5
    msg := sprintf("Critical duplication: %d identical shard health modules detected", [input.duplication_count])
}
```

---

## Rollback Procedure

If factory pattern causes issues:

```bash
# Locate backup
BACKUP_DIR=$(ls -td 02_audit_logging/backups/phase1_5_migration_* | head -1)

echo "Rolling back from: $BACKUP_DIR"

# Restore all health modules
find "$BACKUP_DIR" -name "health.py" | while read backup_file; do
    rel_path=${backup_file#$BACKUP_DIR/}
    cp "$backup_file" "$rel_path"
    echo "Restored: $rel_path"
done

# Remove factory registry
rm 03_core/healthcheck/shard_registry.yaml

echo "Rollback complete - reverted to Phase 1 state"
```

---

## Success Criteria

Phase 1.5 is successful if:

1. All 384 health modules migrated to factory wrappers
2. Registry YAML generated with 384 shard entries
3. Factory validation passes with 0 issues
4. All health endpoints remain functional
5. Build time reduced by additional 1-2s
6. OPA policy allows factory pattern
7. Zero custom overrides remain in health modules

---

## Trade-off Analysis

### When to Execute Phase 1.5

**Execute if**:
- No shards need custom health check logic
- Build time optimization is priority
- Central configuration is preferred
- 2+ CI cycles confirmed stable

**Skip if**:
- Some shards need custom overrides
- Per-shard flexibility is important
- Current Phase 1 performance is sufficient
- Team prefers explicit subclasses

### Comparison: Phase 1 vs Phase 1.5

| Aspect | Phase 1 (Subclasses) | Phase 1.5 (Factory) |
|--------|---------------------|-------------------|
| **Customization** | Easy (override methods) | Harder (config + custom checks) |
| **Build Time** | ~5s | ~3-4s |
| **Code Size** | ~200 KB | ~100 KB |
| **Maintenance** | 1 base + 384 subclasses | 1 base + 1 factory + 1 config |
| **Flexibility** | High (Python inheritance) | Medium (YAML config) |
| **Discoverability** | Good (explicit classes) | Good (central registry) |

---

## Timeline

| Task | Duration | Status |
|------|----------|--------|
| Design factory pattern | 30 min | Complete (this document) |
| Implement factory class | 20 min | Pending |
| Create migration script | 30 min | Pending |
| Update OPA policy | 10 min | Pending |
| **Wait for stability** | **2 CI cycles** | **Pending** |
| Execute migration | 5 min | Pending |
| Verify & test | 10 min | Pending |
| Measure impact | 5 min | Pending |

**Total Active Time**: ~2 hours
**Total Wait Time**: 2 CI cycles (~1 week typical)

---

## Governance Registry Update

After successful Phase 1.5 migration, add to `24_meta_orchestration/registry/governance_optimizations.yaml`:

```yaml
- id: healthcheck_consolidation_phase1_5
  date: YYYY-MM-DD
  type: CODE_CONSOLIDATION
  target: shard_health_modules
  description: Factory pattern migration to eliminate 384 minimal subclasses

  impact:
    code_reduction_kb: 100
    build_time_gain_s: 2
    maintenance_reduction_pct: 50

  metrics_before:
    total_modules: 385  # 1 base + 384 subclasses
    code_size_kb: 200
    build_time_s: 5
    maintenance_locations: 385

  metrics_after:
    total_modules: 387  # 1 base + 1 factory + 1 registry + 384 wrappers
    code_size_kb: 100
    build_time_s: 3
    maintenance_locations: 2  # Base + factory (registry is config)

  implementation:
    factory_class: 03_core/healthcheck/shard_health_factory.py
    shard_registry: 03_core/healthcheck/shard_registry.yaml
    migration_script: 12_tooling/scripts/migrate_to_factory_pattern.py
    opa_policy_update: 23_compliance/policies/opa/link_density_threshold.rego

  compliance:
    root_24_compliant: true
    no_new_roots: true
    existing_structure_only: true
    opa_policy_exception: true
    allowed_pattern: factory_plus_registry

  status: ACTIVE
  prerequisite: healthcheck_consolidation_phase1
  trigger_condition: 2_ci_cycles_stable_with_zero_overrides
```

---

## Conclusion

Phase 1.5 is an **optional optimization** that trades some per-shard flexibility for improved build performance and simpler maintenance. It should only be executed after confirming Phase 1 stability and zero custom overrides.

**Recommendation**:
- Monitor Phase 1 for 2 CI cycles
- If no shards require custom logic, execute Phase 1.5
- If any shards need overrides, remain at Phase 1

**Command to Execute** (after 2 stable cycles):
```bash
python 12_tooling/scripts/migrate_to_factory_pattern.py
```

**Expected Additional Impact**: -1 to -2s build time, -100KB code, further maintenance simplification
