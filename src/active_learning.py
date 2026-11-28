"""
src/active_learning.py
=============================================================================
Active Continuous Learning & SOC Human-in-the-Loop Feedback Engine
-----------------------------------------------------------------------------
Captures analyst feedback on ambiguous / REVIEW requests, logs ground-truth labels,
and triggers continuous online calibration to reduce false positives and adapt
to emerging threat mutations over time without downtime.
=============================================================================
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
import sqlite3


class ActiveLearningEngine:
    """
    Manages human-in-the-loop feedback and incremental decision recalibration.
    """

    def __init__(self, db_path: str = "backend/active_learning.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyst_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    payload TEXT NOT NULL,
                    assigned_verdict TEXT NOT NULL,
                    true_label INTEGER NOT NULL, -- 0 for Benign, 1 for Attack
                    analyst_notes TEXT,
                    analyst_id TEXT DEFAULT 'SOC_TIER1',
                    retrained_flag INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calibration_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    block_threshold REAL,
                    review_threshold REAL,
                    sample_count_retrained INTEGER,
                    status TEXT
                )
            """)
            conn.commit()

    def submit_feedback(self, payload: str, assigned_verdict: str, true_label: int, notes: str = "", analyst_id: str = "SOC_ANALYST") -> Dict[str, Any]:
        """
        Records human-in-the-loop ground truth verification from SOC analyst.
        """
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analyst_feedback (timestamp, payload, assigned_verdict, true_label, analyst_notes, analyst_id, retrained_flag)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (now, payload, assigned_verdict, int(true_label), notes, analyst_id))
            conn.commit()
            record_id = cursor.lastrowid

        return {
            "status": "success",
            "feedback_id": record_id,
            "true_label": "ATTACK" if true_label == 1 else "BENIGN",
            "message": "Analyst feedback recorded in active learning training pool."
        }

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """
        Returns summary metrics of logged analyst feedback.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM analyst_feedback")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM analyst_feedback WHERE true_label = 0")
            confirmed_benign = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM analyst_feedback WHERE true_label = 1")
            confirmed_attack = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM analyst_feedback WHERE retrained_flag = 0")
            pending_retrain = cursor.fetchone()[0]

        return {
            "total_feedback_samples": total,
            "confirmed_benign_count": confirmed_benign,
            "confirmed_attack_count": confirmed_attack,
            "pending_retrain_count": pending_retrain
        }

    def trigger_adaptive_recalibration(self, current_block_thresh: float = 0.65, current_review_thresh: float = 0.35) -> Dict[str, Any]:
        """
        Performs adaptive threshold recalibration based on recent feedback.
        If recent feedback indicates high false positive rate (benign flagged as review/block),
        safely adapts the threshold to preserve legitimate traffic availability.
        """
        stats = self.get_feedback_statistics()
        pending = stats["pending_retrain_count"]

        if pending == 0:
            return {
                "status": "noop",
                "message": "No new feedback samples available for recalibration.",
                "block_threshold": current_block_thresh,
                "review_threshold": current_review_thresh
            }

        # Calculate false positive ratio in pending feedback
        benign_ratio = stats["confirmed_benign_count"] / max(1, stats["total_feedback_samples"])

        # Dynamically adjust thresholds slightly if needed
        new_block_thresh = current_block_thresh
        new_review_thresh = current_review_thresh

        if benign_ratio > 0.40:
            # High false alarm rate: raise review lower bound slightly to dampen alarms
            new_review_thresh = min(0.42, current_review_thresh + 0.02)
        elif stats["confirmed_attack_count"] > stats["confirmed_benign_count"] * 2:
            # High attack rate: lower threshold slightly to tighten security
            new_block_thresh = max(0.60, current_block_thresh - 0.02)

        # Mark samples as retrained
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE analyst_feedback SET retrained_flag = 1 WHERE retrained_flag = 0")
            cursor.execute("""
                INSERT INTO calibration_history (timestamp, block_threshold, review_threshold, sample_count_retrained, status)
                VALUES (?, ?, ?, ?, 'SUCCESS')
            """, (time.time(), new_block_thresh, new_review_thresh, pending))
            conn.commit()

        return {
            "status": "recalibrated",
            "samples_processed": pending,
            "previous_block_thresh": current_block_thresh,
            "new_block_thresh": round(new_block_thresh, 4),
            "previous_review_thresh": current_review_thresh,
            "new_review_thresh": round(new_review_thresh, 4),
            "timestamp": time.time()
        }
