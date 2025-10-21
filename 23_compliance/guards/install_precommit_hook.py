#!/usr/bin/env python3
"""
Pre-Commit Hook Installer
Installs root-immunity pre-commit hook with UTF-8 enforcement
"""
import sys
import os
from pathlib import Path

if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(__file__).parent.parent.parent
git_dir = repo_root / '.git'
hooks_dir = git_dir / 'hooks'
hooks_dir.mkdir(parents=True, exist_ok=True)
hook_file = hooks_dir / 'pre-commit'

hook_script = """#!/usr/bin/env bash
export PYTHONIOENCODING=utf-8
python 23_compliance/guards/root_immunity_daemon.py --precommit
"""

with open(hook_file, 'w', encoding='utf-8', newline='\n') as f:
    f.write(hook_script)

if sys.platform != 'win32':
    os.chmod(hook_file, 0o755)

print(f"✅ Pre-commit hook installed: {hook_file}")
