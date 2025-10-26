"""
Layer 9-10: Duplikat-Cluster & Version-Tracker
==============================================

Semantic clustering and duplicate detection
Version tracking and evolution history

Version: 3.0.0
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class DuplicateCluster:
    """Cluster of duplicate or similar rules"""
    cluster_id: str
    rules: List[str] = field(default_factory=list)
    similarity_score: float = 1.0
    cluster_type: str = 'exact'  # 'exact', 'semantic', 'partial'


@dataclass
class RuleVersion:
    """Version information for a rule"""
    rule_id: str
    version: str
    timestamp: datetime
    changes: str
    hash_signature: str


class SemanticSimilarity:
    """Semantic similarity calculator"""

    @staticmethod
    def cosine_similarity(text1: str, text2: str) -> float:
        """Simple cosine similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def jaccard_similarity(text1: str, text2: str) -> float:
        """Jaccard similarity coefficient"""
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0


class DuplicateDetector:
    """Duplicate and similarity detection"""

    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.clusters: List[DuplicateCluster] = []
        self.hash_map: Dict[str, List[str]] = {}

    def add_rule(self, rule_id: str, content: str, content_hash: str):
        """Add rule for duplicate detection"""
        if content_hash in self.hash_map:
            self.hash_map[content_hash].append(rule_id)
        else:
            self.hash_map[content_hash] = [rule_id]

    def find_duplicates(self) -> List[DuplicateCluster]:
        """Find exact duplicate clusters"""
        clusters = []

        for content_hash, rule_ids in self.hash_map.items():
            if len(rule_ids) > 1:
                cluster = DuplicateCluster(
                    cluster_id=f"DUP-{content_hash[:8]}",
                    rules=rule_ids,
                    similarity_score=1.0,
                    cluster_type='exact'
                )
                clusters.append(cluster)

        self.clusters.extend(clusters)
        return clusters

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []

        # Check for empty clusters
        empty_clusters = [c for c in self.clusters if len(c.rules) == 0]
        if empty_clusters:
            issues.append(f"{len(empty_clusters)} empty clusters found")

        return len(issues) == 0, issues


class VersionTracker:
    """Track rule evolution and version history"""

    def __init__(self):
        self.versions: Dict[str, List[RuleVersion]] = {}

    def add_version(self, rule_id: str, version: str, changes: str, content: str):
        """Add new version of a rule"""
        hash_sig = hashlib.sha256(content.encode()).hexdigest()

        version_obj = RuleVersion(
            rule_id=rule_id,
            version=version,
            timestamp=datetime.now(),
            changes=changes,
            hash_signature=hash_sig
        )

        if rule_id not in self.versions:
            self.versions[rule_id] = []

        self.versions[rule_id].append(version_obj)

    def get_version_history(self, rule_id: str) -> List[RuleVersion]:
        """Get all versions of a rule"""
        return self.versions.get(rule_id, [])

    def get_latest_version(self, rule_id: str) -> Optional[RuleVersion]:
        """Get latest version of a rule"""
        versions = self.versions.get(rule_id, [])
        return versions[-1] if versions else None

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []

        # Check for duplicate versions
        for rule_id, versions in self.versions.items():
            version_strings = [v.version for v in versions]
            if len(version_strings) != len(set(version_strings)):
                issues.append(f"Duplicate versions for {rule_id}")

        return len(issues) == 0, issues
