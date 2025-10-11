#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Overfitting Detection for AI/ML Models
Anti-Gaming Module - Detects training manipulation and model gaming
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timezone


def is_overfitting(
    train_acc: float,
    val_acc: float,
    gap_threshold: float = 0.15,
    min_train: float = 0.95
) -> bool:
    """
    Heuristic: overfitting if training accuracy high but validation low.

    Args:
        train_acc: Training accuracy (0.0 - 1.0)
        val_acc: Validation accuracy (0.0 - 1.0)
        gap_threshold: Maximum acceptable accuracy gap (default 0.15)
        min_train: Minimum training accuracy to trigger check (default 0.95)

    Returns:
        True if overfitting detected, False otherwise
    """
    if train_acc is None or val_acc is None:
        return False

    # Overfitting signature: high training accuracy with significant validation drop
    return train_acc >= min_train and (train_acc - val_acc) >= gap_threshold


def analyze_model_metrics(
    model_id: str,
    train_acc: float,
    val_acc: float,
    test_acc: Optional[float] = None,
    gap_threshold: float = 0.15,
    min_train: float = 0.95
) -> Dict:
    """
    Comprehensive overfitting analysis for a model.

    Args:
        model_id: Unique identifier for the model
        train_acc: Training accuracy
        val_acc: Validation accuracy
        test_acc: Optional test accuracy
        gap_threshold: Accuracy gap threshold
        min_train: Minimum training accuracy

    Returns:
        Dict with analysis results and risk assessment
    """
    overfitting_detected = is_overfitting(train_acc, val_acc, gap_threshold, min_train)
    accuracy_gap = train_acc - val_acc if (train_acc and val_acc) else None

    # Risk level assessment
    if not overfitting_detected:
        risk_level = "NONE"
    elif accuracy_gap < 0.20:
        risk_level = "MEDIUM"
    elif accuracy_gap < 0.30:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    result = {
        "model_id": model_id,
        "train_accuracy": train_acc,
        "val_accuracy": val_acc,
        "test_accuracy": test_acc,
        "accuracy_gap": round(accuracy_gap, 4) if accuracy_gap else None,
        "overfitting_detected": overfitting_detected,
        "risk_level": risk_level,
        "threshold_config": {
            "gap_threshold": gap_threshold,
            "min_train": min_train
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Additional warnings
    warnings = []
    if train_acc and train_acc >= 0.99:
        warnings.append("Training accuracy suspiciously high (>= 0.99)")
    if val_acc and val_acc < 0.50:
        warnings.append("Validation accuracy critically low (< 0.50)")
    if test_acc and val_acc and abs(test_acc - val_acc) > 0.10:
        warnings.append("Test/validation accuracy mismatch (> 0.10 gap)")

    if warnings:
        result["warnings"] = warnings

    return result


def batch_analyze_models(models: List[Dict]) -> Dict:
    """
    Analyze multiple models for overfitting patterns.

    Args:
        models: List of model dicts with keys: model_id, train_acc, val_acc, test_acc

    Returns:
        Dict with batch analysis results
    """
    results = []
    overfitting_count = 0
    high_risk_count = 0

    for model in models:
        analysis = analyze_model_metrics(
            model_id=model.get("model_id", "unknown"),
            train_acc=model.get("train_acc"),
            val_acc=model.get("val_acc"),
            test_acc=model.get("test_acc")
        )
        results.append(analysis)

        if analysis["overfitting_detected"]:
            overfitting_count += 1
        if analysis["risk_level"] in ["HIGH", "CRITICAL"]:
            high_risk_count += 1

    return {
        "total_models": len(models),
        "overfitting_count": overfitting_count,
        "high_risk_count": high_risk_count,
        "overfitting_rate": round(overfitting_count / len(models), 4) if models else 0.0,
        "results": results,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def generate_evidence_report(analysis: Dict, output_path: Path) -> None:
    """
    Generate evidence report for audit trail.

    Args:
        analysis: Analysis results from analyze_model_metrics or batch_analyze_models
        output_path: Path to output evidence file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Add evidence hash
    canonical = json.dumps(analysis, sort_keys=True)
    evidence_hash = hashlib.sha256(canonical.encode()).hexdigest()
    analysis["evidence_hash"] = evidence_hash

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Overfitting Detection - Test Run")
    print("=" * 60)

    # Test cases
    test_models = [
        {
            "model_id": "identity_scorer_v1",
            "train_acc": 0.98,
            "val_acc": 0.95,
            "test_acc": 0.94
        },
        {
            "model_id": "fraud_detector_v2",
            "train_acc": 0.99,
            "val_acc": 0.75,  # Overfitting!
            "test_acc": 0.73
        },
        {
            "model_id": "risk_classifier_v1",
            "train_acc": 0.97,
            "val_acc": 0.60,  # Overfitting!
            "test_acc": 0.62
        },
        {
            "model_id": "kyc_validator_v3",
            "train_acc": 0.92,
            "val_acc": 0.90,
            "test_acc": 0.89
        }
    ]

    # Run batch analysis
    batch_result = batch_analyze_models(test_models)

    print(f"\nTotal models analyzed: {batch_result['total_models']}")
    print(f"Overfitting detected: {batch_result['overfitting_count']}")
    print(f"High-risk models: {batch_result['high_risk_count']}")
    print(f"Overfitting rate: {batch_result['overfitting_rate']:.2%}")

    print("\nModel-by-Model Results:")
    for result in batch_result['results']:
        status = "[FAIL]" if result['overfitting_detected'] else "[OK]"
        print(f"  {status} {result['model_id']}: train={result['train_accuracy']:.3f}, val={result['val_accuracy']:.3f}, gap={result['accuracy_gap']:.3f}, risk={result['risk_level']}")

        if result.get("warnings"):
            for warning in result["warnings"]:
                print(f"       WARNING: {warning}")

    # Generate evidence
    repo_root = Path(__file__).resolve().parents[2]
    evidence_path = repo_root / "23_compliance" / "evidence" / "anti_gaming" / f"overfitting_analysis_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    generate_evidence_report(batch_result, evidence_path)

    print(f"\nEvidence report: {evidence_path}")
    print(f"\n[OK] Analysis complete")

    # Exit with error if high-risk models detected
    sys.exit(1 if batch_result['high_risk_count'] > 0 else 0)
