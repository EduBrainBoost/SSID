"""
Layer 7: Policy-Verknüpfung
===========================

Policy linking and cross-reference validation:
- File existence checks
- Version matching
- Broken link detection
- Dependency resolution

Version: 3.0.0
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class PolicyLink:
    """Policy link with metadata"""
    source_file: str
    target_file: str
    link_type: str  # 'import', 'reference', 'include', 'extend'
    line_number: int
    is_valid: bool = False
    error_message: Optional[str] = None
    version_match: bool = True


class PolicyLinker:
    """Policy linking and validation system"""

    LINK_PATTERNS = {
        'import': r'import\s+["\']([^"\']+)["\']',
        'reference': r'see\s+([a-z0-9_/.]+\.(?:yaml|rego|md))',
        'include': r'include\s+["\']([^"\']+)["\']',
        'extend': r'extends?\s+["\']([^"\']+)["\']',
    }

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.links: List[PolicyLink] = []
        self.file_cache: Set[str] = set()
        self._build_file_cache()

    def _build_file_cache(self):
        """Build cache of all existing files"""
        if self.root_dir.exists():
            for file_path in self.root_dir.rglob('*'):
                if file_path.is_file():
                    self.file_cache.add(str(file_path.relative_to(self.root_dir)))

    def extract_links(self, file_path: str, content: str) -> List[PolicyLink]:
        """Extract all policy links from content"""
        links = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for link_type, pattern in self.LINK_PATTERNS.items():
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    target = match.group(1)
                    links.append(PolicyLink(
                        source_file=file_path,
                        target_file=target,
                        link_type=link_type,
                        line_number=line_num
                    ))

        self.links.extend(links)
        return links

    def validate_link(self, link: PolicyLink) -> bool:
        """Validate a single policy link"""
        # Check if target file exists
        target_path = Path(link.target_file)

        if target_path.is_absolute():
            exists = target_path.exists()
        else:
            # Try relative to root
            full_path = self.root_dir / target_path
            exists = full_path.exists()

            # Try relative to source file directory
            if not exists and link.source_file:
                source_dir = Path(link.source_file).parent
                relative_path = self.root_dir / source_dir / target_path
                exists = relative_path.exists()

        link.is_valid = exists
        if not exists:
            link.error_message = f"Target file not found: {link.target_file}"

        return exists

    def validate_all_links(self) -> Tuple[int, int]:
        """Validate all extracted links

        Returns:
            (valid_count, invalid_count)
        """
        valid = 0
        invalid = 0

        for link in self.links:
            if self.validate_link(link):
                valid += 1
            else:
                invalid += 1

        return valid, invalid

    def get_broken_links(self) -> List[PolicyLink]:
        """Get all broken links"""
        return [link for link in self.links if not link.is_valid]

    def get_link_report(self) -> str:
        """Generate link validation report"""
        lines = []
        lines.append("=" * 70)
        lines.append("POLICY LINK VALIDATION REPORT")
        lines.append("=" * 70)

        valid, invalid = self.validate_all_links()
        lines.append(f"\nTotal Links: {len(self.links)}")
        lines.append(f"Valid: {valid}")
        lines.append(f"Broken: {invalid}")

        broken = self.get_broken_links()
        if broken:
            lines.append(f"\nBroken Links:")
            for link in broken:
                lines.append(f"  {link.source_file}:{link.line_number}")
                lines.append(f"    -> {link.target_file}")
                lines.append(f"    Error: {link.error_message}")

        lines.append("=" * 70)
        return "\n".join(lines)

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []

        broken = self.get_broken_links()
        if broken:
            issues.append(f"{len(broken)} broken links detected")

        return len(issues) == 0, issues
