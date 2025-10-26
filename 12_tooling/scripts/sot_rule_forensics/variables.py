"""
Layer 6: Variablen-Auflösung
============================

Erkennt und löst Variablen auf:
- $ROOT, $SHARD, $VERSION
- $VAR, ${ENV_VAR}
- Platzhalter-Ersetzung
- Template-Variable Expansion

Version: 3.0.0
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import re
import os


@dataclass
class VariableDefinition:
    """Variable definition with metadata"""
    name: str
    value: str
    var_type: str  # 'dollar', 'brace', 'env', 'ssid'
    source: str  # where it was defined
    line_number: int = 0
    is_resolved: bool = False


@dataclass
class VariableReference:
    """Variable reference/usage"""
    name: str
    full_match: str
    line_number: int
    column: int
    resolved_value: Optional[str] = None


class VariableResolver:
    """Resolves variables in SoT documents

    Handles:
    - SSID variables: $ROOT, $SHARD, $VERSION
    - Dollar variables: $VAR
    - Brace variables: ${VAR}
    - Environment variables: ${ENV:PATH}
    - Template expansions
    """

    # SSID-specific variables
    SSID_VARS = {
        'ROOT': '24 SSID Roots',
        'SHARD': '16 Shards per Root',
        'VERSION': '3.0.0',
        'FRAMEWORK': 'SSID',
        'GOVERNANCE': '24_meta_orchestration',
    }

    # Pattern definitions
    DOLLAR_VAR_PATTERN = r'\$([A-Z_][A-Z0-9_]*)'
    BRACE_VAR_PATTERN = r'\$\{([A-Z_][A-Z0-9_]*)\}'
    ENV_VAR_PATTERN = r'\$\{ENV:([A-Z_][A-Z0-9_]*)\}'
    TEMPLATE_VAR_PATTERN = r'\{\{([A-Z_][A-Z0-9_]*)\}\}'

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path.cwd()
        self.variables: Dict[str, VariableDefinition] = {}
        self.references: List[VariableReference] = []
        self._init_ssid_variables()

    def _init_ssid_variables(self):
        """Initialize SSID-specific variables"""
        for name, value in self.SSID_VARS.items():
            self.variables[name] = VariableDefinition(
                name=name,
                value=value,
                var_type='ssid',
                source='built-in',
                is_resolved=True
            )

    def define_variable(self, name: str, value: str, source: str = 'user',
                       line_number: int = 0):
        """Define a new variable"""
        self.variables[name] = VariableDefinition(
            name=name,
            value=value,
            var_type='user',
            source=source,
            line_number=line_number,
            is_resolved=True
        )

    def extract_variables(self, content: str, source: str = 'unknown') -> List[VariableReference]:
        """Extract all variable references from content

        Args:
            content: Text content to scan
            source: Source identifier

        Returns:
            List of VariableReference objects
        """
        refs = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Dollar variables ($VAR)
            for match in re.finditer(self.DOLLAR_VAR_PATTERN, line):
                var_name = match.group(1)
                refs.append(VariableReference(
                    name=var_name,
                    full_match=match.group(0),
                    line_number=line_num,
                    column=match.start()
                ))

            # Brace variables (${VAR})
            for match in re.finditer(self.BRACE_VAR_PATTERN, line):
                var_name = match.group(1)
                refs.append(VariableReference(
                    name=var_name,
                    full_match=match.group(0),
                    line_number=line_num,
                    column=match.start()
                ))

            # Environment variables (${ENV:VAR})
            for match in re.finditer(self.ENV_VAR_PATTERN, line):
                var_name = match.group(1)
                env_value = os.environ.get(var_name)
                refs.append(VariableReference(
                    name=f'ENV:{var_name}',
                    full_match=match.group(0),
                    line_number=line_num,
                    column=match.start(),
                    resolved_value=env_value
                ))

            # Template variables ({{VAR}})
            for match in re.finditer(self.TEMPLATE_VAR_PATTERN, line):
                var_name = match.group(1)
                refs.append(VariableReference(
                    name=var_name,
                    full_match=match.group(0),
                    line_number=line_num,
                    column=match.start()
                ))

        self.references.extend(refs)
        return refs

    def resolve_variable(self, name: str) -> Optional[str]:
        """Resolve a variable name to its value

        Args:
            name: Variable name

        Returns:
            Resolved value or None
        """
        # Check environment variables first
        if name.startswith('ENV:'):
            env_var = name[4:]
            return os.environ.get(env_var)

        # Check defined variables
        if name in self.variables:
            return self.variables[name].value

        # Check SSID variables
        if name in self.SSID_VARS:
            return self.SSID_VARS[name]

        return None

    def resolve_text(self, text: str) -> str:
        """Resolve all variables in text

        Args:
            text: Text with variable references

        Returns:
            Text with variables replaced
        """
        resolved = text

        # Resolve environment variables first (${ENV:VAR})
        for match in re.finditer(self.ENV_VAR_PATTERN, resolved):
            var_name = match.group(1)
            value = os.environ.get(var_name, match.group(0))
            resolved = resolved.replace(match.group(0), value)

        # Resolve brace variables (${VAR})
        for match in re.finditer(self.BRACE_VAR_PATTERN, resolved):
            var_name = match.group(1)
            value = self.resolve_variable(var_name)
            if value:
                resolved = resolved.replace(match.group(0), value)

        # Resolve dollar variables ($VAR)
        for match in re.finditer(self.DOLLAR_VAR_PATTERN, resolved):
            var_name = match.group(1)
            value = self.resolve_variable(var_name)
            if value:
                resolved = resolved.replace(match.group(0), value)

        # Resolve template variables ({{VAR}})
        for match in re.finditer(self.TEMPLATE_VAR_PATTERN, resolved):
            var_name = match.group(1)
            value = self.resolve_variable(var_name)
            if value:
                resolved = resolved.replace(match.group(0), value)

        return resolved

    def resolve_references(self):
        """Resolve all extracted variable references"""
        for ref in self.references:
            if not ref.resolved_value:
                ref.resolved_value = self.resolve_variable(ref.name)

    def get_unresolved_variables(self) -> List[str]:
        """Get list of unresolved variable names"""
        unresolved = set()
        for ref in self.references:
            if not ref.resolved_value and not self.resolve_variable(ref.name):
                unresolved.add(ref.name)
        return sorted(unresolved)

    def get_variable_usage_report(self) -> str:
        """Generate variable usage report"""
        lines = []
        lines.append("=" * 70)
        lines.append("VARIABLE RESOLUTION REPORT")
        lines.append("=" * 70)

        lines.append(f"\nDefined Variables: {len(self.variables)}")
        for name, var_def in sorted(self.variables.items()):
            lines.append(f"  ${name} = {var_def.value} ({var_def.var_type})")

        lines.append(f"\nVariable References: {len(self.references)}")
        resolved_count = sum(1 for r in self.references if r.resolved_value)
        lines.append(f"  Resolved: {resolved_count}/{len(self.references)}")

        unresolved = self.get_unresolved_variables()
        if unresolved:
            lines.append(f"\nUnresolved Variables: {len(unresolved)}")
            for var_name in unresolved:
                lines.append(f"  ${var_name}")

        lines.append("=" * 70)
        return "\n".join(lines)

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification check

        Returns:
            (success, list_of_issues)
        """
        issues = []

        # Check all SSID variables are defined
        for ssid_var in self.SSID_VARS:
            if ssid_var not in self.variables:
                issues.append(f"Missing SSID variable: ${ssid_var}")

        # Check for unresolved references
        unresolved = self.get_unresolved_variables()
        if unresolved:
            issues.append(f"Unresolved variables: {', '.join(unresolved)}")

        # Check for circular references (simple check)
        for name, var_def in self.variables.items():
            if f'${name}' in var_def.value:
                issues.append(f"Potential circular reference in ${name}")

        return len(issues) == 0, issues
