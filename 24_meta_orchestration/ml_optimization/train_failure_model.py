#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID - ML Model Training Script (ADVANCED PHASE 4)
Trains failure prediction model on historical validation data

Usage:
    python train_failure_model.py --min-samples 100 --model-type random_forest
    python train_failure_model.py --retrain --accuracy-threshold 0.75
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from validation_database import ValidationDatabase
    from failure_prediction_model import FailurePredictionModel, SKLEARN_AVAILABLE
except ImportError:
    from .validation_database import ValidationDatabase
    from .failure_prediction_model import FailurePredictionModel, SKLEARN_AVAILABLE


class ModelTrainer:
    """
    Manages ML model training and retraining.

    Handles:
    - Initial training from scratch
    - Periodic retraining with new data
    - Model versioning and storage
    - Performance tracking
    """

    def __init__(self, repo_root: Path, db_path: Optional[Path] = None):
        """
        Initialize model trainer.

        Args:
            repo_root: Repository root directory
            db_path: Path to validation database
        """
        self.repo_root = Path(repo_root)

        if db_path is None:
            db_path = self.repo_root / ".ssid_cache" / "validation_history.db"

        self.db = ValidationDatabase(db_path)
        self.models_dir = self.repo_root / ".ssid_cache" / "ml_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def check_training_readiness(self, min_samples: int = 100) -> dict:
        """
        Check if we have enough data to train.

        Args:
            min_samples: Minimum validation runs required

        Returns:
            Dict with readiness status
        """
        stats = self.db.get_stats()

        status = {
            'ready': stats['total_validations'] >= min_samples,
            'total_validations': stats['total_validations'],
            'min_required': min_samples,
            'deficit': max(0, min_samples - stats['total_validations']),
            'total_rule_executions': stats['total_rule_executions']
        }

        return status

    def train_new_model(
        self,
        model_type: str = "random_forest",
        min_samples: int = 100
    ) -> dict:
        """
        Train new ML model from scratch.

        Args:
            model_type: "logistic" or "random_forest"
            min_samples: Minimum training samples

        Returns:
            Training metrics dict
        """
        if not SKLEARN_AVAILABLE:
            return {
                'success': False,
                'error': 'sklearn not available - ML features disabled'
            }

        print(f"[TRAIN] Starting new {model_type} model training...")
        print(f"[TRAIN] Minimum samples required: {min_samples}")

        # Check readiness
        readiness = self.check_training_readiness(min_samples)
        if not readiness['ready']:
            return {
                'success': False,
                'error': f"Insufficient training data: {readiness['total_validations']}/{min_samples}",
                'readiness': readiness
            }

        print(f"[TRAIN] Found {readiness['total_validations']} validation runs")
        print(f"[TRAIN] Total rule executions: {readiness['total_rule_executions']}")

        # Initialize model
        predictor = FailurePredictionModel(self.db, model_type=model_type)

        # Train
        metrics = predictor.train(min_samples=min_samples)

        if not metrics['success']:
            return metrics

        # Save model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"failure_predictor_{model_type}_{timestamp}.pkl"
        model_path = self.models_dir / model_filename
        predictor.save(model_path)

        # Create symlink to latest model
        latest_path = self.models_dir / f"failure_predictor_{model_type}_latest.pkl"
        if latest_path.exists():
            latest_path.unlink()
        try:
            latest_path.symlink_to(model_filename)
        except OSError:
            # Windows may not support symlinks, copy instead
            import shutil
            shutil.copy(model_path, latest_path)

        print(f"[TRAIN] Model saved: {model_path}")
        print(f"[TRAIN] Latest symlink: {latest_path}")

        # Store metrics in database
        self.db.store_model_metrics(
            model_version=predictor.model_version,
            metrics=metrics,
            model_path=str(model_path)
        )

        # Add paths to metrics
        metrics['model_path'] = str(model_path)
        metrics['model_version'] = predictor.model_version

        return metrics

    def should_retrain(self, accuracy_threshold: float = 0.75, max_age_days: int = 30) -> dict:
        """
        Check if model should be retrained.

        Args:
            accuracy_threshold: Minimum acceptable accuracy
            max_age_days: Maximum model age in days

        Returns:
            Dict with retrain recommendation
        """
        stats = self.db.get_stats()

        if 'latest_model' not in stats:
            return {
                'should_retrain': True,
                'reason': 'No model exists',
                'stats': stats
            }

        latest_model = stats['latest_model']

        # Check accuracy threshold
        if latest_model['accuracy'] < accuracy_threshold:
            return {
                'should_retrain': True,
                'reason': f"Accuracy {latest_model['accuracy']:.1%} below threshold {accuracy_threshold:.1%}",
                'current_accuracy': latest_model['accuracy'],
                'threshold': accuracy_threshold
            }

        # Check false negative rate (critical)
        if latest_model['false_negative_rate'] > 0.05:
            return {
                'should_retrain': True,
                'reason': f"False negative rate {latest_model['false_negative_rate']:.1%} above 5%",
                'current_fnr': latest_model['false_negative_rate']
            }

        # Could add age-based retraining, but would need timestamp in model_metrics table

        return {
            'should_retrain': False,
            'reason': 'Model performance acceptable',
            'current_accuracy': latest_model['accuracy'],
            'current_fnr': latest_model['false_negative_rate']
        }

    def print_training_report(self, metrics: dict):
        """Print formatted training report."""
        print("\n" + "=" * 70)
        print("ML MODEL TRAINING REPORT")
        print("=" * 70)

        if not metrics['success']:
            print(f"\n[ERROR] Training failed: {metrics.get('error', 'Unknown error')}")
            return

        print(f"\nModel Type: {metrics['model_type']}")
        print(f"Model Version: {metrics.get('model_version', 'N/A')}")
        print(f"\nTraining Data:")
        print(f"  Training samples: {metrics['training_samples']}")
        print(f"  Test samples: {metrics['test_samples']}")
        print(f"  Unique rules: {metrics['unique_rules']}")
        print(f"  Failure rate: {metrics['failure_rate']:.1%}")

        print(f"\nPerformance Metrics:")
        print(f"  Accuracy: {metrics['accuracy']:.1%}")
        print(f"  Precision: {metrics['precision']:.1%}")
        print(f"  Recall: {metrics['recall']:.1%}")
        print(f"  F1 Score: {metrics['f1_score']:.3f}")

        print(f"\nError Rates:")
        print(f"  False Positive Rate: {metrics['false_positive_rate']:.1%}")
        print(f"  False Negative Rate: {metrics['false_negative_rate']:.1%}", end='')

        if metrics['false_negative_rate'] > 0.05:
            print(" [WARN: Above 5% threshold]")
        else:
            print(" [OK: Below 5% threshold]")

        print(f"\nConfusion Matrix:")
        cm = metrics['confusion_matrix']
        print(f"  True Negatives:  {cm['true_negatives']:4d}")
        print(f"  False Positives: {cm['false_positives']:4d}")
        print(f"  False Negatives: {cm['false_negatives']:4d}")
        print(f"  True Positives:  {cm['true_positives']:4d}")

        if 'feature_importance_top10' in metrics:
            print(f"\nTop 10 Important Features:")
            for feat in metrics['feature_importance_top10']:
                print(f"  {feat['feature']:30s} {feat['importance']:.3f}")

        print(f"\nModel saved to: {metrics.get('model_path', 'N/A')}")
        print("=" * 70)


def main():
    """Main entry point for model training."""
    parser = argparse.ArgumentParser(
        description="Train ML model for rule failure prediction"
    )
    parser.add_argument(
        '--model-type',
        choices=['logistic', 'random_forest'],
        default='random_forest',
        help='ML model type (default: random_forest)'
    )
    parser.add_argument(
        '--min-samples',
        type=int,
        default=100,
        help='Minimum validation runs required for training (default: 100)'
    )
    parser.add_argument(
        '--retrain',
        action='store_true',
        help='Check if retraining is needed and retrain if necessary'
    )
    parser.add_argument(
        '--accuracy-threshold',
        type=float,
        default=0.75,
        help='Minimum acceptable accuracy for retraining (default: 0.75)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force training even if model exists and performs well'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path.cwd(),
        help='Repository root directory'
    )
    parser.add_argument(
        '--db-path',
        type=Path,
        help='Custom database path'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check training readiness, do not train'
    )
    parser.add_argument(
        '--json-output',
        type=Path,
        help='Write metrics to JSON file'
    )

    args = parser.parse_args()

    # Initialize trainer
    trainer = ModelTrainer(repo_root=args.repo_root, db_path=args.db_path)

    # Check training readiness
    readiness = trainer.check_training_readiness(args.min_samples)

    print("=" * 70)
    print("ML MODEL TRAINING")
    print("=" * 70)
    print(f"\nTraining readiness check:")
    print(f"  Validation runs: {readiness['total_validations']}/{readiness['min_required']}")
    print(f"  Rule executions: {readiness['total_rule_executions']}")
    print(f"  Status: {'READY' if readiness['ready'] else f'NOT READY (need {readiness['deficit']} more)'}")

    if args.check_only:
        sys.exit(0 if readiness['ready'] else 1)

    if not readiness['ready']:
        print(f"\n[ERROR] Insufficient training data")
        print(f"[INFO] Run validator with --store-results to collect data")
        print(f"[INFO] Need {readiness['deficit']} more validation runs")
        sys.exit(1)

    # Check if retraining is needed
    if args.retrain and not args.force:
        retrain_check = trainer.should_retrain(accuracy_threshold=args.accuracy_threshold)
        print(f"\nRetrain check:")
        print(f"  Should retrain: {retrain_check['should_retrain']}")
        print(f"  Reason: {retrain_check['reason']}")

        if not retrain_check['should_retrain']:
            print("\n[INFO] Model performance acceptable - no retraining needed")
            print("[INFO] Use --force to retrain anyway")
            sys.exit(0)

    # Train model
    print(f"\nTraining {args.model_type} model...")
    metrics = trainer.train_new_model(
        model_type=args.model_type,
        min_samples=args.min_samples
    )

    # Print report
    trainer.print_training_report(metrics)

    # Save JSON output if requested
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_output, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"\n[INFO] Metrics saved to: {args.json_output}")

    # Exit with success if training succeeded
    sys.exit(0 if metrics['success'] else 1)


if __name__ == "__main__":
    main()
