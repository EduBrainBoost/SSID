"""
SSID AI Policy Agent v6.0
AI-Assisted Governance Parameter Optimization

Analyzes:
- Trust score trends and fluctuations
- Audit cycle completion rates
- Node performance patterns
- Anomaly frequencies

Recommends:
- Trust threshold adjustments
- Epoch duration optimization
- Slashing rate calibration

Security: Deterministic, no PII, signed recommendations
"""

import time
import json
import logging
import hashlib
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class TrustTrend:
    """Trust score trend analysis"""
    federation_id: str
    avg_trust: float
    std_dev: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    volatility: float
    sample_size: int

@dataclass
class PolicyRecommendation:
    """AI-generated policy recommendation"""
    recommendation_id: str
    trust_threshold: int  # 0-1000000
    epoch_duration: int   # seconds
    slashing_rate: int    # 0-100
    confidence_score: float  # 0.0-1.0
    reasoning: str
    timestamp: int
    model_version: str
    signature: str

class AIPolicyAgent:
    """
    AI Policy Agent for Autonomous Governance

    Uses statistical analysis and trend detection (mock ML)
    to recommend governance parameter adjustments.

    In production: Replace with actual ML model (TensorFlow/PyTorch)
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_version = "6.0.0-deterministic"

        # Thresholds for recommendations
        self.volatility_high_threshold = 0.15  # 15% volatility triggers adjustment
        self.trust_low_threshold = 0.80       # Average trust below 80%
        self.trust_high_threshold = 0.95      # Average trust above 95%

        # Default parameters
        self.default_trust_threshold = 750000  # 0.75
        self.default_epoch_duration = 7 * 24 * 3600  # 7 days
        self.default_slashing_rate = 10

    def analyze_trust_trends(
        self,
        trust_history: List[Dict[str, Any]]
    ) -> List[TrustTrend]:
        """
        Analyze trust score trends across federations

        Args:
            trust_history: List of trust score records

        Returns: List of TrustTrend analysis per federation
        """
        # Group by federation
        by_federation: Dict[str, List[float]] = {}

        for record in trust_history:
            fed_id = record.get('federation_id', 'unknown')
            trust_score = record.get('trust_score', 0.0)

            if fed_id not in by_federation:
                by_federation[fed_id] = []

            by_federation[fed_id].append(trust_score)

        trends = []

        for fed_id, scores in by_federation.items():
            if len(scores) < 3:
                continue  # Need at least 3 data points

            scores_array = np.array(scores)

            # Calculate statistics
            avg_trust = float(np.mean(scores_array))
            std_dev = float(np.std(scores_array))
            volatility = std_dev / avg_trust if avg_trust > 0 else 0.0

            # Determine trend direction (simple linear regression)
            x = np.arange(len(scores))
            slope = np.polyfit(x, scores_array, 1)[0]

            if slope > 0.01:
                trend_direction = "increasing"
            elif slope < -0.01:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"

            trends.append(TrustTrend(
                federation_id=fed_id,
                avg_trust=avg_trust,
                std_dev=std_dev,
                trend_direction=trend_direction,
                volatility=volatility,
                sample_size=len(scores)
            ))

            logger.info(
                f"Federation {fed_id}: avg_trust={avg_trust:.3f}, "
                f"volatility={volatility:.3f}, trend={trend_direction}"
            )

        return trends

    def generate_recommendation(
        self,
        trends: List[TrustTrend],
        current_params: Dict[str, int]
    ) -> PolicyRecommendation:
        """
        Generate policy recommendation based on trends

        Args:
            trends: List of trust trends
            current_params: Current governance parameters

        Returns: PolicyRecommendation
        """
        # Calculate aggregate metrics
        avg_trust_all = np.mean([t.avg_trust for t in trends])
        max_volatility = max([t.volatility for t in trends])

        # Default to current parameters
        new_trust_threshold = current_params.get('trust_threshold', self.default_trust_threshold)
        new_epoch_duration = current_params.get('epoch_duration', self.default_epoch_duration)
        new_slashing_rate = current_params.get('slashing_rate', self.default_slashing_rate)

        reasoning_parts = []
        confidence_score = 0.85  # Base confidence

        # Rule 1: Low average trust → increase trust threshold
        if avg_trust_all < self.trust_low_threshold:
            # Increase threshold by 5%
            new_trust_threshold = min(1000000, int(new_trust_threshold * 1.05))
            reasoning_parts.append(
                f"Average trust ({avg_trust_all:.2f}) below threshold ({self.trust_low_threshold}). "
                "Increasing trust threshold to maintain quality."
            )
            confidence_score += 0.05

        # Rule 2: High volatility → shorten epoch duration (more frequent audits)
        if max_volatility > self.volatility_high_threshold:
            # Reduce epoch duration by 20%
            new_epoch_duration = max(1 * 24 * 3600, int(new_epoch_duration * 0.8))  # Min 1 day
            reasoning_parts.append(
                f"High volatility detected ({max_volatility:.2f}). "
                "Shortening epoch duration for more frequent audits."
            )
            confidence_score += 0.05

        # Rule 3: Stable high trust → relax threshold slightly (efficiency)
        if avg_trust_all > self.trust_high_threshold and max_volatility < 0.05:
            # Decrease threshold by 2%
            new_trust_threshold = max(500000, int(new_trust_threshold * 0.98))  # Min 0.50
            reasoning_parts.append(
                f"Consistently high trust ({avg_trust_all:.2f}) with low volatility. "
                "Slightly relaxing threshold for efficiency."
            )
            confidence_score += 0.03

        # Rule 4: Decreasing trend → increase slashing rate (deterrent)
        decreasing_count = sum(1 for t in trends if t.trend_direction == "decreasing")
        if decreasing_count >= len(trends) / 2:
            # Increase slashing rate by 5 percentage points
            new_slashing_rate = min(100, new_slashing_rate + 5)
            reasoning_parts.append(
                f"{decreasing_count}/{len(trends)} federations show decreasing trust. "
                "Increasing slashing rate as deterrent."
            )
            confidence_score += 0.04

        # Compile reasoning
        if not reasoning_parts:
            reasoning = "No significant changes recommended. Current parameters are optimal."
            confidence_score = 0.90
        else:
            reasoning = " ".join(reasoning_parts)

        # Clamp confidence
        confidence_score = min(1.0, confidence_score)

        # Generate recommendation ID
        rec_id = hashlib.sha256(
            f"{new_trust_threshold}{new_epoch_duration}{new_slashing_rate}{int(time.time())}".encode()
        ).hexdigest()[:16]

        
        signature = self._sign_recommendation(
            rec_id,
            new_trust_threshold,
            new_epoch_duration,
            new_slashing_rate
        )

        recommendation = PolicyRecommendation(
            recommendation_id=rec_id,
            trust_threshold=new_trust_threshold,
            epoch_duration=new_epoch_duration,
            slashing_rate=new_slashing_rate,
            confidence_score=confidence_score,
            reasoning=reasoning,
            timestamp=int(time.time()),
            model_version=self.model_version,
            signature=signature
        )

        logger.info(f"Generated recommendation {rec_id}")
        logger.info(f"  Trust Threshold: {new_trust_threshold} (scaled)")
        logger.info(f"  Epoch Duration: {new_epoch_duration} seconds ({new_epoch_duration // 86400} days)")
        logger.info(f"  Slashing Rate: {new_slashing_rate}%")
        logger.info(f"  Confidence: {confidence_score:.2f}")

        return recommendation

    def _sign_recommendation(
        self,
        rec_id: str,
        trust_threshold: int,
        epoch_duration: int,
        slashing_rate: int
    ) -> str:
        """
        Sign recommendation with model key (mock EdDSA)

        In production: Use actual EdDSA private key
        """
        data = f"{rec_id}{trust_threshold}{epoch_duration}{slashing_rate}{self.model_version}"
        signature_hash = hashlib.sha256(data.encode()).hexdigest()

        
        full_signature = signature_hash + signature_hash[:64]

        return f"0x{full_signature}"

    def export_recommendation_for_blockchain(
        self,
        recommendation: PolicyRecommendation
    ) -> Dict[str, Any]:
        """
        Export recommendation in format for AutonomousGovernanceProtocol.sol

        Returns: Transaction parameters
        """
        return {
            "function": "submitRecommendation",
            "parameters": {
                "trustThreshold": recommendation.trust_threshold,
                "epochDuration": recommendation.epoch_duration,
                "slashingRate": recommendation.slashing_rate,
                "confidenceScore": int(recommendation.confidence_score * 1000000),
                "reasoning": recommendation.reasoning
            },
            "metadata": {
                "recommendation_id": recommendation.recommendation_id,
                "timestamp": recommendation.timestamp,
                "model_version": recommendation.model_version,
                "signature": recommendation.signature
            }
        }

    def save_recommendation(
        self,
        recommendation: PolicyRecommendation,
        output_path: str
    ):
        """Save recommendation to JSON file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(asdict(recommendation), f, indent=2)
            logger.info(f"Recommendation saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save recommendation: {e}")

def create_agent(config: Dict[str, Any]) -> AIPolicyAgent:
    """Factory function"""
    return AIPolicyAgent(config)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    
    trust_history = [
        {"federation_id": "opencore", "trust_score": 0.95, "timestamp": 1728000000},
        {"federation_id": "opencore", "trust_score": 0.94, "timestamp": 1728086400},
        {"federation_id": "opencore", "trust_score": 0.93, "timestamp": 1728172800},
        {"federation_id": "trustnet", "trust_score": 0.96, "timestamp": 1728000000},
        {"federation_id": "trustnet", "trust_score": 0.85, "timestamp": 1728086400},  # Drop
        {"federation_id": "trustnet", "trust_score": 0.84, "timestamp": 1728172800},  # Drop
        {"federation_id": "govchain", "trust_score": 0.88, "timestamp": 1728000000},
        {"federation_id": "govchain", "trust_score": 0.87, "timestamp": 1728086400},
        {"federation_id": "govchain", "trust_score": 0.86, "timestamp": 1728172800},
        {"federation_id": "eudi", "trust_score": 0.98, "timestamp": 1728000000},
        {"federation_id": "eudi", "trust_score": 0.98, "timestamp": 1728086400},
        {"federation_id": "eudi", "trust_score": 0.97, "timestamp": 1728172800},
    ]

    current_params = {
        "trust_threshold": 750000,  # 0.75
        "epoch_duration": 7 * 24 * 3600,  # 7 days
        "slashing_rate": 10
    }

    config = {}
    agent = create_agent(config)

    # Analyze trends
    trends = agent.analyze_trust_trends(trust_history)

    # Generate recommendation
    recommendation = agent.generate_recommendation(trends, current_params)

    # Export for blockchain
    blockchain_tx = agent.export_recommendation_for_blockchain(recommendation)

    print("\nBlockchain Transaction:")
    print(json.dumps(blockchain_tx, indent=2))

    # Save recommendation
    agent.save_recommendation(
        recommendation,
        "07_governance_legal/autonomy/ai_recommendation.json"
    )

    print("\n✓ AI Policy Agent: Recommendation generated successfully")
