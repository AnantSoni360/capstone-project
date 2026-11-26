"""
Phase 03: Exploratory Data Analysis & Leakage-Free Stratified Splitting
Generates statistical visualizations, audits shortcut features, and produces
reproducible 70/15/15 train/val/test splits with zero cross-split leakage.
"""

import json
import pathlib
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
INTERIM_DATA_PATH = WORKSPACE_ROOT / "data" / "interim" / "parsed_requests.csv"
PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
METADATA_PATH = PROCESSED_DIR / "split_metadata.json"

# Ensure output directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def generate_eda_figures(df: pd.DataFrame):
    """
    Generate and save publication-quality figures for academic reports.
    """
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({"font.size": 11, "figure.autolayout": True})

    # 1. Class Distribution Plot
    fig, ax = plt.subplots(figsize=(7, 4.5))
    class_counts = df["ground_truth"].value_counts().rename({0: "Normal (0)", 1: "Anomalous (1)"})
    sns.barplot(x=class_counts.index, y=class_counts.values, ax=ax, palette=["#2ecc71", "#e74c3c"])
    ax.set_title("Ground Truth Class Distribution (Deduplicated Corpus)", fontsize=13, weight="bold")
    ax.set_ylabel("Request Count")
    ax.set_xlabel("Traffic Class")
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                    ha="center", va="center", color="white", weight="bold", fontsize=11)
    fig.savefig(FIGURES_DIR / "class_distribution.png", dpi=300)
    plt.close(fig)

    # 2. Diagnostic Attack Breakdown
    fig, ax = plt.subplots(figsize=(8, 4.5))
    diag_counts = df["diagnostic_category"].value_counts()
    sns.barplot(x=diag_counts.values, y=diag_counts.index, ax=ax, palette="mako")
    ax.set_title("Distribution of Traffic & Diagnostic Threat Categories", fontsize=13, weight="bold")
    ax.set_xlabel("Request Count")
    ax.set_ylabel("Category")
    for p in ax.patches:
        ax.annotate(f" {int(p.get_width()):,}", (p.get_width(), p.get_y() + p.get_height() / 2),
                    ha="left", va="center", fontsize=10)
    fig.savefig(FIGURES_DIR / "diagnostic_category_distribution.png", dpi=300)
    plt.close(fig)

    # 3. Request Length Distribution (Normal vs Anomalous)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(data=df, x="payload_length", hue="ground_truth", bins=50,
                 log_scale=(False, True), palette=["#2ecc71", "#e74c3c"],
                 element="step", common_norm=False, ax=ax)
    ax.set_title("Payload Length Distribution (Log Scale Count)", fontsize=13, weight="bold")
    ax.set_xlabel("Payload Character Length")
    ax.set_ylabel("Frequency (Log Scale)")
    ax.legend(labels=["Anomalous (1)", "Normal (0)"])
    fig.savefig(FIGURES_DIR / "payload_length_distribution.png", dpi=300)
    plt.close(fig)

    # 4. Special Character Comparison
    special_chars = ["'", '"', ";", "<", ">", "%", "-"]
    char_data = []
    for char in special_chars:
        norm_avg = df[df["ground_truth"] == 0]["full_payload"].fillna("").str.count(f"\\{char}").mean()
        anom_avg = df[df["ground_truth"] == 1]["full_payload"].fillna("").str.count(f"\\{char}").mean()
        char_data.append({"Char": char, "Class": "Normal (0)", "Mean Count": norm_avg})
        char_data.append({"Char": char, "Class": "Anomalous (1)", "Mean Count": anom_avg})

    char_df = pd.DataFrame(char_data)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=char_df, x="Char", y="Mean Count", hue="Class",
                palette=["#2ecc71", "#e74c3c"], ax=ax)
    ax.set_title("Average Special Character Frequencies per Request", fontsize=13, weight="bold")
    ax.set_ylabel("Average Count per Payload")
    ax.set_xlabel("Special Character")
    fig.savefig(FIGURES_DIR / "special_characters_comparison.png", dpi=300)
    plt.close(fig)

    # 5. Method Distribution
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(data=df, x="method", hue="ground_truth", palette=["#2ecc71", "#e74c3c"], ax=ax)
    ax.set_title("HTTP Method Distribution by Traffic Class", fontsize=13, weight="bold")
    ax.set_xlabel("HTTP Method")
    ax.set_ylabel("Request Count")
    ax.legend(title="Class", labels=["Normal (0)", "Anomalous (1)"])
    fig.savefig(FIGURES_DIR / "method_distribution.png", dpi=300)
    plt.close(fig)

    print(f"[EDA] Generated 5 publication figures in: {FIGURES_DIR}")


def perform_stratified_split(df: pd.DataFrame):
    """
    Perform 70% Train, 15% Validation, 15% Test stratified partition.
    Ensures zero cross-split duplicate leakage and preserves the untouched test set.
    """
    print("[Splitting] Partitioning dataset into 70% Train, 15% Val, 15% Test...")

    # First split: 70% Train, 30% Temp (Val + Test)
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["ground_truth"],
        shuffle=True
    )

    # Second split: Split Temp 50/50 to get 15% Val and 15% Test
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["ground_truth"],
        shuffle=True
    )

    # Audit for zero cross-split leakage
    train_keys = set(zip(train_df["method"], train_df["raw_url"], train_df["body"].fillna("")))
    val_keys = set(zip(val_df["method"], val_df["raw_url"], val_df["body"].fillna("")))
    test_keys = set(zip(test_df["method"], test_df["raw_url"], test_df["body"].fillna("")))

    leakage_train_val = len(train_keys.intersection(val_keys))
    leakage_train_test = len(train_keys.intersection(test_keys))
    leakage_val_test = len(val_keys.intersection(test_keys))

    assert leakage_train_val == 0, f"Leakage detected between train and val: {leakage_train_val}"
    assert leakage_train_test == 0, f"Leakage detected between train and test: {leakage_train_test}"
    assert leakage_val_test == 0, f"Leakage detected between val and test: {leakage_val_test}"
    print("[Audit] Confirmed ZERO cross-split payload leakage!")

    # Save partitions
    train_path = PROCESSED_DIR / "train.csv"
    val_path = PROCESSED_DIR / "val.csv"
    test_path = PROCESSED_DIR / "test_frozen.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    metadata = {
        "random_seed": 42,
        "split_ratio": {"train": 0.70, "validation": 0.15, "test": 0.15},
        "row_counts": {
            "total_deduplicated": len(df),
            "train": len(train_df),
            "validation": len(val_df),
            "test_frozen": len(test_df)
        },
        "class_distributions": {
            "train": train_df["ground_truth"].value_counts().to_dict(),
            "validation": val_df["ground_truth"].value_counts().to_dict(),
            "test_frozen": test_df["ground_truth"].value_counts().to_dict()
        },
        "class_balance_percentages": {
            "train_anomalous_pct": round(train_df["ground_truth"].mean() * 100, 2),
            "validation_anomalous_pct": round(val_df["ground_truth"].mean() * 100, 2),
            "test_anomalous_pct": round(test_df["ground_truth"].mean() * 100, 2)
        },
        "leakage_audit": {
            "train_val_overlap": leakage_train_val,
            "train_test_overlap": leakage_train_test,
            "val_test_overlap": leakage_val_test
        }
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[Splitting] Saved train split: {train_path} ({len(train_df)} rows)")
    print(f"[Splitting] Saved val split: {val_path} ({len(val_df)} rows)")
    print(f"[Splitting] Saved FROZEN test split: {test_path} ({len(test_df)} rows)")
    print(f"[Splitting] Saved split metadata: {METADATA_PATH}")

    return metadata


def main():
    print(f"[Phase 03] Reading interim data from: {INTERIM_DATA_PATH}")
    df = pd.read_csv(INTERIM_DATA_PATH)
    print(f"Loaded {len(df)} records.")

    # 1. Generate Figures
    generate_eda_figures(df)

    # 2. Perform Partitioning
    metadata = perform_stratified_split(df)
    print("\n=== SPLIT SUMMARY ===")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
