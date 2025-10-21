"""Hashing utilities - SHA3-256"""

import hashlib
from typing import Optional

_PEPPER: Optional[str] = None

def init_hasher(pepper: Optional[str] = None):
    """Initialize hasher with optional pepper"""
    global _PEPPER
    _PEPPER = pepper

def hash_data(data: str, pepper: Optional[str] = None) -> str:
    """
    Hash data using SHA3-256
    
    Args:
        data: Raw data to hash
        pepper: Optional per-tenant pepper (overrides global)
    
    Returns:
        64-character hex string
    """
    use_pepper = pepper or _PEPPER or ""
    combined = f"{use_pepper}{data}"
    return hashlib.sha3_256(combined.encode()).hexdigest()

def validate_hash(hash_str: str) -> bool:
    """Validate hash format"""
    if not isinstance(hash_str, str):
        return False
    if len(hash_str) != 64:
        return False
    try:
        int(hash_str, 16)
        return True
    except ValueError:
        return False
