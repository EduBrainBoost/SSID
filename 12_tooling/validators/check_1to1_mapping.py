#!/usr/bin/env python3
"""
Prüft 1:1:1:1:1 Manifestation aller SOT-Regeln

Jede Regel MUSS haben:
1. Eigene Python-Funktion
2. Eigene Rego-Policy
3. YAML-Contract-Eintrag
4. CLI-Command
5. Testfunktion
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '03_core'))

from validators.sot.sot_validator_core import ALL_VALIDATORS, RULE_PRIORITIES
from collections import Counter

def check_python_1to1():
    """Prüfe: Jede Regel hat eigene Python-Funktion"""
    print('=' * 80)
    print('PYTHON VALIDATOR FUNKTIONEN (1:1 Mapping)')
    print('=' * 80)

    print(f'\nTotal Regeln in ALL_VALIDATORS: {len(ALL_VALIDATORS)}')
    print(f'Total Prioritäten in RULE_PRIORITIES: {len(RULE_PRIORITIES)}')

    # Zeige erste 15 Regeln
    print('\n--- Erste 15 Regeln ---')
    for i, (rule_id, func) in enumerate(list(ALL_VALIDATORS.items())[:15]):
        priority = RULE_PRIORITIES.get(rule_id, 'UNKNOWN')
        func_name = func.__name__
        print(f'{rule_id} -> {func_name}() | Priority: {priority.upper()}')

    print(f'\n... und {len(ALL_VALIDATORS) - 15} weitere Regeln')

    # Prüfe Deduplizierung
    func_names = [func.__name__ for func in ALL_VALIDATORS.values()]
    unique_funcs = set(func_names)

    print(f'\n--- DEDUPLIZIERUNG ---')
    print(f'Total Funktionen: {len(func_names)}')
    print(f'Unique Funktionen: {len(unique_funcs)}')

    if len(func_names) != len(unique_funcs):
        print('\n❌ VERLETZUNG: Einige Funktionen werden mehrfach verwendet!')
        print('   -> Anti-Abstraction Principle VERLETZT')
        print('   -> Keine individuelle Auditierbarkeit!')

        duplicates = {name: count for name, count in Counter(func_names).items() if count > 1}
        print(f'\nGefundene Duplikate: {len(duplicates)}')

        for func_name, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True):
            rules_using_it = [rid for rid, f in ALL_VALIDATORS.items() if f.__name__ == func_name]
            print(f'\n  {func_name}() wird von {count} Regeln verwendet:')
            for rule_id in rules_using_it:
                priority = RULE_PRIORITIES.get(rule_id, 'unknown')
                print(f'    - {rule_id} (Priority: {priority})')

        return False
    else:
        print('\n✅ KONFORM: Jede Regel hat ihre eigene, dedizierte Funktion!')
        print('   -> Anti-Abstraction Principle eingehalten')
        print('   -> Individuelle Auditierbarkeit gegeben')
        return True

if __name__ == '__main__':
    python_ok = check_python_1to1()

    print('\n' + '=' * 80)
    print('ZUSAMMENFASSUNG')
    print('=' * 80)

    if python_ok:
        print('✅ Python: 1:1 Mapping korrekt')
    else:
        print('❌ Python: VERLETZUNG des 1:1 Mappings')
        print('\n🔧 LÖSUNG: Generiere individuelle Funktionen für jede Regel')
        print('   Benutze: 12_tooling/generators/sot_validator_generator_v2_append_only.py')

    sys.exit(0 if python_ok else 1)
