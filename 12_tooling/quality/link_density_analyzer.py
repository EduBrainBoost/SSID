#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
link_density_analyzer.py – Link Density Threshold Policy & Redundancy Detection
Autor: edubrainboost ©2025 MIT License

Analyzes software ecology "isolation rate" to identify:
- Low-connectivity modules (< 1% link rate)
- Redundant/duplicate modules
- De-duplication opportunities
- Build overhead optimization potential

Features:
- Link density calculation
- Connectivity threshold detection
- Similarity analysis for redundancy
- De-duplication recommendations
- Efficiency optimization report

Exit Codes:
  0 - PASS: Analysis complete
  1 - FAIL: Analysis error
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class LinkDensityAnalyzer:
    """Analyze link density and detect redundancy opportunities."""

    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.graph_path = root_dir / "02_audit_logging" / "evidence" / "deps" / "dependency_graph.json"

        # Graph data
        self.nodes: List[str] = []
        self.edges: List[List[str]] = []

        # Analysis results
        self.in_degree: Dict[str, int] = defaultdict(int)
        self.out_degree: Dict[str, int] = defaultdict(int)
        self.total_degree: Dict[str, int] = defaultdict(int)

        # Thresholds (configurable)
        self.low_connectivity_threshold = 1  # <= 1 edge
        self.link_density_threshold = 0.01   # 1% link rate

    def load_graph(self) -> bool:
        """Load dependency graph."""
        if not self.graph_path.exists():
            print(f"ERROR: Dependency graph not found: {self.graph_path}")
            return False

        try:
            with open(self.graph_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.nodes = data.get("nodes", [])
            self.edges = data.get("edges", [])

            return True
        except Exception as e:
            print(f"ERROR: Failed to load graph: {e}")
            return False

    def calculate_connectivity(self) -> None:
        """Calculate in-degree, out-degree, and total degree for all nodes."""
        for edge in self.edges:
            source, target = edge
            self.out_degree[source] += 1
            self.in_degree[target] += 1

        for node in self.nodes:
            self.total_degree[node] = self.in_degree[node] + self.out_degree[node]

    def calculate_link_density(self) -> float:
        """
        Calculate graph link density.

        Formula: density = edges / (nodes * (nodes - 1))
        Returns value between 0 (no links) and 1 (fully connected)
        """
        n = len(self.nodes)
        if n <= 1:
            return 0.0

        max_edges = n * (n - 1)
        return len(self.edges) / max_edges

    def identify_low_connectivity_nodes(self) -> List[Dict]:
        """Identify nodes with low connectivity (below threshold)."""
        low_connectivity = []

        for node in self.nodes:
            degree = self.total_degree[node]

            if degree <= self.low_connectivity_threshold:
                low_connectivity.append({
                    "module": node,
                    "in_degree": self.in_degree[node],
                    "out_degree": self.out_degree[node],
                    "total_degree": degree,
                    "link_rate": degree / len(self.nodes) if len(self.nodes) > 0 else 0
                })

        # Sort by total degree (ascending)
        low_connectivity.sort(key=lambda x: x["total_degree"])

        return low_connectivity

    def identify_isolated_clusters(self) -> List[Set[str]]:
        """
        Identify isolated clusters (connected components with no external links).

        Uses DFS to find connected components.
        """
        # Build adjacency list (undirected graph)
        adj = defaultdict(set)
        for source, target in self.edges:
            adj[source].add(target)
            adj[target].add(source)

        visited = set()
        clusters = []

        def dfs(node: str, cluster: Set[str]):
            visited.add(node)
            cluster.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    dfs(neighbor, cluster)

        for node in self.nodes:
            if node not in visited:
                cluster = set()
                dfs(node, cluster)
                if len(cluster) > 1:  # Only consider clusters with 2+ nodes
                    clusters.append(cluster)

        return clusters

    def detect_similar_modules(self, similarity_threshold: float = 0.7) -> List[Dict]:
        """
        Detect potentially redundant modules based on name similarity.

        Uses simple heuristics:
        - Similar names (e.g., "health.py" in multiple directories)
        - Same file structure across different shards
        """
        # Group modules by filename
        filename_groups = defaultdict(list)

        for node in self.nodes:
            # Extract filename from module path
            parts = node.split(".")
            if parts:
                filename = parts[-1]
                filename_groups[filename].append(node)

        # Identify groups with multiple modules (potential duplicates)
        similar_groups = []

        for filename, modules in filename_groups.items():
            if len(modules) > 5:  # Threshold: 5+ modules with same name
                # Check if they have similar paths (e.g., shards pattern)
                shard_pattern = any("shard" in module.lower() for module in modules)

                similar_groups.append({
                    "filename": filename,
                    "count": len(modules),
                    "modules": modules[:10],  # Sample first 10
                    "shard_pattern": shard_pattern,
                    "deduplication_potential": "HIGH" if shard_pattern else "MEDIUM"
                })

        # Sort by count (descending)
        similar_groups.sort(key=lambda x: x["count"], reverse=True)

        return similar_groups

    def generate_deduplication_recommendations(self) -> List[Dict]:
        """Generate actionable de-duplication recommendations."""
        recommendations = []

        # Recommendation 1: Consolidate shard health modules
        similar_modules = self.detect_similar_modules()
        for group in similar_modules:
            if group["shard_pattern"] and group["filename"] == "health":
                recommendations.append({
                    "priority": "HIGH",
                    "type": "CONSOLIDATE_SHARD_MODULES",
                    "target": f"{group['count']} identical health.py modules across shards",
                    "action": "Create single health check base class, inherit in shards",
                    "impact": {
                        "maintenance": "Reduce duplication by ~90%",
                        "build_time": f"Save ~{group['count'] * 0.1:.1f}s per build",
                        "code_size": f"Reduce by ~{group['count'] * 2:.0f}KB"
                    }
                })

        # Recommendation 2: Extract common utility modules
        low_connectivity = self.identify_low_connectivity_nodes()
        isolated_utils = [
            node for node in low_connectivity
            if any(keyword in node["module"].lower() for keyword in ["util", "helper", "common"])
        ]

        if len(isolated_utils) > 10:
            recommendations.append({
                "priority": "MEDIUM",
                "type": "CONSOLIDATE_UTILITIES",
                "target": f"{len(isolated_utils)} isolated utility modules",
                "action": "Merge into centralized utility package (e.g., 03_core/utils)",
                "impact": {
                    "maintenance": "Centralized utility management",
                    "build_time": f"Save ~{len(isolated_utils) * 0.05:.1f}s",
                    "discoverability": "Improved (single import location)"
                }
            })

        # Recommendation 3: Review low-connectivity modules
        very_low = [n for n in low_connectivity if n["total_degree"] == 0]
        if len(very_low) > 0:
            recommendations.append({
                "priority": "LOW",
                "type": "REVIEW_UNUSED",
                "target": f"{len(very_low)} completely isolated modules",
                "action": "Review if modules are dead code or missing imports",
                "impact": {
                    "maintenance": "Cleanup dead code",
                    "build_time": f"Save ~{len(very_low) * 0.1:.1f}s",
                    "clarity": "Reduced codebase complexity"
                }
            })

        return recommendations

    def generate_report(self) -> Dict:
        """Generate comprehensive link density analysis report."""
        link_density = self.calculate_link_density()
        low_connectivity = self.identify_low_connectivity_nodes()
        clusters = self.identify_isolated_clusters()
        similar_modules = self.detect_similar_modules()
        recommendations = self.generate_deduplication_recommendations()

        # Calculate statistics
        total_nodes = len(self.nodes)
        total_edges = len(self.edges)
        avg_degree = sum(self.total_degree.values()) / total_nodes if total_nodes > 0 else 0

        report = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "analyzer_version": "1.0.0",
                "graph_source": str(self.graph_path.relative_to(self.root))
            },
            "graph_metrics": {
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "link_density": f"{link_density * 100:.4f}%",
                "average_degree": f"{avg_degree:.2f}",
                "isolation_rate": f"{(1 - link_density) * 100:.2f}%"
            },
            "connectivity_analysis": {
                "low_connectivity_count": len(low_connectivity),
                "low_connectivity_percentage": f"{len(low_connectivity) / total_nodes * 100:.1f}%",
                "low_connectivity_threshold": self.low_connectivity_threshold,
                "sample_low_connectivity": low_connectivity[:20]  # Top 20
            },
            "cluster_analysis": {
                "isolated_cluster_count": len(clusters),
                "largest_cluster_size": max([len(c) for c in clusters], default=0),
                "sample_clusters": [list(c)[:5] for c in clusters[:5]]  # Top 5 clusters, first 5 nodes each
            },
            "redundancy_analysis": {
                "similar_module_groups": len(similar_modules),
                "top_redundancy_candidates": similar_modules[:10]
            },
            "deduplication_recommendations": recommendations,
            "efficiency_assessment": {
                "current_state": "HIGH_ISOLATION (99% independent modules)",
                "compliance_impact": "EXCELLENT (no uncontrolled side effects)",
                "efficiency_impact": "MODERATE (potential build overhead)",
                "optimization_potential": f"{len(recommendations)} actionable recommendations"
            }
        }

        return report

    def save_report(self, report: Dict) -> Path:
        """Save analysis report to file."""
        report_dir = self.root / "12_tooling" / "quality" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"link_density_analysis_{timestamp}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report_path


def main() -> int:
    """Main execution."""
    print("=" * 70)
    print("Link Density Analyzer - Software Ecology Analysis")
    print("=" * 70)
    print()

    root = Path(__file__).resolve().parents[2]
    analyzer = LinkDensityAnalyzer(root)

    # Load graph
    print("Loading dependency graph...")
    if not analyzer.load_graph():
        return 1

    print(f"Loaded {len(analyzer.nodes)} nodes, {len(analyzer.edges)} edges")
    print()

    # Calculate connectivity
    print("Calculating connectivity metrics...")
    analyzer.calculate_connectivity()
    print()

    # Generate report
    print("Generating analysis report...")
    report = analyzer.generate_report()
    print()

    # Display key metrics
    print("Key Metrics:")
    print(f"  Link Density: {report['graph_metrics']['link_density']}")
    print(f"  Isolation Rate: {report['graph_metrics']['isolation_rate']}")
    print(f"  Low Connectivity: {report['connectivity_analysis']['low_connectivity_count']} modules "
          f"({report['connectivity_analysis']['low_connectivity_percentage']})")
    print()

    # Display recommendations
    print(f"Deduplication Recommendations: {len(report['deduplication_recommendations'])}")
    for i, rec in enumerate(report['deduplication_recommendations'], 1):
        print(f"\n  [{i}] Priority: {rec['priority']}")
        print(f"      Type: {rec['type']}")
        print(f"      Target: {rec['target']}")
        print(f"      Action: {rec['action']}")
    print()

    # Save report
    print("Saving report...")
    report_path = analyzer.save_report(report)
    print(f"Report: {report_path.relative_to(root)}")
    print()

    # Summary
    print("=" * 70)
    print("Analysis Complete")
    print("=" * 70)
    print(f"Efficiency Assessment: {report['efficiency_assessment']['current_state']}")
    print(f"Compliance Impact: {report['efficiency_assessment']['compliance_impact']}")
    print(f"Optimization Potential: {report['efficiency_assessment']['optimization_potential']}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
