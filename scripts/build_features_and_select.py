"""
Feature Engineering Execution & Selection Script (Phase 04)
Fits FeatureExtractor strictly on train split, transforms val and test splits,
stores sparse matrices in SciPy NPZ format, and evaluates feature importance.
"""

import json
import pathlib
import sys
import time

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.linear_model import LogisticRegression

from src.features import FeatureExtractor

PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
MODELS_DIR = WORKSPACE_ROOT / "models"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
PIPELINE_PATH = MODELS_DIR / "feature_extractor.joblib"
METADATA_PATH = PROCESSED_DIR / "feature_metadata.json"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def main():
    start_time = time.time()
    print("[Phase 04] Loading data partitions...")
    train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DIR / "val.csv")
    test_df = pd.read_csv(PROCESSED_DIR / "test_frozen.csv")

    y_train = train_df["ground_truth"].values.astype(int)
    y_val = val_df["ground_truth"].values.astype(int)
    y_test = test_df["ground_truth"].values.astype(int)

    # 1. Fit Feature Extractor strictly on Train
    extractor = FeatureExtractor(max_tfidf_features=500, char_ngram_range=(3, 5))
    extractor.fit(train_df)

    # 2. Transform splits
    print("[Phase 04] Transforming train split...")
    X_train_num, X_train_tfidf, X_train_comb = extractor.transform(train_df)

    print("[Phase 04] Transforming validation split...")
    X_val_num, X_val_tfidf, X_val_comb = extractor.transform(val_df)

    print("[Phase 04] Transforming FROZEN test split...")
    X_test_num, X_test_tfidf, X_test_comb = extractor.transform(test_df)

    # 3. Save fitted pipeline
    extractor.save(str(PIPELINE_PATH))

    # 4. Save matrices (SciPy NPZ for sparse, NumPy NPY for dense targets & numerical)
    print("[Phase 04] Saving sparse matrices and dense feature sets...")
    sparse.save_npz(PROCESSED_DIR / "X_train_combined.npz", X_train_comb)
    sparse.save_npz(PROCESSED_DIR / "X_val_combined.npz", X_val_comb)
    sparse.save_npz(PROCESSED_DIR / "X_test_combined.npz", X_test_comb)

    sparse.save_npz(PROCESSED_DIR / "X_train_tfidf.npz", X_train_tfidf)
    sparse.save_npz(PROCESSED_DIR / "X_val_tfidf.npz", X_val_tfidf)
    sparse.save_npz(PROCESSED_DIR / "X_test_tfidf.npz", X_test_tfidf)

    np.save(PROCESSED_DIR / "X_train_num.npy", X_train_num)
    np.save(PROCESSED_DIR / "X_val_num.npy", X_val_num)
    np.save(PROCESSED_DIR / "X_test_num.npy", X_test_num)

    np.save(PROCESSED_DIR / "y_train.npy", y_train)
    np.save(PROCESSED_DIR / "y_val.npy", y_val)
    np.save(PROCESSED_DIR / "y_test.npy", y_test)

    # 5. Feature Selection Evaluation on Handcrafted Features
    print("[Phase 04] Running Feature Importance & Selection...")
    num_feature_names = extractor.feature_names

    # Method 1: Random Forest Feature Importance
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train_num, y_train)
    rf_importances = rf.feature_importances_

    # Method 2: SelectKBest (ANOVA F-statistic)
    selector_kbest = SelectKBest(score_func=f_classif, k=20)
    selector_kbest.fit(X_train_num, y_train)
    kbest_scores = selector_kbest.scores_

    # Method 3: Recursive Feature Elimination (RFE) on Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42)
    rfe = RFE(estimator=lr, n_features_to_select=20, step=5)
    rfe.fit(X_train_num, y_train)
    rfe_ranking = rfe.ranking_

    importance_df = pd.DataFrame({
        "feature": num_feature_names,
        "rf_importance": rf_importances,
        "f_score": np.nan_to_num(kbest_scores),
        "rfe_rank": rfe_ranking
    }).sort_values(by="rf_importance", ascending=False)

    top20_rf = importance_df.head(20)

    # 6. Generate Publication Feature Importance Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top20_rf, x="rf_importance", y="feature", palette="viridis", ax=ax)
    ax.set_title("Top 20 Domain Features by Random Forest Importance", fontsize=13, weight="bold")
    ax.set_xlabel("Relative Importance Score")
    ax.set_ylabel("Feature Name")
    fig.savefig(FIGURES_DIR / "feature_importance.png", dpi=300)
    plt.close(fig)

    metadata = {
        "execution_time_seconds": round(time.time() - start_time, 2),
        "feature_dimensions": {
            "handcrafted_numerical_features": len(num_feature_names),
            "tfidf_char_ngram_features": X_train_tfidf.shape[1],
            "total_combined_features": X_train_comb.shape[1]
        },
        "matrix_shapes": {
            "X_train_combined": list(X_train_comb.shape),
            "X_val_combined": list(X_val_comb.shape),
            "X_test_combined": list(X_test_comb.shape)
        },
        "top_10_features_by_rf_importance": top20_rf.head(10)[["feature", "rf_importance"]].to_dict(orient="records"),
        "top_10_features_by_f_score": importance_df.sort_values(by="f_score", ascending=False).head(10)[["feature", "f_score"]].to_dict(orient="records")
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n=== FEATURE ENGINEERING & SELECTION COMPLETE ===")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
