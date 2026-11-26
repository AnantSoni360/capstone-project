"""
HTTP Request Parser and Normalizer Module (Phase 02)
Handles raw HTTP request extraction, recursive decoding, parameter parsing,
and diagnostic threat tagging for the AI-Based WAF.
"""

import json
import re
import urllib.parse
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd


class HTTPRequestParser:
    """
    Robust parser and normalizer for incoming HTTP requests.
    Supports single request dictionary parsing and batch DataFrame parsing.
    """

    # Diagnostic regex patterns for attack classification (analytical only)
    SQLI_PATTERNS = re.compile(
        r"(\b(union|select|insert|update|delete|drop|alter|exec|declare|cast|convert)\b|"
        r"(--|#|/\*|\*/)|"
        r"(\b(or|and)\b\s+['\"\d\w]+(\s*=\s*['\"\d\w]+|\s+like\s+))|"
        r"(\bwaitfor\s+delay\b|\bsleep\s*\(|\bbenchmark\s*\())",
        re.IGNORECASE
    )

    XSS_PATTERNS = re.compile(
        r"(<\s*script\b|javascript\s*:|<\s*img\b[^>]*\bonerror\s*=|"
        r"<\s*svg\b[^>]*\bonload\s*=|\balert\s*\(|\bdocument\.cookie\b|"
        r"<\s*iframe\b|<\s*body\b[^>]*\bonload\s*=|\bonmouseover\s*=)",
        re.IGNORECASE
    )

    TRAVERSAL_PATTERNS = re.compile(
        r"(\.\./|\.\.\\|/etc/passwd|\bboot\.ini\b|\bwin\.ini\b|/WEB-INF/)",
        re.IGNORECASE
    )

    CRLF_PATTERNS = re.compile(
        r"(%0d%0a|\r\n|set-cookie\s*:)",
        re.IGNORECASE
    )

    def __init__(self, max_decode_depth: int = 3):
        self.max_decode_depth = max_decode_depth

    def recursive_url_decode(self, text: Optional[str]) -> str:
        """
        Recursively decode percent-encoded strings to counteract evasion techniques.
        Stops when string stabilizes or max depth is reached.
        """
        if not text or not isinstance(text, str):
            return ""

        current = text
        for _ in range(self.max_decode_depth):
            try:
                decoded = urllib.parse.unquote_plus(current)
                if decoded == current:
                    break
                current = decoded
            except Exception:
                break
        return current

    def clean_url_path(self, raw_url: str) -> Tuple[str, str]:
        """
        Extract clean path and query string from URL, stripping protocol versions (e.g., ' HTTP/1.1').
        """
        if not raw_url or not isinstance(raw_url, str):
            return "", ""

        # Remove trailing HTTP protocol version if present
        cleaned = re.sub(r"\s+HTTP/\d\.\d$", "", raw_url.strip(), flags=re.IGNORECASE)

        # Parse URL components
        parsed = urllib.parse.urlparse(cleaned)
        path = parsed.path
        query = parsed.query

        return path, query

    def parse_parameters(self, query_string: str, body: str) -> Dict[str, List[str]]:
        """
        Parse query parameters and form-urlencoded body into a unified dictionary.
        """
        params: Dict[str, List[str]] = {}

        if query_string:
            try:
                query_params = urllib.parse.parse_qs(query_string, keep_blank_values=True)
                for k, v in query_params.items():
                    params.setdefault(k, []).extend(v)
            except Exception:
                pass

        if body and isinstance(body, str):
            try:
                body_params = urllib.parse.parse_qs(body, keep_blank_values=True)
                for k, v in body_params.items():
                    params.setdefault(k, []).extend(v)
            except Exception:
                pass

        return params

    def diagnose_attack_category(self, payload: str, ground_truth_label: int = 0) -> str:
        """
        Assign an analytical diagnostic category based on payload contents.
        NOTE: Ground-truth remains ground_truth_label (0=Normal, 1=Anomalous).
        """
        # Check patterns in order of specificity
        if self.SQLI_PATTERNS.search(payload):
            return "SQL_INJECTION"
        elif self.XSS_PATTERNS.search(payload):
            return "XSS"
        elif self.TRAVERSAL_PATTERNS.search(payload):
            return "PATH_TRAVERSAL"
        elif self.CRLF_PATTERNS.search(payload):
            return "CRLF_INJECTION"
        elif ground_truth_label == 1:
            return "GENERIC_ANOMALY"
        else:
            return "BENIGN"

    def parse_single_request(
        self,
        method: str,
        raw_url: str,
        body: Optional[str] = "",
        headers: Optional[Dict[str, str]] = None,
        ground_truth: int = 0
    ) -> Dict[str, Any]:
        """
        Parses a single HTTP request into canonical representation.
        """
        method_clean = (method or "GET").strip().upper()
        raw_url_clean = (raw_url or "").strip()
        body_clean = (body or "") if isinstance(body, str) else ""

        path, query = self.clean_url_path(raw_url_clean)

        decoded_path = self.recursive_url_decode(path)
        decoded_query = self.recursive_url_decode(query)
        decoded_body = self.recursive_url_decode(body_clean)

        # Full concatenated payload for lexical inspection
        query_part = f"?{decoded_query}" if decoded_query else ""
        body_part = f"{decoded_body}" if decoded_body else ""
        path_part = f"{decoded_path}" if decoded_path else ""
        parts = [p for p in [path_part, query_part, body_part] if p]
        full_payload = " ".join(parts).strip()

        params = self.parse_parameters(query, body_clean)
        diagnostic_cat = self.diagnose_attack_category(full_payload, ground_truth)

        return {
            "method": method_clean,
            "raw_url": raw_url_clean,
            "path": path,
            "query": query,
            "body": body_clean,
            "decoded_path": decoded_path,
            "decoded_query": decoded_query,
            "decoded_body": decoded_body,
            "full_payload": full_payload,
            "params": params,
            "params_json": json.dumps(params),
            "param_count": len(params),
            "payload_length": len(full_payload),
            "ground_truth": ground_truth,
            "diagnostic_category": diagnostic_cat,
        }

    def process_dataframe(
        self,
        df: pd.DataFrame,
        deduplicate: bool = True
    ) -> pd.DataFrame:
        """
        Processes an entire CSIC dataset DataFrame, normalizes records,
        applies optional deduplication on (Method, URL, content), and produces
        structured interim data.
        """
        records: List[Dict[str, Any]] = []

        for _, row in df.iterrows():
            method = str(row.get("Method", "GET"))
            raw_url = str(row.get("URL", ""))
            body = str(row.get("content", "")) if pd.notna(row.get("content")) else ""
            gt = int(row.get("classification", 0))

            parsed = self.parse_single_request(
                method=method,
                raw_url=raw_url,
                body=body,
                ground_truth=gt
            )
            records.append(parsed)

        parsed_df = pd.DataFrame(records)

        if deduplicate:
            # Deduplicate strictly on the functional request tuple
            initial_count = len(parsed_df)
            parsed_df = parsed_df.drop_duplicates(
                subset=["method", "raw_url", "body"]
            ).reset_index(drop=True)
            print(f"[Deduplication] Reduced from {initial_count} to {len(parsed_df)} unique requests.")

        return parsed_df


if __name__ == "__main__":
    parser = HTTPRequestParser()
    sample = parser.parse_single_request(
        method="GET",
        raw_url="http://localhost:8080/search?q=%27%20OR%201%3D1--%20 HTTP/1.1",
        body="",
        ground_truth=1
    )
    print("Sample parsed result:")
    for k, v in sample.items():
        print(f"  {k}: {v}")
