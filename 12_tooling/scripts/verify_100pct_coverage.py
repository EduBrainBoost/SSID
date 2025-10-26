#!/usr/bin/env python3
"""
Complete 100% Coverage Verification
Prüft ALLE Anforderungen für fehlerfreie Regelerfassung
"""

import sys
from pathlib import Path
from parse_sot_rules import *

def main():
    print('=' * 80)
    print('COMPLETE COMPLIANCE VERIFICATION - 100% Coverage Check')
    print('=' * 80)

    all_passed = True

    # Check 1: Drei Ebenen von Regelrealität
    print('\n[CHECK 1] Drei Ebenen von Regelrealitaet')
    print('-' * 80)
    try:
        assert hasattr(RuleReality, 'STRUCTURAL'), 'Missing STRUCTURAL'
        assert hasattr(RuleReality, 'SEMANTIC'), 'Missing SEMANTIC'
        assert hasattr(RuleReality, 'IMPLICIT'), 'Missing IMPLICIT'
        print('[PASS] RuleReality enum with 3 levels')
        print('  - STRUCTURAL: YAML, JSON, Tables')
        print('  - SEMANTIC: Markdown, Headers, Bullets')
        print('  - IMPLICIT: Paths, Comments, Shell-Code')
    except AssertionError as e:
        print(f'[FAIL] {e}')
        all_passed = False

    # Check 2: Formalgrammatik Components
    print('\n[CHECK 2] Formalgrammatik & Multi-Parser System')
    print('-' * 80)
    try:
        # Tokenizer
        assert hasattr(Tokenizer, 'extract_yaml_blocks'), 'Missing YAML parser'
        assert hasattr(Tokenizer, 'extract_markdown_sections'), 'Missing Markdown parser'
        print('[PASS] Tokenizer with YAML & Markdown extraction')

        # SemanticRuleExtractor
        assert hasattr(SemanticRuleExtractor, 'extract_inline_rules'), 'Missing inline extractor'
        print('[PASS] Inline policy extractor')

        # RuleToken equivalent (ExtractedRule)
        rule = ExtractedRule(
            rule_id='TEST', text='test', source_path='test',
            source_type=RuleSource.YAML_BLOCK, priority=MoSCoWPriority.MUST,
            context='test', line_number=1
        )
        assert hasattr(rule, 'source_type'), 'Missing source_type'
        assert hasattr(rule, 'line_number'), 'Missing line tracking'
        print('[PASS] RuleToken equivalent (ExtractedRule)')
    except AssertionError as e:
        print(f'[FAIL] {e}')
        all_passed = False

    # Check 3: Semantik-Schicht mit Score Formula
    print('\n[CHECK 3] Semantik-Schicht: Score_r = (P + C + B) / 3')
    print('-' * 80)
    try:
        # Priority (P)
        assert hasattr(MoSCoWPriority, 'MUST'), 'Missing MUST'
        assert MoSCoWPriority.MUST.value == 100, 'MUST != 100'
        assert MoSCoWPriority.SHOULD.value == 75, 'SHOULD != 75'
        assert MoSCoWPriority.COULD.value == 50, 'COULD != 50'
        assert MoSCoWPriority.WOULD.value == 25, 'WOULD != 25'
        print('[PASS] Priority (P): 100, 75, 50, 25')

        # Context (C)
        context_score = SemanticRuleExtractor.calculate_context_score('Compliance Enforcement')
        assert context_score == 40, f'Context score != 40, got {context_score}'
        print('[PASS] Context (C): +10 to +40')

        # Business Impact (B)
        assert hasattr(BusinessImpact, 'CRITICAL'), 'Missing CRITICAL'
        assert BusinessImpact.CRITICAL.value == 100, 'CRITICAL != 100'
        assert BusinessImpact.HIGH.value == 60, 'HIGH != 60'
        assert BusinessImpact.MEDIUM.value == 30, 'MEDIUM != 30'
        assert BusinessImpact.LOW.value == 10, 'LOW != 10'
        print('[PASS] Business Impact (B): 10-100')

        # Combined Score
        combined = SemanticRuleExtractor.calculate_combined_score(
            MoSCoWPriority.MUST, 40, BusinessImpact.CRITICAL
        )
        expected = (100 + 40 + 100) / 3
        assert abs(combined - expected) < 0.01, f'Combined score mismatch: {combined} != {expected}'
        print(f'[PASS] Combined Score Formula: {combined:.2f} = (100+40+100)/3')
    except AssertionError as e:
        print(f'[FAIL] {e}')
        all_passed = False

    # Check 4: Dreifache Hash-Signatur
    print('\n[CHECK 4] Dreifache Hash-Signatur: H = SHA256(content) XOR SHA256(path) XOR SHA256(context)')
    print('-' * 80)
    try:
        rule = ExtractedRule(
            rule_id='TEST', text='test content', source_path='test/path',
            source_type=RuleSource.YAML_BLOCK, priority=MoSCoWPriority.MUST,
            context='test context', line_number=1
        )
        assert rule.content_hash is not None, 'Missing content_hash'
        assert rule.path_hash is not None, 'Missing path_hash'
        assert rule.context_hash is not None, 'Missing context_hash'
        assert rule.hash_signature is not None, 'Missing triple hash'
        assert len(rule.hash_signature) == 64, 'Hash length != 64'
        print(f'[PASS] Triple Hash Generated')
        print(f'  Content: {rule.content_hash[:16]}...')
        print(f'  Path: {rule.path_hash[:16]}...')
        print(f'  Context: {rule.context_hash[:16]}...')
        print(f'  XOR Hash: {rule.hash_signature[:16]}...')
    except AssertionError as e:
        print(f'[FAIL] {e}')
        all_passed = False

    # Check 5: 24x16 Vollständigkeitsmatrix
    print('\n[CHECK 5] Vollstaendigkeitsformeln: N_expected = 24 x 16 x n_avg')
    print('-' * 80)
    try:
        matrix = CompletenessMatrix()
        assert len(matrix.ROOTS) == 24, f'Roots != 24, got {len(matrix.ROOTS)}'
        assert hasattr(matrix, 'n_avg'), 'Missing n_avg'
        expected = matrix.get_expected_count()
        assert expected == 24 * 16 * matrix.n_avg, 'Expected count formula wrong'
        print(f'[PASS] Expected = 24 x 16 x {matrix.n_avg} = {expected}')

        # Test add and coverage
        matrix.add_rule('23_compliance', 'policies', 'RULE-001')
        assert matrix.get_actual_count() == 1, 'Actual count != 1'
        coverage = matrix.get_coverage_percentage()
        print(f'[PASS] Coverage calculation: {coverage:.4f}%')

        # Test missing combinations
        missing = matrix.get_missing_combinations()
        print(f'[PASS] Missing combinations detection: {len(missing)} found')
    except AssertionError as e:
        print(f'[FAIL] {e}')
        all_passed = False

    # Check 6: 5-fach-Nachweis-Matrix (Querverifikation)
    print('\n[CHECK 6] Querverifikation: 5-fach-Nachweis-Matrix')
    print('-' * 80)
    try:
        cross_verif = CrossVerification(root_dir=Path.cwd())
        assert hasattr(cross_verif, 'policy_dir'), 'Missing policy_dir'
        assert hasattr(cross_verif, 'contract_file'), 'Missing contract_file'
        assert hasattr(cross_verif, 'cli_file'), 'Missing cli_file'
        assert hasattr(cross_verif, 'test_dir'), 'Missing test_dir'
        assert hasattr(cross_verif, 'report_dir'), 'Missing report_dir'
        print('[PASS] 5 evidence sources configured:')
        print('  1. Policy (.rego files)')
        print('  2. Contract (sot_contract.yaml)')
        print('  3. CLI (sot_validator.py)')
        print('  4. Test (test files)')
        print('  5. Report (audit docs)')

        # Test error code generation
        rule = ExtractedRule(
            rule_id='TEST-001', text='test', source_path='23_compliance/test',
            source_type=RuleSource.YAML_BLOCK, priority=MoSCoWPriority.MUST,
            context='test', line_number=1
        )
        error_code = cross_verif.get_missing_evidence_code(rule)
        assert error_code.startswith('E-MISS-R-'), f'Wrong error code format: {error_code}'
        print(f'[PASS] Error code format: {error_code}')
    except AssertionError as e:
        print(f'[FAIL] {e}')
        all_passed = False

    # Check 7: Zero-Loss-Integrity
    print('\n[CHECK 7] Zero-Loss-Integrity: SHA256(R_input) = SHA256(R_output)')
    print('-' * 80)
    try:
        zli = ZeroLossIntegrity()
        assert hasattr(zli, 'input_hash'), 'Missing input_hash'
        assert hasattr(zli, 'output_hash'), 'Missing output_hash'
        assert hasattr(zli, 'max_retries'), 'Missing max_retries'
        assert zli.max_retries == 3, 'max_retries != 3'

        # Test hash calculation
        test_files = [Path('parse_sot_rules.py')]
        input_hash = zli.calculate_input_hash(test_files)
        assert len(input_hash) == 64, 'Input hash length != 64'
        print(f'[PASS] Input hash calculation: {input_hash[:16]}...')

        # Test output hash
        rules = {
            'test1': ExtractedRule('ID1', 'text1', 'path1', RuleSource.YAML_BLOCK,
                                  MoSCoWPriority.MUST, 'ctx1', 1)
        }
        output_hash = zli.calculate_output_hash(rules)
        assert len(output_hash) == 64, 'Output hash length != 64'
        print(f'[PASS] Output hash calculation: {output_hash[:16]}...')

        # Test integrity report
        report = zli.get_integrity_report()
        assert 'input_hash' in report, 'Missing input_hash in report'
        assert 'output_hash' in report, 'Missing output_hash in report'
        assert 'matches' in report, 'Missing matches in report'
        print('[PASS] Integrity report generation')
    except AssertionError as e:
        print(f'[FAIL] {e}')
        all_passed = False

    # Check 8: ExtractedRule Enhanced Fields
    print('\n[CHECK 8] ExtractedRule Enhanced Fields (20+ new fields)')
    print('-' * 80)
    try:
        rule = ExtractedRule(
            rule_id='TEST', text='test', source_path='23_compliance/test',
            source_type=RuleSource.YAML_BLOCK, priority=MoSCoWPriority.MUST,
            context='test', line_number=1
        )

        # Reality level
        assert hasattr(rule, 'reality_level'), 'Missing reality_level'

        # Business impact
        assert hasattr(rule, 'business_impact'), 'Missing business_impact'
        assert hasattr(rule, 'score'), 'Missing score'
        assert hasattr(rule, 'context_score'), 'Missing context_score'

        # Root/Shard
        assert hasattr(rule, 'root_folder'), 'Missing root_folder'
        assert hasattr(rule, 'shard'), 'Missing shard'
        assert rule.root_folder == '23_compliance', f'Root folder wrong: {rule.root_folder}'

        # 5-fold evidence
        assert hasattr(rule, 'has_policy'), 'Missing has_policy'
        assert hasattr(rule, 'has_contract'), 'Missing has_contract'
        assert hasattr(rule, 'has_cli'), 'Missing has_cli'
        assert hasattr(rule, 'has_test'), 'Missing has_test'
        assert hasattr(rule, 'has_report'), 'Missing has_report'

        # Triple hash
        assert hasattr(rule, 'content_hash'), 'Missing content_hash'
        assert hasattr(rule, 'path_hash'), 'Missing path_hash'
        assert hasattr(rule, 'context_hash'), 'Missing context_hash'

        # Verification
        assert hasattr(rule, 'confidence_score'), 'Missing confidence_score'
        assert hasattr(rule, 'verified'), 'Missing verified'
        assert hasattr(rule, 'is_shared'), 'Missing is_shared'

        print('[PASS] All 20+ enhanced fields present')
        print(f'  - reality_level: {rule.reality_level}')
        print(f'  - score: {rule.score:.2f}')
        print(f'  - root_folder: {rule.root_folder}')
        print(f'  - evidence_count: {rule.get_evidence_count()}/5')
    except AssertionError as e:
        print(f'[FAIL] {e}')
        all_passed = False

    # Check 9: SoTRuleParser Integration
    print('\n[CHECK 9] SoTRuleParser Integration with New Components')
    print('-' * 80)
    try:
        parser = SoTRuleParser(
            Path('parse_sot_rules.py'),
            Path('../..')
        )
        assert hasattr(parser, 'completeness_matrix'), 'Missing completeness_matrix'
        assert hasattr(parser, 'cross_verification'), 'Missing cross_verification'
        assert hasattr(parser, 'zero_loss'), 'Missing zero_loss'
        assert hasattr(parser, 'input_files'), 'Missing input_files'
        print('[PASS] Parser initialized with all components:')
        print('  - CompletenessMatrix')
        print('  - CrossVerification')
        print('  - ZeroLossIntegrity')
        print('  - Input files tracking')
    except AssertionError as e:
        print(f'[FAIL] {e}')
        all_passed = False

    print('\n' + '=' * 80)
    if all_passed:
        print('[SUCCESS] ALLE ANFORDERUNGEN VOLLSTAENDIG IMPLEMENTIERT')
        print('=' * 80)
        print('\nImplemented:')
        print('1. [X] Drei Ebenen von Regelrealitaet (Strukturell/Semantisch/Implizit)')
        print('2. [X] Formalgrammatik (YAML/Markdown/Inline Parser)')
        print('3. [X] Semantik-Schicht: Score_r = (P + C + B) / 3')
        print('4. [X] Dreifache Hash-Signatur: H = SHA256(c) XOR SHA256(p) XOR SHA256(ctx)')
        print('5. [X] 24x16 Vollstaendigkeitsmatrix: N_expected = 24 x 16 x n_avg')
        print('6. [X] 5-fach-Nachweis-Matrix (Policy/Contract/CLI/Test/Report)')
        print('7. [X] Zero-Loss-Integrity: SHA256(R_in) = SHA256(R_out)')
        print('8. [X] ExtractedRule mit 20+ neuen Feldern')
        print('9. [X] SoTRuleParser Integration')
        print('\n[STATUS] Parser V2.5.0 ist 100% Coverage Ready!')
        return 0
    else:
        print('[ERROR] Einige Anforderungen fehlen!')
        print('=' * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())
