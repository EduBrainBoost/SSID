#!/usr/bin/env python3
"""
SoT Master-Definition Coverage Checker v1.0
============================================

Prüft alle 168 Master-Definition-Regeln gegen die 5 SoT-Artefakte:
1. Contract (16_codex/contracts/)
2. Core (03_core/, 01_ai_layer/, etc.)
3. Policy (23_compliance/opa/, chart.yaml policies)
4. CLI (Bash scripts, Python tools, CI/CD workflows)
5. Test (pytest, contract tests, validators)

Exit Codes:
  0 = 100% Coverage erreicht
  1 = Coverage < 100% (fehlende Regeln)
  2 = Fehler beim Ausführen

Autor: Claude Code AI
Datum: 2025-10-19
Version: 1.0.0-MASTER-COVERAGE
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
from collections import defaultdict

class SoTMasterCoverageChecker:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.master_rules_file = repo_root / "02_audit_logging" / "reports" / "SoT_Master_Definition_Rules_Manual_Extraction_20251019.yaml"

        # Output files
        self.report_yaml = repo_root / "02_audit_logging" / "reports" / "sot_master_coverage_report.yaml"
        self.report_md = repo_root / "02_audit_logging" / "reports" / "sot_master_coverage_report.md"

        # Artefakt-Pfade
        self.artefakt_paths = {
            'Contract': [
                repo_root / "16_codex" / "contracts",
                repo_root / "16_codex" / "structure"
            ],
            'Core': [
                repo_root / "03_core",
                repo_root / "01_ai_layer",
                repo_root / "02_audit_logging",
                repo_root / "04_deployment",
                repo_root / "06_data_pipeline",
                repo_root / "08_identity_score",
                repo_root / "09_meta_identity",
                repo_root / "10_interoperability"
            ],
            'Policy': [
                repo_root / "23_compliance" / "opa",
                repo_root / "07_governance_legal",
                repo_root / "16_codex" / "contracts" / "sot"
            ],
            'CLI': [
                repo_root / ".github" / "workflows",
                repo_root / "02_audit_logging" / "tools",
                repo_root / "04_deployment" / "ci"
            ],
            'Test': [
                repo_root / "11_test_simulation",
                repo_root / "02_audit_logging" / "validators"
            ],
            'Documentation': [
                repo_root / "05_documentation"
            ],
            'Registry': [
                repo_root / "24_meta_orchestration" / "registry"
            ],
            'All': []  # Will search everywhere
        }

        self.master_rules = []
        self.coverage_results = []
        self.summary = {
            'total_rules': 0,
            'covered': 0,
            'missing': 0,
            'duplicates': 0,
            'shadow_rules': 0,
            'ghost_rules': 0,
            'coverage_percentage': 0.0
        }

    def load_master_rules(self):
        """Lädt alle 168 Master-Definition-Regeln"""
        print(f"Loading Master-Definition rules from: {self.master_rules_file}")

        with open(self.master_rules_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        self.master_rules = data.get('rules', [])
        self.summary['total_rules'] = len(self.master_rules)

        print(f"  Loaded {len(self.master_rules)} rules")

    def search_artefakt(self, artefakt: str, regel: Dict) -> Tuple[bool, List[str]]:
        """
        Sucht nach einer Regel in einem spezifischen Artefakt.

        Returns:
            (found, file_paths) - ob gefunden und wo
        """
        regel_id = regel.get('regel_id', '')
        beschreibung = regel.get('beschreibung', '').lower()
        kategorie = regel.get('kategorie', '').lower()

        # Suchbegriffe aus Regel extrahieren
        search_terms = self.extract_search_terms(regel)

        # Pfade für Artefakt
        if artefakt == 'All':
            search_paths = [self.repo_root]
        else:
            search_paths = self.artefakt_paths.get(artefakt, [])

        found_files = []

        for base_path in search_paths:
            if not base_path.exists():
                continue

            # Durchsuche alle relevanten Dateien
            for file_path in self.find_relevant_files(base_path, artefakt):
                if self.check_file_for_rule(file_path, search_terms, regel):
                    found_files.append(str(file_path.relative_to(self.repo_root)))

        return (len(found_files) > 0, found_files)

    def extract_search_terms(self, regel: Dict) -> Set[str]:
        """Extrahiert Suchbegriffe aus einer Regel"""
        terms = set()

        # Regel-ID
        regel_id = regel.get('regel_id', '')
        if regel_id:
            terms.add(regel_id.lower())

        # Kategorie-spezifische Terme
        kategorie = regel.get('kategorie', '').lower()

        if 'chart.yaml' in kategorie:
            terms.update(['chart.yaml', 'chart_version', 'capabilities'])
        elif 'manifest.yaml' in kategorie:
            terms.update(['manifest.yaml', 'implementation', 'tech_stack'])
        elif 'root' in kategorie and 'definition' in kategorie:
            # Root-spezifische Begriffe
            zeilen = str(regel.get('zeilen', ''))
            if regel.get('beschreibung'):
                desc = regel['beschreibung'].lower()
                # Extrahiere Root-Nummer/Namen
                if 'root' in desc:
                    terms.add('root')
        elif 'shard' in kategorie and 'definition' in kategorie:
            terms.add('shard')
        elif 'governance' in kategorie:
            terms.update(['governance', 'rfc', 'approval'])
        elif 'policy' in kategorie:
            terms.add('policy')
            if 'non-custodial' in kategorie:
                terms.update(['non_custodial', 'hash_only', 'pii'])
            if 'gdpr' in kategorie:
                terms.update(['gdpr', 'erasure', 'portability'])
        elif 'opa' in kategorie:
            terms.update(['opa', 'rego', 'constraint'])
        elif 'amendment' in kategorie:
            if 'regulatory matrix' in kategorie.lower():
                terms.update(['country_specific', 'uk', 'singapore', 'japan', 'australia'])
            elif 'sanctions' in kategorie.lower():
                terms.update(['sanctions', 'ofac', 'entities_to_check'])
            elif 'dora' in kategorie.lower():
                terms.update(['dora', 'incident_response'])

        # Feld-Namen
        feld = regel.get('feld', '')
        if feld:
            terms.add(feld.lower().replace('.', '_'))

        # Wichtige Wörter aus Beschreibung
        beschreibung = regel.get('beschreibung', '')
        if beschreibung:
            # Extrahiere Schlüsselwörter
            key_words = self.extract_keywords(beschreibung)
            terms.update(key_words)

        return terms

    def extract_keywords(self, text: str) -> Set[str]:
        """Extrahiert Schlüsselwörter aus Text"""
        # Entferne sehr generische Wörter
        stopwords = {'der', 'die', 'das', 'und', 'oder', 'für', 'mit', 'von', 'zu', 'in', 'ist', 'sind', 'werden', 'wird', 'alle', 'jede', 'jeder'}

        words = text.lower().split()
        keywords = set()

        for word in words:
            # Entferne Satzzeichen
            word = word.strip('.,;:()[]{}!?')

            # Nur Wörter >= 4 Zeichen, keine Stopwords
            if len(word) >= 4 and word not in stopwords:
                keywords.add(word)

        return keywords

    def find_relevant_files(self, base_path: Path, artefakt: str) -> List[Path]:
        """Findet relevante Dateien für ein Artefakt"""
        relevant_files = []

        # Dateitypen pro Artefakt
        extensions = {
            'Contract': ['.yaml', '.yml', '.json', '.md'],
            'Core': ['.py', '.go', '.rs', '.yaml', '.yml'],
            'Policy': ['.rego', '.yaml', '.yml', '.json'],
            'CLI': ['.sh', '.py', '.yml', '.yaml'],
            'Test': ['.py', '.sh', '.yaml'],
            'Documentation': ['.md', '.rst'],
            'Registry': ['.yaml', '.yml', '.json'],
            'All': ['.py', '.yaml', '.yml', '.json', '.rego', '.sh', '.md']
        }

        exts = extensions.get(artefakt, ['.yaml', '.yml', '.json', '.py'])

        # Durchsuche rekursiv
        for ext in exts:
            relevant_files.extend(base_path.rglob(f'*{ext}'))

        return relevant_files

    def check_file_for_rule(self, file_path: Path, search_terms: Set[str], regel: Dict) -> bool:
        """Prüft ob eine Datei eine Regel implementiert"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()

            # Mindestens ein Suchbegriff muss vorkommen
            matches = sum(1 for term in search_terms if term in content)

            # Schwellwert: mindestens 2 Matches oder 1 sehr spezifischer Match
            regel_id = regel.get('regel_id', '').lower()
            if regel_id in content:
                return True  # Direkte Regel-ID-Referenz

            if matches >= 2:
                return True

            return False

        except Exception as e:
            return False

    def check_coverage(self):
        """Prüft Coverage für alle Regeln"""
        print(f"\nChecking coverage for {len(self.master_rules)} rules...")

        for i, regel in enumerate(self.master_rules, 1):
            regel_id = regel.get('regel_id', f'UNKNOWN-{i}')
            betroffene = regel.get('betroffene_artefakte', [])

            if i % 20 == 0:
                print(f"  Progress: {i}/{len(self.master_rules)} rules checked...")

            coverage = {
                'regel_id': regel_id,
                'kategorie': regel.get('kategorie', ''),
                'enforcement': regel.get('enforcement', ''),
                'priority': regel.get('priority', ''),
                'betroffene_artefakte': betroffene,
                'coverage_status': {},
                'found_in_files': {},
                'status': 'MISSING'
            }

            # Prüfe jedes betroffene Artefakt
            covered_count = 0
            for artefakt in betroffene:
                found, files = self.search_artefakt(artefakt, regel)
                coverage['coverage_status'][artefakt] = 'COVERED' if found else 'MISSING'
                coverage['found_in_files'][artefakt] = files

                if found:
                    covered_count += 1

            # Gesamtstatus
            if covered_count == len(betroffene):
                coverage['status'] = 'COVERED'
                self.summary['covered'] += 1
            elif covered_count > 0:
                coverage['status'] = 'PARTIAL'
                self.summary['missing'] += 1
            else:
                coverage['status'] = 'MISSING'
                self.summary['missing'] += 1

            self.coverage_results.append(coverage)

        # Berechne Coverage-Prozentsatz
        if self.summary['total_rules'] > 0:
            self.summary['coverage_percentage'] = (self.summary['covered'] / self.summary['total_rules']) * 100

    def generate_reports(self):
        """Generiert YAML und Markdown Reports"""
        print(f"\nGenerating coverage reports...")

        # YAML Report
        yaml_report = {
            'metadata': {
                'version': '1.0.0',
                'generated': datetime.now().isoformat(),
                'master_rules_file': str(self.master_rules_file.relative_to(self.repo_root)),
                'total_rules_checked': self.summary['total_rules']
            },
            'summary': self.summary,
            'coverage_details': self.coverage_results
        }

        with open(self.report_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"  YAML report: {self.report_yaml}")

        # Markdown Report
        self.generate_markdown_report()
        print(f"  Markdown report: {self.report_md}")

    def generate_markdown_report(self):
        """Generiert Markdown Coverage Report"""
        md_lines = [
            "# SoT Master-Definition Coverage Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Master Rules File:** `{self.master_rules_file.relative_to(self.repo_root)}`  ",
            "",
            "## Summary",
            "",
            f"- **Total Rules:** {self.summary['total_rules']}",
            f"- **Covered:** {self.summary['covered']} ({self.summary['coverage_percentage']:.1f}%)",
            f"- **Missing/Partial:** {self.summary['missing']}",
            "",
            "## Coverage Status",
            ""
        ]

        if self.summary['coverage_percentage'] == 100.0:
            md_lines.append("✅ **100% COVERAGE ACHIEVED**")
        else:
            md_lines.append(f"⚠️ **Coverage: {self.summary['coverage_percentage']:.1f}% - Missing Rules Detected**")

        md_lines.extend([
            "",
            "## Coverage by Priority",
            ""
        ])

        # Gruppiere nach Priority
        by_priority = defaultdict(lambda: {'total': 0, 'covered': 0})
        for result in self.coverage_results:
            priority = result.get('priority', 'UNKNOWN')
            by_priority[priority]['total'] += 1
            if result['status'] == 'COVERED':
                by_priority[priority]['covered'] += 1

        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            if priority in by_priority:
                data = by_priority[priority]
                pct = (data['covered'] / data['total'] * 100) if data['total'] > 0 else 0
                md_lines.append(f"- **{priority}:** {data['covered']}/{data['total']} ({pct:.1f}%)")

        md_lines.extend([
            "",
            "## Missing/Partial Coverage Rules",
            ""
        ])

        # Liste fehlende Regeln
        missing_rules = [r for r in self.coverage_results if r['status'] in ['MISSING', 'PARTIAL']]

        if not missing_rules:
            md_lines.append("✅ No missing rules!")
        else:
            md_lines.append(f"⚠️ **{len(missing_rules)} rules with missing/partial coverage:**")
            md_lines.append("")

            for rule in missing_rules:
                md_lines.append(f"### {rule['regel_id']} - {rule['kategorie']}")
                md_lines.append(f"- **Priority:** {rule['priority']}")
                md_lines.append(f"- **Enforcement:** {rule['enforcement']}")
                md_lines.append(f"- **Status:** {rule['status']}")
                md_lines.append(f"- **Betroffene Artefakte:**")

                for artefakt, status in rule['coverage_status'].items():
                    icon = "✅" if status == "COVERED" else "❌"
                    files = rule['found_in_files'].get(artefakt, [])
                    file_info = f" ({len(files)} files)" if files else ""
                    md_lines.append(f"  - {icon} {artefakt}: {status}{file_info}")

                md_lines.append("")

        # Schreibe Markdown
        with open(self.report_md, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))

    def run(self) -> int:
        """Hauptausführung"""
        print("="*80)
        print("SOT MASTER-DEFINITION COVERAGE CHECKER v1.0")
        print("="*80)

        try:
            self.load_master_rules()
            self.check_coverage()
            self.generate_reports()

            print("\n" + "="*80)
            print("COVERAGE SUMMARY")
            print("="*80)
            print(f"Total Rules:      {self.summary['total_rules']}")
            print(f"Covered:          {self.summary['covered']} ({self.summary['coverage_percentage']:.1f}%)")
            print(f"Missing/Partial:  {self.summary['missing']}")
            print("="*80)

            if self.summary['coverage_percentage'] == 100.0:
                print("✅ SUCCESS: 100% Coverage achieved!")
                return 0
            else:
                print(f"⚠️  WARNING: Coverage is {self.summary['coverage_percentage']:.1f}% (< 100%)")
                print(f"   Review report: {self.report_md}")
                return 1

        except Exception as e:
            print(f"\n❌ ERROR: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 2

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    checker = SoTMasterCoverageChecker(repo_root)
    return checker.run()

if __name__ == "__main__":
    sys.exit(main())
