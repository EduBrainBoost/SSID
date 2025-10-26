"""
SoT Rule Forensics - V3.0 Complete Rule Recognition System
==========================================================

A forensic-grade rule extraction and verification system implementing
30 layers of deterministic, auditable, and mathematically verifiable
rule recognition.

Layers:
  1-7:   Advanced Lexer & Parser
  8-14:  Data Management
  15-22: Verification & Audit
  23-30: Performance & Quality

Version: 3.0.0
Status: PRODUCTION READY
"""

__version__ = "3.0.0"
__author__ = "Claude Code"

from .lexer import MultiTrackLexer, CommentToken, VariablePattern
from .mapping import HierarchicalMapping, RootShardMapper
from .context import ContextWindow, InlineNumerator
from .variables import VariableResolver
from .linking import PolicyLinker
from .indexing import CrossReferenceIndex
from .clustering import DuplicateCluster, SemanticSimilarity
from .tagging import ComplianceTagging
from .resolution import ConflictResolution
from .evidence import EvidenceChain
from .aggregation import HashAggregation
from .verification import CyclicVerification, DeprecationHandler
from .ml_recovery import MLPatternRecovery
from .i18n import LanguageNormalizer
from .healing import ErrorTolerance
from .dashboard import CoverageDashboard
from .timestamped_logging import TimeStampedLogger
from .parallel import ParallelProcessor
from .failfast import FailFastMechanism
from .reproduc import ReproducibilityTest
from .confidence import ConfidenceNormalizer
from .diff import SemanticDiff
from .selfaudit import SelfAuditMode
from .replay import EvidenceReplay
from .certification import AuditCertification

__all__ = [
    'MultiTrackLexer',
    'HierarchicalMapping',
    'ContextWindow',
    'VariableResolver',
    'PolicyLinker',
    'CrossReferenceIndex',
    'DuplicateCluster',
    'ComplianceTagging',
    'ConflictResolution',
    'EvidenceChain',
    'HashAggregation',
    'CyclicVerification',
    'MLPatternRecovery',
    'LanguageNormalizer',
    'ErrorTolerance',
    'CoverageDashboard',
    'TimeStampedLogger',
    'ParallelProcessor',
    'FailFastMechanism',
    'ReproducibilityTest',
    'ConfidenceNormalizer',
    'SemanticDiff',
    'SelfAuditMode',
    'EvidenceReplay',
    'AuditCertification',
]
