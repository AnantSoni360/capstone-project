import json
import pathlib
import pandas as pd
import pytest

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORTS_DIR = WORKSPACE_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
BENCHMARK_CSV = REPORTS_DIR / "final_model_benchmark_test_set.csv"
BENCHMARK_JSON = REPORTS_DIR / "final_model_benchmark.json"
ROBUSTNESS_JSON = REPORTS_DIR / "robustness_metrics.json"


def test_robustness_artifacts_exist():
    """Verify adversarial robustness JSON and comparison figure exist."""
    assert ROBUSTNESS_JSON.exists(), f"Missing {ROBUSTNESS_JSON}"
    assert (FIGURES_DIR / "robustness_comparison.png").exists()
    assert (FIGURES_DIR / "robustness_comparison.png").stat().st_size > 5000

    with open(ROBUSTNESS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "Traditional_Rules" in data
    assert "XGBoost" in data
    assert "PyTorch_1D_CNN" in data

    # Verify all 6 vectors are evaluated
    vectors = [
        "baseline_clean", "double_url_encoding", "comment_injection",
        "mixed_casing", "whitespace_substitution", "equivalent_tautologies"
    ]
    for v in vectors:
        assert v in data["Traditional_Rules"]
        assert v in data["XGBoost"]
        assert v in data["PyTorch_1D_CNN"]


def test_final_benchmark_artifacts_and_results():
    """Verify final test benchmark artifacts exist and validate academic criteria."""
    assert BENCHMARK_CSV.exists(), f"Missing {BENCHMARK_CSV}"
    assert BENCHMARK_JSON.exists(), f"Missing {BENCHMARK_JSON}"
    assert (FIGURES_DIR / "master_model_benchmark.png").exists()

    df = pd.read_csv(BENCHMARK_CSV)
    assert len(df) == 9, f"Expected 9 systems evaluated on test set, found {len(df)}"

    # PyTorch 1D-CNN and XGBoost should be the top-tier models
    top_models = df[df["System"].isin(["PyTorch 1D CNN", "Xgboost"])]
    for _, row in top_models.iterrows():
        assert row["F1_Score"] > 0.90, f"F1 score too low on frozen test set for {row['System']}: {row['F1_Score']}"
        assert row["Accuracy"] > 0.90, f"Accuracy too low on frozen test set for {row['System']}: {row['Accuracy']}"
        assert row["Latency_ms"] < 5.0, f"Latency exceeds budget for {row['System']}: {row['Latency_ms']} ms"

    # Traditional Rule WAF baseline checks
    rule_row = df[df["System"] == "Traditional Rule WAF"].iloc[0]
    assert rule_row["Precision"] > 0.95, "Rule precision should be very high on clear signatures"
    assert rule_row["False_Negative_Rate"] > 0.50, "Rule engine should have high FNR on diverse attack vectors"
