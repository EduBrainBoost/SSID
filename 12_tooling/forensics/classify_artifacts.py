#!/usr/bin/env python3
"""
SSID Forensic Artifact Classification v12.4
Classifies all artifacts from inventory by type, origin, and relevance.

Usage:
    python classify_artifacts.py --source <inventory.json> --output-json <output.json> --output-md <output.md>
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple


class ArtifactClassifier:
    """Classifies artifacts from forensic inventory."""

    # Category definitions
    CATEGORIES = {
        'POLICIES': ['.rego'],
        'MODELS': ['.yaml', '.yml'],
        'REPORTS': ['.md'],
        'CODE': ['.py', '.ts', '.tsx', '.sh'],
        'WASM': ['.wasm'],
        'HASH': ['.sha256'],
        'SCHEMA': ['.json'],
        'CONFIG': ['.yaml', '.yml', '.json'],
        'MISC': []
    }

    # Patterns for generated/temporary artifacts
    GENERATED_PATTERNS = [
        '/backups/',
        '/reports/',
        '/.pytest_cache/',
        '/node_modules/',
        '/__pycache__/',
        '/dist/',
        '/build/',
        '.pyc',
        '.log',
        '.tmp',
        '_generated',
        'quarantine'
    ]

    def __init__(self, inventory_path: str):
        self.inventory_path = Path(inventory_path)
        self.data = None
        self.extensions = Counter()
        self.extension_sizes = defaultdict(list)
        self.all_artifacts = []
        self.category_stats = defaultdict(lambda: {'count': 0, 'size_kb': 0, 'files': []})

    def load_inventory(self) -> bool:
        """Load and parse the artifact inventory JSON."""
        try:
            print(f"[INFO] Loading inventory: {self.inventory_path}")
            with open(self.inventory_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            total = self.data.get('global_metrics', {}).get('total_artifacts', 0)
            print(f"[OK] Loaded inventory: {total:,} total artifacts")
            return True
        except FileNotFoundError:
            print(f"[ERROR] Inventory file not found: {self.inventory_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in inventory: {e}")
            return False

    def classify_all_artifacts(self):
        """Classify all artifacts by extension and category."""
        print("[INFO] Classifying artifacts...")

        for module in self.data.get('root_modules', []):
            for artifact in module.get('artifacts', []):
                file_path = artifact.get('file_path', '')
                file_size = artifact.get('file_size_kb', 0)

                # Extract extension
                ext = Path(file_path).suffix.lower()
                if not ext:
                    ext = '.none'

                self.extensions[ext] += 1
                self.extension_sizes[ext].append(file_size)

                # Store artifact with classification
                artifact_data = {
                    'path': file_path,
                    'size_kb': file_size,
                    'ext': ext,
                    'root_module': file_path.split('/')[0] if '/' in file_path else 'unknown',
                    'artifact_type': artifact.get('artifact_type', 'Unknown'),
                    'is_generated': self._is_generated(file_path)
                }
                self.all_artifacts.append(artifact_data)

                # Categorize
                category = self._get_category(file_path, ext)
                self.category_stats[category]['count'] += 1
                self.category_stats[category]['size_kb'] += file_size
                self.category_stats[category]['files'].append(artifact_data)

        print(f"[OK] Classified {len(self.all_artifacts):,} artifacts")
        print(f"[OK] Found {len(self.extensions)} unique file extensions")

    def _is_generated(self, file_path: str) -> bool:
        """Check if artifact is likely generated or temporary."""
        return any(pattern in file_path for pattern in self.GENERATED_PATTERNS)

    def _get_category(self, file_path: str, ext: str) -> str:
        """Determine artifact category."""
        # Special case: JSON can be schema or config
        if ext == '.json':
            if '/schemas/' in file_path or 'schema.json' in file_path:
                return 'SCHEMA'
            elif '/reports/' in file_path or 'report' in file_path.lower():
                return 'REPORTS'
            else:
                return 'CONFIG'

        # Check each category
        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                if category == 'MODELS' and ext in ['.yaml', '.yml']:
                    if '/reports/' in file_path:
                        return 'REPORTS'
                    return 'MODELS'
                if category == 'REPORTS':
                    return 'REPORTS'
                return category

        return 'MISC'

    def get_top_largest_files(self, n: int = 10) -> List[Dict]:
        """Get top N largest files."""
        sorted_artifacts = sorted(self.all_artifacts, key=lambda x: x['size_kb'], reverse=True)
        return sorted_artifacts[:n]

    def get_roots_with_anomalies(self, threshold: int = 1000) -> List[Tuple[str, int]]:
        """Find root modules with more than threshold artifacts."""
        root_counts = Counter()
        for artifact in self.all_artifacts:
            root_counts[artifact['root_module']] += 1

        return [(root, count) for root, count in root_counts.most_common() if count >= threshold]

    def estimate_generated_artifacts(self) -> Dict:
        """Estimate temporary/generated artifacts."""
        generated = [a for a in self.all_artifacts if a['is_generated']]
        total = len(self.all_artifacts)

        return {
            'total_generated': len(generated),
            'percentage': (len(generated) / total * 100) if total > 0 else 0,
            'total_size_kb': sum(a['size_kb'] for a in generated),
            'breakdown': Counter(a['root_module'] for a in generated).most_common(10)
        }

    def analyze_80_20_rule(self) -> Dict:
        """Analyze which types cause 80% of artifacts."""
        total = len(self.all_artifacts)
        sorted_exts = self.extensions.most_common()

        cumulative = 0
        types_for_80 = []

        for ext, count in sorted_exts:
            cumulative += count
            types_for_80.append((ext, count, cumulative / total * 100))
            if cumulative / total >= 0.80:
                break

        return {
            'total_artifacts': total,
            'types_for_80_percent': types_for_80,
            'num_types': len(types_for_80)
        }

    def generate_json_report(self, output_path: str):
        """Generate machine-readable JSON classification report."""
        print(f"[INFO] Generating JSON report: {output_path}")

        # Calculate extension stats
        ext_stats = []
        total_artifacts = len(self.all_artifacts)
        for ext, count in self.extensions.most_common():
            sizes = self.extension_sizes[ext]
            ext_stats.append({
                'extension': ext,
                'count': count,
                'percentage': round(count / total_artifacts * 100, 2),
                'total_size_kb': round(sum(sizes), 2),
                'avg_size_kb': round(sum(sizes) / len(sizes), 2) if sizes else 0,
                'min_size_kb': round(min(sizes), 2) if sizes else 0,
                'max_size_kb': round(max(sizes), 2) if sizes else 0
            })

        # Category summary
        category_summary = []
        total_size = self.data.get('global_metrics', {}).get('total_size_mb', 0) * 1024
        for category, stats in sorted(self.category_stats.items()):
            category_summary.append({
                'category': category,
                'count': stats['count'],
                'percentage': round(stats['count'] / total_artifacts * 100, 2),
                'total_size_kb': round(stats['size_kb'], 2),
                'size_percentage': round(stats['size_kb'] / total_size * 100, 2) if total_size > 0 else 0,
                'avg_size_kb': round(stats['size_kb'] / stats['count'], 2) if stats['count'] > 0 else 0
            })

        # Top largest files
        largest_files = [
            {
                'rank': i + 1,
                'path': f['path'],
                'size_kb': round(f['size_kb'], 2),
                'size_mb': round(f['size_kb'] / 1024, 2),
                'root_module': f['root_module'],
                'extension': f['ext']
            }
            for i, f in enumerate(self.get_top_largest_files(10))
        ]

        # Root anomalies
        anomalies = [
            {'root_module': root, 'artifact_count': count}
            for root, count in self.get_roots_with_anomalies(1000)
        ]

        # Generated artifacts
        generated = self.estimate_generated_artifacts()

        # 80/20 analysis
        pareto = self.analyze_80_20_rule()

        report = {
            'audit_version': 'v12.4',
            'status': 'READ_ONLY_CLASSIFICATION_COMPLETE',
            'timestamp_utc': datetime.utcnow().isoformat() + 'Z',
            'summary': {
                'total_artifacts': total_artifacts,
                'total_size_mb': self.data.get('global_metrics', {}).get('total_size_mb', 0),
                'unique_extensions': len(self.extensions),
                'unique_categories': len(self.category_stats)
            },
            'extensions': ext_stats,
            'categories': category_summary,
            'largest_files': largest_files,
            'root_anomalies': anomalies,
            'generated_artifacts': {
                'total': generated['total_generated'],
                'percentage': round(generated['percentage'], 2),
                'total_size_kb': round(generated['total_size_kb'], 2),
                'top_roots': [{'root': r, 'count': c} for r, c in generated['breakdown']]
            },
            'pareto_analysis': {
                'total_artifacts': pareto['total_artifacts'],
                'num_types_for_80_percent': pareto['num_types'],
                'types': [
                    {'extension': ext, 'count': count, 'cumulative_percentage': round(pct, 2)}
                    for ext, count, pct in pareto['types_for_80_percent']
                ]
            }
        }

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"[OK] JSON report written: {output}")
        print(f"     Size: {output.stat().st_size / 1024:.1f} KB")

    def generate_markdown_report(self, output_path: str):
        """Generate human-readable Markdown classification report."""
        print(f"[INFO] Generating Markdown report: {output_path}")

        total_artifacts = len(self.all_artifacts)
        total_size_mb = self.data.get('global_metrics', {}).get('total_size_mb', 0)
        timestamp = datetime.utcnow().isoformat() + 'Z'

        lines = [
            "# SSID Forensic Artifact Classification Report v12.4",
            "",
            f"**Generated:** {timestamp}  ",
            f"**Source:** {self.inventory_path.name}  ",
            f"**Total Artifacts:** {total_artifacts:,}  ",
            f"**Total Size:** {total_size_mb:.2f} MB  ",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"This report classifies all **{total_artifacts:,}** artifacts from the SSID repository inventory.",
            "",
            f"- **Unique File Extensions:** {len(self.extensions)}",
            f"- **Artifact Categories:** {len(self.category_stats)}",
            f"- **Total Repository Size:** {total_size_mb:.2f} MB",
            "",
            "---",
            "",
            "## Artifact Distribution by File Extension",
            "",
            "Top 20 file extensions by count:",
            "",
            "| Rank | Extension | Count | Percentage | Avg Size (KB) | Total Size (MB) |",
            "|------|-----------|-------|------------|---------------|-----------------|"
        ]

        for i, (ext, count) in enumerate(self.extensions.most_common(20), 1):
            sizes = self.extension_sizes[ext]
            avg_size = sum(sizes) / len(sizes) if sizes else 0
            total_size = sum(sizes) / 1024
            pct = count / total_artifacts * 100
            lines.append(f"| {i} | `{ext}` | {count:,} | {pct:.2f}% | {avg_size:.2f} | {total_size:.2f} |")

        # Category breakdown
        lines.extend([
            "",
            "---",
            "",
            "## Artifact Categories",
            "",
            "Artifacts grouped by functional category:",
            "",
            "| Category | Count | Percentage | Total Size (MB) | Size % | Avg Size (KB) |",
            "|----------|-------|------------|-----------------|--------|---------------|"
        ])

        total_size_kb = total_size_mb * 1024
        for category, stats in sorted(self.category_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            count = stats['count']
            size_kb = stats['size_kb']
            size_mb = size_kb / 1024
            pct = count / total_artifacts * 100
            size_pct = size_kb / total_size_kb * 100 if total_size_kb > 0 else 0
            avg_size = size_kb / count if count > 0 else 0
            lines.append(f"| **{category}** | {count:,} | {pct:.2f}% | {size_mb:.2f} | {size_pct:.2f}% | {avg_size:.2f} |")

        # Top 10 largest files
        lines.extend([
            "",
            "---",
            "",
            "## Top 10 Largest Files",
            "",
            "| Rank | File Path | Size (MB) | Root Module | Extension |",
            "|------|-----------|-----------|-------------|-----------|"
        ])

        for i, artifact in enumerate(self.get_top_largest_files(10), 1):
            size_mb = artifact['size_kb'] / 1024
            lines.append(f"| {i} | `{artifact['path']}` | {size_mb:.2f} | {artifact['root_module']} | {artifact['ext']} |")

        # Root modules with anomalies
        anomalies = self.get_roots_with_anomalies(1000)
        lines.extend([
            "",
            "---",
            "",
            f"## Root Modules with >1,000 Artifacts",
            "",
            f"Found **{len(anomalies)}** root modules with anomalously high artifact counts:",
            "",
            "| Root Module | Artifact Count | Percentage |",
            "|-------------|----------------|------------|"
        ])

        for root, count in anomalies:
            pct = count / total_artifacts * 100
            lines.append(f"| `{root}` | {count:,} | {pct:.2f}% |")

        # Generated/temporary artifacts
        generated = self.estimate_generated_artifacts()
        lines.extend([
            "",
            "---",
            "",
            "## Generated/Temporary Artifacts Analysis",
            "",
            f"Artifacts identified as likely generated or temporary:",
            "",
            f"- **Total Generated:** {generated['total_generated']:,} ({generated['percentage']:.2f}%)",
            f"- **Total Size:** {generated['total_size_kb'] / 1024:.2f} MB",
            "",
            "**Top 10 roots contributing generated artifacts:**",
            "",
            "| Rank | Root Module | Generated Count |",
            "|------|-------------|-----------------|"
        ])

        for i, (root, count) in enumerate(generated['breakdown'], 1):
            lines.append(f"| {i} | `{root}` | {count:,} |")

        # 80/20 analysis
        pareto = self.analyze_80_20_rule()
        lines.extend([
            "",
            "---",
            "",
            "## Pareto Analysis (80/20 Rule)",
            "",
            f"**{pareto['num_types']} file types** account for **80%** of all artifacts:",
            "",
            "| Extension | Count | Cumulative % |",
            "|-----------|-------|--------------|"
        ])

        for ext, count, cum_pct in pareto['types_for_80_percent']:
            lines.append(f"| `{ext}` | {count:,} | {cum_pct:.2f}% |")

        # Analysis insights
        lines.extend([
            "",
            "---",
            "",
            "## Key Insights",
            "",
            "### 1. Dominant Artifact Types",
            ""
        ])

        top_3_exts = self.extensions.most_common(3)
        for ext, count in top_3_exts:
            pct = count / total_artifacts * 100
            lines.append(f"- **`{ext}`**: {count:,} files ({pct:.1f}%) - Primary driver of repository size")

        lines.extend([
            "",
            "### 2. Root Module Concentration",
            ""
        ])

        top_root = anomalies[0] if anomalies else ('unknown', 0)
        lines.append(f"- **`{top_root[0]}`** contains {top_root[1]:,} artifacts ({top_root[1]/total_artifacts*100:.1f}% of total)")
        lines.append(f"- This suggests significant backup/report accumulation or redundancy")

        lines.extend([
            "",
            "### 3. Generated Content Estimate",
            "",
            f"- Approximately **{generated['percentage']:.1f}%** of artifacts are likely generated or temporary",
            f"- These include backups, reports, cache files, and build artifacts",
            f"- Cleanup could reduce repository size by ~{generated['total_size_kb'] / 1024:.1f} MB",
            "",
            "### 4. Configuration Dominance",
            ""
        ])

        config_count = self.category_stats['CONFIG']['count']
        if config_count > 0:
            lines.append(f"- **{config_count:,}** configuration files ({config_count/total_artifacts*100:.1f}%)")
            lines.append(f"- Most are YAML/JSON descriptors for shards, Helm charts, and Kubernetes configs")

        lines.extend([
            "",
            "---",
            "",
            "## Recommendations",
            "",
            "1. **Archive Historical Backups**: Move `02_audit_logging/backups/` to external storage",
            "2. **Prune Generated Reports**: Keep only latest reports, archive older versions",
            "3. **Consolidate Policies**: Centralize similar YAML/REGO policies to reduce duplication",
            "4. **Review MISC Category**: Investigate unclassified artifacts for cleanup opportunities",
            "",
            "---",
            "",
            "## Audit Signature",
            "",
            "```json",
            "{",
            '  "audit_version": "v12.4",',
            '  "analysis_type": "forensic_classification",',
            '  "status": "READ_ONLY_CLASSIFICATION_COMPLETE",',
            f'  "timestamp_utc": "{timestamp}",',
            f'  "total_artifacts_classified": {total_artifacts},',
            f'  "unique_extensions": {len(self.extensions)},',
            f'  "categories": {len(self.category_stats)}',
            "}",
            "```",
            "",
            "*Generated by SSID Forensic Artifact Classifier v12.4*"
        ])

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text('\n'.join(lines), encoding='utf-8')

        print(f"[OK] Markdown report written: {output}")
        print(f"     Lines: {len(lines)}, Size: {len('\\n'.join(lines)) / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(
        description='SSID Forensic Artifact Classification v12.4'
    )
    parser.add_argument('--source', required=True, help='Path to global_artifact_inventory.json')
    parser.add_argument('--output-json', required=True, help='Output JSON classification report')
    parser.add_argument('--output-md', required=True, help='Output Markdown classification report')

    args = parser.parse_args()

    print("=" * 70)
    print("SSID Forensic Artifact Classification v12.4")
    print("=" * 70)
    print()

    classifier = ArtifactClassifier(args.source)

    if not classifier.load_inventory():
        sys.exit(1)

    classifier.classify_all_artifacts()
    classifier.generate_json_report(args.output_json)
    classifier.generate_markdown_report(args.output_md)

    print()
    print("=" * 70)
    print("[SUCCESS] Classification complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
