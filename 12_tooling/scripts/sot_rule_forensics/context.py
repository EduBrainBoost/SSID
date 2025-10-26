"""
Layer 4 & 5: Kontext-Fenster & Inline-Numerator
================================================

Layer 4: Kontext-Fenster mit Look-Ahead/Look-Behind
Layer 5: Inline-Numerator für hierarchische Nummerierung

Version: 3.0.0
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import re


@dataclass
class ContextWindow:
    """Context window around a rule with look-ahead/look-behind

    Provides contextual information for better rule understanding:
    - Lines before (look-behind)
    - Current line
    - Lines after (look-ahead)
    - Hierarchical position
    """
    center_line: int
    center_text: str
    lines_before: List[str] = field(default_factory=list)
    lines_after: List[str] = field(default_factory=list)
    window_size: int = 5
    parent_heading: Optional[str] = None
    section_path: List[str] = field(default_factory=list)

    def get_full_context(self) -> str:
        """Get complete context as single string"""
        lines = []
        lines.extend(self.lines_before)
        lines.append(f">>> {self.center_text}")
        lines.extend(self.lines_after)
        return "\n".join(lines)

    def get_context_score(self) -> int:
        """Calculate context quality score (0-40)

        Higher score for:
        - Presence of policy keywords in context
        - Section headers
        - Numbered items
        - Related terms
        """
        score = 0
        context = self.get_full_context().lower()

        # Policy keywords in context (+10)
        policy_keywords = ['must', 'should', 'may', 'required', 'forbidden']
        if any(kw in context for kw in policy_keywords):
            score += 10

        # Section header present (+10)
        if self.parent_heading:
            score += 10

        # Numbered items (+5)
        if re.search(r'\d+\.|\b[a-z]\)', context):
            score += 5

        # Related terms (+15)
        related = ['compliance', 'security', 'audit', 'governance', 'validation']
        matching_terms = sum(1 for term in related if term in context)
        score += min(matching_terms * 5, 15)

        return min(score, 40)


class ContextExtractor:
    """Extract context windows from document"""

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.lines: List[str] = []
        self.heading_stack: List[Tuple[int, str]] = []  # (level, heading)

    def load_document(self, content: str):
        """Load document for context extraction"""
        self.lines = content.split('\n')
        self._build_heading_stack()

    def _build_heading_stack(self):
        """Build hierarchical heading structure"""
        self.heading_stack = []
        for i, line in enumerate(self.lines):
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                heading = heading_match.group(2)
                self.heading_stack.append((level, heading))

    def extract_context(self, line_number: int) -> ContextWindow:
        """Extract context window around line number

        Args:
            line_number: Center line (1-indexed)

        Returns:
            ContextWindow with surrounding context
        """
        # Convert to 0-indexed
        idx = line_number - 1

        if idx < 0 or idx >= len(self.lines):
            return ContextWindow(
                center_line=line_number,
                center_text="",
                window_size=self.window_size
            )

        # Extract lines before
        start = max(0, idx - self.window_size)
        lines_before = self.lines[start:idx]

        # Extract lines after
        end = min(len(self.lines), idx + self.window_size + 1)
        lines_after = self.lines[idx + 1:end]

        # Find parent heading
        parent_heading = self._find_parent_heading(line_number)

        # Build section path
        section_path = self._build_section_path(line_number)

        return ContextWindow(
            center_line=line_number,
            center_text=self.lines[idx],
            lines_before=lines_before,
            lines_after=lines_after,
            window_size=self.window_size,
            parent_heading=parent_heading,
            section_path=section_path
        )

    def _find_parent_heading(self, line_number: int) -> Optional[str]:
        """Find nearest parent heading above line"""
        for i in range(line_number - 1, -1, -1):
            if i < len(self.lines):
                heading_match = re.match(r'^(#{1,6})\s+(.+)$', self.lines[i])
                if heading_match:
                    return heading_match.group(2)
        return None

    def _build_section_path(self, line_number: int) -> List[str]:
        """Build hierarchical section path"""
        path = []
        current_level = 999

        for i in range(line_number - 1, -1, -1):
            if i < len(self.lines):
                heading_match = re.match(r'^(#{1,6})\s+(.+)$', self.lines[i])
                if heading_match:
                    level = len(heading_match.group(1))
                    heading = heading_match.group(2)
                    if level < current_level:
                        path.insert(0, heading)
                        current_level = level

        return path


@dataclass
class NumberedItem:
    """Numbered item in hierarchical structure"""
    number: str
    text: str
    level: int
    line_number: int
    parent_numbers: List[str] = field(default_factory=list)
    full_path: str = ""


class InlineNumerator:
    """Inline numerator for hierarchical numbering

    Recognizes:
    - 1., 2., 3. (decimal)
    - a), b), c) (alphabetic)
    - i., ii., iii. (roman)
    - 1.1, 1.2, 1.2.1 (nested)
    """

    # Patterns for different numbering styles
    DECIMAL_PATTERN = r'^\s*(\d+)\.\s+(.+)$'
    ALPHA_PATTERN = r'^\s*([a-z])\)\s+(.+)$'
    ROMAN_PATTERN = r'^\s*([ivxlcdm]+)\.\s+(.+)$'
    NESTED_PATTERN = r'^\s*([\d.]+)\s+(.+)$'

    def __init__(self):
        self.numbered_items: List[NumberedItem] = []
        self.hierarchy_stack: List[Tuple[int, str]] = []

    def extract_numbered_items(self, content: str) -> List[NumberedItem]:
        """Extract all numbered items from content

        Args:
            content: Document content

        Returns:
            List of NumberedItem objects
        """
        lines = content.split('\n')
        items = []

        for line_num, line in enumerate(lines, 1):
            item = self._parse_numbered_line(line, line_num)
            if item:
                items.append(item)

        self.numbered_items = items
        return items

    def _parse_numbered_line(self, line: str, line_num: int) -> Optional[NumberedItem]:
        """Parse a single line for numbering"""

        # Try nested pattern first (1.2.3)
        match = re.match(self.NESTED_PATTERN, line)
        if match:
            number = match.group(1)
            text = match.group(2)
            level = number.count('.')
            return NumberedItem(
                number=number,
                text=text,
                level=level,
                line_number=line_num,
                full_path=number
            )

        # Try decimal (1., 2., 3.)
        match = re.match(self.DECIMAL_PATTERN, line)
        if match:
            number = match.group(1)
            text = match.group(2)
            return NumberedItem(
                number=number,
                text=text,
                level=1,
                line_number=line_num,
                full_path=number
            )

        # Try alphabetic (a), b), c))
        match = re.match(self.ALPHA_PATTERN, line)
        if match:
            letter = match.group(1)
            text = match.group(2)
            return NumberedItem(
                number=letter,
                text=text,
                level=2,
                line_number=line_num,
                full_path=letter
            )

        # Try roman (i., ii., iii.)
        match = re.match(self.ROMAN_PATTERN, line)
        if match:
            roman = match.group(1)
            text = match.group(2)
            return NumberedItem(
                number=roman,
                text=text,
                level=3,
                line_number=line_num,
                full_path=roman
            )

        return None

    def build_hierarchy(self) -> Dict[str, List[NumberedItem]]:
        """Build hierarchical structure of numbered items

        Returns:
            Dictionary mapping parent numbers to children
        """
        hierarchy = {}

        for item in self.numbered_items:
            # Extract parent number
            if '.' in item.number:
                parts = item.number.split('.')
                parent = '.'.join(parts[:-1])
                if parent not in hierarchy:
                    hierarchy[parent] = []
                hierarchy[parent].append(item)
            else:
                # Root level item
                if 'root' not in hierarchy:
                    hierarchy['root'] = []
                hierarchy['root'].append(item)

        return hierarchy

    def get_hierarchy_path(self, item: NumberedItem) -> List[str]:
        """Get full hierarchy path for an item

        Args:
            item: NumberedItem to trace

        Returns:
            List of numbers representing path from root
        """
        if '.' in item.number:
            parts = item.number.split('.')
            return parts
        return [item.number]

    def get_statistics(self) -> Dict[str, int]:
        """Get numbering statistics"""
        stats = {
            'total_items': len(self.numbered_items),
            'level_1': sum(1 for i in self.numbered_items if i.level == 1),
            'level_2': sum(1 for i in self.numbered_items if i.level == 2),
            'level_3': sum(1 for i in self.numbered_items if i.level == 3),
            'nested': sum(1 for i in self.numbered_items if '.' in i.number)
        }
        return stats
