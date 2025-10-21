#!/usr/bin/env python3
"""
SSID Forensic Artifact Classification v12.4 (READ-ONLY)
Analyzes global_artifact_inventory.json to classify all 52,217 artifacts
by type, origin, and relevance.
"""

import json
import os
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# Configuration
INPUT_FILE = "02_audit_logging/reports/global_artifact_inventory.json"
OUTPUT_JSON = "02_audit_logging/reports/artifact_classification_v12_4.json"
OUTPUT_MD = "02_audit_logging/reports/ARTIFACT_CLASSIFICATION_V12_4.md"

# Category definitions
CATEGORIES = {
    "POLICIES": [".rego"],
    "MODELS": [".yaml", ".yml", ".json"],
    "REPORTS": [".md"],
    "CODE": [".py", ".ts", ".tsx", ".js", ".jsx", ".sh", ".bash"],
    "WASM/HASH": [".wasm", ".sha256", ".hash"],
    "MISC": []  # Catch-all
}


def load_inventory(file_path):
    """Load the inventory JSON file."""
    print(f"Loading inventory from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def get_extension(file_path):
    """Extract file extension from path."""
    return Path(file_path).suffix.lower()


def get_root_module(file_path):
    """Extract root module (first directory) from path."""
    parts = Path(file_path).parts
    if len(parts) > 0:
        return parts[0]
    return "unknown"


def categorize_extension(ext):
    """Categorize file extension into predefined categories."""
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "MISC"


def analyze_inventory(inventory_data):
    """Perform comprehensive artifact classification."""

    # Extract artifacts from nested structure
    artifacts = []
    root_modules = inventory_data.get("root_modules", [])
    for root_module in root_modules:
        root_artifacts = root_module.get("artifacts", [])
        # Convert to unified format
        for artifact in root_artifacts:
            artifacts.append({
                "path": artifact.get("file_path", ""),
                "size_bytes": int(artifact.get("file_size_kb", 0) * 1024),  # Convert KB to bytes
                "root_module": root_module.get("root_module", "unknown")
            })

    total_count = len(artifacts)
    total_size = sum(a.get("size_bytes", 0) for a in artifacts)

    print(f"Analyzing {total_count:,} artifacts ({total_size:,} bytes)...")

    # Initialize counters
    ext_stats = defaultdict(lambda: {"count": 0, "total_size": 0})
    category_stats = defaultdict(lambda: {"count": 0, "total_size": 0, "files": []})
    root_stats = defaultdict(lambda: {"count": 0, "total_size": 0})

    largest_files = []

    # Process each artifact
    for artifact in artifacts:
        path = artifact.get("path", "")
        size = artifact.get("size_bytes", 0)

        # Extract extension
        ext = get_extension(path)
        ext_stats[ext]["count"] += 1
        ext_stats[ext]["total_size"] += size

        # Categorize
        category = categorize_extension(ext)
        category_stats[category]["count"] += 1
        category_stats[category]["total_size"] += size
        category_stats[category]["files"].append(path)

        # Root module
        root = get_root_module(path)
        root_stats[root]["count"] += 1
        root_stats[root]["total_size"] += size

        # Track largest files
        largest_files.append({"path": path, "size": size})

    # Sort largest files
    largest_files.sort(key=lambda x: x["size"], reverse=True)
    top_10_largest = largest_files[:10]

    # Sort stats
    ext_stats_sorted = sorted(ext_stats.items(), key=lambda x: x[1]["count"], reverse=True)
    category_stats_sorted = sorted(category_stats.items(), key=lambda x: x[1]["count"], reverse=True)
    root_stats_sorted = sorted(root_stats.items(), key=lambda x: x[1]["count"], reverse=True)

    # Identify anomalies (roots with > 1000 artifacts)
    root_anomalies = [
        {"root": root, "count": stats["count"], "size": stats["total_size"]}
        for root, stats in root_stats.items()
        if stats["count"] > 1000
    ]
    root_anomalies.sort(key=lambda x: x["count"], reverse=True)

    # Calculate percentages
    ext_distribution = []
    for ext, stats in ext_stats_sorted:
        percentage = (stats["count"] / total_count) * 100
        avg_size = stats["total_size"] / stats["count"] if stats["count"] > 0 else 0
        ext_distribution.append({
            "extension": ext or "(no extension)",
            "count": stats["count"],
            "percentage": round(percentage, 2),
            "total_size": stats["total_size"],
            "avg_size": round(avg_size, 2)
        })

    category_distribution = []
    for category, stats in category_stats_sorted:
        percentage = (stats["count"] / total_count) * 100
        size_percentage = (stats["total_size"] / total_size) * 100 if total_size > 0 else 0
        category_distribution.append({
            "category": category,
            "count": stats["count"],
            "percentage": round(percentage, 2),
            "total_size": stats["total_size"],
            "size_percentage": round(size_percentage, 2)
        })

    # Pareto analysis: Which types cause > 80% of artifacts?
    pareto_80_types = []
    cumulative_count = 0
    for item in ext_distribution:
        cumulative_count += item["count"]
        pareto_80_types.append(item["extension"])
        if (cumulative_count / total_count) >= 0.80:
            break

    # Estimate generated/temporary files
    generated_extensions = [".pyc", ".log", ".tmp", ".cache", ".lock", ".sha256",
                           ".hash", ".wasm", ".map", ".min.js", ".min.css"]
    generated_count = sum(
        stats["count"]
        for ext, stats in ext_stats.items()
        if ext in generated_extensions
    )

    report_pattern_count = sum(
        1 for a in artifacts
        if "reports/" in a.get("path", "") or "logs/" in a.get("path", "")
    )

    estimated_generated = generated_count + report_pattern_count

    # Handle division by zero
    generated_percentage = 0
    if total_count > 0:
        generated_percentage = round((estimated_generated / total_count) * 100, 2)

    # Build result
    result = {
        "audit_version": "v12.4",
        "status": "READ_ONLY_CLASSIFICATION_COMPLETE",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_artifacts": total_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "unique_extensions": len(ext_stats),
            "unique_root_modules": len(root_stats)
        },
        "extension_distribution": ext_distribution,
        "category_distribution": category_distribution,
        "top_10_largest_files": [
            {"path": f["path"], "size_bytes": f["size"], "size_mb": round(f["size"] / (1024 * 1024), 2)}
            for f in top_10_largest
        ],
        "root_module_stats": [
            {"root": root, "count": stats["count"], "size_bytes": stats["total_size"]}
            for root, stats in root_stats_sorted
        ],
        "root_anomalies": root_anomalies,
        "pareto_analysis": {
            "types_causing_80_percent": pareto_80_types,
            "count": len(pareto_80_types)
        },
        "generated_files_estimate": {
            "count": estimated_generated,
            "percentage": generated_percentage,
            "note": "Estimated based on extensions and path patterns"
        }
    }

    return result


def generate_json_report(data, output_path):
    """Generate machine-readable JSON report."""
    print(f"Writing JSON report to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_markdown_report(data, output_path):
    """Generate human-readable Markdown report."""
    print(f"Writing Markdown report to {output_path}...")

    md = []
    md.append("# SSID Forensic Artifact Classification v12.4")
    md.append("")
    md.append("**Status:** READ-ONLY CLASSIFICATION COMPLETE")
    md.append(f"**Timestamp:** {data['timestamp']}")
    md.append(f"**Audit Version:** {data['audit_version']}")
    md.append("")

    # Summary
    md.append("## Executive Summary")
    md.append("")
    summary = data["summary"]
    md.append(f"- **Total Artifacts:** {summary['total_artifacts']:,}")
    md.append(f"- **Total Size:** {summary['total_size_mb']} MB ({summary['total_size_bytes']:,} bytes)")
    md.append(f"- **Unique Extensions:** {summary['unique_extensions']}")
    md.append(f"- **Unique Root Modules:** {summary['unique_root_modules']}")
    md.append("")

    # Extension distribution
    md.append("## Extension Distribution")
    md.append("")
    md.append("| Extension | Count | Percentage | Total Size (MB) | Avg Size (bytes) |")
    md.append("|-----------|-------|------------|-----------------|------------------|")
    for item in data["extension_distribution"][:20]:  # Top 20
        ext = item["extension"]
        count = item["count"]
        pct = item["percentage"]
        size_mb = round(item["total_size"] / (1024 * 1024), 2)
        avg = item["avg_size"]
        md.append(f"| `{ext}` | {count:,} | {pct}% | {size_mb} | {avg:.0f} |")
    md.append("")

    # Category distribution
    md.append("## Category Distribution")
    md.append("")
    md.append("| Category | Count | Artifact % | Total Size (MB) | Size % |")
    md.append("|----------|-------|------------|-----------------|--------|")
    for item in data["category_distribution"]:
        cat = item["category"]
        count = item["count"]
        pct = item["percentage"]
        size_mb = round(item["total_size"] / (1024 * 1024), 2)
        size_pct = item["size_percentage"]
        md.append(f"| **{cat}** | {count:,} | {pct}% | {size_mb} | {size_pct}% |")
    md.append("")

    # Top 10 largest files
    md.append("## Top 10 Largest Files")
    md.append("")
    md.append("| Rank | Path | Size (MB) |")
    md.append("|------|------|-----------|")
    for i, item in enumerate(data["top_10_largest_files"], 1):
        path = item["path"]
        size_mb = item["size_mb"]
        md.append(f"| {i} | `{path}` | {size_mb} |")
    md.append("")

    # Root anomalies
    md.append("## Root Module Anomalies (>1000 artifacts)")
    md.append("")
    if data["root_anomalies"]:
        md.append("| Root Module | Artifact Count | Total Size (MB) |")
        md.append("|-------------|----------------|-----------------|")
        for item in data["root_anomalies"]:
            root = item["root"]
            count = item["count"]
            size_mb = round(item["size"] / (1024 * 1024), 2)
            md.append(f"| `{root}` | {count:,} | {size_mb} |")
    else:
        md.append("*No anomalies detected.*")
    md.append("")

    # Pareto analysis
    md.append("## Pareto Analysis (80/20 Rule)")
    md.append("")
    pareto = data["pareto_analysis"]
    md.append(f"**{pareto['count']} file types** cause **80%** of all artifacts:")
    md.append("")
    md.append(", ".join(f"`{t}`" for t in pareto["types_causing_80_percent"]))
    md.append("")

    # Generated files estimate
    md.append("## Generated/Temporary Files Estimate")
    md.append("")
    gen = data["generated_files_estimate"]
    md.append(f"- **Estimated Count:** {gen['count']:,}")
    md.append(f"- **Percentage:** {gen['percentage']}%")
    md.append(f"- **Note:** {gen['note']}")
    md.append("")

    # Signature
    md.append("---")
    md.append("")
    md.append(f"**Audit Version:** `{data['audit_version']}`")
    md.append(f"**Status:** `{data['status']}`")
    md.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))


def main():
    """Main execution function."""
    print("=" * 70)
    print("SSID FORENSIC ARTIFACT CLASSIFICATION v12.4")
    print("=" * 70)
    print()

    # Load inventory
    inventory_data = load_inventory(INPUT_FILE)

    # Analyze
    analysis_result = analyze_inventory(inventory_data)

    # Generate reports
    generate_json_report(analysis_result, OUTPUT_JSON)
    generate_markdown_report(analysis_result, OUTPUT_MD)

    print()
    print("=" * 70)
    print("CLASSIFICATION COMPLETE")
    print("=" * 70)
    print(f"JSON Report: {OUTPUT_JSON}")
    print(f"Markdown Report: {OUTPUT_MD}")
    print()


if __name__ == "__main__":
    main()
