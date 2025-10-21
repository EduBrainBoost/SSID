#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yaml_deduplication_analyzer.py - YAML Structural Equivalence Detector
Author: edubrainboost ©2025 MIT License

Analyzes 26,000+ YAML files to detect semantic equivalence despite
syntactic variation. Uses merkle hashing for structural fingerprints.

Problem:
    - 408 chart.yaml files (one per shard)
    - 384 values.yaml files (one per shard)
    - 384 deployment.yaml files (one per shard)
    - Many are structurally identical with only metadata differences

Solution:
    1. Parse YAML to normalized AST
    2. Extract "variable" fields (names, IDs, paths)
    3. Generate "template hash" from invariant structure
    4. Group files by template hash (semantic equivalence)
    5. Generate consolidation recommendations

Usage:
    python 12_tooling/quality/yaml_deduplication_analyzer.py
"""

import sys
import hashlib
import json
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict
import re


class YAMLDeduplicationAnalyzer:
    """Analyze YAML files for structural equivalence."""

    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[2]

        self.root = root_dir
        self.output_dir = root_dir / "12_tooling" / "quality" / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Analysis results
        self.yaml_files = []
        self.template_groups = defaultdict(list)
        self.variable_patterns = {}

    def scan_yaml_files(self, exclude_backups: bool = True) -> List[Path]:
        """
        Scan repository for YAML files.

        Args:
            exclude_backups: Skip backup directories

        Returns:
            List of YAML file paths
        """
        print("Scanning for YAML files...")

        patterns = ["**/*.yaml", "**/*.yml"]
        yaml_files = []

        for pattern in patterns:
            for file_path in self.root.rglob(pattern):
                # Skip backups if requested
                if exclude_backups and "backups" in file_path.parts:
                    continue

                # Skip hidden directories
                if any(part.startswith(".") for part in file_path.parts):
                    continue

                yaml_files.append(file_path)

        self.yaml_files = sorted(yaml_files)
        print(f"Found {len(self.yaml_files)} YAML files")
        return self.yaml_files

    def normalize_yaml_structure(self, data: Any, path: str = "") -> str:
        """
        Normalize YAML structure for template comparison.

        Replaces variable values with placeholders:
        - Shard IDs: "01" → "${SHARD_ID}"
        - Shard names: "identitaet_personen" → "${SHARD_NAME}"
        - Paths: "01_ai_layer/shards/..." → "${LAYER}/${SHARDS}/..."
        - Versions: "1.0.0" → "${VERSION}"

        Args:
            data: Parsed YAML data
            path: Current path in structure (for tracking)

        Returns:
            Normalized JSON string representation
        """
        if isinstance(data, dict):
            normalized = {}
            for key, value in sorted(data.items()):
                norm_key = self._normalize_key(key)
                norm_value = self.normalize_yaml_structure(value, f"{path}.{key}")
                normalized[norm_key] = norm_value
            return normalized

        elif isinstance(data, list):
            return [self.normalize_yaml_structure(item, f"{path}[]") for item in data]

        elif isinstance(data, str):
            return self._normalize_string_value(data, path)

        else:
            return data

    def _normalize_key(self, key: str) -> str:
        """Normalize dictionary keys."""
        # Keep keys as-is for structural comparison
        return key

    def _normalize_string_value(self, value: str, path: str) -> str:
        """
        Normalize string values by replacing variable content.

        Args:
            value: String value
            path: Path in YAML structure

        Returns:
            Normalized value with placeholders
        """
        # Shard ID pattern: "01", "02", etc.
        if re.match(r'^\d{2}$', value):
            return "${SHARD_ID}"

        # Shard name pattern: "identitaet_personen", "dokumente_nachweise"
        if re.match(r'^[a-z_]+$', value) and "_" in value:
            # Check if it looks like a shard name
            if any(part in value for part in ["identitaet", "dokumente", "zugang", "kommunikation",
                                               "gesundheit", "bildung", "familie", "mobilitaet",
                                               "arbeit", "finanzen", "versicherungen", "immobilien",
                                               "unternehmen", "vertraege", "handel", "behoerden"]):
                return "${SHARD_NAME}"

        # Layer path pattern: "01_ai_layer", "02_audit_logging"
        if re.match(r'^\d{2}_[a-z_]+$', value):
            return "${LAYER}"

        # Full path pattern
        if "/" in value or "\\" in value:
            # Replace specific path segments
            normalized = value
            normalized = re.sub(r'\d{2}_[a-z_]+', '${LAYER}', normalized)
            normalized = re.sub(r'shards/\d{2}_[a-z_]+', 'shards/${SHARD}', normalized)
            return normalized

        # Version pattern: "1.0.0", "v1.2.3"
        if re.match(r'^v?\d+\.\d+\.\d+', value):
            return "${VERSION}"

        # Port numbers
        if re.match(r'^\d{4,5}$', value):
            return "${PORT}"

        # Keep other values
        return value

    def compute_template_hash(self, normalized_structure: Any) -> str:
        """
        Compute merkle-style hash of normalized structure.

        Args:
            normalized_structure: Normalized YAML structure

        Returns:
            SHA-256 hash hex string
        """
        # Convert to deterministic JSON
        json_str = json.dumps(normalized_structure, sort_keys=True, separators=(',', ':'))

        # Compute SHA-256
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def analyze_file(self, file_path: Path) -> Optional[Dict]:
        """
        Analyze single YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Analysis result dict or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data is None:
                return None

            # Normalize structure
            normalized = self.normalize_yaml_structure(data)

            # Compute template hash
            template_hash = self.compute_template_hash(normalized)

            # Extract variable values
            variables = self._extract_variables(data)

            return {
                "file_path": str(file_path.relative_to(self.root)),
                "template_hash": template_hash,
                "variables": variables,
                "size_bytes": file_path.stat().st_size,
                "line_count": len(file_path.read_text(encoding='utf-8').splitlines())
            }

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def _extract_variables(self, data: Any) -> Dict[str, Any]:
        """
        Extract variable values from YAML data.

        Returns:
            Dict of detected variables
        """
        variables = {}

        def extract_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    extract_recursive(value, f"{prefix}.{key}" if prefix else key)
            elif isinstance(obj, str):
                # Extract shard IDs
                if re.match(r'^\d{2}$', obj):
                    variables.setdefault("shard_ids", set()).add(obj)
                # Extract layer names
                if re.match(r'^\d{2}_[a-z_]+$', obj):
                    variables.setdefault("layers", set()).add(obj)

        extract_recursive(data)

        # Convert sets to lists for JSON serialization
        return {k: sorted(list(v)) if isinstance(v, set) else v
                for k, v in variables.items()}

    def analyze_all_files(self):
        """Analyze all YAML files and group by template hash."""
        print()
        print("Analyzing YAML structures...")

        for i, file_path in enumerate(self.yaml_files):
            if i % 100 == 0:
                print(f"  Processed {i}/{len(self.yaml_files)} files...")

            result = self.analyze_file(file_path)
            if result:
                template_hash = result["template_hash"]
                self.template_groups[template_hash].append(result)

        print(f"  Processed {len(self.yaml_files)}/{len(self.yaml_files)} files")
        print()
        print(f"Found {len(self.template_groups)} unique templates")

    def generate_deduplication_report(self) -> Dict:
        """
        Generate deduplication analysis report.

        Returns:
            Report dict with statistics and recommendations
        """
        # Calculate statistics
        total_files = len(self.yaml_files)
        unique_templates = len(self.template_groups)

        # Find templates with most duplicates
        template_stats = []
        for template_hash, files in self.template_groups.items():
            if len(files) > 1:
                # Calculate potential savings
                total_size = sum(f["size_bytes"] for f in files)
                total_lines = sum(f["line_count"] for f in files)

                # Keep one instance, consolidate others
                saved_size = total_size - files[0]["size_bytes"]
                saved_lines = total_lines - files[0]["line_count"]

                template_stats.append({
                    "template_hash": template_hash[:16] + "...",
                    "duplicate_count": len(files),
                    "example_files": [f["file_path"] for f in files[:5]],
                    "total_size_kb": total_size / 1024,
                    "saved_size_kb": saved_size / 1024,
                    "saved_lines": saved_lines,
                    "duplication_rate": (len(files) - 1) / len(files) * 100
                })

        # Sort by potential savings
        template_stats.sort(key=lambda x: x["saved_size_kb"], reverse=True)

        # Calculate totals
        total_saved_kb = sum(t["saved_size_kb"] for t in template_stats)
        total_saved_lines = sum(t["saved_lines"] for t in template_stats)

        # Calculate deduplication efficiency
        dedup_efficiency = (1 - unique_templates / total_files) * 100 if total_files > 0 else 0

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "analysis_scope": {
                "total_yaml_files": total_files,
                "unique_templates": unique_templates,
                "duplicate_templates": len(template_stats),
                "deduplication_efficiency_pct": round(dedup_efficiency, 2)
            },
            "savings_potential": {
                "total_saved_kb": round(total_saved_kb, 2),
                "total_saved_lines": total_saved_lines,
                "average_duplication_rate_pct": round(
                    sum(t["duplication_rate"] for t in template_stats) / len(template_stats)
                    if template_stats else 0, 2
                )
            },
            "top_duplication_patterns": template_stats[:20],
            "consolidation_recommendations": self._generate_recommendations(template_stats)
        }

        return report

    def _generate_recommendations(self, template_stats: List[Dict]) -> List[Dict]:
        """
        Generate consolidation recommendations.

        Args:
            template_stats: List of template statistics

        Returns:
            List of recommendations
        """
        recommendations = []

        for i, stat in enumerate(template_stats[:10]):
            # Analyze file patterns
            example_files = stat["example_files"]
            common_pattern = self._detect_common_pattern(example_files)

            priority = "HIGH" if stat["duplicate_count"] > 100 else \
                      "MEDIUM" if stat["duplicate_count"] > 10 else "LOW"

            recommendations.append({
                "id": f"yaml_dedup_{i+1}",
                "priority": priority,
                "pattern": common_pattern,
                "duplicate_count": stat["duplicate_count"],
                "potential_savings_kb": round(stat["saved_size_kb"], 2),
                "approach": self._recommend_approach(common_pattern, stat),
                "example_files": example_files
            })

        return recommendations

    def _detect_common_pattern(self, file_paths: List[str]) -> str:
        """
        Detect common pattern in file paths.

        Args:
            file_paths: List of file paths

        Returns:
            Pattern description
        """
        # Check for shard pattern
        if all("shards" in path for path in file_paths):
            # Extract filename
            filenames = [Path(p).name for p in file_paths]
            if len(set(filenames)) == 1:
                return f"shard/{filenames[0]}"

        # Check for layer pattern
        layers = set()
        for path in file_paths:
            match = re.search(r'(\d{2}_[a-z_]+)', path)
            if match:
                layers.add(match.group(1))

        if len(layers) > 1:
            filename = Path(file_paths[0]).name
            return f"cross-layer/{filename}"

        return "mixed"

    def _recommend_approach(self, pattern: str, stat: Dict) -> str:
        """
        Recommend consolidation approach.

        Args:
            pattern: Detected pattern
            stat: Template statistics

        Returns:
            Recommendation text
        """
        if pattern.startswith("shard/"):
            filename = pattern.split("/")[1]
            return f"Create base template for {filename}, generate per-shard instances via templating engine (Helm/Jinja2)"

        elif pattern.startswith("cross-layer/"):
            return "Extract common template, use layer-specific overlays (Kustomize pattern)"

        else:
            return "Manual review recommended - mixed patterns detected"

    def save_report(self, report: Dict):
        """Save analysis report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"yaml_deduplication_analysis_{timestamp}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"Report saved: {report_file}")
        return report_file

    def print_summary(self, report: Dict):
        """Print analysis summary to console."""
        print()
        print("=" * 70)
        print("YAML Deduplication Analysis")
        print("=" * 70)
        print()

        scope = report["analysis_scope"]
        savings = report["savings_potential"]

        print(f"Total YAML files:        {scope['total_yaml_files']}")
        print(f"Unique templates:        {scope['unique_templates']}")
        print(f"Duplicate templates:     {scope['duplicate_templates']}")
        print(f"Deduplication efficiency: {scope['deduplication_efficiency_pct']:.2f}%")
        print()

        print(f"Potential savings:")
        print(f"  Code size:             {savings['total_saved_kb']:.2f} KB")
        print(f"  Lines of code:         {savings['total_saved_lines']}")
        print(f"  Avg duplication rate:  {savings['average_duplication_rate_pct']:.2f}%")
        print()

        print("Top Duplication Patterns:")
        print()

        for i, pattern in enumerate(report["top_duplication_patterns"][:5], 1):
            print(f"{i}. {pattern['duplicate_count']} duplicates")
            print(f"   Examples: {', '.join(pattern['example_files'][:3])}")
            print(f"   Savings: {pattern['saved_size_kb']:.2f} KB")
            print()

        print("Consolidation Recommendations:")
        print()

        for rec in report["consolidation_recommendations"][:5]:
            print(f"[{rec['priority']}] {rec['pattern']}")
            print(f"  Duplicates: {rec['duplicate_count']}")
            print(f"  Savings: {rec['potential_savings_kb']} KB")
            print(f"  Approach: {rec['approach']}")
            print()


def main():
    """Main execution."""
    analyzer = YAMLDeduplicationAnalyzer()

    # Scan files
    analyzer.scan_yaml_files(exclude_backups=True)

    # Analyze
    analyzer.analyze_all_files()

    # Generate report
    report = analyzer.generate_deduplication_report()

    # Print summary
    analyzer.print_summary(report)

    # Save report
    analyzer.save_report(report)


if __name__ == "__main__":
    main()
