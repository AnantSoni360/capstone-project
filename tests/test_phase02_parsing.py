import json
import pathlib
import pandas as pd
import pytest

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
PARSED_CSV_PATH = WORKSPACE_ROOT / "data" / "interim" / "parsed_requests.csv"
SUMMARY_JSON_PATH = WORKSPACE_ROOT / "data" / "interim" / "parsing_summary.json"


def test_interim_dataset_integrity():
    assert PARSED_CSV_PATH.exists(), f"Parsed CSV missing at {PARSED_CSV_PATH}"
    assert SUMMARY_JSON_PATH.exists(), f"Summary JSON missing at {SUMMARY_JSON_PATH}"

    with open(SUMMARY_JSON_PATH, "r", encoding="utf-8") as f:
        summary = json.load(f)

    assert summary["raw_record_count"] == 61065
    assert summary["deduplicated_record_count"] == 25608
    assert summary["duplicate_count_removed"] == 35457

    df = pd.read_csv(PARSED_CSV_PATH)
    assert len(df) == 25608
    expected_cols = [
        "method", "raw_url", "path", "query", "body",
        "decoded_path", "decoded_query", "decoded_body",
        "full_payload", "param_count", "payload_length",
        "ground_truth", "diagnostic_category"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing column {col} in parsed dataset"

    # Verify no nulls in ground truth
    assert df["ground_truth"].isnull().sum() == 0
    assert set(df["ground_truth"].unique()) == {0, 1}

    # Verify exact unique counts match summary
    assert (df["ground_truth"] == 0).sum() == summary["ground_truth_distribution"]["0_normal"]
    assert (df["ground_truth"] == 1).sum() == summary["ground_truth_distribution"]["1_anomalous"]
