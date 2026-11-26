import hashlib
import os
import pathlib
import pytest
import pandas as pd

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW_DATA_PATH = WORKSPACE_ROOT / "data" / "raw" / "csic_database.csv"
CHECKSUM_FILE = WORKSPACE_ROOT / "data" / "raw" / "checksums.sha256"

REQUIRED_DIRS = [
    "data/raw",
    "data/interim",
    "data/processed",
    "docs",
    "notebooks",
    "src",
    "models",
    "backend",
    "dashboard",
    "proxy",
    "tests",
    "reports/figures",
]

def compute_sha256(filepath: pathlib.Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def test_directories_exist():
    """Verify that all project directories exist and are accessible."""
    for rel_path in REQUIRED_DIRS:
        full_path = WORKSPACE_ROOT / rel_path
        assert full_path.exists(), f"Missing directory: {rel_path}"
        assert full_path.is_dir(), f"Not a directory: {rel_path}"

def test_raw_dataset_exists_and_checksum():
    """Verify raw dataset presence, compute/verify SHA-256 hash, and assert file size."""
    assert RAW_DATA_PATH.exists(), f"Raw dataset not found at {RAW_DATA_PATH}"
    file_size = RAW_DATA_PATH.stat().st_size
    assert file_size == 29539583, f"Unexpected file size: {file_size} bytes (expected 29539583)"

    sha256_hash = compute_sha256(RAW_DATA_PATH)
    assert len(sha256_hash) == 64

    # Write or verify checksum file
    manifest_line = f"{sha256_hash}  csic_database.csv\n"
    if not CHECKSUM_FILE.exists():
        with open(CHECKSUM_FILE, "w", encoding="utf-8") as f:
            f.write(manifest_line)
    
    with open(CHECKSUM_FILE, "r", encoding="utf-8") as f:
        recorded_hash = f.read().split()[0]
    
    assert sha256_hash == recorded_hash, f"Checksum mismatch: {sha256_hash} != {recorded_hash}"

def test_raw_dataset_loadable():
    """Verify raw dataset structure and initial counts without modifying it."""
    df = pd.read_csv(RAW_DATA_PATH)
    assert len(df) == 61065, f"Expected 61065 rows, got {len(df)}"
    assert len(df.columns) == 17, f"Expected 17 columns, got {len(df.columns)}"
    assert "classification" in df.columns, "Missing 'classification' column"
    assert set(df["classification"].unique()) == {0, 1}, "Classification column should only contain 0 and 1"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
