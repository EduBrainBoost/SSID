#!/usr/bin/env python3
"""
Split 5 Original SoT Artefacts at 50KB
=======================================
Splits each of the 5 core SoT artefacts individually at 50KB boundaries.
Maintains original file structure for easy navigation.

Output: 5 directories with auto-split parts
"""

import hashlib
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import json


class SoTArtefactSplitter:
    """Split individual SoT artefacts at 50KB"""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent
        self.max_size_kb = 50
        self.max_size_bytes = self.max_size_kb * 1024

        self.artefacts = [
            {
                'path': '03_core/validators/sot/sot_validator_core.py',
                'name': 'sot_validator_core',
                'type': 'PYTHON'
            },
            {
                'path': '23_compliance/policies/sot/sot_policy.rego',
                'name': 'sot_policy',
                'type': 'REGO'
            },
            {
                'path': '16_codex/contracts/sot/sot_contract.yaml',
                'name': 'sot_contract',
                'type': 'YAML'
            },
            {
                'path': '12_tooling/cli/sot_validator.py',
                'name': 'sot_validator_cli',
                'type': 'PYTHON'
            },
            {
                'path': '11_test_simulation/tests_compliance/test_sot_validator.py',
                'name': 'test_sot_validator',
                'type': 'PYTHON'
            }
        ]

    def generate_header(self, artefact_name: str, part_num: int, total_parts: int) -> str:
        """Generate header for split part"""
        return f"""# SSID SoT Artefact Split - {artefact_name}
# Root-24-LOCK enforced | Auto-Split at 50KB
# Part: {part_num} of {total_parts}
# Generated: {datetime.now().isoformat()}
# Max size per part: {self.max_size_kb} KB
# ============================================================

"""

    def split_content(self, content: str) -> List[str]:
        """Split content into parts at 50KB boundaries"""
        parts = []
        current_part = ""
        lines = content.split('\n')

        for line in lines:
            # Check if adding this line would exceed max size
            if len(current_part.encode('utf-8')) + len(line.encode('utf-8')) + 1 > self.max_size_bytes:
                if current_part:
                    parts.append(current_part)
                    current_part = line + '\n'
            else:
                current_part += line + '\n'

        # Add last part
        if current_part:
            parts.append(current_part)

        return parts

    def calculate_sha256(self, content: str) -> str:
        """Calculate SHA256 hash"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def split_artefact(self, artefact: Dict) -> Dict:
        """Split single artefact and return metadata"""
        file_path = self.repo_root / artefact['path']

        if not file_path.exists():
            print(f"  ERROR: File not found: {artefact['path']}")
            return None

        # Load content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_size = len(content.encode('utf-8')) / 1024

        # Split content
        parts = self.split_content(content)

        # Create output directory
        output_dir = self.repo_root / f"SOT_ARTEFACTS_SPLIT/{artefact['name']}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write parts
        part_metadata = []
        for i, part_content in enumerate(parts, 1):
            # Add header
            full_part = self.generate_header(artefact['name'], i, len(parts)) + part_content

            # Write file
            extension = Path(artefact['path']).suffix
            part_filename = f"{artefact['name']}_part{i}{extension}"
            part_path = output_dir / part_filename

            with open(part_path, 'w', encoding='utf-8') as f:
                f.write(full_part)

            # Calculate hash
            part_hash = self.calculate_sha256(full_part)
            part_size = len(full_part.encode('utf-8')) / 1024

            part_metadata.append({
                'part_number': i,
                'filename': part_filename,
                'size_kb': round(part_size, 2),
                'sha256': part_hash,
                'line_count': full_part.count('\n')
            })

        # Write manifest for this artefact
        manifest = {
            'artefact': artefact['name'],
            'original_path': artefact['path'],
            'type': artefact['type'],
            'original_size_kb': round(original_size, 2),
            'split_date': datetime.now().isoformat(),
            'total_parts': len(parts),
            'parts': part_metadata
        }

        manifest_path = output_dir / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        return manifest

    def split_all(self):
        """Split all 5 artefacts"""
        print("="*80)
        print("SoT Artefact Splitter - 50KB Auto-Split")
        print("="*80)

        all_manifests = []

        for i, artefact in enumerate(self.artefacts, 1):
            print(f"\n[{i}/5] Splitting {artefact['name']}...")

            manifest = self.split_artefact(artefact)

            if manifest:
                print(f"  Original: {manifest['original_size_kb']:.2f} KB")
                print(f"  Parts: {manifest['total_parts']}")
                print(f"  Location: SOT_ARTEFACTS_SPLIT/{artefact['name']}/")
                all_manifests.append(manifest)

        # Write master manifest
        print("\nWriting master manifest...")
        master_manifest = {
            'version': '3.2.0',
            'generated': datetime.now().isoformat(),
            'total_artefacts': len(all_manifests),
            'artefacts': all_manifests
        }

        master_path = self.repo_root / 'SOT_ARTEFACTS_SPLIT/master_manifest.json'
        with open(master_path, 'w', encoding='utf-8') as f:
            json.dump(master_manifest, f, indent=2)

        print(f"  [OK] {master_path}")

        print("\n" + "="*80)
        print("SPLIT COMPLETE")
        print("="*80)
        print(f"Total artefacts split: {len(all_manifests)}")
        print(f"Total parts generated: {sum(m['total_parts'] for m in all_manifests)}")
        print(f"Output directory: SOT_ARTEFACTS_SPLIT/")
        print("="*80)


def main():
    splitter = SoTArtefactSplitter()
    splitter.split_all()


if __name__ == "__main__":
    main()
