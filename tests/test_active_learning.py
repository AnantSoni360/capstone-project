"""
tests/test_active_learning.py
Unit tests for Active Continuous Learning & SOC Human-in-the-Loop Feedback Engine.
"""

import os
import pytest
from src.active_learning import ActiveLearningEngine

@pytest.fixture
def engine(tmp_path):
    test_db = str(tmp_path / "test_active_learning.db")
    return ActiveLearningEngine(db_path=test_db)

def test_submit_feedback(engine):
    res = engine.submit_feedback(
        payload="/product?name=O'Connor",
        assigned_verdict="REVIEW",
        true_label=0,
        notes="Legitimate customer name with apostrophe"
    )
    assert res["status"] == "success"
    assert res["true_label"] == "BENIGN"

    stats = engine.get_feedback_statistics()
    assert stats["total_feedback_samples"] == 1
    assert stats["confirmed_benign_count"] == 1
    assert stats["pending_retrain_count"] == 1

def test_adaptive_recalibration_loop(engine):
    # Submit 3 benign false alarms
    for i in range(3):
        engine.submit_feedback(f"payload_{i}", "REVIEW", true_label=0, notes="Benign query")

    # Trigger recalibration
    recal = engine.trigger_adaptive_recalibration(current_block_thresh=0.65, current_review_thresh=0.35)
    assert recal["status"] == "recalibrated"
    assert recal["samples_processed"] == 3
    assert recal["new_review_thresh"] >= 0.35

    # Check pending samples cleared
    stats = engine.get_feedback_statistics()
    assert stats["pending_retrain_count"] == 0
