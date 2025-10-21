#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Graph Versioning System
SSID Phase 2 Implementation

Purpose:
- Version every dependency graph generation
- Create audit trail of dependency changes
- Enable rückverfolgbare governance decisions
- Track cycle detection over time

Architecture:
Graph Generation → Versioned Storage → Change Detection → Audit Log

Every graph generation creates:
1. Timestamped snapshot (JSON + DOT + SVG)
2. Hash of graph structure
3. Diff from previous version
4. Change log entry

Integration:
- 23_compliance/anti_gaming/dependency_graph_generator.py → versions here
- CI/CD → consumes versions for Zero-Cycle Gate
- Governance → reviews version history for architecture decisions
"""

import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

@dataclass
class GraphVersion:
    """
    Represents a versioned dependency graph snapshot.

    Fields:
    - version_id: Unique version identifier (timestamp-based)
    - timestamp: ISO 8601 UTC
    - graph_hash: SHA-256 of canonical graph structure
    - total_modules: Number of modules in graph
    - total_dependencies: Number of edges in graph
    - cycles_found: Number of cycles detected
    - files: Paths to generated files (JSON, DOT, SVG)
    - metadata: Additional context
    """
    version_id: str
    timestamp: str
    graph_hash: str
    total_modules: int
    total_dependencies: int
    cycles_found: int
    files: Dict[str, str]
    metadata: Dict

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class GraphChange:
    """
    Represents a change between two graph versions.

    Fields:
    - from_version: Previous version ID
    - to_version: New version ID
    - modules_added: List of added modules
    - modules_removed: List of removed modules
    - dependencies_added: List of added dependencies
    - dependencies_removed: List of removed dependencies
    - cycles_delta: Change in number of cycles
    """
    from_version: str
    to_version: str
    modules_added: List[str]
    modules_removed: List[str]
    dependencies_added: List[Tuple[str, str]]
    dependencies_removed: List[Tuple[str, str]]
    cycles_delta: int

    def to_dict(self) -> Dict:
        return asdict(self)

class DependencyGraphVersioning:
    """
    Version control system for dependency graphs.

    Responsibilities:
    1. Store timestamped graph snapshots
    2. Compute graph hashes for change detection
    3. Generate diffs between versions
    4. Maintain version history
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.versions_dir = repo_root / "24_meta_orchestration" / "registry" / "logs" / "dependency_graphs"
        self.versions_dir.mkdir(parents=True, exist_ok=True)

        self.version_index_file = self.versions_dir / "version_index.json"
        self.version_index = self._load_version_index()

    def _load_version_index(self) -> Dict:
        """Load version index from disk"""
        if self.version_index_file.exists():
            with open(self.version_index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"versions": [], "latest_version_id": None}

    def _save_version_index(self) -> None:
        """Save version index to disk"""
        with open(self.version_index_file, 'w', encoding='utf-8') as f:
            json.dump(self.version_index, f, indent=2, sort_keys=True)

    def compute_graph_hash(self, graph: Dict[str, List[str]]) -> str:
        """
        Compute deterministic hash of graph structure.

        Args:
            graph: Adjacency list representation (module_id → [dependency_ids])

        Returns:
            SHA-256 hash of canonical graph representation
        """
        # Create canonical representation (sorted)
        canonical = json.dumps(
            {k: sorted(v) for k, v in sorted(graph.items())},
            sort_keys=True
        )
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def create_version(
        self,
        graph: Dict[str, List[str]],
        modules: List[str],
        cycles: List[List[str]],
        graph_files: Dict[str, Path],
        metadata: Optional[Dict] = None
    ) -> GraphVersion:
        """
        Create a new versioned snapshot of the dependency graph.

        Args:
            graph: Adjacency list representation
            modules: List of all modules
            cycles: List of detected cycles
            graph_files: Dict mapping file type to path (e.g., {"dot": path, "svg": path})
            metadata: Additional context

        Returns:
            GraphVersion object
        """
        # Generate version ID
        version_id = f"DGV-{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Compute graph hash
        graph_hash = self.compute_graph_hash(graph)

        # Count dependencies
        total_deps = sum(len(deps) for deps in graph.values())

        # Create version directory
        version_dir = self.versions_dir / version_id
        version_dir.mkdir(parents=True, exist_ok=True)

        # Copy graph files to version directory
        versioned_files = {}
        for file_type, source_path in graph_files.items():
            if source_path and source_path.exists():
                dest_path = version_dir / f"graph.{file_type}"
                shutil.copy2(source_path, dest_path)
                versioned_files[file_type] = str(dest_path.relative_to(self.repo_root))

        # Save graph structure
        graph_json_path = version_dir / "graph_structure.json"
        with open(graph_json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "graph": graph,
                "modules": sorted(modules),
                "cycles": cycles,
                "total_modules": len(modules),
                "total_dependencies": total_deps,
                "cycles_found": len(cycles)
            }, f, indent=2, sort_keys=True)

        versioned_files["json"] = str(graph_json_path.relative_to(self.repo_root))

        # Create version object
        version = GraphVersion(
            version_id=version_id,
            timestamp=timestamp,
            graph_hash=graph_hash,
            total_modules=len(modules),
            total_dependencies=total_deps,
            cycles_found=len(cycles),
            files=versioned_files,
            metadata=metadata or {}
        )

        # Save version metadata
        version_meta_path = version_dir / "version_metadata.json"
        with open(version_meta_path, 'w', encoding='utf-8') as f:
            json.dump(version.to_dict(), f, indent=2, sort_keys=True)

        # Update version index
        self.version_index["versions"].append(version.to_dict())
        self.version_index["latest_version_id"] = version_id
        self._save_version_index()

        return version

    def get_latest_version(self) -> Optional[GraphVersion]:
        """Get the most recent graph version"""
        if not self.version_index["versions"]:
            raise NotImplementedError("TODO: Implement this function")

        latest_version_dict = self.version_index["versions"][-1]
        return GraphVersion(**latest_version_dict)

    def get_version(self, version_id: str) -> Optional[GraphVersion]:
        """Get a specific graph version by ID"""
        for version_dict in self.version_index["versions"]:
            if version_dict["version_id"] == version_id:
                return GraphVersion(**version_dict)
        raise NotImplementedError("TODO: Implement this function")

    def compute_diff(
        self,
        from_version_id: str,
        to_version_id: str
    ) -> Optional[GraphChange]:
        """
        Compute the difference between two graph versions.

        Args:
            from_version_id: Previous version ID
            to_version_id: New version ID

        Returns:
            GraphChange object describing the differences
        """
        from_version = self.get_version(from_version_id)
        to_version = self.get_version(to_version_id)

        if not from_version or not to_version:
            raise NotImplementedError("TODO: Implement this function")

        # Load graph structures
        from_graph_file = self.repo_root / from_version.files["json"]
        to_graph_file = self.repo_root / to_version.files["json"]

        with open(from_graph_file, 'r', encoding='utf-8') as f:
            from_data = json.load(f)

        with open(to_graph_file, 'r', encoding='utf-8') as f:
            to_data = json.load(f)

        # Compute module changes
        from_modules = set(from_data["modules"])
        to_modules = set(to_data["modules"])

        modules_added = list(to_modules - from_modules)
        modules_removed = list(from_modules - to_modules)

        # Compute dependency changes
        from_graph = from_data["graph"]
        to_graph = to_data["graph"]

        from_edges = set()
        for src, targets in from_graph.items():
            for tgt in targets:
                from_edges.add((src, tgt))

        to_edges = set()
        for src, targets in to_graph.items():
            for tgt in targets:
                to_edges.add((src, tgt))

        dependencies_added = list(to_edges - from_edges)
        dependencies_removed = list(from_edges - to_edges)

        # Compute cycles delta
        cycles_delta = to_version.cycles_found - from_version.cycles_found

        return GraphChange(
            from_version=from_version_id,
            to_version=to_version_id,
            modules_added=modules_added,
            modules_removed=modules_removed,
            dependencies_added=dependencies_added,
            dependencies_removed=dependencies_removed,
            cycles_delta=cycles_delta
        )

    def generate_changelog(
        self,
        start_version_id: Optional[str] = None,
        end_version_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate a changelog showing all changes between versions.

        Args:
            start_version_id: Starting version (default: first version)
            end_version_id: Ending version (default: latest version)

        Returns:
            List of change entries
        """
        if not self.version_index["versions"]:
            return []

        # Determine range
        versions = self.version_index["versions"]

        start_idx = 0
        if start_version_id:
            for i, v in enumerate(versions):
                if v["version_id"] == start_version_id:
                    start_idx = i
                    break

        end_idx = len(versions) - 1
        if end_version_id:
            for i, v in enumerate(versions):
                if v["version_id"] == end_version_id:
                    end_idx = i
                    break

        # Generate changelog
        changelog = []
        for i in range(start_idx, end_idx):
            from_version_id = versions[i]["version_id"]
            to_version_id = versions[i + 1]["version_id"]

            change = self.compute_diff(from_version_id, to_version_id)
            if change:
                changelog.append(change.to_dict())

        return changelog

def main():
    """CLI entry point for testing"""
    repo_root = Path(__file__).resolve().parents[3]

    versioning = DependencyGraphVersioning(repo_root)

    # Example: Create a test version
    test_graph = {
        "module_a": ["module_b", "module_c"],
        "module_b": ["module_c"],
        "module_c": []
    }

    test_modules = ["module_a", "module_b", "module_c"]
    test_cycles = []

    version = versioning.create_version(
        graph=test_graph,
        modules=test_modules,
        cycles=test_cycles,
        graph_files={},
        metadata={"test": True}
    )

    print(json.dumps(version.to_dict(), indent=2))
    print(f"\nVersion created: {version.version_id}")
    print(f"Version index: {versioning.version_index_file}")

if __name__ == "__main__":
    main()
