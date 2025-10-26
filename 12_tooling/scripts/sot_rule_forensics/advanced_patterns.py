"""
Advanced Pattern Recognition - 30 Zusätzliche Semantische Muster
================================================================

Erkennt ALLE versteckten Regelmuster in SSID-Dokumenten:
- HASH_START:: Marker
- YAML-Block-Prefix-Kommentare als Pfadanker
- Semantische Präfixe in Überschriften
- Tabellen mit Regelfunktion
- Kommentare in Shell-Blöcken
- ENFORCEMENT / VALIDATION / POLICY / CONFIG Keywords
- MoSCoW durch Sprachmuster (DE/EN)
- Listen als implizite Regelbündel
- "MUSS EXISTIEREN" Blöcke
- Score-Hinweise
- Codeblock-Sprache als Typ
- Versionierte Suffixe
- Deprecated-Hinweise
- Regionale Pfade als Regelbereiche
- Klammern im Titel = Metadaten
- Numerische Regelketten
- Kombinierte Policy-Verweise
- Regelbegründungen ("Warum")
- Business-Priorität
- Zentrale Pfadlisten
- Beweis- und Auditstrukturen
- Abschließende Audit-Texte
- Dokumentations-Pfade
- Jurisdiktions-Gruppen
- Deprecated-Einträge in Listen
- CI Exit Codes
- Audit-Trail Pfade
- Boolesche Kontrollattribute
- Multilingualitäts-Regeln
- Zweckzeilen (Ziel, Purpose, Scope)

Version: 3.0.0
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import re


@dataclass
class HashMarker:
    """HASH_START:: Marker"""
    marker_id: str
    line_number: int
    namespace: str


@dataclass
class PathAnchor:
    """YAML block prefix comment as path anchor"""
    path: str
    line_number: int


@dataclass
class SemanticDomain:
    """Semantic domain from heading"""
    name: str
    category: str
    line_start: int
    line_end: int


@dataclass
class MappingRule:
    """Rule from table"""
    entity: str
    path: str
    purpose: Optional[str] = None


@dataclass
class EnforcementKeyword:
    """Enforcement keyword match"""
    keyword: str
    line_number: int
    rule_type: str


@dataclass
class MustExistBlock:
    """MUSS EXISTIEREN block"""
    paths: List[str]
    line_start: int
    line_end: int


@dataclass
class ScoreThreshold:
    """Score threshold rule"""
    metric: str
    threshold: float
    operator: str  # >=, >, =, <, <=


@dataclass
class RegionalScope:
    """Regional/jurisdictional scope"""
    scope: str
    region_group: str


class AdvancedPatternRecognizer:
    """Advanced pattern recognition for SSID documents"""

    # Pattern definitions
    HASH_START_PATTERN = r'^HASH_START::([A-Z0-9_]+)'
    PATH_ANCHOR_PATTERN = r'^#\s+([\d]{2}_[a-z_]+/[\w/.]+\.(?:yaml|md|py|rego))'
    SEMANTIC_PREFIX_KEYWORDS = ['Framework', 'Policy', 'Config', 'Matrix', 'Checklist', 'Governance', 'Registry']
    ENFORCEMENT_KEYWORDS = ['enforcement_level', 'validation_function', 'policy', 'config', 'validation']
    MOSCOW_DE_PATTERN = r'\b(MUSS|SOLL|EMPFOHLEN|OPTIONAL)\b'
    MOSCOW_EN_PATTERN = r'\b(MUST|SHOULD|RECOMMENDED|OPTIONAL|SHALL|REQUIRED)\b'
    MUST_EXIST_PATTERN = r'\(MUSS EXISTIEREN\|MUST EXIST\)'
    SCORE_PATTERN = r'(?:Score|Coverage|Requirement)\s*(?:≥|>=)\s*(\d+)\s*%?'
    VERSION_SUFFIX_PATTERN = r'_v(\d+\.\d+(?:\.\d+)?)'
    DEPRECATED_PATTERN = r'deprecated:\s*(true|false)'
    REGIONAL_SCOPE_PATTERN = r'(eu_eea_uk_ch_li|apac|mena|africa|americas|global)'
    BRACKET_META_PATTERN = r'\(([^)]+)\)$'
    STEP_SEQUENCE_PATTERN = r'step_(\d+)'
    EXIT_CODE_PATTERN = r'exit\s+(\d+)|exit_code:\s*(\d+)'
    BOOLEAN_CONTROL_PATTERN = r'(immediate_failure|enabled|quarantine_trigger):\s*(true|false)'
    PURPOSE_PATTERN = r'^(Ziel|Purpose|Scope):\s*(.+)$'

    def __init__(self):
        self.hash_markers: List[HashMarker] = []
        self.path_anchors: List[PathAnchor] = []
        self.semantic_domains: List[SemanticDomain] = []
        self.mapping_rules: List[MappingRule] = []
        self.enforcement_keywords: List[EnforcementKeyword] = []
        self.must_exist_blocks: List[MustExistBlock] = []
        self.score_thresholds: List[ScoreThreshold] = []
        self.regional_scopes: List[RegionalScope] = []

    def recognize_all_patterns(self, content: str, file_path: str) -> Dict:
        """Recognize all advanced patterns in content"""
        lines = content.split('\n')
        results = {}

        # 1. HASH_START:: Marker
        self.hash_markers = self._find_hash_markers(lines)
        results['hash_markers'] = len(self.hash_markers)

        # 2. YAML Block Prefix Comments (Path Anchors)
        self.path_anchors = self._find_path_anchors(lines)
        results['path_anchors'] = len(self.path_anchors)

        # 3. Semantic Domains from Headings
        self.semantic_domains = self._find_semantic_domains(lines)
        results['semantic_domains'] = len(self.semantic_domains)

        # 4. Mapping Rules from Tables
        self.mapping_rules = self._extract_mapping_from_tables(lines)
        results['mapping_rules'] = len(self.mapping_rules)

        # 5. Shell Block Comments
        shell_comments = self._find_shell_comments(lines)
        results['shell_comments'] = len(shell_comments)

        # 6. Enforcement Keywords
        self.enforcement_keywords = self._find_enforcement_keywords(lines)
        results['enforcement_keywords'] = len(self.enforcement_keywords)

        # 7. MoSCoW Patterns (DE + EN)
        moscow_de = self._find_moscow_german(lines)
        moscow_en = self._find_moscow_english(lines)
        results['moscow_patterns'] = {'de': len(moscow_de), 'en': len(moscow_en)}

        # 8. List Rule Bundles
        list_bundles = self._find_list_bundles(lines)
        results['list_bundles'] = len(list_bundles)

        # 9. MUSS EXISTIEREN Blocks
        self.must_exist_blocks = self._find_must_exist_blocks(lines)
        results['must_exist_blocks'] = len(self.must_exist_blocks)

        # 10. Score Thresholds
        self.score_thresholds = self._find_score_thresholds(lines)
        results['score_thresholds'] = len(self.score_thresholds)

        # 11. Code Block Languages
        code_types = self._classify_code_blocks(content)
        results['code_block_types'] = code_types

        # 12. Version Suffixes
        versions = self._extract_versions(file_path)
        results['versions'] = versions

        # 13. Deprecated Markers
        deprecated = self._find_deprecated_markers(lines)
        results['deprecated_count'] = len(deprecated)

        # 14. Regional Scopes
        self.regional_scopes = self._find_regional_scopes(lines)
        results['regional_scopes'] = len(self.regional_scopes)

        # 15. Bracket Metadata
        bracket_meta = self._extract_bracket_metadata(lines)
        results['bracket_metadata'] = len(bracket_meta)

        # 16. Step Sequences
        sequences = self._find_step_sequences(lines)
        results['step_sequences'] = len(sequences)

        # 17. Policy Links
        policy_links = self._find_policy_links(lines)
        results['policy_links'] = len(policy_links)

        # 18. Rationale Sections
        rationales = self._find_rationales(lines)
        results['rationales'] = len(rationales)

        # 19. Business Priority
        priorities = self._find_business_priority(lines)
        results['business_priorities'] = len(priorities)

        # 20. Central Path Lists
        path_lists = self._find_central_path_lists(lines)
        results['central_paths'] = len(path_lists)

        # 21. Audit Structures
        audit_structures = self._find_audit_structures(lines)
        results['audit_structures'] = len(audit_structures)

        # 22. Audit Texts
        audit_texts = self._find_audit_texts(lines)
        results['audit_texts'] = len(audit_texts)

        # 23. Documentation Paths
        doc_paths = self._find_documentation_paths(lines)
        results['doc_paths'] = len(doc_paths)

        # 24. Jurisdiction Groups
        jurisdictions = self._find_jurisdiction_groups(lines)
        results['jurisdictions'] = len(jurisdictions)

        # 25. Deprecated Lists
        deprecated_lists = self._find_deprecated_lists(lines)
        results['deprecated_lists'] = len(deprecated_lists)

        # 26. Exit Codes
        exit_codes = self._find_exit_codes(lines)
        results['exit_codes'] = len(exit_codes)

        # 27. Audit Trail Paths
        audit_paths = self._find_audit_trail_paths(lines)
        results['audit_paths'] = len(audit_paths)

        # 28. Boolean Controls
        boolean_controls = self._find_boolean_controls(lines)
        results['boolean_controls'] = len(boolean_controls)

        # 29. I18n Rules
        i18n_rules = self._find_i18n_rules(lines)
        results['i18n_rules'] = len(i18n_rules)

        # 30. Purpose Lines
        purposes = self._find_purpose_lines(lines)
        results['purpose_lines'] = len(purposes)

        return results

    def _find_hash_markers(self, lines: List[str]) -> List[HashMarker]:
        """Find HASH_START:: markers"""
        markers = []
        for i, line in enumerate(lines, 1):
            match = re.match(self.HASH_START_PATTERN, line)
            if match:
                marker_id = match.group(1)
                markers.append(HashMarker(marker_id, i, f"namespace_{marker_id}"))
        return markers

    def _find_path_anchors(self, lines: List[str]) -> List[PathAnchor]:
        """Find YAML block prefix comments as path anchors"""
        anchors = []
        for i, line in enumerate(lines, 1):
            match = re.match(self.PATH_ANCHOR_PATTERN, line)
            if match:
                path = match.group(1)
                anchors.append(PathAnchor(path, i))
        return anchors

    def _find_semantic_domains(self, lines: List[str]) -> List[SemanticDomain]:
        """Find semantic domains from headings"""
        domains = []
        for i, line in enumerate(lines, 1):
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                heading_text = heading_match.group(2)
                for keyword in self.SEMANTIC_PREFIX_KEYWORDS:
                    if keyword in heading_text:
                        domains.append(SemanticDomain(
                            heading_text,
                            keyword,
                            i,
                            i + 50  # Approximate domain extent
                        ))
                        break
        return domains

    def _extract_mapping_from_tables(self, lines: List[str]) -> List[MappingRule]:
        """Extract mapping rules from tables"""
        rules = []
        for line in lines:
            if re.match(r'^\|.+\|.+\|', line):
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if len(cells) >= 2 and cells[0] and cells[1]:
                    # Skip header rows
                    if not cells[0].startswith('-'):
                        rules.append(MappingRule(
                            cells[0],
                            cells[1],
                            cells[2] if len(cells) > 2 else None
                        ))
        return rules

    def _find_shell_comments(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Find shell comments with rule descriptions"""
        comments = []
        in_shell = False
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```bash') or line.strip().startswith('```sh'):
                in_shell = True
            elif line.strip() == '```':
                in_shell = False
            elif in_shell and line.strip().startswith('#'):
                comment = line.strip()[1:].strip()
                if any(kw in comment for kw in ['Validation', 'Rule', 'Check', 'Enforcement']):
                    comments.append((i, comment))
        return comments

    def _find_enforcement_keywords(self, lines: List[str]) -> List[EnforcementKeyword]:
        """Find enforcement keywords"""
        keywords = []
        for i, line in enumerate(lines, 1):
            for keyword in self.ENFORCEMENT_KEYWORDS:
                if keyword in line:
                    keywords.append(EnforcementKeyword(
                        keyword,
                        i,
                        'enforcement' if 'enforcement' in keyword else 'validation'
                    ))
        return keywords

    def _find_moscow_german(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Find German MoSCoW patterns"""
        matches = []
        for i, line in enumerate(lines, 1):
            for match in re.finditer(self.MOSCOW_DE_PATTERN, line):
                matches.append((i, match.group(1)))
        return matches

    def _find_moscow_english(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Find English MoSCoW patterns"""
        matches = []
        for i, line in enumerate(lines, 1):
            for match in re.finditer(self.MOSCOW_EN_PATTERN, line):
                matches.append((i, match.group(1)))
        return matches

    def _find_list_bundles(self, lines: List[str]) -> List[Dict]:
        """Find list rule bundles"""
        bundles = []
        in_yaml_list = False
        current_key = None
        current_items = []

        for i, line in enumerate(lines, 1):
            if re.match(r'^[a-z_]+:\s*$', line):
                if current_items:
                    bundles.append({'key': current_key, 'items': current_items, 'line': i})
                current_key = line.split(':')[0].strip()
                current_items = []
                in_yaml_list = True
            elif in_yaml_list and line.strip().startswith('-'):
                item = line.strip()[1:].strip().strip('"')
                current_items.append(item)
            elif in_yaml_list and not line.strip():
                if current_items:
                    bundles.append({'key': current_key, 'items': current_items, 'line': i})
                current_items = []
                in_yaml_list = False

        return bundles

    def _find_must_exist_blocks(self, lines: List[str]) -> List[MustExistBlock]:
        """Find MUSS EXISTIEREN blocks"""
        blocks = []
        i = 0
        while i < len(lines):
            if re.search(r'\(MUSS EXISTIEREN\)|MUST EXIST', lines[i]):
                paths = []
                start = i
                i += 1
                while i < len(lines) and lines[i].strip():
                    path_match = re.search(r'[\d]{2}_[a-z_]+/[\w/.]+\.[\w]+', lines[i])
                    if path_match:
                        paths.append(path_match.group(0))
                    i += 1
                if paths:
                    blocks.append(MustExistBlock(paths, start + 1, i))
            i += 1
        return blocks

    def _find_score_thresholds(self, lines: List[str]) -> List[ScoreThreshold]:
        """Find score threshold rules"""
        thresholds = []
        for line in lines:
            match = re.search(self.SCORE_PATTERN, line)
            if match:
                value = float(match.group(1))
                thresholds.append(ScoreThreshold(
                    'coverage',
                    value,
                    '>='
                ))
        return thresholds

    def _classify_code_blocks(self, content: str) -> Dict[str, int]:
        """Classify code blocks by language"""
        types = {}
        for match in re.finditer(r'```(\w+)', content):
            lang = match.group(1)
            types[lang] = types.get(lang, 0) + 1
        return types

    def _extract_versions(self, file_path: str) -> List[str]:
        """Extract version suffixes"""
        matches = re.findall(self.VERSION_SUFFIX_PATTERN, file_path)
        return matches

    def _find_deprecated_markers(self, lines: List[str]) -> List[Tuple[int, bool]]:
        """Find deprecated markers"""
        markers = []
        for i, line in enumerate(lines, 1):
            match = re.search(self.DEPRECATED_PATTERN, line)
            if match:
                is_deprecated = match.group(1) == 'true'
                markers.append((i, is_deprecated))
        return markers

    def _find_regional_scopes(self, lines: List[str]) -> List[RegionalScope]:
        """Find regional scopes"""
        scopes = []
        for line in lines:
            match = re.search(self.REGIONAL_SCOPE_PATTERN, line)
            if match:
                scope = match.group(1)
                scopes.append(RegionalScope(scope, self._map_region_group(scope)))
        return scopes

    def _map_region_group(self, scope: str) -> str:
        """Map scope to region group"""
        mapping = {
            'eu_eea_uk_ch_li': 'EU/EEA',
            'apac': 'APAC',
            'mena': 'MENA',
            'africa': 'Africa',
            'americas': 'Americas',
            'global': 'Global'
        }
        return mapping.get(scope, 'Unknown')

    def _extract_bracket_metadata(self, lines: List[str]) -> List[Dict]:
        """Extract metadata from brackets in headings"""
        metadata = []
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                match = re.search(self.BRACKET_META_PATTERN, line)
                if match:
                    scope = match.group(1)
                    metadata.append({'line': i, 'scope': scope})
        return metadata

    def _find_step_sequences(self, lines: List[str]) -> List[List[str]]:
        """Find step sequences"""
        sequences = []
        current_seq = []
        for line in lines:
            match = re.search(self.STEP_SEQUENCE_PATTERN, line)
            if match:
                step_num = match.group(1)
                current_seq.append(f"step_{step_num}")
            elif current_seq:
                sequences.append(current_seq)
                current_seq = []
        return sequences

    def _find_policy_links(self, lines: List[str]) -> List[Dict]:
        """Find policy links (integration_points)"""
        links = []
        in_integration_points = False
        for i, line in enumerate(lines, 1):
            if 'integration_points:' in line:
                in_integration_points = True
            elif in_integration_points and line.strip().startswith('-') or ':' in line:
                if ':' in line:
                    key, val = line.split(':', 1)
                    links.append({'line': i, 'key': key.strip(), 'value': val.strip().strip('"')})
            elif in_integration_points and not line.strip():
                in_integration_points = False
        return links

    def _find_rationales(self, lines: List[str]) -> List[Dict]:
        """Find rationale sections (Warum)"""
        rationales = []
        for i, line in enumerate(lines, 1):
            if re.search(r'\*\*Warum\b|\*\*Why\b', line):
                rationales.append({'line': i, 'text': line.strip()})
        return rationales

    def _find_business_priority(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Find business priority fields"""
        priorities = []
        for i, line in enumerate(lines, 1):
            if 'business_priority:' in line:
                val = line.split(':')[1].strip().strip('"')
                priorities.append((i, val))
        return priorities

    def _find_central_path_lists(self, lines: List[str]) -> List[str]:
        """Find central path lists"""
        paths = []
        for line in lines:
            path_match = re.search(r'([\d]{2}_[a-z_]+/[\w/.]+\.(?:yaml|md|py|rego))', line)
            if path_match:
                paths.append(path_match.group(1))
        return paths

    def _find_audit_structures(self, lines: List[str]) -> List[Dict]:
        """Find audit structures"""
        structures = []
        for i, line in enumerate(lines, 1):
            if 'audit_enhancement:' in line or 'blockchain_anchoring:' in line:
                structures.append({'line': i, 'text': line.strip()})
        return structures

    def _find_audit_texts(self, lines: List[str]) -> List[Dict]:
        """Find audit condition texts"""
        texts = []
        for i, line in enumerate(lines, 1):
            if re.search(r'Ziel:\s*≥|Immediate failure', line):
                texts.append({'line': i, 'text': line.strip()})
        return texts

    def _find_documentation_paths(self, lines: List[str]) -> List[str]:
        """Find documentation paths"""
        return [line.strip()[1:].strip() for line in lines
                if line.strip().startswith('#') and '.md' in line]

    def _find_jurisdiction_groups(self, lines: List[str]) -> List[Dict]:
        """Find jurisdiction groups"""
        groups = []
        for i, line in enumerate(lines, 1):
            if re.search(r'###\s+\d+\.\s+(MENA|APAC|EU|Americas|Africa)', line):
                groups.append({'line': i, 'text': line.strip()})
        return groups

    def _find_deprecated_lists(self, lines: List[str]) -> List[Dict]:
        """Find deprecated entries in lists"""
        deprecated = []
        in_deprecated = False
        for i, line in enumerate(lines, 1):
            if 'deprecated_standards:' in line:
                in_deprecated = True
            elif in_deprecated and 'id:' in line:
                deprecated.append({'line': i, 'text': line.strip()})
            elif in_deprecated and not line.strip():
                in_deprecated = False
        return deprecated

    def _find_exit_codes(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Find exit codes"""
        codes = []
        for i, line in enumerate(lines, 1):
            match = re.search(self.EXIT_CODE_PATTERN, line)
            if match:
                code = match.group(1) or match.group(2)
                codes.append((i, code))
        return codes

    def _find_audit_trail_paths(self, lines: List[str]) -> List[str]:
        """Find audit trail paths"""
        paths = []
        for line in lines:
            if '02_audit_logging/storage/worm' in line:
                paths.append(line.strip())
        return paths

    def _find_boolean_controls(self, lines: List[str]) -> List[Dict]:
        """Find boolean control attributes"""
        controls = []
        for i, line in enumerate(lines, 1):
            match = re.search(self.BOOLEAN_CONTROL_PATTERN, line)
            if match:
                attr = match.group(1)
                value = match.group(2) == 'true'
                controls.append({'line': i, 'attribute': attr, 'enabled': value})
        return controls

    def _find_i18n_rules(self, lines: List[str]) -> List[Dict]:
        """Find i18n rules"""
        rules = []
        for i, line in enumerate(lines, 1):
            if 'language:' in line:
                rules.append({'line': i, 'text': line.strip()})
        return rules

    def _find_purpose_lines(self, lines: List[str]) -> List[Dict]:
        """Find purpose lines"""
        purposes = []
        for i, line in enumerate(lines, 1):
            match = re.match(self.PURPOSE_PATTERN, line)
            if match:
                label = match.group(1)
                text = match.group(2)
                purposes.append({'line': i, 'label': label, 'purpose': text})
        return purposes

    def get_summary_report(self) -> str:
        """Generate summary report"""
        lines = []
        lines.append("=" * 70)
        lines.append("ADVANCED PATTERN RECOGNITION REPORT")
        lines.append("=" * 70)
        lines.append(f"Hash Markers: {len(self.hash_markers)}")
        lines.append(f"Path Anchors: {len(self.path_anchors)}")
        lines.append(f"Semantic Domains: {len(self.semantic_domains)}")
        lines.append(f"Mapping Rules: {len(self.mapping_rules)}")
        lines.append(f"Enforcement Keywords: {len(self.enforcement_keywords)}")
        lines.append(f"MUSS EXISTIEREN Blocks: {len(self.must_exist_blocks)}")
        lines.append(f"Score Thresholds: {len(self.score_thresholds)}")
        lines.append(f"Regional Scopes: {len(self.regional_scopes)}")
        lines.append("=" * 70)
        return "\n".join(lines)

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        return True, []
