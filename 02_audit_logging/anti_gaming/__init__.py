#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID Anti-Gaming Module
Detects and prevents reputation manipulation, gaming, and duplicate identities.
Autor: edubrainboost ©2025 MIT License
"""

__version__ = "1.0.0"
__author__ = "edubrainboost"

from pathlib import Path
import sys

# Import from new location
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "12_tooling" / "duplicate_checks"))
from detect_duplicate_identity_hashes import (
    build_index,
    detect_collisions,
    scan_dir,
    extract_candidates,
    log_findings
)

__all__ = [
    "build_index",
    "detect_collisions",
    "scan_dir",
    "extract_candidates",
    "log_findings"
]
