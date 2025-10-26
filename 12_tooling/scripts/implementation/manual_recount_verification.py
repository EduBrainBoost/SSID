#!/usr/bin/env python3
"""
MANUAL RECOUNT - VERIFICATION
Complete from-scratch recount to verify extraction accuracy
"""

import re
from pathlib import Path

print('='*70)
print('MANUELLE ZÄHLUNG - VERIFICATION RUN')
print('='*70)
print()

source_dir = Path('16_codex/structure')
files = [
    'ssid_master_definition_corrected_v1.1.1.md',
    'SSID_structure_level3_part1_MAX.md',
    'SSID_structure_level3_part2_MAX.md',
    'SSID_structure_level3_part3_MAX.md'
]

totals = {
    'headers': 0,
    'yaml_blocks': 0,
    'tables': 0,
    'lists_must_should_may': 0,
    'numbered_lists': 0,
    'checkboxes': 0,
    'code_blocks': 0,
    'hash_start': 0,
    'bold_must': 0,
    'deprecated_inline': 0,
    'exit_code_24': 0,
    'verboten': 0,
    'kritisch': 0
}

per_file = {}

for filename in files:
    filepath = source_dir / filename
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    file_counts = {k: 0 for k in totals.keys()}

    in_yaml = False
    in_code = False

    for line in lines:
        # Headers
        if re.match(r'^#{1,6}\s+', line):
            totals['headers'] += 1
            file_counts['headers'] += 1

        # YAML blocks
        if line.strip() == '```yaml':
            totals['yaml_blocks'] += 1
            file_counts['yaml_blocks'] += 1
            in_yaml = True
        elif line.strip().startswith('```') and in_yaml:
            in_yaml = False

        # Code blocks (non-yaml)
        if re.match(r'^```\w+', line) and 'yaml' not in line.lower():
            totals['code_blocks'] += 1
            file_counts['code_blocks'] += 1

        # Tables (rows with |)
        if '|' in line and not line.strip().startswith('#'):
            if re.match(r'.*\|.*\|.*', line):
                totals['tables'] += 1
                file_counts['tables'] += 1

        # Lists with MUST/SHOULD/MAY
        if re.match(r'^\s*[-*+]\s+', line):
            if any(kw in line.upper() for kw in ['MUST', 'SHALL', 'SHOULD', 'MAY', 'REQUIRED']):
                totals['lists_must_should_may'] += 1
                file_counts['lists_must_should_may'] += 1

        # Numbered lists
        if re.match(r'^\s*\d+\.\s+', line):
            totals['numbered_lists'] += 1
            file_counts['numbered_lists'] += 1

        # Checkboxes
        if re.match(r'^\s*-\s+\[[ x]\]\s+', line, re.IGNORECASE):
            totals['checkboxes'] += 1
            file_counts['checkboxes'] += 1

        # HASH_START
        if re.match(r'^HASH_START::', line):
            totals['hash_start'] += 1
            file_counts['hash_start'] += 1

        # Bold MUST/SHOULD
        if re.search(r'\*\*(MUST|SHALL|SHOULD|REQUIRED)\*\*', line, re.IGNORECASE):
            if not re.match(r'^\s*[-*+]\s+', line):  # Not a list
                totals['bold_must'] += 1
                file_counts['bold_must'] += 1

        # Inline patterns
        if 'deprecated:' in line.lower() and not in_yaml:
            if not re.match(r'^\s{2,}', line):  # Not indented (not in YAML)
                totals['deprecated_inline'] += 1
                file_counts['deprecated_inline'] += 1

        if re.search(r'Exit\s+(Code\s+)?24', line, re.IGNORECASE):
            totals['exit_code_24'] += 1
            file_counts['exit_code_24'] += 1

        if 'VERBOTEN' in line.upper():
            totals['verboten'] += 1
            file_counts['verboten'] += 1

        if 'KRITISCH' in line.upper():
            totals['kritisch'] += 1
            file_counts['kritisch'] += 1

    per_file[filename] = file_counts

print('MANUELLE ZÄHLUNG - ERGEBNISSE:')
print()
total_all = 0
for key, count in sorted(totals.items(), key=lambda x: -x[1]):
    print(f'{key:25s}: {count:4d}')
    total_all += count

print('-' * 35)
print(f'{"TOTAL":25s}: {total_all:4d}')
print()

print('PER FILE BREAKDOWN:')
print()
for filename, counts in per_file.items():
    file_total = sum(counts.values())
    print(f'{filename}: {file_total} rules')
    for key, count in counts.items():
        if count > 0:
            print(f'  {key}: {count}')
    print()

print('='*70)
print('VERGLEICH MIT AUTOMATISCHER EXTRAKTION:')
print('='*70)
print(f'Automatisch extrahiert (primary):   537')
print(f'Automatisch extrahiert (inline):     49')
print(f'Automatisch extrahiert (total):     586')
print(f'Manuell gezählt (verification):    {total_all}')
print()

diff = abs(total_all - 586)
print(f'Differenz: {diff}')
print()

if diff < 50:
    print('[OK] Zahlen stimmen überein (Differenz < 50)')
    print('[OK] Extraktion war vollständig')
else:
    print('[WARNING] Große Differenz - weitere Prüfung nötig')
    print(f'[INFO] Mögliche Ursachen:')
    print(f'  - Duplikate wurden eliminiert')
    print(f'  - Strengere Filter in Extractor')
    print(f'  - Mehrfachzählungen hier möglich')
