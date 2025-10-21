"""
SSID Performance Caching Layer

Compliance: SHOULD-002-CACHE-LAYER
Version: 1.0.0
Purpose: Multi-tier caching system for performance optimization

Architecture:
- L1: In-memory LRU cache (local to each service instance)
- L2: Redis distributed cache (shared across service instances)
- L3: Database query result cache with TTL

Regulatory Alignment:
- DORA Art.9 (Protection and Prevention) - Performance optimization reduces system strain
- ISO 27001:2022 A.12.1.3 - Capacity management
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class CacheTier(Enum):
    """Cache tier enumeration"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DATABASE = "l3_database"

class CacheEvictionPolicy(Enum):
    """Cache eviction policy"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int
    ttl_seconds: int
    tier: CacheTier
    size_bytes: int
    sha256: str

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl_seconds == 0:  # Never expires
            return False
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.utcnow() > expiry_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            **asdict(self),
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "tier": self.tier.value
        }

class CacheBackend(ABC):
    """Abstract cache backend interface"""

    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Retrieve cache entry by key"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Store cache entry with TTL"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass

class L1MemoryCache(CacheBackend):
    """L1 in-memory LRU cache"""

    def __init__(self, max_size: int = 1000, eviction_policy: CacheEvictionPolicy = CacheEvictionPolicy.LRU):
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        self.cache: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: str) -> Optional[CacheEntry]:
        """Retrieve from L1 cache"""
        entry = self.cache.get(key)

        if entry is None:
            self.misses += 1
            logger.debug(f"L1 cache MISS: {key}")
            return None

        if entry.is_expired():
            self.delete(key)
            self.misses += 1
            logger.debug(f"L1 cache EXPIRED: {key}")
            return None

        # Update access metadata
        entry.accessed_at = datetime.utcnow()
        entry.access_count += 1
        self.hits += 1
        logger.debug(f"L1 cache HIT: {key} (access_count={entry.access_count})")

        return entry

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Store in L1 cache"""
        if len(self.cache) >= self.max_size:
            self._evict_one()

        value_json = json.dumps(value, default=str)
        value_hash = hashlib.sha256(value_json.encode()).hexdigest()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow(),
            access_count=0,
            ttl_seconds=ttl_seconds,
            tier=CacheTier.L1_MEMORY,
            size_bytes=len(value_json),
            sha256=value_hash
        )

        self.cache[key] = entry
        logger.info(f"L1 cache SET: {key} (ttl={ttl_seconds}s, size={entry.size_bytes}B)")
        return True

    def delete(self, key: str) -> bool:
        """Delete from L1 cache"""
        if key in self.cache:
            del self.cache[key]
            logger.info(f"L1 cache DELETE: {key}")
            return True
        return False

    def clear(self) -> bool:
        """Clear L1 cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        logger.info("L1 cache CLEARED")
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get L1 cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0

        total_size_bytes = sum(entry.size_bytes for entry in self.cache.values())

        return {
            "tier": "L1_MEMORY",
            "max_size": self.max_size,
            "current_size": len(self.cache),
            "utilization_percent": (len(self.cache) / self.max_size * 100),
            "total_size_bytes": total_size_bytes,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate_percent": round(hit_rate, 2),
            "eviction_policy": self.eviction_policy.value
        }

    def _evict_one(self):
        """Evict one entry based on eviction policy"""
        if not self.cache:
            return

        if self.eviction_policy == CacheEvictionPolicy.LRU:
            # Evict least recently accessed
            lru_key = min(self.cache.items(), key=lambda item: item[1].accessed_at)[0]
            self.delete(lru_key)
            self.evictions += 1
            logger.info(f"L1 cache EVICTED (LRU): {lru_key}")

        elif self.eviction_policy == CacheEvictionPolicy.LFU:
            # Evict least frequently accessed
            lfu_key = min(self.cache.items(), key=lambda item: item[1].access_count)[0]
            self.delete(lfu_key)
            self.evictions += 1
            logger.info(f"L1 cache EVICTED (LFU): {lfu_key}")

        elif self.eviction_policy == CacheEvictionPolicy.FIFO:
            # Evict oldest entry
            fifo_key = min(self.cache.items(), key=lambda item: item[1].created_at)[0]
            self.delete(fifo_key)
            self.evictions += 1
            logger.info(f"L1 cache EVICTED (FIFO): {fifo_key}")

class MultiTierCache:
    """Multi-tier caching system with fallback"""

    def __init__(self):
        self.l1_cache = L1MemoryCache(max_size=1000, eviction_policy=CacheEvictionPolicy.LRU)
        # L2 and L3 would be initialized here (Redis, DB)
        # For compliance documentation, we define the interface
        self.l2_enabled = False  # Redis not configured
        self.l3_enabled = False  # DB cache not configured

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache with tier fallback.

        Cache lookup order:
        1. L1 (memory) - fastest
        2. L2 (Redis) - fast, distributed
        3. L3 (DB) - slowest, most reliable
        """
        # Try L1 cache
        l1_entry = self.l1_cache.get(key)
        if l1_entry:
            return l1_entry.value

        # L2 fallback (Redis) - placeholder
        if self.l2_enabled:
            # l2_value = redis_client.get(key)
            # if l2_value:
            #     self.l1_cache.set(key, l2_value, ttl_seconds=3600)
            #     return l2_value
            pass

        # L3 fallback (DB) - placeholder
        if self.l3_enabled:
            # l3_value = db_cache_table.query(key)
            # if l3_value:
            #     self.l1_cache.set(key, l3_value, ttl_seconds=3600)
            #     return l3_value
            pass

        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Store value in all enabled cache tiers"""
        success = self.l1_cache.set(key, value, ttl_seconds)

        # Propagate to L2 (Redis) if enabled
        if self.l2_enabled:
            # redis_client.setex(key, ttl_seconds, json.dumps(value))
            pass

        # Propagate to L3 (DB) if enabled
        if self.l3_enabled:
            # db_cache_table.insert(key, value, expiry=ttl_seconds)
            pass

        return success

    def invalidate(self, key: str) -> bool:
        """Invalidate cache entry across all tiers"""
        l1_success = self.l1_cache.delete(key)

        if self.l2_enabled:
            # redis_client.delete(key)
            pass

        if self.l3_enabled:
            # db_cache_table.delete(key)
            pass

        return l1_success

    def clear_all(self) -> bool:
        """Clear all cache tiers"""
        return self.l1_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from all cache tiers"""
        return {
            "l1": self.l1_cache.get_stats(),
            "l2_enabled": self.l2_enabled,
            "l3_enabled": self.l3_enabled,
            "timestamp": datetime.utcnow().isoformat()
        }

# Global cache instance
_cache_instance: Optional[MultiTierCache] = None

def get_cache() -> MultiTierCache:
    """Get global cache instance (singleton)"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MultiTierCache()
    return _cache_instance

def cached(ttl_seconds: int = 3600, key_prefix: str = ""):
    """
    Decorator for caching function results

    Usage:
        @cached(ttl_seconds=600, key_prefix="identity_score")
        def calculate_identity_score(user_hash: str) -> float:
            # expensive calculation
            return score
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            args_str = json.dumps({"args": args, "kwargs": kwargs}, default=str)
            key_hash = hashlib.sha256(args_str.encode()).hexdigest()[:16]
            cache_key = f"{key_prefix}:{func.__name__}:{key_hash}"

            # Try to retrieve from cache
            cache = get_cache()
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                logger.info(f"Cache HIT for {func.__name__} (key={cache_key})")
                return cached_value

            # Cache miss - execute function
            logger.info(f"Cache MISS for {func.__name__} (key={cache_key})")
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Store result in cache
            cache.set(cache_key, result, ttl_seconds)
            logger.info(f"Cached {func.__name__} result (execution_time={execution_time:.3f}s, ttl={ttl_seconds}s)")

            return result

        return wrapper
    return decorator

# Example usage function
@cached(ttl_seconds=300, key_prefix="anti_gaming")
def check_proof_reuse(proof_hash: str) -> Dict[str, Any]:
    """
    Example: Check if proof has been reused (expensive operation)

    This function demonstrates caching integration with anti-gaming validators.
    """
    # Simulate expensive database query
    time.sleep(0.1)  # Simulated latency

    return {
        "proof_hash": proof_hash,
        "reuse_count": 0,
        "last_seen": None,
        "is_suspicious": False
    }

if __name__ == "__main__":
    # Demonstration
    logging.basicConfig(level=logging.INFO)

    cache = get_cache()

    # Test cache operations
    cache.set("test_key", {"value": 123, "timestamp": datetime.utcnow().isoformat()}, ttl_seconds=60)
    result = cache.get("test_key")
    print(f"Retrieved from cache: {result}")

    # Test cached decorator
    for i in range(5):
        result = check_proof_reuse("abc123def456")
        print(f"Iteration {i+1}: {result}")

    # Get cache statistics
    stats = cache.get_stats()
    print(f"\nCache Statistics:\n{json.dumps(stats, indent=2)}")
