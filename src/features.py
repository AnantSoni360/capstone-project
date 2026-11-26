"""
Feature Engineering and Extraction Pipeline (Phase 04)
Extracts handcrafted cybersecurity domain features, Shannon entropy, lexical ratios,
and character n-gram TF-IDF representations with strict fit/transform isolation.
"""

import math
import re
from typing import Dict, Any, List, Optional, Tuple, Union
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler


class FeatureExtractor:
    """
    Stateful Feature Extractor for HTTP Requests.
    Ensures zero data leakage by fitting scalers and vectorizers strictly on training data.
    """

    # Keyword and token regular expressions
    SQL_KEYWORDS = [
        "select", "union", "insert", "update", "delete", "drop",
        "from", "where", "table", "database", "exec", "declare",
        "cast", "convert", "or", "and", "like", "order by", "group by"
    ]

    SQL_PATTERNS = [
        (r"--|#|/\*", "sql_comment"),
        (r"(\b(or|and)\b\s+['\"\d\w]+(\s*=\s*['\"\d\w]+))", "sql_tautology"),
        (r"\bwaitfor\s+delay\b|\bsleep\s*\(|\bbenchmark\s*\(", "sql_blind_delay"),
    ]

    XSS_PATTERNS = [
        (r"<\s*script\b", "xss_script_tag"),
        (r"javascript\s*:", "xss_javascript_uri"),
        (r"\bonerror\s*=", "xss_onerror"),
        (r"\bonload\s*=", "xss_onload"),
        (r"\balert\s*\(", "xss_alert"),
        (r"\bdocument\.cookie\b", "xss_cookie"),
        (r"<\s*iframe\b", "xss_iframe"),
        (r"<\s*svg\b", "xss_svg"),
        (r"<\s*img\b", "xss_img"),
        (r"\beval\s*\(", "xss_eval"),
    ]

    TRAVERSAL_PATTERNS = [
        (r"\.\./|\.\.\\", "traversal_dot_dot"),
        (r"/etc/passwd|\bwin\.ini\b|\bboot\.ini\b", "traversal_sensitive_file"),
    ]

    def __init__(self, max_tfidf_features: int = 500, char_ngram_range: Tuple[int, int] = (3, 5)):
        self.max_tfidf_features = max_tfidf_features
        self.char_ngram_range = char_ngram_range

        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=self.char_ngram_range,
            max_features=self.max_tfidf_features,
            lowercase=True
        )
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        self.is_fitted = False

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """
        Calculates the Shannon Entropy of a string to measure obfuscation/randomness.
        """
        if not text:
            return 0.0
        entropy = 0.0
        length = len(text)
        counts = {}
        for char in text:
            counts[char] = counts.get(char, 0) + 1
        for count in counts.values():
            prob = count / length
            entropy -= prob * math.log2(prob)
        return float(entropy)

    def extract_handcrafted_features_single(self, record: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract domain-specific numerical features from a single parsed HTTP request record.
        """
        full_payload = str(record.get("full_payload", ""))
        decoded_path = str(record.get("decoded_path", ""))
        decoded_query = str(record.get("decoded_query", ""))
        decoded_body = str(record.get("decoded_body", ""))
        raw_url = str(record.get("raw_url", ""))
        method = str(record.get("method", "GET")).upper()
        param_count = float(record.get("param_count", 0))

        payload_len = len(full_payload)
        safe_len = max(payload_len, 1)

        features: Dict[str, float] = {}

        # 1. Length features
        features["length_raw_url"] = float(len(raw_url))
        features["length_path"] = float(len(decoded_path))
        features["length_query"] = float(len(decoded_query))
        features["length_body"] = float(len(decoded_body))
        features["length_total_payload"] = float(payload_len)
        features["param_count"] = param_count
        features["avg_param_length"] = float(payload_len / max(param_count, 1))

        # 2. HTTP Method one-hot
        features["is_method_get"] = 1.0 if method == "GET" else 0.0
        features["is_method_post"] = 1.0 if method == "POST" else 0.0
        features["is_method_put"] = 1.0 if method == "PUT" else 0.0

        # 3. Special character frequencies & counts
        special_chars = {
            "single_quote": "'",
            "double_quote": '"',
            "semicolon": ";",
            "angle_bracket_open": "<",
            "angle_bracket_close": ">",
            "percent": "%",
            "hyphen": "-",
            "equal": "=",
            "ampersand": "&",
            "slash": "/",
            "backslash": "\\",
            "paren_open": "(",
            "paren_close": ")",
            "space": " ",
            "plus": "+",
        }
        for name, ch in special_chars.items():
            cnt = full_payload.count(ch)
            features[f"count_{name}"] = float(cnt)
            features[f"ratio_{name}"] = float(cnt / safe_len)

        # 4. Lexical ratios & Entropy
        num_digits = sum(c.isdigit() for c in full_payload)
        num_alphas = sum(c.isalpha() for c in full_payload)
        num_uppers = sum(c.isupper() for c in full_payload)
        num_specials = payload_len - num_digits - num_alphas

        features["ratio_digits"] = float(num_digits / safe_len)
        features["ratio_alphas"] = float(num_alphas / safe_len)
        features["ratio_uppers"] = float(num_uppers / safe_len)
        features["ratio_specials"] = float(num_specials / safe_len)
        features["shannon_entropy"] = self.calculate_entropy(full_payload)

        # 5. SQL Keyword indicators
        lower_payload = full_payload.lower()
        for kw in self.SQL_KEYWORDS:
            kw_clean = kw.replace(" ", "_")
            cnt = len(re.findall(r"\b" + re.escape(kw) + r"\b", lower_payload))
            features[f"sql_kw_{kw_clean}"] = float(cnt)

        for pat, pat_name in self.SQL_PATTERNS:
            features[f"sql_pat_{pat_name}"] = 1.0 if re.search(pat, lower_payload) else 0.0

        # 6. XSS Pattern indicators
        for pat, pat_name in self.XSS_PATTERNS:
            features[f"xss_pat_{pat_name}"] = 1.0 if re.search(pat, lower_payload) else 0.0

        # 7. Path Traversal indicators
        for pat, pat_name in self.TRAVERSAL_PATTERNS:
            features[f"trav_pat_{pat_name}"] = 1.0 if re.search(pat, lower_payload) else 0.0

        return features

    def extract_handcrafted_features_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Vectorized/iterative handcrafted feature extraction across an entire DataFrame.
        """
        rows: List[Dict[str, float]] = []
        for _, row in df.iterrows():
            f_dict = self.extract_handcrafted_features_single(row.to_dict())
            rows.append(f_dict)
        feat_df = pd.DataFrame(rows)
        return feat_df

    def fit(self, train_df: pd.DataFrame) -> "FeatureExtractor":
        """
        Fits the TF-IDF vectorizer and numerical standard scaler strictly on training data.
        """
        print(f"[FeatureExtractor] Fitting on {len(train_df)} training samples...")

        # 1. Fit handcrafted feature scaler
        X_num_raw = self.extract_handcrafted_features_dataframe(train_df)
        self.feature_names = list(X_num_raw.columns)
        self.scaler.fit(X_num_raw.values)

        # 2. Fit TF-IDF character n-gram vectorizer
        payloads = train_df["full_payload"].fillna("").astype(str).tolist()
        self.tfidf_vectorizer.fit(payloads)

        self.is_fitted = True
        print(f"[FeatureExtractor] Fitted with {len(self.feature_names)} numerical features and {len(self.tfidf_vectorizer.get_feature_names_out())} TF-IDF n-grams.")
        return self

    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, sparse.csr_matrix, sparse.csr_matrix]:
        """
        Transforms a DataFrame using the fitted scalers and vectorizers.
        Returns:
            - X_num_scaled: Scaled numerical features (dense 2D numpy array)
            - X_tfidf: Sparse TF-IDF matrix (CSR format)
            - X_combined: Horizontally stacked sparse matrix of [numerical, tfidf]
        """
        if not self.is_fitted:
            raise ValueError("FeatureExtractor must be fitted before calling transform().")

        # 1. Extract and scale numerical features
        X_num_raw = self.extract_handcrafted_features_dataframe(df)
        X_num_scaled = self.scaler.transform(X_num_raw[self.feature_names].values)

        # 2. Transform text with fitted TF-IDF vectorizer
        payloads = df["full_payload"].fillna("").astype(str).tolist()
        X_tfidf = self.tfidf_vectorizer.transform(payloads)

        # 3. Combine into sparse representation
        X_num_sparse = sparse.csr_matrix(X_num_scaled)
        X_combined = sparse.hstack([X_num_sparse, X_tfidf], format="csr")

        return X_num_scaled, X_tfidf, X_combined

    def transform_single(self, record: Dict[str, Any]) -> Tuple[np.ndarray, sparse.csr_matrix, sparse.csr_matrix]:
        """
        Transforms a single request record for real-time inference in FastAPI.
        """
        single_df = pd.DataFrame([record])
        return self.transform(single_df)

    def save(self, filepath: str):
        """Serialize fitted extractor pipeline."""
        joblib.dump(self, filepath)
        print(f"[FeatureExtractor] Saved fitted pipeline to: {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "FeatureExtractor":
        """Deserialize fitted extractor pipeline."""
        obj = joblib.load(filepath)
        if not isinstance(obj, cls):
            raise TypeError(f"Loaded object is not an instance of {cls.__name__}")
        return obj
