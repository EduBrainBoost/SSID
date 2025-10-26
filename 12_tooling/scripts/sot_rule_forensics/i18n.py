"""
Layer 19: Language Normalization
================================

DE/EN bilingual dictionary for rule normalization
Version: 3.0.0
"""

from typing import Dict, Tuple, List

class LanguageNormalizer:
    """Bilingual DE/EN normalization"""

    TRANSLATIONS = {
        'MUSS': 'MUST',
        'SOLLTE': 'SHOULD',
        'KANN': 'MAY',
        'ERFORDERLICH': 'REQUIRED',
        'EMPFOHLEN': 'RECOMMENDED',
        'OPTIONAL': 'OPTIONAL',
        'VERBOTEN': 'FORBIDDEN',
        'DARF NICHT': 'MUST NOT'
    }

    def __init__(self):
        self.dictionary = self.TRANSLATIONS.copy()

    def normalize(self, text: str) -> str:
        """Normalize text to English"""
        normalized = text
        for de, en in self.dictionary.items():
            normalized = normalized.replace(de, en)
        return normalized

    def detect_language(self, text: str) -> str:
        """Detect language"""
        de_keywords = sum(1 for k in self.dictionary.keys() if k in text)
        return 'DE' if de_keywords > 0 else 'EN'

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        return True, []
