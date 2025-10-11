#!/usr/bin/env python3
"""
Logic-Gap-Tester: Validiert MUST-Logiken gegen SoT-Hashs
=============================================================================
Prüft, dass:
1. Alle MUST-Requirements aus SoT eine implementierte Logik haben
2. Jede Logik-Implementierung mit dem korrekten SoT-Hash referenziert wird
3. Keine Hash-Diskrepanzen zwischen SoT und Implementierung existieren
4. Alle MUST-Logiken getestet sind

Exit Codes:
  0 = Alle Checks erfolgreich
  1 = Logic-Gaps gefunden (fehlende Implementierungen)
  2 = Hash-Diskrepanzen gefunden
  3 = Konfigurationsfehler
"""

import sys
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

# --- KONFIGURATION ---
REPO_ROOT = Path(__file__).parent.parent
SOT_PATHS = [
    REPO_ROOT / "23_compliance" / "policies" / "sot_root24.yaml",
    REPO_ROOT / "23_compliance" / "policies" / "sot_nist.yaml",
]
IMPLEMENTATION_PATHS = [
    REPO_ROOT / "31_ml_analytics",
    REPO_ROOT / "41_devsecops_cicd",
    REPO_ROOT / "51_monitoring_siem",
]
TEST_PATHS = [
    REPO_ROOT / "11_test_simulation" / "tests",
]
LOG_FILE = REPO_ROOT / "02_audit_logging" / "logic_gap_tester.log"

# --- DATENSTRUKTUREN ---

@dataclass
class Requirement:
    """Repräsentiert ein einzelnes Requirement aus der SoT"""
    id: str
    level: str  # MUST, SHOULD, MAY
    description: str
    hash: str
    source_file: Path
    line_number: int = 0

@dataclass
class Implementation:
    """Repräsentiert eine Logik-Implementierung"""
    file: Path
    line_number: int
    requirement_id: str
    referenced_hash: Optional[str] = None
    code_snippet: str = ""

@dataclass
class TestCase:
    """Repräsentiert einen Test für ein Requirement"""
    file: Path
    line_number: int
    requirement_id: str
    test_name: str

@dataclass
class ValidationResult:
    """Ergebnis der Validierung"""
    missing_implementations: List[Requirement] = field(default_factory=list)
    hash_mismatches: List[Tuple[Requirement, Implementation]] = field(default_factory=list)
    untested_requirements: List[Requirement] = field(default_factory=list)
    orphaned_implementations: List[Implementation] = field(default_factory=list)
    total_requirements: int = 0
    total_must_requirements: int = 0
    implemented_count: int = 0
    tested_count: int = 0

# --- LOGGING SETUP ---

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- FARBEN FÜR TERMINAL OUTPUT ---

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

# --- SOT PARSING ---

def calculate_hash(content: str) -> str:
    """Berechnet SHA-256 Hash für gegebenen Content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def parse_sot_yaml(file_path: Path) -> List[Requirement]:
    """Parst SoT YAML und extrahiert Requirements mit Hashs"""
    requirements = []

    if not file_path.exists():
        logger.warning(f"SoT file not found: {file_path}")
        return requirements

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        current_req_id = None
        current_level = None
        current_desc_lines = []
        current_line_num = 0

        for line_num, line in enumerate(lines, 1):
            # Beispiel-Format: "  - id: REQ-ROOT24-001"
            id_match = re.match(r'\s*-?\s*id:\s*([A-Z0-9\-]+)', line, re.IGNORECASE)
            if id_match:
                # Speichere vorheriges Requirement
                if current_req_id and current_level:
                    req_text = f"{current_req_id} {current_level} {' '.join(current_desc_lines)}"
                    req_hash = calculate_hash(req_text)
                    requirements.append(Requirement(
                        id=current_req_id,
                        level=current_level,
                        description=' '.join(current_desc_lines),
                        hash=req_hash,
                        source_file=file_path,
                        line_number=current_line_num
                    ))

                # Starte neues Requirement
                current_req_id = id_match.group(1)
                current_desc_lines = []
                current_line_num = line_num
                continue

            # Level: MUST, SHOULD, MAY
            level_match = re.match(r'\s*level:\s*(MUST|SHOULD|MAY)', line, re.IGNORECASE)
            if level_match:
                current_level = level_match.group(1).upper()
                continue

            # Description
            desc_match = re.match(r'\s*description:\s*["\']?(.+?)["\']?\s*$', line)
            if desc_match:
                current_desc_lines.append(desc_match.group(1))
                continue

            # Multi-line description continuation
            if current_req_id and line.strip() and not line.strip().startswith('-'):
                if not re.match(r'\s*\w+:', line):  # Nicht ein neues Feld
                    current_desc_lines.append(line.strip())

        # Letztes Requirement speichern
        if current_req_id and current_level:
            req_text = f"{current_req_id} {current_level} {' '.join(current_desc_lines)}"
            req_hash = calculate_hash(req_text)
            requirements.append(Requirement(
                id=current_req_id,
                level=current_level,
                description=' '.join(current_desc_lines),
                hash=req_hash,
                source_file=file_path,
                line_number=current_line_num
            ))

        logger.info(f"Parsed {len(requirements)} requirements from {file_path.name}")

    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")

    return requirements

def load_all_requirements() -> Dict[str, Requirement]:
    """Lädt alle Requirements aus allen SoT-Dateien"""
    all_requirements = {}

    for sot_path in SOT_PATHS:
        requirements = parse_sot_yaml(sot_path)
        for req in requirements:
            if req.id in all_requirements:
                logger.warning(f"Duplicate requirement ID: {req.id}")
            all_requirements[req.id] = req

    return all_requirements

# --- IMPLEMENTATION PARSING ---

def find_implementations(search_paths: List[Path]) -> List[Implementation]:
    """Findet alle Implementierungen mit Requirement-Referenzen"""
    implementations = []

    # Pattern für Requirement-Referenzen im Code:
    # @req REQ-ROOT24-001 hash:abc123...
    # // Implements: REQ-ROOT24-001 (hash: abc123)
    # # Requirement: REQ-ROOT24-001 | hash: abc123
    patterns = [
        re.compile(r'@req[uirement]*\s+([A-Z0-9\-]+)(?:\s+hash:\s*([a-f0-9]+))?', re.IGNORECASE),
        re.compile(r'//\s*[Ii]mplements?:\s*([A-Z0-9\-]+)(?:\s*\(hash:\s*([a-f0-9]+)\))?'),
        re.compile(r'#\s*[Rr]equirement:\s*([A-Z0-9\-]+)(?:\s*\|\s*hash:\s*([a-f0-9]+))?'),
        re.compile(r'["\']requirement["\']:\s*["\']([A-Z0-9\-]+)["\'](?:,\s*["\']hash["\']:\s*["\']([a-f0-9]+)["\'])?'),
    ]

    for search_path in search_paths:
        if not search_path.exists():
            logger.warning(f"Implementation path not found: {search_path}")
            continue

        # Durchsuche alle Code-Dateien
        for file_path in search_path.rglob('*'):
            if not file_path.is_file():
                continue

            # Nur relevante Dateien
            if file_path.suffix not in ['.py', '.js', '.ts', '.go', '.java', '.yaml', '.yml', '.json', '.sh']:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        match = pattern.search(line)
                        if match:
                            req_id = match.group(1)
                            req_hash = match.group(2) if match.lastindex >= 2 else None

                            # Hole Code-Snippet (aktuelle + nächste 2 Zeilen)
                            snippet_lines = lines[line_num-1:line_num+2]
                            snippet = ''.join(snippet_lines).strip()[:200]

                            implementations.append(Implementation(
                                file=file_path,
                                line_number=line_num,
                                requirement_id=req_id,
                                referenced_hash=req_hash,
                                code_snippet=snippet
                            ))

            except Exception as e:
                logger.debug(f"Error reading {file_path}: {e}")

    logger.info(f"Found {len(implementations)} requirement implementations")
    return implementations

# --- TEST PARSING ---

def find_tests(search_paths: List[Path]) -> List[TestCase]:
    """Findet alle Tests für Requirements"""
    tests = []

    # Pattern für Test-Referenzen:
    # def test_req_root24_001():
    # test("REQ-ROOT24-001", ...)
    # it('should satisfy REQ-ROOT24-001', ...)
    patterns = [
        re.compile(r'def\s+test_\w*req[_\-]?([a-z0-9\-]+)', re.IGNORECASE),
        re.compile(r'test\s*\(\s*["\']([A-Z0-9\-]+)["\']'),
        re.compile(r'it\s*\(\s*["\'][^"\']*?([A-Z0-9\-]+)[^"\']*?["\']'),
        re.compile(r'@[Tt]est.*?([A-Z0-9\-]+)'),
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        for file_path in search_path.rglob('test_*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        match = pattern.search(line)
                        if match:
                            req_id_part = match.group(1).upper().replace('_', '-')

                            # Rekonstruiere volle ID
                            if not req_id_part.startswith('REQ-'):
                                req_id_part = f"REQ-{req_id_part}"

                            test_name = line.strip()[:100]

                            tests.append(TestCase(
                                file=file_path,
                                line_number=line_num,
                                requirement_id=req_id_part,
                                test_name=test_name
                            ))

            except Exception as e:
                logger.debug(f"Error reading {file_path}: {e}")

    logger.info(f"Found {len(tests)} requirement tests")
    return tests

# --- VALIDIERUNG ---

def validate_logic_gaps(
    requirements: Dict[str, Requirement],
    implementations: List[Implementation],
    tests: List[TestCase]
) -> ValidationResult:
    """Hauptvalidierung: Findet Logic-Gaps und Hash-Diskrepanzen"""

    result = ValidationResult()
    result.total_requirements = len(requirements)
    result.total_must_requirements = sum(1 for r in requirements.values() if r.level == 'MUST')

    # Erstelle Lookup-Sets
    implemented_ids = {impl.requirement_id for impl in implementations}
    tested_ids = {test.requirement_id for test in tests}

    # Index Implementations by ID
    impl_by_id: Dict[str, List[Implementation]] = {}
    for impl in implementations:
        impl_by_id.setdefault(impl.requirement_id, []).append(impl)

    # Check 1: Fehlende Implementierungen für MUST-Requirements
    for req_id, req in requirements.items():
        if req.level == 'MUST' and req_id not in implemented_ids:
            result.missing_implementations.append(req)

    # Check 2: Hash-Diskrepanzen
    for req_id, impls in impl_by_id.items():
        if req_id not in requirements:
            # Orphaned implementation
            result.orphaned_implementations.extend(impls)
            continue

        req = requirements[req_id]
        result.implemented_count += 1

        for impl in impls:
            if impl.referenced_hash and impl.referenced_hash != req.hash:
                result.hash_mismatches.append((req, impl))

    # Check 3: Fehlende Tests
    for req_id, req in requirements.items():
        if req.level == 'MUST' and req_id not in tested_ids:
            result.untested_requirements.append(req)

    result.tested_count = len(tested_ids.intersection(requirements.keys()))

    return result

# --- REPORTING ---

def print_results(result: ValidationResult):
    """Gibt Ergebnisse formatiert aus"""

    print(f"\n{Colors.BLUE}{'='*80}{Colors.NC}")
    print(f"{Colors.BLUE}Logic-Gap-Tester: Validation Results{Colors.NC}")
    print(f"{Colors.BLUE}{'='*80}{Colors.NC}\n")

    # Statistiken
    print(f"{Colors.CYAN}📊 Statistiken:{Colors.NC}")
    print(f"   Total Requirements:      {result.total_requirements}")
    print(f"   MUST Requirements:       {result.total_must_requirements}")
    print(f"   Implemented:             {result.implemented_count}")
    print(f"   Tested:                  {result.tested_count}")
    print()

    # Missing Implementations
    if result.missing_implementations:
        print(f"{Colors.RED}❌ Fehlende Implementierungen ({len(result.missing_implementations)}):{Colors.NC}")
        for req in result.missing_implementations[:10]:  # Top 10
            print(f"   • {req.id}: {req.description[:80]}")
            print(f"     Source: {req.source_file.name}:{req.line_number}")
        if len(result.missing_implementations) > 10:
            print(f"   ... und {len(result.missing_implementations) - 10} weitere")
        print()

    # Hash Mismatches
    if result.hash_mismatches:
        print(f"{Colors.RED}❌ Hash-Diskrepanzen ({len(result.hash_mismatches)}):{Colors.NC}")
        for req, impl in result.hash_mismatches[:5]:  # Top 5
            print(f"   • {req.id}")
            print(f"     SoT Hash:          {req.hash[:16]}...")
            print(f"     Implementation Hash: {impl.referenced_hash[:16] if impl.referenced_hash else 'None'}...")
            print(f"     File: {impl.file.name}:{impl.line_number}")
        if len(result.hash_mismatches) > 5:
            print(f"   ... und {len(result.hash_mismatches) - 5} weitere")
        print()

    # Untested Requirements
    if result.untested_requirements:
        print(f"{Colors.YELLOW}⚠️  Nicht getestete MUST-Requirements ({len(result.untested_requirements)}):{Colors.NC}")
        for req in result.untested_requirements[:10]:
            print(f"   • {req.id}: {req.description[:80]}")
        if len(result.untested_requirements) > 10:
            print(f"   ... und {len(result.untested_requirements) - 10} weitere")
        print()

    # Orphaned Implementations
    if result.orphaned_implementations:
        print(f"{Colors.YELLOW}⚠️  Verwaiste Implementierungen ({len(result.orphaned_implementations)}):{Colors.NC}")
        print(f"   (Implementierungen ohne zugehöriges Requirement)")
        for impl in result.orphaned_implementations[:5]:
            print(f"   • {impl.requirement_id} in {impl.file.name}:{impl.line_number}")
        print()

    # Zusammenfassung
    print(f"{Colors.BLUE}{'='*80}{Colors.NC}")

    if not result.missing_implementations and not result.hash_mismatches:
        print(f"{Colors.GREEN}✅ VALIDATION PASSED{Colors.NC}")
        print(f"Alle MUST-Requirements sind implementiert und Hash-konsistent.")
        return 0
    elif result.missing_implementations:
        print(f"{Colors.RED}❌ VALIDATION FAILED: Logic-Gaps gefunden{Colors.NC}")
        return 1
    elif result.hash_mismatches:
        print(f"{Colors.RED}❌ VALIDATION FAILED: Hash-Diskrepanzen gefunden{Colors.NC}")
        return 2

# --- MAIN ---

def main():
    """Hauptfunktion"""

    logger.info("Starting Logic-Gap-Tester")

    try:
        # Phase 1: Lade SoT Requirements
        print(f"{Colors.BLUE}Phase 1: Loading SoT Requirements...{Colors.NC}")
        requirements = load_all_requirements()

        if not requirements:
            logger.error("No requirements found in SoT files")
            print(f"{Colors.RED}❌ ERROR: Keine Requirements gefunden{Colors.NC}")
            return 3

        # Phase 2: Finde Implementierungen
        print(f"{Colors.BLUE}Phase 2: Scanning Implementations...{Colors.NC}")
        implementations = find_implementations(IMPLEMENTATION_PATHS)

        # Phase 3: Finde Tests
        print(f"{Colors.BLUE}Phase 3: Scanning Tests...{Colors.NC}")
        tests = find_tests(TEST_PATHS)

        # Phase 4: Validierung
        print(f"{Colors.BLUE}Phase 4: Validating Logic Gaps...{Colors.NC}")
        result = validate_logic_gaps(requirements, implementations, tests)

        # Phase 5: Reporting
        exit_code = print_results(result)

        logger.info(f"Logic-Gap-Tester completed with exit code {exit_code}")
        return exit_code

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"{Colors.RED}❌ FATAL ERROR: {e}{Colors.NC}")
        return 3

if __name__ == "__main__":
    sys.exit(main())
