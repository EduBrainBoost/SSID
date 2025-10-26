"""
Layer 2: Hierarchisches Mapping (Hierarchical Mapping)
======================================================

Bildet jedes File auf die 24 Roots und 16 Shards ab.
Ermöglicht sofortige Erkennung des SSID-Bereichs für jede Regel.

Features:
- Root → Shard → Regel Mapping
- SSID-Bereich-Erkennung (automatisch aus Pfaden)
- Governance-Isolation (07_governance_legal ≠ 23_compliance)
- 24×16 Matrix-Koordinaten für jede Regel

Version: 3.0.0
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class ShardInfo:
    """Information about a shard within a root"""
    shard_id: str
    shard_name: str
    file_path: Optional[Path] = None
    rule_count: int = 0
    categories: Set[str] = field(default_factory=set)


@dataclass
class RootInfo:
    """Information about an SSID root folder"""
    root_id: str
    root_name: str
    root_number: int
    shards: Dict[str, ShardInfo] = field(default_factory=dict)
    total_rules: int = 0
    governance_area: str = "general"  # general, compliance, governance, identity, etc.


class HierarchicalMapping:
    """Hierarchical mapping system for SSID 24×16 structure

    Maps every file and rule to:
    - Root folder (1 of 24)
    - Shard (1 of 16 possible per root)
    - Position within shard

    Prevents governance area mixing (e.g., 07_governance_legal vs 23_compliance)
    """

    # 24 SSID Root Folders (as defined in CompletenessMatrix)
    ROOTS = [
        '01_ai_layer', '02_audit_logging', '03_core', '04_deployment',
        '05_documentation', '06_federation', '07_governance_legal', '08_integration',
        '09_meta_identity', '10_networking', '11_test_simulation', '12_tooling',
        '13_ui_ux', '14_user_management', '15_wallet', '16_codex',
        '17_observability', '18_plugins', '19_schemas', '20_secrets',
        '21_services', '22_storage', '23_compliance', '24_meta_orchestration'
    ]

    # Governance Area Classification
    GOVERNANCE_AREAS = {
        '07_governance_legal': 'legal',
        '23_compliance': 'compliance',
        '09_meta_identity': 'identity',
        '24_meta_orchestration': 'orchestration',
        '02_audit_logging': 'audit',
        '03_core': 'core',
        '01_ai_layer': 'ai',
        '20_secrets': 'security',
    }

    # Standard 16 Shard Categories (flexible per root)
    STANDARD_SHARDS = [
        'policies', 'contracts', 'validators', 'tests', 'reports',
        'configs', 'schemas', 'templates', 'scripts', 'docs',
        'monitors', 'alerts', 'metrics', 'logs', 'cache', 'misc'
    ]

    def __init__(self):
        self.root_map: Dict[str, RootInfo] = {}
        self.path_cache: Dict[str, Tuple[str, str]] = {}  # path -> (root, shard)
        self._initialize_roots()

    def _initialize_roots(self):
        """Initialize all 24 roots with metadata"""
        for i, root in enumerate(self.ROOTS, 1):
            root_info = RootInfo(
                root_id=root,
                root_name=root.replace('_', ' ').title(),
                root_number=i,
                governance_area=self.GOVERNANCE_AREAS.get(root, 'general')
            )
            self.root_map[root] = root_info

    def extract_root_from_path(self, path: str) -> Optional[str]:
        """Extract root folder from file path

        Args:
            path: File path (absolute or relative)

        Returns:
            Root folder name (e.g., '23_compliance') or None

        Examples:
            '23_compliance/policies/sot.rego' -> '23_compliance'
            'C:/SSID/03_core/validators/sot_validator.py' -> '03_core'
            '16_codex/contracts/sot/sot_contract.yaml' -> '16_codex'
        """
        # Normalize path separators
        normalized = path.replace('\\', '/')

        # Try to find root pattern: XX_folder_name
        root_pattern = r'\b(\d{2}_[a-z_]+)\b'
        matches = re.findall(root_pattern, normalized)

        if matches:
            # Return first match that's in our ROOTS list
            for match in matches:
                if match in self.ROOTS:
                    return match

        return None

    def extract_shard_from_path(self, path: str, root: str) -> Optional[str]:
        """Extract shard name from file path

        Args:
            path: File path
            root: Root folder (already extracted)

        Returns:
            Shard name (e.g., 'policies', 'validators') or None

        Examples:
            '23_compliance/policies/sot.rego' -> 'policies'
            '03_core/validators/sot/sot_validator.py' -> 'validators'
            '16_codex/contracts/sot_contract.yaml' -> 'contracts'
        """
        # Normalize path
        normalized = path.replace('\\', '/')

        # Find root position
        root_idx = normalized.find(root)
        if root_idx == -1:
            return None

        # Extract path after root
        after_root = normalized[root_idx + len(root):].lstrip('/')

        # First folder after root is the shard
        if '/' in after_root:
            shard = after_root.split('/')[0]
            return shard
        else:
            # File directly in root -> 'root' shard
            return 'root'

    def map_file_to_coordinates(self, file_path: str) -> Optional[Tuple[str, str]]:
        """Map a file to (root, shard) coordinates

        Args:
            file_path: Path to file

        Returns:
            Tuple of (root, shard) or None if unmappable
        """
        # Check cache first
        if file_path in self.path_cache:
            return self.path_cache[file_path]

        # Extract root
        root = self.extract_root_from_path(file_path)
        if not root:
            return None

        # Extract shard
        shard = self.extract_shard_from_path(file_path, root)
        if not shard:
            return None

        # Cache result
        self.path_cache[file_path] = (root, shard)

        # Update root info
        if root in self.root_map:
            if shard not in self.root_map[root].shards:
                self.root_map[root].shards[shard] = ShardInfo(
                    shard_id=f"{root}.{shard}",
                    shard_name=shard,
                    file_path=Path(file_path)
                )

        return (root, shard)

    def register_rule(self, file_path: str, rule_id: str) -> Optional[str]:
        """Register a rule and return its full coordinate ID

        Args:
            file_path: Source file path
            rule_id: Rule identifier

        Returns:
            Full coordinate ID: 'ROOT.SHARD.RULE_ID' or None
        """
        coords = self.map_file_to_coordinates(file_path)
        if not coords:
            return None

        root, shard = coords

        # Update statistics
        if root in self.root_map:
            self.root_map[root].total_rules += 1
            if shard in self.root_map[root].shards:
                self.root_map[root].shards[shard].rule_count += 1

        # Return full coordinate ID
        return f"{root}.{shard}.{rule_id}"

    def get_governance_area(self, file_path: str) -> str:
        """Get governance area for a file path

        Args:
            file_path: File path

        Returns:
            Governance area (e.g., 'compliance', 'legal', 'general')
        """
        root = self.extract_root_from_path(file_path)
        if root and root in self.root_map:
            return self.root_map[root].governance_area
        return 'general'

    def check_governance_isolation(self, path1: str, path2: str) -> bool:
        """Check if two paths violate governance isolation

        Args:
            path1: First file path
            path2: Second file path

        Returns:
            True if paths can be mixed (same governance area or 'general')
            False if mixing would violate isolation
        """
        area1 = self.get_governance_area(path1)
        area2 = self.get_governance_area(path2)

        # General can mix with anything
        if area1 == 'general' or area2 == 'general':
            return True

        # Same area is fine
        if area1 == area2:
            return True

        # Different specific areas -> isolation violation
        return False

    def get_root_info(self, root: str) -> Optional[RootInfo]:
        """Get detailed info about a root"""
        return self.root_map.get(root)

    def get_shard_info(self, root: str, shard: str) -> Optional[ShardInfo]:
        """Get detailed info about a shard"""
        if root in self.root_map:
            return self.root_map[root].shards.get(shard)
        return None

    def get_all_roots(self) -> List[str]:
        """Get list of all 24 roots"""
        return self.ROOTS.copy()

    def get_shards_for_root(self, root: str) -> List[str]:
        """Get all discovered shards for a root"""
        if root in self.root_map:
            return list(self.root_map[root].shards.keys())
        return []

    def get_statistics(self) -> Dict[str, any]:
        """Get mapping statistics"""
        total_rules = sum(r.total_rules for r in self.root_map.values())
        total_shards = sum(len(r.shards) for r in self.root_map.values())
        active_roots = sum(1 for r in self.root_map.values() if r.total_rules > 0)

        return {
            'total_roots': len(self.ROOTS),
            'active_roots': active_roots,
            'total_shards': total_shards,
            'total_rules': total_rules,
            'cache_size': len(self.path_cache),
            'governance_areas': len(set(r.governance_area for r in self.root_map.values()))
        }

    def generate_matrix_report(self) -> str:
        """Generate 24×16 matrix coverage report"""
        lines = []
        lines.append("=" * 80)
        lines.append("HIERARCHICAL MAPPING MATRIX - 24 Roots × Discovered Shards")
        lines.append("=" * 80)

        for root in self.ROOTS:
            if root in self.root_map:
                info = self.root_map[root]
                if info.total_rules > 0:
                    lines.append(f"\n[{info.root_number:02d}] {info.root_id} ({info.governance_area})")
                    lines.append(f"     Total Rules: {info.total_rules}")
                    lines.append(f"     Shards: {len(info.shards)}")

                    for shard_name, shard_info in sorted(info.shards.items()):
                        lines.append(f"       - {shard_name}: {shard_info.rule_count} rules")

        lines.append("\n" + "=" * 80)
        stats = self.get_statistics()
        lines.append(f"Active Roots: {stats['active_roots']}/{stats['total_roots']}")
        lines.append(f"Total Shards: {stats['total_shards']}")
        lines.append(f"Total Rules: {stats['total_rules']}")
        lines.append(f"Governance Areas: {stats['governance_areas']}")
        lines.append("=" * 80)

        return "\n".join(lines)


class RootShardMapper:
    """Convenience class for quick root/shard lookups"""

    def __init__(self):
        self.mapping = HierarchicalMapping()

    def get_coordinates(self, path: str) -> Optional[Tuple[str, str]]:
        """Quick coordinate lookup"""
        return self.mapping.map_file_to_coordinates(path)

    def get_full_id(self, path: str, rule_id: str) -> Optional[str]:
        """Quick full ID generation"""
        return self.mapping.register_rule(path, rule_id)

    def is_same_governance_area(self, path1: str, path2: str) -> bool:
        """Quick governance area check"""
        return self.mapping.check_governance_isolation(path1, path2)
