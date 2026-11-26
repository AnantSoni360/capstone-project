"""
Batch Dataset Parsing Script (Phase 02)
Parses raw CSIC 2010 dataset into structured canonical representation.
"""

import json
import pathlib
import sys
import time

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import pandas as pd
from src.parser import HTTPRequestParser
RAW_CSV_PATH = WORKSPACE_ROOT / "data" / "raw" / "csic_database.csv"
OUTPUT_CSV_PATH = WORKSPACE_ROOT / "data" / "interim" / "parsed_requests.csv"
SUMMARY_PATH = WORKSPACE_ROOT / "data" / "interim" / "parsing_summary.json"


def main():
    print(f"[Phase 02] Loading raw dataset from: {RAW_CSV_PATH}")
    start_time = time.time()
    raw_df = pd.read_csv(RAW_CSV_PATH)
    total_raw = len(raw_df)
    print(f"Loaded {total_raw} raw records in {time.time() - start_time:.2f}s")

    parser = HTTPRequestParser(max_decode_depth=3)
    print("Processing and normalizing HTTP requests...")
    parsed_df = parser.process_dataframe(raw_df, deduplicate=True)
    total_parsed = len(parsed_df)

    # Compute summary metrics
    gt_counts = parsed_df["ground_truth"].value_counts().to_dict()
    diag_counts = parsed_df["diagnostic_category"].value_counts().to_dict()

    summary = {
        "raw_record_count": total_raw,
        "deduplicated_record_count": total_parsed,
        "duplicate_count_removed": total_raw - total_parsed,
        "deduplication_ratio": round((total_raw - total_parsed) / total_raw * 100, 2),
        "ground_truth_distribution": {
            "0_normal": gt_counts.get(0, 0),
            "1_anomalous": gt_counts.get(1, 0),
        },
        "diagnostic_category_distribution": diag_counts,
        "processing_time_seconds": round(time.time() - start_time, 2)
    }

    # Drop internal python object column before saving CSV (keep params_json)
    if "params" in parsed_df.columns:
        parsed_df = parsed_df.drop(columns=["params"])

    print(f"Saving parsed interim dataset to: {OUTPUT_CSV_PATH}")
    parsed_df.to_csv(OUTPUT_CSV_PATH, index=False)

    print(f"Saving parsing summary to: {SUMMARY_PATH}")
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== PARSING COMPLETE ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
