"""
src/adversarial_fuzzer.py
=============================================================================
Automated Adversarial Mutation Fuzzer & WAF Resilience Engine
-----------------------------------------------------------------------------
Generates synthetic adversarial evasion variants (inspired by WAF-A-MoLE)
using 8 mutation operators:
  1. Multi-layer URL Double Encoding
  2. SQL Comment Interleaving / Splicing
  3. Whitespace / Tab / Delimiter Jitter
  4. Non-Deterministic Mixed Casing
  5. Hex / ASCII Literal Obfuscation
  6. Null-Byte Infiltration
  7. HTML Entity & Script Encoding
  8. Mathematical Tautology Substitution
=============================================================================
"""

import random
import urllib.parse
from typing import List, Dict, Any, Callable


class AdversarialMutationFuzzer:
    """
    Automated fuzzing and adversarial mutation engine for testing WAF evasion robustness.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def mutate_case_randomization(self, payload: str) -> str:
        """Randomly alters uppercase and lowercase casing across alphabetic characters."""
        return "".join(c.upper() if self.rng.random() > 0.5 else c.lower() for c in payload)

    def mutate_sql_comment_splicing(self, payload: str) -> str:
        """Injects inline SQL comments (/**/) inside SQL control words (e.g. UN/**/ION)."""
        keywords = ["UNION", "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "WHERE", "FROM", "AND", "OR"]
        mutated = payload
        for kw in keywords:
            if kw in mutated.upper():
                # Split keyword in half and insert /**/
                mid = len(kw) // 2
                split_kw = kw[:mid] + "/**/" + kw[mid:]
                # Case-insensitive replacement
                idx = mutated.upper().find(kw)
                if idx != -1:
                    mutated = mutated[:idx] + split_kw + mutated[idx+len(kw):]
        return mutated

    def mutate_url_double_encoding(self, payload: str) -> str:
        """Applies double URL percent encoding to high-risk punctuation characters."""
        charmap = {
            "'": "%2527",
            '"': "%2522",
            "<": "%253C",
            ">": "%253E",
            " ": "%2520",
            ";": "%253B",
            "=": "%253D"
        }
        res = []
        for c in payload:
            res.append(charmap.get(c, c))
        return "".join(res)

    def mutate_whitespace_jitter(self, payload: str) -> str:
        """Replaces standard space characters with alternative delimiters (%09, %0a, +, /**/)."""
        replacements = ["%09", "%0a", "+", "/**/", "/*\t*/"]
        res = []
        for c in payload:
            if c == " ":
                res.append(self.rng.choice(replacements))
            else:
                res.append(c)
        return "".join(res)

    def mutate_hex_encoding(self, payload: str) -> str:
        """Converts quoted string literals like 'admin' to hex 0x61646d696e."""
        import re
        def to_hex(match):
            val = match.group(1)
            hex_str = "0x" + "".join(f"{ord(c):02x}" for c in val)
            return hex_str
        return re.sub(r"'([a-zA-Z0-9_]{3,12})'", to_hex, payload)

    def mutate_null_byte_injection(self, payload: str) -> str:
        """Inserts null byte terminators (%00) before string boundaries."""
        if "'" in payload:
            return payload.replace("'", "%00'", 1)
        return "%00" + payload

    def mutate_html_entity_encoding(self, payload: str) -> str:
        """Encodes XSS characters using HTML hexadecimal / decimal entities."""
        charmap = {
            "<": "&#x3c;",
            ">": "&#x3e;",
            '"': "&quot;",
            "'": "&#39;"
        }
        res = []
        for c in payload:
            res.append(charmap.get(c, c))
        return "".join(res)

    def mutate_tautology_substitution(self, payload: str) -> str:
        """Substitutes 1=1 with equivalent mathematical identities (2>1, 'a'='a', 5=5)."""
        substitutions = ["2>1", "'a'='a'", "5=5", "100>50", "'x'='x'"]
        chosen = self.rng.choice(substitutions)
        if "1=1" in payload:
            return payload.replace("1=1", chosen)
        elif "'1'='1'" in payload:
            return payload.replace("'1'='1'", chosen)
        return payload

    def generate_all_mutations(self, payload: str) -> List[Dict[str, str]]:
        """
        Applies each individual mutation operator and combined chained mutations.
        """
        operators = [
            ("Case Randomization", self.mutate_case_randomization),
            ("SQL Comment Splicing", self.mutate_sql_comment_splicing),
            ("URL Double Encoding", self.mutate_url_double_encoding),
            ("Whitespace Jitter", self.mutate_whitespace_jitter),
            ("Hex Literal Encoding", self.mutate_hex_encoding),
            ("Null-Byte Infiltration", self.mutate_null_byte_injection),
            ("HTML Entity Encoding", self.mutate_html_entity_encoding),
            ("Tautology Substitution", self.mutate_tautology_substitution)
        ]

        results = []
        for name, op in operators:
            mutated_text = op(payload)
            results.append({
                "operator": name,
                "mutated_payload": mutated_text
            })

        # Multi-operator chained mutation (Case + Comments + Whitespace)
        chained = self.mutate_case_randomization(
            self.mutate_sql_comment_splicing(
                self.mutate_whitespace_jitter(payload)
            )
        )
        results.append({
            "operator": "Chained Multi-Vector Mutation",
            "mutated_payload": chained
        })

        return results

    def audit_waf_resilience(self, base_payload: str, inspect_func: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates WAF detection rates across all synthetic mutations of an exploit string.
        """
        mutations = self.generate_all_mutations(base_payload)
        tested_results = []
        blocked_count = 0

        for m in mutations:
            out = inspect_func(m["mutated_payload"])
            verdict = out.get("verdict", "ALLOW")
            is_blocked = verdict in ("BLOCK", "REVIEW")
            if is_blocked:
                blocked_count += 1
            tested_results.append({
                "operator": m["operator"],
                "mutated_payload": m["mutated_payload"],
                "verdict": verdict,
                "threat_score": out.get("threat_score", out.get("risk_score", 0.0)),
                "is_blocked": is_blocked
            })

        total = len(tested_results)
        resilience_rate = round((blocked_count / total) * 100, 2) if total > 0 else 0.0

        return {
            "base_payload": base_payload,
            "total_mutations_tested": total,
            "blocked_or_flagged_count": blocked_count,
            "evaded_count": total - blocked_count,
            "resilience_percentage": resilience_rate,
            "mutation_details": tested_results
        }
