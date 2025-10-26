"""
Layer 26: Confidence-Weight Normalization
=========================================

Score normalization with confidence threshold
Version: 3.0.0
"""

from typing import List, Tuple

class ConfidenceNormalizer:
    """Confidence score normalization"""

    CONFIDENCE_THRESHOLD = 0.85

    def __init__(self):
        self.scores: List[float] = []

    def normalize_score(self, score: float) -> float:
        """Normalize score to 0.0-1.0 range"""
        return max(0.0, min(1.0, score / 100.0))

    def is_valid_confidence(self, score: float) -> bool:
        """Check if confidence score is above threshold"""
        return score >= self.CONFIDENCE_THRESHOLD

    def calculate_weighted_average(self, scores: List[Tuple[float, float]]) -> float:
        """Calculate weighted average of (score, weight) pairs"""
        if not scores:
            return 0.0

        total_weight = sum(weight for _, weight in scores)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(score * weight for score, weight in scores)
        return weighted_sum / total_weight

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []
        invalid_scores = [s for s in self.scores if s < 0 or s > 1]
        if invalid_scores:
            issues.append(f"{len(invalid_scores)} scores out of range")
        return len(issues) == 0, issues
