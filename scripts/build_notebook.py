"""
Generator script to build the interactive Jupyter Notebook
for B.Tech capstone academic evaluation.
"""

import json
import pathlib

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Capstone Project: Comparative Analysis of Traditional and AI-Driven Threat Detection\n",
                "## Course: AI in Cybersecurity | B.Tech Final Year Evaluation\n",
                "**System:** AI-Based Web Application Firewall (AI-WAF)\n\n",
                "**Core Models:** PyTorch 1D-CNN (Sequence Deep Learning) + XGBoost (Domain Features) + Traditional Rule Engine\n\n",
                "**Corpus:** Spanish National Research Council (CSIC 2010) HTTP Dataset (25,608 unique records, 0% leakage)\n\n",
                "---"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys, os, pathlib, json, time\n",
                "import numpy as np\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "import torch\n",
                "import joblib\n",
                "from scipy import sparse\n",
                "\n",
                "# Add workspace root to Python path\n",
                "ROOT_DIR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()\n",
                "if str(ROOT_DIR) not in sys.path:\n",
                "    sys.path.insert(0, str(ROOT_DIR))\n",
                "\n",
                "print(f'Workspace Root: {ROOT_DIR}')\n",
                "print(f'PyTorch Version: {torch.__version__} | CUDA Available: {torch.cuda.is_available()}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Activity 2 & 3: Dataset Ingestion, Deduplication Audit & EDA\n",
                "We examine the raw CSIC 2010 dataset and verify the critical session-cookie deduplication."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {},
            "outputs": [],
            "source": [
                "split_meta_path = ROOT_DIR / 'data' / 'processed' / 'split_metadata.json'\n",
                "with open(split_meta_path, 'r') as f:\n",
                "    split_meta = json.load(f)\n",
                "\n",
                "print('--- Corpus Partition & Leakage Audit ---')\n",
                "print(json.dumps(split_meta, indent=2))\n",
                "\n",
                "test_df = pd.read_csv(ROOT_DIR / 'data' / 'processed' / 'test_frozen.csv')\n",
                "print(f'\\nFrozen Test Set Shape: {test_df.shape}')\n",
                "print(test_df['diagnostic_category'].value_counts())"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Activity 4: Feature Engineering & Selection Analysis\n",
                "We inspect the 79 handcrafted numerical features and the feature selection results from Random Forest, ANOVA F-statistic, and RFE."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 3,
            "metadata": {},
            "outputs": [],
            "source": [
                "feat_meta_path = ROOT_DIR / 'data' / 'processed' / 'feature_metadata.json'\n",
                "with open(feat_meta_path, 'r') as f:\n",
                "    feat_meta = json.load(f)\n",
                "\n",
                "dims = feat_meta['feature_dimensions']\n",
                "print(f\"Total Handcrafted Features: {dims['handcrafted_numerical_features']}\")\n",
                "print(f\"TF-IDF Character n-grams: {dims['tfidf_char_ngram_features']}\")\n",
                "print(f\"Total Combined Representation: {dims['total_combined_features']}\")\n",
                "print('\\nTop 10 Most Influential Features (Random Forest Gini Importance):')\n",
                "for item in feat_meta['top_10_features_by_rf_importance']:\n",
                "    print(f\"  - {item['feature']:<30}: {item['rf_importance']:.4f}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Activity 5: Machine Learning Models & Master Benchmark\n",
                "We evaluate all trained models on the untouched frozen test set (3,842 requests)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 4,
            "metadata": {},
            "outputs": [],
            "source": [
                "benchmark_csv = ROOT_DIR / 'reports' / 'final_model_benchmark_test_set.csv'\n",
                "df_bench = pd.read_csv(benchmark_csv)\n",
                "display = df_bench[['System', 'Accuracy', 'Precision', 'Recall', 'F1_Score', 'ROC_AUC', 'False_Positive_Rate', 'Latency_ms']].copy()\n",
                "print(display.to_string(index=False))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Activity 6 & 8: Ablation Study & Attack Subgroup Analysis\n",
                "Evidence-based comparison demonstrating the superiority of the complete Hybrid Ensemble over isolated models."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 5,
            "metadata": {},
            "outputs": [],
            "source": [
                "with open(ROOT_DIR / 'reports' / 'ablation_study_metrics.json', 'r') as f:\n",
                "    abl_data = json.load(f)\n",
                "\n",
                "df_abl = pd.DataFrame(abl_data).T\n",
                "print('=== ABLATION STUDY COMPARISON ===')\n",
                "print(df_abl[['accuracy', 'precision', 'recall', 'f1_score', 'false_positive_rate', 'latency_ms']])\n",
                "\n",
                "with open(ROOT_DIR / 'reports' / 'class_specific_metrics.json', 'r') as f:\n",
                "    class_data = json.load(f)\n",
                "\n",
                "print('\\n=== ATTACK SUBGROUP DETECTION RECALL ===')\n",
                "for threat, stats in class_data.items():\n",
                "    if threat == 'BENIGN':\n",
                "        print(f\"{threat:<18} (N={stats['sample_count']}): Clean Pass Rate = {stats['ensemble_clean_allow_rate']*100:.2f}%\")\n",
                "    else:\n",
                "        print(f\"{threat:<18} (N={stats['sample_count']}): Recall = {stats['ensemble_recall']*100:.2f}% (Rules: {stats['rule_recall']*100:.2f}%, XGB: {stats['xgb_recall']*100:.2f}%, CNN: {stats['cnn_recall']*100:.2f}%)\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Activity 7: Explainable AI (TreeSHAP & Token Attribution)\n",
                "We test the WAF decision engine on a live attack payload and inspect the AI evidence."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 6,
            "metadata": {},
            "outputs": [],
            "source": [
                "from backend.decision_engine import WAFDecisionEngine\n",
                "\n",
                "engine = WAFDecisionEngine()\n",
                "sample_attack = \"/tienda1/publico/anadir.jsp?id=1%27%20UNION%20SELECT%20username,%20password%20FROM%20usuarios--\"\n",
                "inspection_result = engine.inspect_request(method='GET', url=sample_attack)\n",
                "\n",
                "print(f'Target Request: {sample_attack}')\n",
                "print(f\"Verdict:       {inspection_result['verdict']} (HTTP Status: {inspection_result['http_status']})\")\n",
                "print(f\"Risk Score:    {inspection_result['risk_score']} (Confidence: {inspection_result['confidence']})\")\n",
                "print(f\"Reason:        {inspection_result['reason']}\")\n",
                "print(f\"Rule Evidence: {inspection_result['rule_evidence']['matched_rules']}\")\n",
                "print(f\"AI Evidence:   {inspection_result['ai_evidence']}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Summary & Viva Defense Takeaways\n",
                "1. **Traditional Rules Alone Fail:** 78.08% False Negative Rate on the CSIC 2010 test set.\n",
                "2. **PyTorch 1D-CNN Champion:** 94.35% accuracy, 99.86% precision, and sub-millisecond inference (0.866 ms).\n",
                "3. **Hybrid Ensemble:** Achieves 95.13% accuracy, 100% recall on SQLi/XSS, and 0.41% false alarm rate with calibrated 3-way decision logic (ALLOW, REVIEW, BLOCK).\n",
                "4. **Zero-Trust Network Isolation:** Protected target application operates with zero host ports exposed on strict Docker internal network."
            ]
        }
    ],
    "metadata": {
        "language_info": {
            "name": "python",
            "version": "3.12.10"
        },
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

out_path = WORKSPACE_ROOT / "notebooks" / "capstone_complete_pipeline.ipynb"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Jupyter notebook generated successfully at: {out_path}")
