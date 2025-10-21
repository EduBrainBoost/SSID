#!/usr/bin/env python3
"""
Result Cache - Persistent Validation Result Caching
====================================================

Implements persistent result caching with file hash-based invalidation
for dramatic speedup on repeated validation runs.

Performance Targets:
- First run: ~15s (with parallel execution)
- Cached run (no changes): <1s (15x speedup)
- Partial changes: Only re-validate affected rules
- Cache hit rate: >95% in typical development

Features:
- SHA256 file hash tracking
- Persistent JSON storage
- Granular invalidation (per-rule)
- TTL-based expiration (24 hours default)
- Cache size limits with LRU eviction
- Cache statistics (hit/miss rates, age, size)

Usage:
    cache = ResultCache(cache_dir=Path(".ssid_cache"))

    # Try to get cached result
    result = cache.get_cached_result("AR001")
    if result is None:
        # Cache miss - run validation
        result = validator.validate_ar001()
        cache.store_result("AR001", result)
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Optional, List, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

# Import ValidationResult from core
try:
    from sot_validator_core import ValidationResult, Severity
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from sot_validator_core import ValidationResult, Severity


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class CachedResult:
    """
    Cached validation result with file hash tracking.

    Attributes:
        rule_id: Rule identifier (e.g., AR001)
        result: ValidationResult as dict
        timestamp: When result was cached
        file_hashes: Dict mapping file paths to their SHA256 hashes
        file_count: Number of files tracked
    """
    rule_id: str
    result: Dict[str, Any]  # ValidationResult serialized
    timestamp: float
    file_hashes: Dict[str, str]  # file_path -> SHA256 hash
    file_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'rule_id': self.rule_id,
            'result': self.result,
            'timestamp': self.timestamp,
            'file_hashes': self.file_hashes,
            'file_count': self.file_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CachedResult':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            rule_id=data['rule_id'],
            result=data['result'],
            timestamp=data['timestamp'],
            file_hashes=data.get('file_hashes', {}),
            file_count=data.get('file_count', 0)
        )


@dataclass
class CacheMetadata:
    """
    Cache metadata and statistics.

    Tracks overall cache health, size, and performance.
    """
    version: str = "1.0"
    created: str = ""
    last_updated: str = ""
    total_entries: int = 0
    total_size_bytes: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    invalidations: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheMetadata':
        return cls(**data)


# ============================================================
# RESULT CACHE
# ============================================================

class ResultCache:
    """
    Persistent result cache with file hash-based invalidation.

    Features:
    - Persistent JSON storage (.ssid_cache/validation_results.json)
    - File hash tracking (SHA256)
    - TTL-based expiration (default: 24 hours)
    - Granular invalidation (per-rule)
    - Cache size limits (default: 100MB)
    - LRU eviction when size limit exceeded

    Performance:
    - Cache hit: <0.001s (instant)
    - Cache miss: Full validation time
    - Hash computation: <0.1s overhead
    """

    def __init__(
        self,
        cache_dir: Path,
        repo_root: Path,
        ttl: int = 86400,  # 24 hours
        max_size_mb: int = 100
    ):
        """
        Initialize result cache.

        Args:
            cache_dir: Directory for cache storage (e.g., .ssid_cache)
            repo_root: Repository root path (for resolving file paths)
            ttl: Time-to-live in seconds (default: 86400 = 24 hours)
            max_size_mb: Maximum cache size in MB (default: 100)
        """
        self.cache_dir = Path(cache_dir)
        self.repo_root = Path(repo_root).resolve()
        self.ttl = ttl
        self.max_size_bytes = max_size_mb * 1024 * 1024

        # Cache files
        self.cache_file = self.cache_dir / "validation_results.json"
        self.metadata_file = self.cache_dir / "cache_metadata.json"

        # In-memory cache
        self._cache: Dict[str, CachedResult] = {}
        self._metadata: CacheMetadata = CacheMetadata()

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load existing cache
        self._load_cache()

        # Statistics
        self.session_hits = 0
        self.session_misses = 0
        self.session_stores = 0
        self.session_invalidations = 0

    # ============================================================
    # CORE CACHE OPERATIONS
    # ============================================================

    def get_cached_result(self, rule_id: str) -> Optional[ValidationResult]:
        """
        Get cached validation result if valid.

        Returns None if:
        - No cached result exists
        - Cache has expired (TTL)
        - Any tracked file has changed (hash mismatch)

        Args:
            rule_id: Rule identifier (e.g., AR001)

        Returns:
            ValidationResult if cache valid, None otherwise
        """
        # Check if result is cached
        if rule_id not in self._cache:
            self.session_misses += 1
            self._metadata.cache_misses += 1
            return None

        cached = self._cache[rule_id]

        # Check TTL expiration
        age = time.time() - cached.timestamp
        if age > self.ttl:
            self.session_misses += 1
            self._metadata.cache_misses += 1
            self._invalidate_entry(rule_id, reason="TTL expired")
            return None

        # Check file hashes (validate cache integrity)
        for file_path_str, old_hash in cached.file_hashes.items():
            file_path = Path(file_path_str)

            # Skip if file no longer exists (will be invalidated)
            if not file_path.exists():
                self.session_misses += 1
                self._metadata.cache_misses += 1
                self._invalidate_entry(rule_id, reason=f"File deleted: {file_path_str}")
                return None

            # Compute current hash
            current_hash = self._compute_file_hash(file_path)

            # Hash mismatch = file changed = cache invalid
            if current_hash != old_hash:
                self.session_misses += 1
                self._metadata.cache_misses += 1
                self._invalidate_entry(rule_id, reason=f"File modified: {file_path_str}")
                return None

        # Cache is valid - return result
        self.session_hits += 1
        self._metadata.cache_hits += 1

        # Reconstruct ValidationResult from dict
        result_dict = cached.result

        # Handle Severity enum
        if 'severity' in result_dict:
            if isinstance(result_dict['severity'], str):
                result_dict['severity'] = Severity[result_dict['severity']]

        return ValidationResult(**result_dict)

    def store_result(self, rule_id: str, result: ValidationResult, relevant_files: Optional[List[Path]] = None):
        """
        Store validation result in cache with file hash tracking.

        Args:
            rule_id: Rule identifier (e.g., AR001)
            result: ValidationResult to cache
            relevant_files: List of files that affect this rule (optional)
                          If None, will auto-detect based on rule_id
        """
        # Determine relevant files if not provided
        if relevant_files is None:
            relevant_files = self._get_relevant_files(rule_id)

        # Compute file hashes
        file_hashes = {}
        for file_path in relevant_files:
            if file_path.exists():
                file_hash = self._compute_file_hash(file_path)
                # Store relative path for portability
                rel_path = self._get_relative_path(file_path)
                file_hashes[str(rel_path)] = file_hash

        # Convert ValidationResult to dict
        result_dict = result.to_dict()

        # Handle Severity enum serialization
        if 'severity' in result_dict and hasattr(result_dict['severity'], 'value'):
            result_dict['severity'] = result_dict['severity'].value

        # Create cached entry
        cached = CachedResult(
            rule_id=rule_id,
            result=result_dict,
            timestamp=time.time(),
            file_hashes=file_hashes,
            file_count=len(file_hashes)
        )

        # Store in memory
        self._cache[rule_id] = cached

        # Update statistics
        self.session_stores += 1
        self._metadata.total_entries = len(self._cache)
        self._metadata.last_updated = datetime.utcnow().isoformat()

        # Persist to disk
        self._save_cache()

        # Check cache size and evict if needed
        self._enforce_size_limit()

    def invalidate(self, rule_id: str):
        """Manually invalidate a specific rule's cached result"""
        if rule_id in self._cache:
            self._invalidate_entry(rule_id, reason="Manual invalidation")
            self._save_cache()

    def invalidate_all(self):
        """Clear entire cache"""
        self._cache.clear()
        self._metadata.total_entries = 0
        self._metadata.invalidations += len(self._cache)
        self.session_invalidations += len(self._cache)
        self._save_cache()

    def find_affected_rules(self, file_path: Path) -> List[str]:
        """
        Find all rules affected by a file change.

        Args:
            file_path: Path to changed file

        Returns:
            List of rule IDs that track this file
        """
        affected = []
        rel_path = str(self._get_relative_path(file_path))

        for rule_id, cached in self._cache.items():
            if rel_path in cached.file_hashes:
                affected.append(rule_id)

        return affected

    # ============================================================
    # FILE HASH COMPUTATION
    # ============================================================

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of file contents.

        Args:
            file_path: Path to file

        Returns:
            Hex-encoded SHA256 hash
        """
        sha256 = hashlib.sha256()

        try:
            with open(file_path, 'rb') as f:
                # Read in chunks for memory efficiency
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            # If file can't be read, return empty hash
            return ""

    def _get_relative_path(self, file_path: Path) -> Path:
        """Convert absolute path to relative path from repo root"""
        try:
            return file_path.resolve().relative_to(self.repo_root)
        except ValueError:
            # If not relative to repo_root, return as-is
            return file_path

    # ============================================================
    # RELEVANT FILE DETECTION
    # ============================================================

    def _get_relevant_files(self, rule_id: str) -> List[Path]:
        """
        Determine which files affect a specific rule.

        This is critical for cache invalidation granularity.

        Args:
            rule_id: Rule identifier

        Returns:
            List of file paths that affect this rule
        """
        files = []

        # AR001-AR010: Architecture rules - depend on directory structure
        if rule_id.startswith('AR'):
            # Track all root directories
            for root_dir in self.repo_root.iterdir():
                if root_dir.is_dir() and not root_dir.name.startswith('.'):
                    # Track existence, not content
                    # For now, track Chart.yaml in each shard as proxy
                    for shard_dir in root_dir.iterdir():
                        if shard_dir.is_dir():
                            chart_file = shard_dir / "Chart.yaml"
                            if chart_file.exists():
                                files.append(chart_file)

        # CP001: Chart Policy - All Chart.yaml files
        elif rule_id == 'CP001':
            files.extend(self.repo_root.glob('**/Chart.yaml'))

        # VP001: Values Policy - All values.yaml files
        elif rule_id == 'VP001':
            files.extend(self.repo_root.glob('**/values.yaml'))

        # Python-related rules
        elif rule_id.startswith('PY') or 'PYTHON' in rule_id:
            files.extend(self.repo_root.glob('**/*.py'))

        # YAML-related rules
        elif 'YAML' in rule_id or rule_id.startswith('YA'):
            files.extend(self.repo_root.glob('**/*.yaml'))
            files.extend(self.repo_root.glob('**/*.yml'))

        # Template rules
        elif 'TEMPLATE' in rule_id or rule_id.startswith('TP'):
            files.extend(self.repo_root.glob('**/templates/**/*.yaml'))

        # Manifest rules
        elif 'MANIFEST' in rule_id or rule_id.startswith('MS'):
            files.extend(self.repo_root.glob('**/manifest.yaml'))

        # Policy rules
        elif 'POLICY' in rule_id or rule_id.startswith('PO'):
            files.extend(self.repo_root.glob('**/policies/**/*.yaml'))

        # Default: Track all YAML files (conservative)
        else:
            files.extend(self.repo_root.glob('**/*.yaml'))
            files.extend(self.repo_root.glob('**/*.yml'))

        # Limit to reasonable number to avoid performance issues
        # Sort by modification time, take most recent 100 files
        if len(files) > 100:
            files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:100]

        return list(files)

    # ============================================================
    # CACHE PERSISTENCE
    # ============================================================

    def _load_cache(self):
        """Load cache from disk"""
        # Load metadata
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    metadata_dict = json.load(f)
                    self._metadata = CacheMetadata.from_dict(metadata_dict)
            except Exception as e:
                # Corrupted metadata, start fresh
                self._metadata = CacheMetadata(
                    created=datetime.utcnow().isoformat()
                )
        else:
            self._metadata = CacheMetadata(
                created=datetime.utcnow().isoformat()
            )

        # Load cache entries
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_dict = json.load(f)

                    for rule_id, entry_dict in cache_dict.items():
                        self._cache[rule_id] = CachedResult.from_dict(entry_dict)
            except Exception as e:
                # Corrupted cache, start fresh
                self._cache = {}

    def _save_cache(self):
        """Persist cache to disk"""
        # Save metadata
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self._metadata.to_dict(), f, indent=2)
        except Exception as e:
            pass  # Non-fatal

        # Save cache entries
        try:
            cache_dict = {
                rule_id: cached.to_dict()
                for rule_id, cached in self._cache.items()
            }

            with open(self.cache_file, 'w') as f:
                json.dump(cache_dict, f, indent=2)
        except Exception as e:
            pass  # Non-fatal

    # ============================================================
    # CACHE MANAGEMENT
    # ============================================================

    def _invalidate_entry(self, rule_id: str, reason: str = ""):
        """Internal: Invalidate single cache entry"""
        if rule_id in self._cache:
            del self._cache[rule_id]
            self._metadata.invalidations += 1
            self.session_invalidations += 1
            self._metadata.total_entries = len(self._cache)

    def _enforce_size_limit(self):
        """Enforce cache size limit with LRU eviction"""
        # Calculate current cache size
        current_size = 0
        if self.cache_file.exists():
            current_size = self.cache_file.stat().st_size

        self._metadata.total_size_bytes = current_size

        # If under limit, nothing to do
        if current_size <= self.max_size_bytes:
            return

        # LRU eviction - sort by timestamp, remove oldest
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda item: item[1].timestamp
        )

        # Evict oldest entries until under limit
        evicted = 0
        for rule_id, cached in sorted_entries:
            if current_size <= self.max_size_bytes:
                break

            # Estimate entry size (rough)
            entry_size = len(json.dumps(cached.to_dict()))
            current_size -= entry_size

            del self._cache[rule_id]
            evicted += 1

        if evicted > 0:
            self._metadata.total_entries = len(self._cache)
            self._save_cache()

    def get_cache_size_mb(self) -> float:
        """Get current cache size in MB"""
        if self.cache_file.exists():
            size_bytes = self.cache_file.stat().st_size
            return size_bytes / (1024 * 1024)
        return 0.0

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._metadata.cache_hits + self._metadata.cache_misses
        hit_rate = (self._metadata.cache_hits / total_requests * 100) if total_requests > 0 else 0

        session_total = self.session_hits + self.session_misses
        session_hit_rate = (self.session_hits / session_total * 100) if session_total > 0 else 0

        return {
            # Overall stats
            'total_entries': self._metadata.total_entries,
            'cache_size_mb': self.get_cache_size_mb(),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),

            # Lifetime stats
            'lifetime_hits': self._metadata.cache_hits,
            'lifetime_misses': self._metadata.cache_misses,
            'lifetime_total': total_requests,
            'lifetime_hit_rate': f"{hit_rate:.2f}%",
            'lifetime_invalidations': self._metadata.invalidations,

            # Session stats
            'session_hits': self.session_hits,
            'session_misses': self.session_misses,
            'session_total': session_total,
            'session_hit_rate': f"{session_hit_rate:.2f}%",
            'session_stores': self.session_stores,
            'session_invalidations': self.session_invalidations,

            # Metadata
            'cache_created': self._metadata.created,
            'cache_updated': self._metadata.last_updated,
            'ttl_seconds': self.ttl,
        }

    def print_stats(self):
        """Print cache statistics to console"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("RESULT CACHE STATISTICS")
        print("="*60)
        print(f"Total Entries:      {stats['total_entries']}")
        print(f"Cache Size:         {stats['cache_size_mb']:.2f} MB / {stats['max_size_mb']:.0f} MB")
        print(f"TTL:                {stats['ttl_seconds']}s ({stats['ttl_seconds']/3600:.1f}h)")
        print()
        print("Lifetime Performance:")
        print(f"  Hits:             {stats['lifetime_hits']}")
        print(f"  Misses:           {stats['lifetime_misses']}")
        print(f"  Hit Rate:         {stats['lifetime_hit_rate']}")
        print(f"  Invalidations:    {stats['lifetime_invalidations']}")
        print()
        print("Session Performance:")
        print(f"  Hits:             {stats['session_hits']}")
        print(f"  Misses:           {stats['session_misses']}")
        print(f"  Hit Rate:         {stats['session_hit_rate']}")
        print(f"  Stores:           {stats['session_stores']}")
        print(f"  Invalidations:    {stats['session_invalidations']}")
        print()
        print(f"Created:            {stats['cache_created']}")
        print(f"Last Updated:       {stats['cache_updated']}")
        print("="*60 + "\n")


# ============================================================
# DEMO / TESTING
# ============================================================

if __name__ == "__main__":
    import sys

    # Get repo root
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    cache_dir = repo_root / ".ssid_cache"

    print(f"Repository: {repo_root}")
    print(f"Cache Dir:  {cache_dir}\n")

    # Create cache
    print("[INIT] Creating ResultCache...")
    cache = ResultCache(
        cache_dir=cache_dir,
        repo_root=repo_root,
        ttl=3600  # 1 hour
    )

    print(f"Loaded {cache._metadata.total_entries} cached entries\n")

    # Demo: Create and store a fake result
    print("[STORE] Storing test result for AR001...")

    from sot_validator_core import ValidationResult, Severity

    test_result = ValidationResult(
        rule_id="AR001",
        passed=True,
        severity=Severity.CRITICAL,
        message="Test validation result",
        evidence={"test": True}
    )

    cache.store_result("AR001", test_result)
    print("Stored!\n")

    # Demo: Retrieve from cache
    print("[RETRIEVE] Retrieving AR001 from cache...")
    cached_result = cache.get_cached_result("AR001")

    if cached_result:
        print(f"[HIT] Retrieved from cache: {cached_result.message}")
    else:
        print("[MISS] Not in cache or invalidated")

    print()

    # Print stats
    cache.print_stats()

    print("[OK] Result cache demo complete!")
