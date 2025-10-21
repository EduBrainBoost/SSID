#!/usr/bin/env python3
"""
Remove xfail markers from all tests
Now that business logic is implemented, tests should pass
"""
import re
from pathlib import Path

TEST_DIR = Path("11_test_simulation/tests")

def remove_xfail_from_file(test_file):
    """Remove xfail markers from a test file"""
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count xfail markers
    xfail_count = content.count('@pytest.mark.xfail')

    if xfail_count == 0:
        return 0

    # Remove xfail markers
    # Pattern: @pytest.mark.xfail(reason="...")
    pattern = r'@pytest\.mark\.xfail\(reason="[^"]+"\)\s*\n'
    new_content = re.sub(pattern, '', content)

    # Write back
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return xfail_count

def main():
    """Remove xfail from all test files"""
    test_files = list(TEST_DIR.glob("test_*_policy_v6_0.py"))

    print("xfail Marker Removal Tool")
    print("=" * 60)

    total_removed = 0

    for test_file in sorted(test_files):
        removed = remove_xfail_from_file(test_file)
        total_removed += removed

        if removed > 0:
            print(f"[OK] {test_file.name}: Removed {removed} xfail markers")
        else:
            print(f"[SKIP] {test_file.name}: No xfail markers")

    print("=" * 60)
    print(f"Total xfail markers removed: {total_removed}")
    print(f"Tests are now expected to pass with real fixtures!")

if __name__ == "__main__":
    main()
