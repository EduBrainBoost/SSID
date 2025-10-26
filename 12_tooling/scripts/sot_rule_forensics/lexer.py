"""
Layer 1: Mehrspuriger Lexer (Multi-Track Lexer)
================================================

Erkennt Regeln in allen Formaten:
- Markdown-Token (Überschriften, Listen, Codeblocks, Tabellen)
- YAML-Token (Mapping, Sequenzen, Literale)
- Inline-Pattern (MUST, SHOULD, etc.)
- Kommentar-Token (#, //, /* ... */)
- Dateipfade und Variablenmuster (23_compliance/..., $VAR, ${ENV})

Version: 3.0.0
"""

import re
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class TokenType(Enum):
    """Token types for multi-track lexer"""
    MARKDOWN_HEADING = "markdown_heading"
    MARKDOWN_LIST = "markdown_list"
    MARKDOWN_CODE = "markdown_code"
    MARKDOWN_TABLE = "markdown_table"
    YAML_MAPPING = "yaml_mapping"
    YAML_SEQUENCE = "yaml_sequence"
    YAML_LITERAL = "yaml_literal"
    INLINE_POLICY = "inline_policy"
    COMMENT_HASH = "comment_hash"
    COMMENT_SLASH = "comment_slash"
    COMMENT_BLOCK = "comment_block"
    PATH_REFERENCE = "path_reference"
    VARIABLE_DOLLAR = "variable_dollar"
    VARIABLE_BRACE = "variable_brace"
    TEXT = "text"


@dataclass
class Token:
    """Generic token with position and metadata"""
    type: TokenType
    content: str
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"Token({self.type.value}, line {self.line_start}-{self.line_end})"


@dataclass
class CommentToken(Token):
    """Specialized token for comments"""
    comment_type: str = "hash"  # hash, slash, block

    def __post_init__(self):
        self.type = TokenType.COMMENT_HASH if self.comment_type == "hash" else \
                   TokenType.COMMENT_SLASH if self.comment_type == "slash" else \
                   TokenType.COMMENT_BLOCK


@dataclass
class VariablePattern:
    """Detected variable pattern"""
    name: str
    type: str  # "dollar" or "brace"
    line: int
    column: int
    full_match: str


class MultiTrackLexer:
    """Multi-track lexer for forensic rule extraction

    Erkennt ALLE Regelformate unabhängig vom Kontext:
    - Markdown-Strukturen
    - YAML-Blöcke
    - Inline-Policies
    - Kommentare (auch in Code)
    - Variablen und Pfade
    """

    # Pattern definitions
    MARKDOWN_HEADING_PATTERN = r'^(#{1,6})\s+(.+)$'
    MARKDOWN_LIST_PATTERN = r'^(\s*)([-*+]|\d+\.)\s+(.+)$'
    MARKDOWN_CODE_FENCE = r'^```(\w+)?'
    MARKDOWN_TABLE_ROW = r'^\|(.+)\|$'

    COMMENT_HASH_PATTERN = r'#(.*)$'
    COMMENT_SLASH_PATTERN = r'//(.*)$'
    COMMENT_BLOCK_START = r'/\*'
    COMMENT_BLOCK_END = r'\*/'

    PATH_PATTERN = r'\b(\d{2}_[a-z_]+(?:/[a-z0-9_/.]+)*)\b'
    VARIABLE_DOLLAR_PATTERN = r'\$([A-Z_][A-Z0-9_]*)'
    VARIABLE_BRACE_PATTERN = r'\$\{([A-Z_][A-Z0-9_]*)\}'

    INLINE_POLICY_KEYWORDS = [
        'MUST', 'SHALL', 'REQUIRED', 'SHOULD', 'RECOMMENDED',
        'MAY', 'OPTIONAL', 'MUST NOT', 'SHALL NOT',
        'DENY', 'WARN', 'INFO', 'CRITICAL'
    ]

    def __init__(self):
        self.tokens: List[Token] = []
        self.current_line = 0
        self.in_code_block = False
        self.code_block_lang = None
        self.in_comment_block = False

    def tokenize(self, content: str) -> List[Token]:
        """Tokenize content into multi-track tokens"""
        self.tokens = []
        self.current_line = 0
        self.in_code_block = False
        self.in_comment_block = False

        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            self.current_line = i
            self._tokenize_line(line, i)

        return self.tokens

    def _tokenize_line(self, line: str, line_num: int):
        """Tokenize a single line across all tracks"""

        # Track 1: Check for code fence
        if self._check_code_fence(line, line_num):
            return

        # Track 2: Check for block comment
        if self._check_block_comment(line, line_num):
            return

        # If in code block, only look for comments and variables
        if self.in_code_block:
            self._tokenize_code_line(line, line_num)
            return

        # Track 3: Markdown structures
        self._check_markdown_heading(line, line_num)
        self._check_markdown_list(line, line_num)
        self._check_markdown_table(line, line_num)

        # Track 4: Comments (hash, slash)
        self._check_comments(line, line_num)

        # Track 5: Inline policies
        self._check_inline_policies(line, line_num)

        # Track 6: Path references
        self._check_path_references(line, line_num)

        # Track 7: Variables
        self._check_variables(line, line_num)

    def _check_code_fence(self, line: str, line_num: int) -> bool:
        """Check for code fence markers"""
        match = re.match(self.MARKDOWN_CODE_FENCE, line.strip())
        if match:
            if not self.in_code_block:
                self.in_code_block = True
                self.code_block_lang = match.group(1) or 'text'
                self.tokens.append(Token(
                    type=TokenType.MARKDOWN_CODE,
                    content=line,
                    line_start=line_num,
                    line_end=line_num,
                    metadata={'lang': self.code_block_lang, 'fence': 'start'}
                ))
            else:
                self.in_code_block = False
                self.tokens.append(Token(
                    type=TokenType.MARKDOWN_CODE,
                    content=line,
                    line_start=line_num,
                    line_end=line_num,
                    metadata={'lang': self.code_block_lang, 'fence': 'end'}
                ))
                self.code_block_lang = None
            return True
        return False

    def _check_block_comment(self, line: str, line_num: int) -> bool:
        """Check for block comment markers"""
        if re.search(self.COMMENT_BLOCK_START, line):
            self.in_comment_block = True
            return True
        if re.search(self.COMMENT_BLOCK_END, line):
            self.in_comment_block = False
            return True
        return False

    def _tokenize_code_line(self, line: str, line_num: int):
        """Tokenize line inside code block"""
        # Look for comments even in code
        self._check_comments(line, line_num)
        # Look for variables
        self._check_variables(line, line_num)

    def _check_markdown_heading(self, line: str, line_num: int):
        """Check for markdown headings"""
        match = re.match(self.MARKDOWN_HEADING_PATTERN, line)
        if match:
            level = len(match.group(1))
            text = match.group(2)
            self.tokens.append(Token(
                type=TokenType.MARKDOWN_HEADING,
                content=text,
                line_start=line_num,
                line_end=line_num,
                metadata={'level': level}
            ))

    def _check_markdown_list(self, line: str, line_num: int):
        """Check for markdown list items"""
        match = re.match(self.MARKDOWN_LIST_PATTERN, line)
        if match:
            indent = len(match.group(1))
            marker = match.group(2)
            text = match.group(3)
            self.tokens.append(Token(
                type=TokenType.MARKDOWN_LIST,
                content=text,
                line_start=line_num,
                line_end=line_num,
                metadata={'indent': indent, 'marker': marker}
            ))

    def _check_markdown_table(self, line: str, line_num: int):
        """Check for markdown table rows"""
        match = re.match(self.MARKDOWN_TABLE_ROW, line)
        if match:
            cells = [cell.strip() for cell in match.group(1).split('|')]
            self.tokens.append(Token(
                type=TokenType.MARKDOWN_TABLE,
                content=line,
                line_start=line_num,
                line_end=line_num,
                metadata={'cells': cells}
            ))

    def _check_comments(self, line: str, line_num: int):
        """Check for comment tokens"""
        # Hash comments
        hash_match = re.search(self.COMMENT_HASH_PATTERN, line)
        if hash_match:
            col = hash_match.start()
            self.tokens.append(CommentToken(
                type=TokenType.COMMENT_HASH,
                content=hash_match.group(1).strip(),
                line_start=line_num,
                line_end=line_num,
                column_start=col,
                comment_type='hash'
            ))

        # Slash comments
        slash_match = re.search(self.COMMENT_SLASH_PATTERN, line)
        if slash_match:
            col = slash_match.start()
            self.tokens.append(CommentToken(
                type=TokenType.COMMENT_SLASH,
                content=slash_match.group(1).strip(),
                line_start=line_num,
                line_end=line_num,
                column_start=col,
                comment_type='slash'
            ))

    def _check_inline_policies(self, line: str, line_num: int):
        """Check for inline policy keywords"""
        for keyword in self.INLINE_POLICY_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', line, re.IGNORECASE):
                self.tokens.append(Token(
                    type=TokenType.INLINE_POLICY,
                    content=line.strip(),
                    line_start=line_num,
                    line_end=line_num,
                    metadata={'keyword': keyword}
                ))
                break  # Only one policy per line

    def _check_path_references(self, line: str, line_num: int):
        """Check for SSID path references"""
        for match in re.finditer(self.PATH_PATTERN, line):
            path = match.group(1)
            col = match.start()
            self.tokens.append(Token(
                type=TokenType.PATH_REFERENCE,
                content=path,
                line_start=line_num,
                line_end=line_num,
                column_start=col,
                column_end=col + len(path)
            ))

    def _check_variables(self, line: str, line_num: int):
        """Check for variable patterns"""
        # $VAR pattern
        for match in re.finditer(self.VARIABLE_DOLLAR_PATTERN, line):
            var_name = match.group(1)
            col = match.start()
            self.tokens.append(Token(
                type=TokenType.VARIABLE_DOLLAR,
                content=var_name,
                line_start=line_num,
                line_end=line_num,
                column_start=col,
                metadata={'pattern': VariablePattern(
                    name=var_name,
                    type='dollar',
                    line=line_num,
                    column=col,
                    full_match=match.group(0)
                )}
            ))

        # ${VAR} pattern
        for match in re.finditer(self.VARIABLE_BRACE_PATTERN, line):
            var_name = match.group(1)
            col = match.start()
            self.tokens.append(Token(
                type=TokenType.VARIABLE_BRACE,
                content=var_name,
                line_start=line_num,
                line_end=line_num,
                column_start=col,
                metadata={'pattern': VariablePattern(
                    name=var_name,
                    type='brace',
                    line=line_num,
                    column=col,
                    full_match=match.group(0)
                )}
            ))

    def get_tokens_by_type(self, token_type: TokenType) -> List[Token]:
        """Filter tokens by type"""
        return [t for t in self.tokens if t.type == token_type]

    def get_tokens_in_range(self, start_line: int, end_line: int) -> List[Token]:
        """Get all tokens in line range"""
        return [t for t in self.tokens
                if t.line_start >= start_line and t.line_end <= end_line]

    def find_variables(self) -> List[VariablePattern]:
        """Extract all variable patterns"""
        variables = []
        for token in self.tokens:
            if token.type in [TokenType.VARIABLE_DOLLAR, TokenType.VARIABLE_BRACE]:
                if 'pattern' in token.metadata:
                    variables.append(token.metadata['pattern'])
        return variables

    def find_path_references(self) -> List[str]:
        """Extract all SSID path references"""
        return [t.content for t in self.tokens if t.type == TokenType.PATH_REFERENCE]

    def get_statistics(self) -> Dict[str, int]:
        """Get token statistics"""
        stats = {}
        for token_type in TokenType:
            count = sum(1 for t in self.tokens if t.type == token_type)
            stats[token_type.value] = count
        return stats
