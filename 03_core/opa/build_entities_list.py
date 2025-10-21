#!/usr/bin/env python3
"""
Sanctions List Builder - Downloads and processes sanctions data from multiple sources

This script:
1. Downloads sanctions lists from OFAC, EU, and UN
2. Parses XML data into normalized format
3. Generates entities_to_check.json for OPA policy enforcement
4. Updates sources.yaml with SHA256 hashes for integrity verification
5. Implements freshness checks per SSID compliance requirements

Usage:
    python build_entities_list.py [--force] [--verbose]

Output:
    - entities_to_check.json: Normalized list of sanctioned entities
    - sources.yaml: Updated with new hashes and timestamps
"""

import argparse
import hashlib
import json
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

try:
    import requests
    import xml.etree.ElementTree as ET
except ImportError:
    print("ERROR: Required dependencies not installed")
    print("Run: pip install requests")
    sys.exit(1)


class SanctionsListBuilder:
    """Builds unified sanctions list from multiple sources"""

    def __init__(self, sources_file: Path, output_file: Path, verbose: bool = False):
        self.sources_file = sources_file
        self.output_file = output_file
        self.verbose = verbose
        self.entities: Set[str] = set()

    def log(self, message: str):
        """Print message if verbose mode enabled"""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def load_sources(self) -> Dict:
        """Load sources configuration"""
        self.log(f"Loading sources from {self.sources_file}")
        with open(self.sources_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def download_and_hash(self, url: str) -> tuple[bytes, str]:
        """Download content and calculate SHA256 hash"""
        self.log(f"Downloading {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        content = response.content
        sha256 = hashlib.sha256(content).hexdigest()

        self.log(f"Downloaded {len(content)} bytes, SHA256: {sha256[:16]}...")
        return content, sha256

    def parse_ofac_sdn(self, xml_content: bytes):
        """Parse OFAC SDN XML format"""
        self.log("Parsing OFAC SDN list")
        root = ET.fromstring(xml_content)

        # OFAC SDN XML structure varies, this is a simplified parser
        for entry in root.findall('.//sdnEntry'):
            name_elem = entry.find('.//lastName')
            if name_elem is not None and name_elem.text:
                self.entities.add(name_elem.text.strip().upper())

            first_name = entry.find('.//firstName')
            if first_name is not None and first_name.text:
                self.entities.add(first_name.text.strip().upper())

        self.log(f"Parsed {len(self.entities)} OFAC entities")

    def parse_eu_consolidated(self, xml_content: bytes):
        """Parse EU consolidated list XML format"""
        self.log("Parsing EU consolidated list")
        root = ET.fromstring(xml_content)

        # EU XML structure - find all name elements
        for name in root.findall('.//*[@name]'):
            entity_name = name.get('name')
            if entity_name:
                self.entities.add(entity_name.strip().upper())

        for wholename in root.findall('.//wholeName'):
            if wholename.text:
                self.entities.add(wholename.text.strip().upper())

        self.log(f"Total entities after EU: {len(self.entities)}")

    def parse_un_consolidated(self, xml_content: bytes):
        """Parse UN consolidated list XML format"""
        self.log("Parsing UN consolidated list")
        root = ET.fromstring(xml_content)

        # UN XML structure
        for individual in root.findall('.//INDIVIDUAL'):
            first = individual.find('.//FIRST_NAME')
            second = individual.find('.//SECOND_NAME')

            if first is not None and first.text:
                self.entities.add(first.text.strip().upper())
            if second is not None and second.text:
                self.entities.add(second.text.strip().upper())

        self.log(f"Total entities after UN: {len(self.entities)}")

    def build(self, force: bool = False) -> Dict:
        """Build entities list from all sources"""
        sources_config = self.load_sources()

        # Check freshness
        if not force:
            last_updated = datetime.strptime(sources_config['last_updated'], '%Y-%m-%d %H:%M:%S')
            age_hours = (datetime.now() - last_updated).total_seconds() / 3600
            max_age = sources_config['freshness_policy']['max_age_hours']

            if age_hours < max_age:
                self.log(f"Data is fresh ({age_hours:.1f}h < {max_age}h), skipping download")
                if self.output_file.exists():
                    with open(self.output_file, 'r', encoding='utf-8') as f:
                        return json.load(f)

        # Download and process each source
        for source in sources_config['sources']:
            try:
                content, sha256 = self.download_and_hash(source['url'])
                source['sha256'] = sha256
                source['last_fetched'] = datetime.now().strftime('%Y-%m-%d')

                # Parse based on source type
                if source['name'] == 'ofac_sdn':
                    self.parse_ofac_sdn(content)
                elif source['name'] == 'eu_consolidated':
                    self.parse_eu_consolidated(content)
                elif source['name'] == 'un_consolidated':
                    self.parse_un_consolidated(content)

            except Exception as e:
                self.log(f"ERROR processing {source['name']}: {e}")
                continue

        # Generate output
        output_data = {
            'version': '1.0.0',
            'generated_at': datetime.now().isoformat(),
            'total_entities': len(self.entities),
            'sources': [s['name'] for s in sources_config['sources']],
            'entities': sorted(list(self.entities))
        }

        # Save entities list
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        # Update sources.yaml
        sources_config['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.sources_file, 'w', encoding='utf-8') as f:
            yaml.dump(sources_config, f, default_flow_style=False, allow_unicode=True)

        self.log(f"Saved {len(self.entities)} entities to {self.output_file}")
        return output_data


def main():
    parser = argparse.ArgumentParser(description='Build sanctions entities list')
    parser.add_argument('--force', action='store_true', help='Force rebuild even if data is fresh')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    sources_file = script_dir / 'sources.yaml'
    output_file = script_dir / 'entities_to_check.json'

    if not sources_file.exists():
        print(f"ERROR: {sources_file} not found")
        sys.exit(1)

    builder = SanctionsListBuilder(sources_file, output_file, verbose=args.verbose)

    try:
        result = builder.build(force=args.force)
        print(f"SUCCESS: Generated {result['total_entities']} entities")
        print(f"Output: {output_file}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
