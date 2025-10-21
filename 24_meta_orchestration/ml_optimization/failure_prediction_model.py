#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID - ML-Based Rule Failure Prediction Model (ADVANCED PHASE 4)
Uses historical validation data to predict which rules will fail

Features:
- Logistic Regression (simple, interpretable baseline)
- Random Forest (better accuracy for complex patterns)
- Feature engineering from file changes and rule history
- Confidence scores for prioritization
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import pickle
import hashlib

# Optional imports (gracefully degrade if not available)
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        confusion_matrix, classification_report
    )
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[WARN] sklearn not available - ML features disabled")


class FeatureExtractor:
    """
    Extract features for failure prediction from validation context.

    Features include:
    - File-based: extensions, locations, change patterns
    - Rule-based: historical failure rate, execution time, severity
    - Temporal: time of day, day of week
    - Author-based: developer failure patterns
    """

    def __init__(self, db):
        """
        Initialize feature extractor.

        Args:
            db: ValidationDatabase instance for historical queries
        """
        self.db = db
        self.feature_names = []
        self._initialize_feature_names()

    def _initialize_feature_names(self):
        """Define feature names for model interpretation."""
        self.feature_names = [
            # File-based features (12)
            'num_changed_files',
            'has_yaml_changes',
            'has_py_changes',
            'has_config_changes',
            'has_chart_changes',
            'has_values_changes',
            'has_root_changes',
            'has_compliance_changes',
            'has_test_changes',
            'has_workflow_changes',
            'yaml_file_ratio',
            'py_file_ratio',

            # Rule-based features (5)
            'rule_failure_rate',
            'rule_avg_time_ms',
            'rule_severity_critical',
            'rule_severity_high',
            'rule_recent_failures',

            # Temporal features (3)
            'hour_of_day',
            'day_of_week',
            'is_weekend',

            # Pattern features (3)
            'file_pattern_correlation',
            'co_occurrence_risk',
            'similar_change_failure_rate'
        ]

    def extract_features(
        self,
        changed_files: List[Path],
        rule_id: str,
        author: str = "unknown",
        timestamp: Optional[datetime] = None
    ) -> np.ndarray:
        """
        Extract feature vector for prediction.

        Args:
            changed_files: List of changed file paths
            rule_id: Rule to predict failure for
            author: Commit author
            timestamp: Validation timestamp

        Returns:
            Feature vector as numpy array
        """
        features = []
        timestamp = timestamp or datetime.now()

        # File-based features
        features.append(len(changed_files))  # num_changed_files

        yaml_files = [f for f in changed_files if f.suffix in ['.yaml', '.yml']]
        py_files = [f for f in changed_files if f.suffix == '.py']
        config_files = [f for f in changed_files if 'config' in str(f).lower()]

        features.append(1.0 if yaml_files else 0.0)  # has_yaml_changes
        features.append(1.0 if py_files else 0.0)  # has_py_changes
        features.append(1.0 if config_files else 0.0)  # has_config_changes

        # Specific file patterns
        chart_files = [f for f in changed_files if 'Chart.yaml' in f.name or 'chart.yaml' in f.name]
        values_files = [f for f in changed_files if 'values.yaml' in f.name]
        root_files = [f for f in changed_files if len(f.parts) <= 2]  # Files in root or 1-level deep
        compliance_files = [f for f in changed_files if '23_compliance' in str(f)]
        test_files = [f for f in changed_files if 'test' in str(f).lower()]
        workflow_files = [f for f in changed_files if '.github/workflows' in str(f)]

        features.append(1.0 if chart_files else 0.0)  # has_chart_changes
        features.append(1.0 if values_files else 0.0)  # has_values_changes
        features.append(1.0 if root_files else 0.0)  # has_root_changes
        features.append(1.0 if compliance_files else 0.0)  # has_compliance_changes
        features.append(1.0 if test_files else 0.0)  # has_test_changes
        features.append(1.0 if workflow_files else 0.0)  # has_workflow_changes

        # File type ratios
        total_files = len(changed_files) or 1
        features.append(len(yaml_files) / total_files)  # yaml_file_ratio
        features.append(len(py_files) / total_files)  # py_file_ratio

        # Rule-based features (from historical data)
        failure_rate, avg_time = self.db.get_rule_failure_rate(rule_id, limit=100)
        features.append(failure_rate)  # rule_failure_rate
        features.append(avg_time)  # rule_avg_time_ms

        # Rule severity (would come from rule metadata)
        # For now, infer from rule_id naming patterns
        is_critical = 'critical' in rule_id.lower() or 'root' in rule_id.lower()
        is_high = 'high' in rule_id.lower() or 'guard' in rule_id.lower()
        features.append(1.0 if is_critical else 0.0)  # rule_severity_critical
        features.append(1.0 if is_high else 0.0)  # rule_severity_high

        # Recent failure trend (last 10 executions)
        recent_rate, _ = self.db.get_rule_failure_rate(rule_id, limit=10)
        features.append(recent_rate)  # rule_recent_failures

        # Temporal features
        features.append(timestamp.hour)  # hour_of_day (0-23)
        features.append(timestamp.weekday())  # day_of_week (0=Monday, 6=Sunday)
        features.append(1.0 if timestamp.weekday() >= 5 else 0.0)  # is_weekend

        # Pattern-based features
        file_extensions = list(set(f.suffix for f in changed_files if f.suffix))
        pattern_corr = self.db.get_file_pattern_failure_correlation(file_extensions, rule_id)
        features.append(pattern_corr)  # file_pattern_correlation

        # Co-occurrence risk (are related rules likely to fail?)
        co_occurring = self.db.get_co_occurring_failures(rule_id, limit=5)
        co_risk = sum(count for _, count in co_occurring) / 100.0 if co_occurring else 0.0
        features.append(min(co_risk, 1.0))  # co_occurrence_risk

        # Similar change failure rate (simplified - use file pattern correlation)
        features.append(pattern_corr)  # similar_change_failure_rate

        return np.array(features, dtype=np.float32)

    def extract_features_batch(
        self,
        changed_files: List[Path],
        rule_ids: List[str],
        author: str = "unknown",
        timestamp: Optional[datetime] = None
    ) -> np.ndarray:
        """
        Extract features for multiple rules at once.

        Args:
            changed_files: List of changed file paths
            rule_ids: List of rules to extract features for
            author: Commit author
            timestamp: Validation timestamp

        Returns:
            2D array of features (n_rules x n_features)
        """
        features_list = []
        for rule_id in rule_ids:
            features = self.extract_features(changed_files, rule_id, author, timestamp)
            features_list.append(features)

        return np.vstack(features_list)


class FailurePredictionModel:
    """
    ML model for predicting rule failures.

    Supports:
    - Logistic Regression (fast, interpretable)
    - Random Forest (more accurate)
    - Automatic model selection based on data size
    """

    def __init__(self, db, model_type: str = "random_forest"):
        """
        Initialize failure prediction model.

        Args:
            db: ValidationDatabase instance
            model_type: "logistic" or "random_forest"
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn required for ML features")

        self.db = db
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_extractor = FeatureExtractor(db)
        self.is_trained = False
        self.model_version = None

    def train(self, min_samples: int = 100) -> Dict:
        """
        Train model on historical validation data.

        Args:
            min_samples: Minimum training samples required

        Returns:
            Training metrics dict
        """
        print(f"[ML-TRAIN] Loading training data (min_samples={min_samples})...")

        # Get training data from database
        training_data = self.db.get_training_data(min_samples=min_samples)

        if training_data is None:
            return {
                'success': False,
                'error': f'Insufficient training data (need {min_samples}+ validations)',
                'available_samples': 0
            }

        print(f"[ML-TRAIN] Loaded {training_data['samples_returned']} validation runs")

        # Extract features and labels
        X_list = []
        y_list = []
        rule_ids_seen = set()

        for validation in training_data['validations']:
            changed_files = [Path(f) for f in validation['changed_files']]
            timestamp = datetime.fromisoformat(validation['timestamp'])
            author = validation['author']

            for rule in validation['rules']:
                rule_id = rule['rule_id']
                rule_ids_seen.add(rule_id)

                # Extract features
                features = self.feature_extractor.extract_features(
                    changed_files, rule_id, author, timestamp
                )
                X_list.append(features)

                # Label: 1 = failure, 0 = pass
                y_list.append(0 if rule['passed'] else 1)

        X = np.vstack(X_list)
        y = np.array(y_list)

        print(f"[ML-TRAIN] Extracted {len(X)} training samples for {len(rule_ids_seen)} unique rules")
        print(f"[ML-TRAIN] Failure rate: {y.mean():.1%} ({y.sum()} failures / {len(y)} total)")

        # Check for class imbalance
        if y.mean() < 0.05 or y.mean() > 0.95:
            print(f"[ML-WARN] Severe class imbalance detected ({y.mean():.1%} failures)")

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        print(f"[ML-TRAIN] Training {self.model_type} model...")

        if self.model_type == "logistic":
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight='balanced'  # Handle class imbalance
            )
        else:  # random_forest
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced',
                n_jobs=-1  # Use all CPU cores
            )

        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True

        # Evaluate on test set
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        metrics = {
            'success': True,
            'model_type': self.model_type,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'unique_rules': len(rule_ids_seen),
            'failure_rate': float(y.mean()),
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'false_positive_rate': float(fpr),
            'false_negative_rate': float(fnr),
            'confusion_matrix': {
                'true_negatives': int(tn),
                'false_positives': int(fp),
                'false_negatives': int(fn),
                'true_positives': int(tp)
            },
            'feature_count': len(self.feature_extractor.feature_names)
        }

        # Feature importance (for Random Forest)
        if self.model_type == "random_forest" and hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_importance = [
                {'feature': name, 'importance': float(imp)}
                for name, imp in zip(self.feature_extractor.feature_names, importances)
            ]
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            metrics['feature_importance_top10'] = feature_importance[:10]

        print(f"[ML-TRAIN] Training complete!")
        print(f"[ML-TRAIN] Accuracy: {accuracy:.1%}")
        print(f"[ML-TRAIN] Precision: {precision:.1%}")
        print(f"[ML-TRAIN] Recall: {recall:.1%}")
        print(f"[ML-TRAIN] False Negative Rate: {fnr:.1%} (critical: should be <5%)")

        # Generate model version
        self.model_version = self._generate_model_version(metrics)

        return metrics

    def predict_failure_probability(
        self,
        changed_files: List[Path],
        rule_id: str,
        author: str = "unknown",
        timestamp: Optional[datetime] = None
    ) -> float:
        """
        Predict probability that rule will fail.

        Args:
            changed_files: Changed files in commit
            rule_id: Rule to predict for
            author: Commit author
            timestamp: Validation time

        Returns:
            Probability of failure (0.0 to 1.0)
        """
        if not self.is_trained:
            # Return historical failure rate as fallback
            failure_rate, _ = self.db.get_rule_failure_rate(rule_id)
            return failure_rate

        # Extract features
        features = self.feature_extractor.extract_features(
            changed_files, rule_id, author, timestamp
        )

        # Scale and predict
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        prob = self.model.predict_proba(features_scaled)[0][1]

        return float(prob)

    def predict_batch(
        self,
        changed_files: List[Path],
        rule_ids: List[str],
        author: str = "unknown",
        timestamp: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Predict failure probabilities for multiple rules.

        Args:
            changed_files: Changed files
            rule_ids: Rules to predict for
            author: Commit author
            timestamp: Validation time

        Returns:
            Dict mapping rule_id -> failure_probability
        """
        if not self.is_trained:
            # Return historical rates as fallback
            return {
                rule_id: self.db.get_rule_failure_rate(rule_id)[0]
                for rule_id in rule_ids
            }

        # Extract features for all rules
        features = self.feature_extractor.extract_features_batch(
            changed_files, rule_ids, author, timestamp
        )

        # Scale and predict
        features_scaled = self.scaler.transform(features)
        probs = self.model.predict_proba(features_scaled)[:, 1]

        return {
            rule_id: float(prob)
            for rule_id, prob in zip(rule_ids, probs)
        }

    def save(self, model_path: Path):
        """Save trained model to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'model_version': self.model_version,
            'feature_names': self.feature_extractor.feature_names,
            'is_trained': self.is_trained
        }

        model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"[ML-SAVE] Model saved to {model_path}")

    def load(self, model_path: Path):
        """Load trained model from disk."""
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.model_type = model_data['model_type']
        self.model_version = model_data['model_version']
        self.feature_extractor.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']

        print(f"[ML-LOAD] Model loaded from {model_path}")
        print(f"[ML-LOAD] Version: {self.model_version}")

    def _generate_model_version(self, metrics: Dict) -> str:
        """Generate unique model version identifier."""
        # Hash based on training data and performance
        version_str = (
            f"{metrics['training_samples']}_"
            f"{metrics['accuracy']:.3f}_"
            f"{metrics['f1_score']:.3f}_"
            f"{datetime.now().isoformat()}"
        )
        version_hash = hashlib.sha256(version_str.encode()).hexdigest()[:12]
        return f"v1_{version_hash}"
