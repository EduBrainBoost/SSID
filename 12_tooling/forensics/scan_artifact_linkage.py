#!/usr/bin/env python3
"""
SSID Artifact Linkage Analysis Scanner v12.4
Analyzes artifact dependencies and generates linkage reports.

Usage:
    python scan_artifact_linkage.py --source <json> --min-links <n> --report <output.md>
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple


class ArtifactLinkageAnalyzer:
    """Analyzes artifact linkage from forensic inventory JSON."""

    def __init__(self, inventory_path: str):
        self.inventory_path = Path(inventory_path)
        self.data = None
        self.linkage_graph = defaultdict(list)
        self.reverse_linkage = defaultdict(list)
        self.isolated_artifacts = []
        self.hub_artifacts = []

    def load_inventory(self) -> bool:
        """Load and parse the artifact inventory JSON."""
        try:
            with open(self.inventory_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"[OK] Loaded inventory: {len(self.data.get('root_modules', []))} root modules")
            return True
        except FileNotFoundError:
            print(f"[ERROR] Inventory file not found: {self.inventory_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in inventory: {e}")
            return False

    def build_linkage_graph(self):
        """Build forward and reverse linkage graphs."""
        print("Building linkage graph...")

        for module in self.data.get('root_modules', []):
            for artifact in module.get('artifacts', []):
                file_path = artifact.get('file_path', '')
                linked_to = artifact.get('linked_to', [])

                if linked_to:
                    self.linkage_graph[file_path] = linked_to
                    for target in linked_to:
                        self.reverse_linkage[target].append(file_path)
                else:
                    self.isolated_artifacts.append(artifact)

        print(f"[OK] Graph built: {len(self.linkage_graph)} artifacts with links")
        print(f"[OK] Isolated artifacts: {len(self.isolated_artifacts)}")

    def identify_hubs(self, min_links: int = 1):
        """Identify hub artifacts (artifacts with many links)."""
        self.hub_artifacts = [
            (path, links) for path, links in self.linkage_graph.items()
            if len(links) >= min_links
        ]
        self.hub_artifacts.sort(key=lambda x: len(x[1]), reverse=True)
        print(f"[OK] Identified {len(self.hub_artifacts)} hub artifacts (min_links={min_links})")

    def analyze_cross_module_links(self) -> Dict[str, int]:
        """Analyze linkage between root modules."""
        cross_module = defaultdict(int)

        for source, targets in self.linkage_graph.items():
            source_module = source.split('/')[0] if '/' in source else 'unknown'
            for target in targets:
                target_module = target.split('/')[0] if '/' in target else 'unknown'
                if source_module != target_module:
                    cross_module[f"{source_module} → {target_module}"] += 1

        return dict(sorted(cross_module.items(), key=lambda x: x[1], reverse=True))

    def analyze_most_referenced(self, top_n: int = 20) -> List[Tuple[str, int]]:
        """Find most referenced artifacts (reverse linkage)."""
        referenced_count = {
            path: len(sources)
            for path, sources in self.reverse_linkage.items()
        }
        return sorted(referenced_count.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def analyze_artifact_types(self) -> Dict[str, Dict[str, int]]:
        """Analyze linkage by artifact type."""
        type_stats = defaultdict(lambda: {'with_links': 0, 'isolated': 0})

        for module in self.data.get('root_modules', []):
            for artifact in module.get('artifacts', []):
                artifact_type = artifact.get('artifact_type', 'Unknown')
                has_links = len(artifact.get('linked_to', [])) > 0

                if has_links:
                    type_stats[artifact_type]['with_links'] += 1
                else:
                    type_stats[artifact_type]['isolated'] += 1

        return dict(type_stats)

    def generate_markdown_report(self, output_path: str, min_links: int):
        """Generate comprehensive Markdown linkage report."""
        print(f"Generating Markdown report: {output_path}")

        cross_module = self.analyze_cross_module_links()
        most_referenced = self.analyze_most_referenced()
        type_stats = self.analyze_artifact_types()

        global_metrics = self.data.get('global_metrics', {})
        timestamp = datetime.utcnow().isoformat() + 'Z'

        lines = [
            "# SSID Artifact Linkage Analysis Report v12.4",
            "",
            f"**Generated:** {timestamp}  ",
            f"**Source:** {self.inventory_path.name}  ",
            f"**Min Links Filter:** {min_links}  ",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"- **Total Artifacts:** {global_metrics.get('total_artifacts', 0):,}",
            f"- **Artifacts with Links:** {len(self.linkage_graph):,} ({len(self.linkage_graph)/max(global_metrics.get('total_artifacts', 1), 1)*100:.1f}%)",
            f"- **Isolated Artifacts:** {len(self.isolated_artifacts):,} ({len(self.isolated_artifacts)/max(global_metrics.get('total_artifacts', 1), 1)*100:.1f}%)",
            f"- **Hub Artifacts (>={min_links} links):** {len(self.hub_artifacts):,}",
            f"- **Cross-Module Links:** {sum(cross_module.values()):,}",
            "",
            "---",
            "",
            "## Hub Artifacts (Top 50)",
            "",
            "Artifacts with the most outgoing links:",
            "",
            "| Rank | File Path | Links | Root Module |",
            "|------|-----------|-------|-------------|"
        ]

        for i, (path, links) in enumerate(self.hub_artifacts[:50], 1):
            root_module = path.split('/')[0] if '/' in path else 'unknown'
            lines.append(f"| {i} | `{path}` | {len(links)} | {root_module} |")

        lines.extend([
            "",
            "---",
            "",
            "## Most Referenced Artifacts (Top 20)",
            "",
            "Artifacts that are referenced by other artifacts (incoming links):",
            "",
            "| Rank | File Path | Referenced By | Root Module |",
            "|------|-----------|---------------|-------------|"
        ])

        for i, (path, count) in enumerate(most_referenced, 1):
            root_module = path.split('/')[0] if '/' in path else 'unknown'
            lines.append(f"| {i} | `{path}` | {count} | {root_module} |")

        lines.extend([
            "",
            "---",
            "",
            "## Cross-Module Linkage (Top 20)",
            "",
            "Artifacts linking between different root modules:",
            "",
            "| Rank | Link Pattern | Count |",
            "|------|--------------|-------|"
        ])

        for i, (pattern, count) in enumerate(list(cross_module.items())[:20], 1):
            lines.append(f"| {i} | {pattern} | {count} |")

        lines.extend([
            "",
            "---",
            "",
            "## Linkage by Artifact Type",
            "",
            "| Artifact Type | With Links | Isolated | Total | Link Rate |",
            "|---------------|------------|----------|-------|-----------|"
        ])

        for art_type, stats in sorted(type_stats.items()):
            with_links = stats['with_links']
            isolated = stats['isolated']
            total = with_links + isolated
            rate = (with_links / total * 100) if total > 0 else 0
            lines.append(f"| {art_type} | {with_links} | {isolated} | {total} | {rate:.1f}% |")

        lines.extend([
            "",
            "---",
            "",
            "## Isolated Artifacts Sample (First 100)",
            "",
            "Artifacts with no outgoing links:",
            "",
            "| File Path | Type | Size (KB) | Root Module |",
            "|-----------|------|-----------|-------------|"
        ])

        for artifact in self.isolated_artifacts[:100]:
            path = artifact.get('file_path', '')
            art_type = artifact.get('artifact_type', 'Unknown')
            size = artifact.get('file_size_kb', 0)
            root_module = path.split('/')[0] if '/' in path else 'unknown'
            lines.append(f"| `{path}` | {art_type} | {size:.2f} | {root_module} |")

        if len(self.isolated_artifacts) > 100:
            lines.append(f"| ... | ... | ... | ... |")
            lines.append(f"| *{len(self.isolated_artifacts) - 100:,} more isolated artifacts* | | | |")

        lines.extend([
            "",
            "---",
            "",
            "## Analysis Notes",
            "",
            "- **Hub Artifacts:** High-degree nodes that link to many other artifacts",
            "- **Most Referenced:** Critical artifacts that many others depend on",
            "- **Cross-Module Links:** Inter-layer dependencies (important for architecture)",
            "- **Isolated Artifacts:** May be standalone, deprecated, or require linkage analysis",
            "",
            "---",
            "",
            "## Audit Signature",
            "",
            "```json",
            "{",
            '  "audit_version": "v12.4",',
            '  "analysis_type": "artifact_linkage",',
            '  "status": "ANALYSIS_COMPLETE",',
            f'  "timestamp_utc": "{timestamp}",',
            f'  "total_artifacts_analyzed": {global_metrics.get("total_artifacts", 0)},',
            f'  "artifacts_with_links": {len(self.linkage_graph)},',
            f'  "hub_artifacts": {len(self.hub_artifacts)}',
            "}",
            "```",
            "",
            "*Generated by SSID Artifact Linkage Analyzer v12.4*"
        ])

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text('\n'.join(lines), encoding='utf-8')

        print(f"[OK] Report written to: {output}")
        print(f"     Lines: {len(lines)}, Size: {len('\\n'.join(lines))/1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(
        description='SSID Artifact Linkage Analysis Scanner v12.4'
    )
    parser.add_argument(
        '--source',
        required=True,
        help='Path to global_artifact_inventory.json'
    )
    parser.add_argument(
        '--min-links',
        type=int,
        default=1,
        help='Minimum number of links to qualify as hub artifact (default: 1)'
    )
    parser.add_argument(
        '--report',
        required=True,
        help='Output Markdown report path'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("SSID Artifact Linkage Analysis Scanner v12.4")
    print("=" * 70)
    print()

    analyzer = ArtifactLinkageAnalyzer(args.source)

    if not analyzer.load_inventory():
        sys.exit(1)

    analyzer.build_linkage_graph()
    analyzer.identify_hubs(args.min_links)
    analyzer.generate_markdown_report(args.report, args.min_links)

    print()
    print("=" * 70)
    print("[SUCCESS] Linkage analysis complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
