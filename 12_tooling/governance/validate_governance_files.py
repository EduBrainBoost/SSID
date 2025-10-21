#!/usr/bin/env python3
"""
Governance File Validator
Validates chart.yaml and manifest.yaml files across all 24 root directories
Real validation - no smoke and mirrors
"""
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# Required fields for chart.yaml
CHART_REQUIRED_FIELDS = {
    'apiVersion': str,
    'kind': str,
    'metadata': dict,
    'spec': dict
}

CHART_METADATA_FIELDS = {
    'name': str,
    'version': str,
    'description': str,
    'created': str,
    'status': str
}

CHART_SPEC_FIELDS = {
    'capabilities': list,
    'interfaces': list,
    'policies': list,
    'dependencies': dict,
    'governance': dict,
    'compliance': dict
}

# Required fields for manifest.yaml
MANIFEST_REQUIRED_FIELDS = {
    'apiVersion': str,
    'kind': str,
    'metadata': dict,
    'spec': dict
}

class GovernanceValidator:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.errors = []
        self.warnings = []
        self.validated_count = 0
        
    def validate_file_structure(self, data: dict, required_fields: Dict, file_path: str) -> bool:
        """Validate that all required fields exist and have correct types"""
        valid = True
        for field, expected_type in required_fields.items():
            if field not in data:
                self.errors.append(f"{file_path}: Missing required field '{field}'")
                valid = False
            elif not isinstance(data[field], expected_type):
                self.errors.append(f"{file_path}: Field '{field}' should be {expected_type.__name__}, got {type(data[field]).__name__}")
                valid = False
        return valid
    
    def validate_chart(self, root_dir: Path) -> bool:
        """Validate chart.yaml for a root directory"""
        chart_file = root_dir / "chart.yaml"
        if not chart_file.exists():
            self.errors.append(f"{root_dir.name}: Missing chart.yaml")
            return False
            
        try:
            with open(chart_file, 'r', encoding='utf-8') as f:
                chart_data = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"{chart_file}: Failed to parse YAML: {e}")
            return False
            
        # Validate top-level structure
        if not self.validate_file_structure(chart_data, CHART_REQUIRED_FIELDS, str(chart_file)):
            return False
            
        # Validate metadata
        if not self.validate_file_structure(chart_data['metadata'], CHART_METADATA_FIELDS, str(chart_file)):
            return False
            
        # Validate spec (partial - just check key fields exist)
        for field in ['capabilities', 'interfaces', 'policies']:
            if field not in chart_data['spec']:
                self.warnings.append(f"{chart_file}: Missing spec.{field}")
                
        return True
    
    def validate_manifest(self, root_dir: Path) -> bool:
        """Validate manifest.yaml for a root directory"""
        manifest_file = root_dir / "manifest.yaml"
        if not manifest_file.exists():
            self.errors.append(f"{root_dir.name}: Missing manifest.yaml")
            return False
            
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"{manifest_file}: Failed to parse YAML: {e}")
            return False
            
        # Validate top-level structure
        if not self.validate_file_structure(manifest_data, MANIFEST_REQUIRED_FIELDS, str(manifest_file)):
            return False
            
        return True
    
    def validate_all_roots(self) -> bool:
        """Validate all 24 root directories"""
        roots = sorted([d for d in self.root_path.glob("*_*") if d.is_dir() and d.name[0:2].isdigit()])
        
        print(f"Found {len(roots)} root directories")
        print("=" * 60)
        
        for root_dir in roots:
            print(f"Validating {root_dir.name}...")
            chart_valid = self.validate_chart(root_dir)
            manifest_valid = self.validate_manifest(root_dir)
            
            if chart_valid and manifest_valid:
                self.validated_count += 1
                print(f"  [OK] {root_dir.name}: Valid")
            else:
                print(f"  [FAIL] {root_dir.name}: Invalid")
                
        print("=" * 60)
        print(f"\nValidation Summary:")
        print(f"  Validated: {self.validated_count}/{len(roots)}")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")
        
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")
                
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        return len(self.errors) == 0

def main():
    # Find SSID root directory
    current = Path(__file__).resolve()
    ssid_root = None
    
    # Walk up to find the SSID root
    for parent in current.parents:
        if (parent / "01_ai_layer").exists() and (parent / "24_meta_orchestration").exists():
            ssid_root = parent
            break
            
    if not ssid_root:
        print("Error: Could not find SSID root directory")
        sys.exit(1)
        
    print(f"SSID Root: {ssid_root}")
    print()
    
    validator = GovernanceValidator(ssid_root)
    success = validator.validate_all_roots()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
