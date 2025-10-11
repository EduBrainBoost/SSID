#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoT Requirement Mapper - SSID Registry Tool
Author: SSID Codex Engine ©2025 MIT License

Maps Source of Truth requirements (MUST/SHOULD/HAVE) to filesystem artifacts.
Generates manifest, score, and compliance report for registry tracking.

Exit Codes:
  0 - PASS (always, generates evidence regardless of compliance)
"""

import sys
import json
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
from dataclasses import dataclass, asdict


ROOT = Path(__file__).resolve().parents[3]
SOT_DIR = ROOT / "16_codex" / "structure"
MANIFEST_DIR = ROOT / "24_meta_orchestration" / "registry" / "manifests"
SCORE_DIR = ROOT / "02_audit_logging" / "scores"
REPORT_DIR = ROOT / "02_audit_logging" / "reports"


@dataclass
class Requirement:
    """Parsed requirement from SoT documentation."""
    req_id: str
    req_type: str  # MUST, SHOULD, HAVE
    description: str
    source_file: str
    source_line: int
    target_paths: List[str]  # Heuristic target paths
    satisfied: bool
    found_artifacts: List[str]


class SoTParser:
    """Parses Source of Truth markdown for requirements."""

    # Requirement patterns
    MUST_PATTERN = re.compile(r'\b(MUST|must)\s+(.+?)(?:\.|$)', re.MULTILINE)
    SHOULD_PATTERN = re.compile(r'\b(SHOULD|should)\s+(.+?)(?:\.|$)', re.MULTILINE)
    HAVE_PATTERN = re.compile(r'\b(HAVE|have|has)\s+(.+?)(?:\.|$)', re.MULTILINE)

    def __init__(self):
        """Initialize parser."""
        self.requirements: List[Requirement] = []
        self.req_counter = 0

    def _extract_requirements(self, content: str, file_path: Path, pattern: re.Pattern, req_type: str) -> None:
        """Extract requirements matching pattern."""
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            matches = pattern.finditer(line)
            for match in matches:
                description = match.group(2).strip()

                # Skip if too short or generic
                if len(description) < 10:
                    continue

                self.req_counter += 1
                req_id = f"SOT-{req_type[0]}{self.req_counter:03d}"

                # Heuristic: extract potential paths from description
                target_paths = self._infer_target_paths(description)

                req = Requirement(
                    req_id=req_id,
                    req_type=req_type,
                    description=description,
                    source_file=str(file_path.relative_to(ROOT)),
                    source_line=line_num,
                    target_paths=target_paths,
                    satisfied=False,
                    found_artifacts=[]
                )
                self.requirements.append(req)

    def _infer_target_paths(self, description: str) -> List[str]:
        """Infer potential filesystem paths from description."""
        targets = []

        # Look for quoted paths
        quote_pattern = re.compile(r'["`\']([a-zA-Z0-9_/.-]+)["`\']')
        for match in quote_pattern.finditer(description):
            path_candidate = match.group(1)
            if '/' in path_candidate or '_' in path_candidate:
                targets.append(path_candidate)

        # Look for common patterns: policy, test, module, shard, etc.
        if 'policy' in description.lower():
            targets.append("23_compliance/policies/")
        if 'test' in description.lower():
            targets.append("11_test_simulation/")
        if 'audit' in description.lower():
            targets.append("02_audit_logging/")
        if 'registry' in description.lower():
            targets.append("24_meta_orchestration/registry/")

        return targets

    def parse_sot_directory(self) -> None:
        """Parse all SoT markdown files."""
        if not SOT_DIR.exists():
            print(f"WARNING: SoT directory not found: {SOT_DIR}")
            return

        for md_file in SOT_DIR.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                self._extract_requirements(content, md_file, self.MUST_PATTERN, "MUST")
                self._extract_requirements(content, md_file, self.SHOULD_PATTERN, "SHOULD")
                self._extract_requirements(content, md_file, self.HAVE_PATTERN, "HAVE")

            except Exception as e:
                print(f"WARNING: Could not parse {md_file}: {e}")


class FilesystemMapper:
    """Maps requirements to actual filesystem artifacts."""

    def __init__(self):
        """Initialize mapper."""
        self.filesystem_index: Set[str] = set()

    def build_index(self) -> None:
        """Build index of all files in repository."""
        for item in ROOT.rglob("*"):
            if item.is_file():
                # Skip common non-artifacts
                if any(skip in str(item) for skip in [
                    ".git", "__pycache__", "node_modules", ".pytest_cache",
                    ".coverage", "venv", ".pyc"
                ]):
                    continue

                rel_path = str(item.relative_to(ROOT))
                self.filesystem_index.add(rel_path)

    def check_requirement(self, req: Requirement) -> None:
        """Check if requirement is satisfied by filesystem artifacts."""
        found = []

        for target in req.target_paths:
            # Check for exact match
            if target in self.filesystem_index:
                found.append(target)
                continue

            # Check for partial matches
            for fs_path in self.filesystem_index:
                if target in fs_path:
                    found.append(fs_path)

        if found:
            req.satisfied = True
            req.found_artifacts = list(set(found))  # Remove duplicates


def calculate_score(requirements: List[Requirement]) -> Dict[str, Any]:
    """Calculate compliance score."""
    total = len(requirements)
    if total == 0:
        return {"score": 100, "total": 0, "satisfied": 0, "unsatisfied": 0}

    satisfied = sum(1 for r in requirements if r.satisfied)
    unsatisfied = total - satisfied

    # Weighted scoring: MUST=3, SHOULD=2, HAVE=1
    must_reqs = [r for r in requirements if r.req_type == "MUST"]
    should_reqs = [r for r in requirements if r.req_type == "SHOULD"]
    have_reqs = [r for r in requirements if r.req_type == "HAVE"]

    must_satisfied = sum(1 for r in must_reqs if r.satisfied)
    should_satisfied = sum(1 for r in should_reqs if r.satisfied)
    have_satisfied = sum(1 for r in have_reqs if r.satisfied)

    total_weight = len(must_reqs) * 3 + len(should_reqs) * 2 + len(have_reqs) * 1
    satisfied_weight = must_satisfied * 3 + should_satisfied * 2 + have_satisfied * 1

    score = (satisfied_weight / total_weight * 100) if total_weight > 0 else 100

    return {
        "score": round(score, 2),
        "total": total,
        "satisfied": satisfied,
        "unsatisfied": unsatisfied,
        "breakdown": {
            "MUST": {"total": len(must_reqs), "satisfied": must_satisfied},
            "SHOULD": {"total": len(should_reqs), "satisfied": should_satisfied},
            "HAVE": {"total": len(have_reqs), "satisfied": have_satisfied}
        }
    }


def generate_manifest(requirements: List[Requirement]) -> Dict[str, Any]:
    """Generate requirement mapping manifest."""
    manifest = {
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": "sot_requirement_mapper",
        "requirements": [asdict(r) for r in requirements]
    }
    return manifest


def generate_score_report(score: Dict[str, Any]) -> Dict[str, Any]:
    """Generate score report."""
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": "sot_requirement_mapper",
        "score": score
    }
    return report


def generate_markdown_report(requirements: List[Requirement], score: Dict[str, Any]) -> str:
    """Generate human-readable markdown report."""
    report_lines = [
        "# SoT Requirement Mapping Report",
        "",
        f"**Generated:** {datetime.utcnow().isoformat()}Z",
        f"**Tool:** sot_requirement_mapper v1.0.0",
        "",
        "## Compliance Score",
        "",
        f"**Overall Score:** {score['score']:.2f}%",
        "",
        f"- Total Requirements: {score['total']}",
        f"- Satisfied: {score['satisfied']}",
        f"- Unsatisfied: {score['unsatisfied']}",
        "",
        "### Breakdown by Type",
        "",
        f"- **MUST**: {score['breakdown']['MUST']['satisfied']}/{score['breakdown']['MUST']['total']}",
        f"- **SHOULD**: {score['breakdown']['SHOULD']['satisfied']}/{score['breakdown']['SHOULD']['total']}",
        f"- **HAVE**: {score['breakdown']['HAVE']['satisfied']}/{score['breakdown']['HAVE']['total']}",
        "",
        "## Unsatisfied Requirements",
        ""
    ]

    unsatisfied = [r for r in requirements if not r.satisfied]
    if unsatisfied:
        for req in unsatisfied:
            report_lines.append(f"### {req.req_id} [{req.req_type}]")
            report_lines.append(f"**Description:** {req.description}")
            report_lines.append(f"**Source:** `{req.source_file}:{req.source_line}`")
            report_lines.append(f"**Expected Paths:** {', '.join(req.target_paths) if req.target_paths else 'N/A'}")
            report_lines.append("")
    else:
        report_lines.append("*All requirements satisfied!*")
        report_lines.append("")

    return "\n".join(report_lines)


def save_outputs(manifest: Dict[str, Any], score_report: Dict[str, Any], md_report: str) -> Dict[str, Path]:
    """Save all output files."""
    # Create directories
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    SCORE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Save manifest
    manifest_path = MANIFEST_DIR / "sot_requirement_mapping.yaml"
    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    # Save score
    score_path = SCORE_DIR / "sot_requirement_score.json"
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(score_report, f, indent=2, sort_keys=True)

    # Save markdown report
    report_path = REPORT_DIR / "sot_requirement_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_report)

    return {
        "manifest": manifest_path,
        "score": score_path,
        "report": report_path
    }


def main() -> int:
    """Main execution."""
    print("SSID SoT Requirement Mapper")
    print("=" * 60)
    print(f"Root: {ROOT}")
    print(f"SoT Dir: {SOT_DIR}")
    print()

    # Parse SoT documents
    print("Parsing SoT requirements...")
    parser = SoTParser()
    parser.parse_sot_directory()

    print(f"Found {len(parser.requirements)} requirements")
    print()

    # Build filesystem index
    print("Indexing filesystem...")
    mapper = FilesystemMapper()
    mapper.build_index()

    print(f"Indexed {len(mapper.filesystem_index)} files")
    print()

    # Check requirements
    print("Mapping requirements to artifacts...")
    for req in parser.requirements:
        mapper.check_requirement(req)

    # Calculate score
    score = calculate_score(parser.requirements)

    # Generate outputs
    manifest = generate_manifest(parser.requirements)
    score_report = generate_score_report(score)
    md_report = generate_markdown_report(parser.requirements, score)

    # Save outputs
    output_paths = save_outputs(manifest, score_report, md_report)

    # Display summary
    print()
    print("=" * 60)
    print(f"Compliance Score: {score['score']:.2f}%")
    print(f"Requirements: {score['satisfied']}/{score['total']} satisfied")
    print()
    print("Output Files:")
    print(f"  Manifest: {output_paths['manifest']}")
    print(f"  Score:    {output_paths['score']}")
    print(f"  Report:   {output_paths['report']}")
    print()
    print("Status: PASS")

    return 0


if __name__ == "__main__":
    sys.exit(main())
