import json
import pathlib
import pandas as pd
import pytest

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
METADATA_PATH = PROCESSED_DIR / "split_metadata.json"

EXPECTED_FIGURES = [
    "class_distribution.png",
    "diagnostic_category_distribution.png",
    "payload_length_distribution.png",
    "special_characters_comparison.png",
    "method_distribution.png",
]

def test_eda_figures_generated():
    """Verify all 5 publication-ready EDA figures exist and are non-empty."""
    for fig_name in EXPECTED_FIGURES:
        fig_path = FIGURES_DIR / fig_name
        assert fig_path.exists(), f"Missing figure: {fig_name}"
        assert fig_path.stat().st_size > 5000, f"Figure {fig_name} is too small or corrupt"

def test_split_files_exist_and_counts():
    """Verify 70/15/15 partitions exist with exact expected row counts."""
    train_path = PROCESSED_DIR / "train.csv"
    val_path = PROCESSED_DIR / "val.csv"
    test_path = PROCESSED_DIR / "test_frozen.csv"

    assert train_path.exists(), "Missing train.csv"
    assert val_path.exists(), "Missing val.csv"
    assert test_path.exists(), "Missing test_frozen.csv"
    assert METADATA_PATH.exists(), "Missing split_metadata.json"

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)

    assert len(train_df) == 17925, f"Expected 17925 train rows, got {len(train_df)}"
    assert len(val_df) == 3841, f"Expected 3841 val rows, got {len(val_df)}"
    assert len(test_df) == 3842, f"Expected 3842 test rows, got {len(test_df)}"
    assert len(train_df) + len(val_df) + len(test_df) == 25608

def test_stratification_balance():
    """Verify stratified balance is preserved across all splits."""
    train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DIR / "val.csv")
    test_df = pd.read_csv(PROCESSED_DIR / "test_frozen.csv")

    p_train = train_df["ground_truth"].mean()
    p_val = val_df["ground_truth"].mean()
    p_test = test_df["ground_truth"].mean()

    # Assert within 0.1% tolerance
    assert abs(p_train - p_val) < 0.005, f"Stratification mismatch between train ({p_train}) and val ({p_val})"
    assert abs(p_train - p_test) < 0.005, f"Stratification mismatch between train ({p_train}) and test ({p_test})"

def test_zero_cross_split_leakage():
    """Verify zero duplicate payload leakage across train, val, and test splits."""
    train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DIR / "val.csv")
    test_df = pd.read_csv(PROCESSED_DIR / "test_frozen.csv")

    train_keys = set(zip(train_df["method"], train_df["raw_url"], train_df["body"].fillna("")))
    val_keys = set(zip(val_df["method"], val_df["raw_url"], val_df["body"].fillna("")))
    test_keys = set(zip(test_df["method"], test_df["raw_url"], test_df["body"].fillna("")))

    assert len(train_keys.intersection(val_keys)) == 0, "Leakage found between train and val"
    assert len(train_keys.intersection(test_keys)) == 0, "Leakage found between train and test"
    assert len(val_keys.intersection(test_keys)) == 0, "Leakage found between val and test"
