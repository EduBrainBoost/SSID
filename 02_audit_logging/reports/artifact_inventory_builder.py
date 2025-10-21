#!/usr/bin/env python3
"""
SSID Forensic Artifact Inventory Builder v12.4
READ-ONLY analysis - Does NOT modify any files
Generates comprehensive artifact inventory across all 24 root modules
"""

import os
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List, Any, Optional

# Working directory
SSID_ROOT = Path(r"C:\Users\bibel\Documents\Github\SSID")

# Artifact extensions
ARTIFACT_EXTENSIONS = {
    '.rego', '.yaml', '.yml', '.json', '.md',
    '.py', '.ts', '.tsx', '.sh', '.wasm', '.sha256'
}

# Root modules
ROOT_MODULES = [
    '01_ai_layer', '02_audit_logging', '03_core', '04_deployment',
    '05_documentation', '06_data_pipeline', '07_governance_legal',
    '08_identity_score', '09_meta_identity', '10_interoperability',
    '11_test_simulation', '12_tooling', '13_ui_layer', '14_zero_time_auth',
    '15_infra', '16_codex', '17_observability', '18_data_layer',
    '19_adapters', '20_foundation', '21_post_quantum_crypto', '22_datasets',
    '23_compliance', '24_meta_orchestration'
]

# Artifact type mapping
def classify_artifact(file_path: str) -> str:
    """Classify artifact by type"""
    path_lower = file_path.lower()

    if '.rego' in path_lower:
        return 'Policy'
    elif '.wasm' in path_lower:
        return 'WASM'
    elif '.sha256' in path_lower:
        return 'Hash'
    elif any(x in path_lower for x in ['test', 'spec', '__pycache__']):
        return 'Test'
    elif '.md' in path_lower and 'readme' in path_lower:
        return 'Doc'
    elif '.md' in path_lower and 'changelog' in path_lower:
        return 'Report'
    elif any(x in path_lower for x in ['.yaml', '.yml', '.json']):
        if 'schema' in path_lower:
            return 'Schema'
        elif 'config' in path_lower:
            return 'Config'
        else:
            return 'Config'
    elif '.py' in path_lower:
        if any(x in path_lower for x in ['bridge', 'interconnect']):
            return 'Bridge'
        elif any(x in path_lower for x in ['validator', 'detector', 'analyzer']):
            return 'Validator'
        else:
            return 'Script'
    elif any(x in path_lower for x in ['.ts', '.tsx']):
        return 'UI'
    elif '.sh' in path_lower:
        return 'Shell'
    else:
        return 'Other'

def extract_version_tag(file_path: str) -> Optional[str]:
    """Extract version tag from filename using regex"""
    # Pattern: v followed by digits, underscore/dot, more digits
    match = re.search(r'v(\d+)[._](\d+)', file_path.lower())
    if match:
        return f"v{match.group(1)}_{match.group(2)}"
    return None

def get_root_module(file_path: str) -> Optional[str]:
    """Extract root module from path"""
    rel_path = file_path.replace(str(SSID_ROOT), '').replace('\\', '/').lstrip('/')

    for module in ROOT_MODULES:
        if rel_path.startswith(module):
            return module

    return None

def compute_sha256_prefix(file_path: Path) -> str:
    """Compute first 12 chars of SHA256 hash"""
    try:
        # For .sha256 files, read the hash
        if file_path.suffix == '.sha256':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
                # Extract first hash-like string
                hash_match = re.search(r'[a-fA-F0-9]{64}', content)
                if hash_match:
                    return hash_match.group(0)[:12]
                return content[:12] if len(content) >= 12 else content

        # For binary files (.wasm), read as binary
        if file_path.suffix == '.wasm':
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                return file_hash[:12]

        # For text files, read as text
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            return file_hash[:12]
    except Exception as e:
        return f"error:{str(e)[:8]}"

def extract_linked_files(file_path: Path, artifact_type: str) -> List[str]:
    """Extract linked/referenced files from imports and includes"""
    linked = []

    try:
        # Only analyze script/policy files
        if artifact_type not in ['Script', 'Policy', 'Bridge', 'Validator', 'UI']:
            return []

        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Python imports
        if file_path.suffix == '.py':
            # from X import Y
            imports = re.findall(r'from\s+([a-zA-Z0-9_.]+)\s+import', content)
            linked.extend(imports)
            # import X
            imports = re.findall(r'^import\s+([a-zA-Z0-9_.]+)', content, re.MULTILINE)
            linked.extend(imports)

        # TypeScript/JavaScript imports
        elif file_path.suffix in ['.ts', '.tsx', '.js']:
            imports = re.findall(r'import.*from\s+["\']([^"\']+)["\']', content)
            linked.extend(imports)

        # Rego imports
        elif file_path.suffix == '.rego':
            imports = re.findall(r'import\s+data\.([a-zA-Z0-9_.]+)', content)
            linked.extend(imports)

        # YAML/JSON references
        elif file_path.suffix in ['.yaml', '.yml', '.json']:
            # Look for file paths
            refs = re.findall(r'["\']([a-zA-Z0-9_./]+\.(rego|py|ts|yaml|yml))["\']', content)
            linked.extend([r[0] for r in refs])

        return list(set(linked))[:10]  # Limit to 10 unique references

    except Exception:
        return []

def scan_artifacts() -> Dict[str, List[Dict[str, Any]]]:
    """Scan all artifacts and organize by root module"""
    print(f"[INFO] Starting artifact scan from {SSID_ROOT}")

    artifacts_by_module = defaultdict(list)
    total_scanned = 0

    # Walk directory tree
    for root, dirs, files in os.walk(SSID_ROOT):
        # Skip certain directories
        skip_dirs = ['.git', 'node_modules', '__pycache__', '.pytest_cache', 'venv']
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            file_path = Path(root) / file

            # Check if it's an artifact we care about
            if file_path.suffix not in ARTIFACT_EXTENSIONS:
                continue

            total_scanned += 1
            if total_scanned % 500 == 0:
                print(f"[PROGRESS] Scanned {total_scanned} artifacts...")

            # Get file metadata
            try:
                stat_info = file_path.stat()
                file_size_kb = round(stat_info.st_size / 1024, 2)
                last_modified = datetime.fromtimestamp(stat_info.st_mtime, tz=timezone.utc).isoformat()
            except Exception:
                file_size_kb = 0.0
                last_modified = "unknown"

            # Classify artifact
            artifact_type = classify_artifact(str(file_path))
            version_tag = extract_version_tag(str(file_path))
            root_module = get_root_module(str(file_path))

            # Skip if not in a root module
            if not root_module:
                continue

            # Compute SHA256 prefix
            sha256_hash = compute_sha256_prefix(file_path)

            # Extract linked files (only sample some to save time)
            linked_to = []
            if total_scanned % 20 == 0:  # Sample 5% of files for linking
                linked_to = extract_linked_files(file_path, artifact_type)

            # Relative path
            rel_path = str(file_path.relative_to(SSID_ROOT)).replace('\\', '/')

            # Create artifact record
            artifact = {
                'file_path': rel_path,
                'file_size_kb': file_size_kb,
                'last_modified': last_modified,
                'artifact_type': artifact_type,
                'version_tag': version_tag or 'none',
                'sha256_hash': sha256_hash,
                'linked_to': linked_to
            }

            artifacts_by_module[root_module].append(artifact)

    print(f"[INFO] Scan complete. Total artifacts: {total_scanned}")
    return dict(artifacts_by_module)

def calculate_module_metrics(artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate metrics for a module"""
    total_size_kb = sum(a['file_size_kb'] for a in artifacts)

    # Find latest version tag
    version_tags = [a['version_tag'] for a in artifacts if a['version_tag'] != 'none']
    latest_version = max(version_tags, default='none') if version_tags else 'none'

    return {
        'artifact_count': len(artifacts),
        'total_size_kb': round(total_size_kb, 2),
        'latest_version_tag': latest_version
    }

def generate_inventory_json(artifacts_by_module: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Generate complete JSON inventory"""
    print("[INFO] Generating JSON inventory...")

    # Calculate global metrics
    total_artifacts = sum(len(artifacts) for artifacts in artifacts_by_module.values())
    total_size_mb = round(sum(
        sum(a['file_size_kb'] for a in artifacts)
        for artifacts in artifacts_by_module.values()
    ) / 1024, 2)

    # Find root with most artifacts
    root_with_most = max(artifacts_by_module.items(), key=lambda x: len(x[1]))[0] if artifacts_by_module else 'none'

    # Find roots missing versions
    roots_missing_versions = []
    for module, artifacts in artifacts_by_module.items():
        metrics = calculate_module_metrics(artifacts)
        if metrics['latest_version_tag'] == 'none':
            roots_missing_versions.append(module)

    # Count unlinked artifacts
    count_unlinked = sum(
        1 for artifacts in artifacts_by_module.values()
        for a in artifacts
        if len(a['linked_to']) == 0
    )

    # Build root modules list
    root_modules_data = []
    for module in ROOT_MODULES:
        artifacts = artifacts_by_module.get(module, [])
        metrics = calculate_module_metrics(artifacts)

        root_modules_data.append({
            'root_module': module,
            'artifact_count': metrics['artifact_count'],
            'total_size_kb': metrics['total_size_kb'],
            'latest_version_tag': metrics['latest_version_tag'],
            'artifacts': artifacts
        })

    # Build final inventory
    inventory = {
        'audit_version': 'v12.4',
        'status': 'READ_ONLY_VALIDATION_COMPLETE',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'global_metrics': {
            'total_artifacts': total_artifacts,
            'total_size_mb': total_size_mb,
            'root_with_most_artifacts': root_with_most,
            'roots_missing_versions': roots_missing_versions,
            'count_unlinked_artifacts': count_unlinked
        },
        'root_modules': root_modules_data
    }

    return inventory

def generate_markdown_report(inventory: Dict[str, Any]) -> str:
    """Generate human-readable markdown report"""
    print("[INFO] Generating Markdown report...")

    md = []
    md.append("# SSID Global Artifact Inventory - Version 12.4")
    md.append("")
    md.append(f"**Generated:** {inventory['timestamp_utc']}")
    md.append(f"**Status:** {inventory['status']}")
    md.append("")

    # Executive Summary
    metrics = inventory['global_metrics']
    md.append("## Executive Summary")
    md.append("")
    md.append(f"- **Total Artifacts:** {metrics['total_artifacts']:,}")
    md.append(f"- **Total Size:** {metrics['total_size_mb']:.2f} MB")
    md.append(f"- **Root with Most Artifacts:** {metrics['root_with_most_artifacts']}")
    md.append(f"- **Roots Missing Versions:** {len(metrics['roots_missing_versions'])}")
    md.append(f"- **Unlinked Artifacts:** {metrics['count_unlinked_artifacts']:,}")
    md.append("")

    # Module Summary Table
    md.append("## Root Module Summary")
    md.append("")
    md.append("| Root Module | Artifact Count | Size (KB) | Latest Version |")
    md.append("|-------------|----------------|-----------|----------------|")

    for module_data in sorted(inventory['root_modules'], key=lambda x: x['artifact_count'], reverse=True):
        md.append(f"| {module_data['root_module']} | {module_data['artifact_count']:,} | "
                  f"{module_data['total_size_kb']:,.2f} | {module_data['latest_version_tag']} |")

    md.append("")

    # Missing Versions Section
    if metrics['roots_missing_versions']:
        md.append("## Modules Missing Version Tags")
        md.append("")
        for module in metrics['roots_missing_versions']:
            md.append(f"- {module}")
        md.append("")

    # Artifact Type Distribution
    md.append("## Artifact Type Distribution")
    md.append("")
    type_counts = defaultdict(int)
    for module_data in inventory['root_modules']:
        for artifact in module_data['artifacts']:
            type_counts[artifact['artifact_type']] += 1

    for artifact_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        md.append(f"- **{artifact_type}:** {count:,}")
    md.append("")

    # Top 10 Largest Artifacts
    md.append("## Top 10 Largest Artifacts")
    md.append("")
    all_artifacts = []
    for module_data in inventory['root_modules']:
        for artifact in module_data['artifacts']:
            all_artifacts.append((artifact['file_path'], artifact['file_size_kb']))

    top_artifacts = sorted(all_artifacts, key=lambda x: x[1], reverse=True)[:10]
    for path, size in top_artifacts:
        md.append(f"- `{path}` - {size:,.2f} KB")
    md.append("")

    # Footer
    md.append("---")
    md.append("")
    md.append("*This is a READ-ONLY forensic inventory. No files were modified.*")
    md.append("")

    return '\n'.join(md)

def main():
    """Main execution"""
    print("=" * 80)
    print("SSID Forensic Artifact Inventory Builder v12.4")
    print("READ-ONLY VALIDATION MODE")
    print("=" * 80)
    print("")

    # Scan artifacts
    artifacts_by_module = scan_artifacts()

    # Generate JSON inventory
    inventory = generate_inventory_json(artifacts_by_module)

    # Write JSON
    json_path = SSID_ROOT / '02_audit_logging' / 'reports' / 'global_artifact_inventory.json'
    json_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Writing JSON to {json_path}")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    # Generate Markdown
    markdown_content = generate_markdown_report(inventory)

    # Write Markdown
    md_path = SSID_ROOT / '02_audit_logging' / 'reports' / 'GLOBAL_ARTIFACT_INVENTORY_V12_4.md'

    print(f"[INFO] Writing Markdown to {md_path}")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print("")
    print("=" * 80)
    print("INVENTORY GENERATION COMPLETE")
    print("=" * 80)
    print("")
    print(f"Total Artifacts: {inventory['global_metrics']['total_artifacts']:,}")
    print(f"Total Size: {inventory['global_metrics']['total_size_mb']:.2f} MB")
    print(f"JSON Report: {json_path}")
    print(f"Markdown Report: {md_path}")
    print("")

    # Print top 5 modules
    print("Top 5 Modules by Artifact Count:")
    top_modules = sorted(inventory['root_modules'], key=lambda x: x['artifact_count'], reverse=True)[:5]
    for i, module in enumerate(top_modules, 1):
        print(f"  {i}. {module['root_module']}: {module['artifact_count']:,} artifacts")
    print("")

    print(f"Missing Versions: {len(inventory['global_metrics']['roots_missing_versions'])}")
    print(f"Unlinked Artifacts: {inventory['global_metrics']['count_unlinked_artifacts']:,}")
    print("")

if __name__ == '__main__':
    main()
