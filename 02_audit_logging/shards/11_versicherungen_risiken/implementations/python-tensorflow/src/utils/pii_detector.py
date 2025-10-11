"""PII detection - Runtime enforcement"""

import re
from typing import List, Dict, Any

# PII patterns
PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "phone": r"\b\d{3}[\s.-]?\d{3}[\s.-]?\d{4}\b",
    "passport": r"\b[A-Z]{1,2}\d{6,9}\b"
}

def detect_pii(data: str) -> Dict[str, List[str]]:
    """
    Detect PII in string data
    
    Returns:
        Dict mapping pattern name to list of matches
    """
    findings = {}
    for pattern_name, pattern in PATTERNS.items():
        matches = re.findall(pattern, data)
        if matches:
            findings[pattern_name] = matches
    return findings

def has_pii(data: str) -> bool:
    """Check if data contains any PII"""
    return bool(detect_pii(data))

def sanitize(data: str) -> str:
    """Replace PII with [REDACTED]"""
    result = data
    for pattern_name, pattern in PATTERNS.items():
        result = re.sub(pattern, f"[{pattern_name.upper()}_REDACTED]", result)
    return result
