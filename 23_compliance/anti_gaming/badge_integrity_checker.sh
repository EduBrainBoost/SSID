#!/usr/bin/env bash
# Badge Integrity Checker Wrapper
# Calls the Python implementation
python3 "$(dirname "$0")/badge_integrity_checker.py" "$@"
