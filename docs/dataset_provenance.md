# Dataset Provenance & Integrity Specification (Phase 01)
**Dataset Identifier:** CSIC 2010 HTTP Dataset  
**Primary Source:** Information Security Institute of CSIC (Spanish National Research Council)  
**Curated Format:** `csic_database.csv` (Tabular extraction of CSIC 2010 HTTP corpus)

---

## 1. Provenance & Research Context

The CSIC 2010 HTTP Dataset was developed by the Information Security Institute of the Spanish National Research Council (CSIC) to evaluate Web Application Firewalls and Web Intrusion Detection Systems. The dataset models incoming web traffic directed at an e-commerce web application.

- **Source Application:** Simulated Java e-commerce store (`tienda1`) running on Tomcat/Apache.
- **Traffic Nature:**
  - Automated benign user browsing (product search, cart additions, user registration, checkout).
  - Malicious attack injection covering SQL Injection, Cross-Site Scripting, Parameter Tampering, Path Traversal, and Header/CRLF injections.

---

## 2. Integrity Manifest & File Specifications

- **Location:** `data/raw/csic_database.csv`
- **File Format:** Comma-Separated Values (CSV, UTF-8 encoded)
- **Total Records:** 61,065 rows
- **Columns (17):** `Unnamed: 0`, `Method`, `User-Agent`, `Pragma`, `Cache-Control`, `Accept`, `Accept-encoding`, `Accept-charset`, `language`, `host`, `cookie`, `content-type`, `connection`, `lenght`, `content`, `classification`, `URL`
- **Ground-Truth Target:** `classification` (0 = Normal, 1 = Anomalous)

---

## 3. Data Governance & Licensing Notes

- **Intended Use:** Academic research, experimental WAF evaluation, and educational benchmarking.
- **Privacy & PII Assessment:** All user IDs, email addresses, and credit card numbers present in the synthetic dataset are procedurally generated mocks (no real-world personal identifying information).
- **Integrity Rule:** The raw file in `data/raw/csic_database.csv` is strictly **read-only**. All transformations, parsing outputs, and cleaned partitions must be written to `data/interim/` or `data/processed/`.
