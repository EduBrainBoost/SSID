#!/usr/bin/env python3
"""Fix all indentation issues in test files"""

import re
from pathlib import Path

def fix_file(file_path: Path) -> bool:
    """Fix indentation in a single file"""
    try:
        lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
        fixed = []
        changed = False

        for i, line in enumerate(lines):
            # Check if previous line was if statement and current line is pytest.skip without proper indent
            if i > 0 and line.strip().startswith('pytest.skip('):
                prev = lines[i-1]
                # Check if previous line is an if statement
                if prev.strip().endswith(':'):
                    # Calculate proper indentation (prev indent + 4 spaces)
                    prev_indent = len(prev) - len(prev.lstrip())
                    proper_indent = ' ' * (prev_indent + 4)

                    # If current line doesn't have proper indentation
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= prev_indent:
                        fixed_line = proper_indent + line.lstrip()
                        fixed.append(fixed_line)
                        changed = True
                        continue

            fixed.append(line)

        if changed:
            file_path.write_text(''.join(fixed), encoding='utf-8')
            return True
        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main execution"""
    repo_root = Path(__file__).resolve().parents[2]
    test_dir = repo_root / "11_test_simulation"

    fixed_count = 0
    for test_file in test_dir.rglob("test_*.py"):
        if fix_file(test_file):
            fixed_count += 1
            print(f"[FIXED] {test_file.relative_to(repo_root)}")

    print(f"\nTotal files fixed: {fixed_count}")
    return 0 if fixed_count > 0 else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
