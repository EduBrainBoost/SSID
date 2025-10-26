"""
Layer 3: Alias-Erkennung & Synonym-Lexikon
==========================================

Erkennt Synonyme und Aliase für Policy-Keywords:
- MUST = SHALL = REQUIRED
- SHOULD = RECOMMENDED
- MAY = OPTIONAL
- MUST NOT = SHALL NOT

Version: 3.0.0
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from enum import Enum


class PolicyLevel(Enum):
    """RFC 2119 Policy Levels"""
    MUST = "MUST"
    SHOULD = "SHOULD"
    MAY = "MAY"
    MUST_NOT = "MUST_NOT"
    UNKNOWN = "UNKNOWN"


@dataclass
class SynonymMatch:
    """Detected synonym match"""
    original_text: str
    normalized_form: str
    policy_level: PolicyLevel
    confidence: float
    line_number: int
    column: int


class SynonymLexicon:
    """RFC 2119 compliant synonym lexicon for policy keywords"""

    # Exact RFC 2119 mappings
    SYNONYM_MAP = {
        # MUST level (100% required)
        'MUST': PolicyLevel.MUST,
        'SHALL': PolicyLevel.MUST,
        'REQUIRED': PolicyLevel.MUST,
        'MANDATORY': PolicyLevel.MUST,
        'NEEDS TO': PolicyLevel.MUST,
        'HAS TO': PolicyLevel.MUST,
        'MUSS': PolicyLevel.MUST,  # German
        'ERFORDERLICH': PolicyLevel.MUST,  # German

        # SHOULD level (recommended)
        'SHOULD': PolicyLevel.SHOULD,
        'RECOMMENDED': PolicyLevel.SHOULD,
        'OUGHT TO': PolicyLevel.SHOULD,
        'SUGGESTED': PolicyLevel.SHOULD,
        'SOLLTE': PolicyLevel.SHOULD,  # German
        'EMPFOHLEN': PolicyLevel.SHOULD,  # German

        # MAY level (optional)
        'MAY': PolicyLevel.MAY,
        'OPTIONAL': PolicyLevel.MAY,
        'CAN': PolicyLevel.MAY,
        'MIGHT': PolicyLevel.MAY,
        'COULD': PolicyLevel.MAY,
        'KANN': PolicyLevel.MAY,  # German
        'DARF': PolicyLevel.MAY,  # German

        # MUST NOT level (forbidden)
        'MUST NOT': PolicyLevel.MUST_NOT,
        'SHALL NOT': PolicyLevel.MUST_NOT,
        'FORBIDDEN': PolicyLevel.MUST_NOT,
        'PROHIBITED': PolicyLevel.MUST_NOT,
        'NOT ALLOWED': PolicyLevel.MUST_NOT,
        'DARF NICHT': PolicyLevel.MUST_NOT,  # German
        'VERBOTEN': PolicyLevel.MUST_NOT,  # German
    }

    # Confidence scores for different match types
    CONFIDENCE_EXACT = 1.0
    CONFIDENCE_CASE_INSENSITIVE = 0.95
    CONFIDENCE_WORD_BOUNDARY = 0.90
    CONFIDENCE_PARTIAL = 0.75

    def __init__(self):
        self.synonym_map = self.SYNONYM_MAP.copy()
        self.custom_synonyms: Dict[str, PolicyLevel] = {}

    def add_custom_synonym(self, keyword: str, policy_level: PolicyLevel):
        """Add custom synonym mapping"""
        self.custom_synonyms[keyword.upper()] = policy_level

    def normalize_keyword(self, keyword: str) -> Optional[PolicyLevel]:
        """Normalize a keyword to its policy level

        Args:
            keyword: Policy keyword to normalize

        Returns:
            PolicyLevel or None if not recognized
        """
        # Check custom synonyms first
        normalized = keyword.upper()
        if normalized in self.custom_synonyms:
            return self.custom_synonyms[normalized]

        # Check built-in synonyms
        if normalized in self.synonym_map:
            return self.synonym_map[normalized]

        return None

    def find_synonyms(self, text: str, line_number: int = 0) -> List[SynonymMatch]:
        """Find all synonym matches in text

        Args:
            text: Text to search
            line_number: Line number for tracking

        Returns:
            List of SynonymMatch objects
        """
        matches = []

        # Search for all keywords
        for keyword, policy_level in {**self.synonym_map, **self.custom_synonyms}.items():
            # Try exact match first
            if keyword in text:
                idx = text.find(keyword)
                matches.append(SynonymMatch(
                    original_text=keyword,
                    normalized_form=policy_level.value,
                    policy_level=policy_level,
                    confidence=self.CONFIDENCE_EXACT,
                    line_number=line_number,
                    column=idx
                ))
                continue

            # Try case-insensitive
            if keyword.lower() in text.lower():
                idx = text.lower().find(keyword.lower())
                matched_text = text[idx:idx+len(keyword)]
                matches.append(SynonymMatch(
                    original_text=matched_text,
                    normalized_form=policy_level.value,
                    policy_level=policy_level,
                    confidence=self.CONFIDENCE_CASE_INSENSITIVE,
                    line_number=line_number,
                    column=idx
                ))

        return matches

    def get_policy_level_name(self, level: PolicyLevel) -> str:
        """Get human-readable name for policy level"""
        names = {
            PolicyLevel.MUST: "Required (MUST)",
            PolicyLevel.SHOULD: "Recommended (SHOULD)",
            PolicyLevel.MAY: "Optional (MAY)",
            PolicyLevel.MUST_NOT: "Forbidden (MUST NOT)",
            PolicyLevel.UNKNOWN: "Unknown"
        }
        return names.get(level, "Unknown")

    def get_all_synonyms_for_level(self, level: PolicyLevel) -> List[str]:
        """Get all synonyms for a given policy level"""
        synonyms = []
        for keyword, policy_level in {**self.synonym_map, **self.custom_synonyms}.items():
            if policy_level == level:
                synonyms.append(keyword)
        return sorted(synonyms)

    def get_statistics(self) -> Dict[str, int]:
        """Get synonym lexicon statistics"""
        stats = {
            'total_synonyms': len(self.synonym_map) + len(self.custom_synonyms),
            'built_in': len(self.synonym_map),
            'custom': len(self.custom_synonyms)
        }

        # Count by policy level
        for level in PolicyLevel:
            count = sum(1 for pl in {**self.synonym_map, **self.custom_synonyms}.values() if pl == level)
            stats[f'{level.value}_count'] = count

        return stats


class AliasRecognizer:
    """High-level alias recognition system"""

    def __init__(self):
        self.lexicon = SynonymLexicon()
        self.recognized_aliases: List[SynonymMatch] = []

    def process_text(self, text: str, line_number: int = 0) -> List[SynonymMatch]:
        """Process text and recognize all aliases"""
        matches = self.lexicon.find_synonyms(text, line_number)
        self.recognized_aliases.extend(matches)
        return matches

    def get_dominant_policy_level(self, text: str) -> PolicyLevel:
        """Determine dominant policy level in text

        Args:
            text: Text to analyze

        Returns:
            Dominant PolicyLevel (highest priority match)
        """
        matches = self.lexicon.find_synonyms(text)

        # Priority order: MUST_NOT > MUST > SHOULD > MAY
        priority = [
            PolicyLevel.MUST_NOT,
            PolicyLevel.MUST,
            PolicyLevel.SHOULD,
            PolicyLevel.MAY
        ]

        for level in priority:
            if any(m.policy_level == level for m in matches):
                return level

        return PolicyLevel.UNKNOWN

    def normalize_text(self, text: str) -> str:
        """Normalize all policy keywords in text to RFC 2119 standard

        Args:
            text: Text to normalize

        Returns:
            Text with normalized keywords
        """
        normalized = text
        matches = self.lexicon.find_synonyms(text)

        # Sort by column (reverse) to replace from end to start
        for match in sorted(matches, key=lambda m: m.column, reverse=True):
            start = match.column
            end = start + len(match.original_text)
            normalized = normalized[:start] + match.normalized_form + normalized[end:]

        return normalized

    def get_summary_report(self) -> str:
        """Generate summary report of recognized aliases"""
        lines = []
        lines.append("=" * 60)
        lines.append("ALIAS RECOGNITION SUMMARY")
        lines.append("=" * 60)

        stats = self.lexicon.get_statistics()
        lines.append(f"Total Synonyms: {stats['total_synonyms']}")
        lines.append(f"  Built-in: {stats['built_in']}")
        lines.append(f"  Custom: {stats['custom']}")

        lines.append(f"\nPolicy Level Distribution:")
        for level in PolicyLevel:
            count = stats.get(f'{level.value}_count', 0)
            if count > 0:
                lines.append(f"  {level.value}: {count} synonyms")

        lines.append(f"\nRecognized Matches: {len(self.recognized_aliases)}")

        # Group by policy level
        by_level = {}
        for match in self.recognized_aliases:
            if match.policy_level not in by_level:
                by_level[match.policy_level] = []
            by_level[match.policy_level].append(match)

        for level, matches in by_level.items():
            lines.append(f"\n{level.value}: {len(matches)} matches")

        lines.append("=" * 60)
        return "\n".join(lines)
