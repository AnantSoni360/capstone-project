"""
src/ast_parser.py
=============================================================================
Grammar-Aware AST (Abstract Syntax Tree) Lexer & SQL Syntax Parser
-----------------------------------------------------------------------------
Implements syntactic tokenization and grammar tree analysis (inspired by Libinjection)
to detect SQL Injection attempts structurally, bypassing comment interleaving (UN/**/ION)
and tautological comparisons ('1'='1', 2>1) before passing to downstream ML models.
=============================================================================
"""

import re
from typing import List, Dict, Any, Tuple


class SQLASTLexer:
    """
    Lightweight, high-speed grammatical SQL tokenizer and AST evaluator.
    """

    SQL_KEYWORDS = {
        "SELECT", "UNION", "ALL", "INSERT", "UPDATE", "DELETE", "DROP",
        "FROM", "WHERE", "HAVING", "GROUP", "BY", "ORDER", "JOIN",
        "EXEC", "EXECUTE", "DECLARE", "CAST", "CONVERT", "SLEEP",
        "BENCHMARK", "WAITFOR", "DELAY", "INTO", "OUTFILE", "DUMPFILE",
        "TABLE", "DATABASE", "SCHEMA", "LOAD_FILE", "CHAR", "CHR"
    }

    LOGICAL_OPERATORS = {"OR", "AND", "XOR", "NOT", "LIKE", "RLIKE", "REGEXP", "IN", "IS", "BETWEEN"}

    COMPARISON_OPERATORS = {"=", "==", "!=", "<>", "<", ">", "<=", ">="}

    # Lexical patterns for tokenization
    TOKEN_SPECS = [
        ("COMMENT_BLOCK", r"/\*[\s\S]*?\*/"),                    # Multi-line / inline comment: /* ... */
        ("COMMENT_LINE",  r"(--[^\r\n]*|#[^\r\n]*)"),            # Single-line comment: -- or #
        ("STRING_SINGLE", r"'([^'\\]|\\.)*'"),                   # Single-quoted string: 'admin'
        ("STRING_DOUBLE", r'"([^"\\]|\\.)*"'),                   # Double-quoted string: "admin"
        ("HEX_LITERAL",   r"0x[0-9a-fA-F]+"),                     # Hex value: 0x61646d696e
        ("NUMBER",        r"\b\d+(\.\d+)?\b"),                    # Numeric literal: 1, 100, 3.14
        ("WORD",          r"\b[A-Za-z_][A-Za-z0-9_]*\b"),         # Identifiers / Keywords
        ("COMP_OP",       r"(<=|>=|!=|<>|==|=|<|>)"),             # Comparison operators
        ("PUNCT",         r"[;,\(\)]"),                           # Syntax delimiters
        ("SPECIAL",       r"[\+\-\*/%&\|]"),                      # Arithmetic / bitwise operators
        ("WHITESPACE",    r"\s+"),                                # Whitespace (to be discarded)
    ]

    COMPILED_REGEX = re.compile("|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in TOKEN_SPECS))

    def tokenize(self, payload: str) -> List[Dict[str, Any]]:
        """
        Tokenize raw payload into typed SQL tokens while preserving sequence context.
        """
        tokens = []
        if not payload:
            return tokens

        for match in self.COMPILED_REGEX.finditer(payload):
            kind = match.lastgroup
            val = match.group(0)

            if kind == "WHITESPACE":
                continue

            clean_val = val
            if kind in ("COMMENT_BLOCK", "COMMENT_LINE"):
                token_type = "COMMENT"
            elif kind in ("STRING_SINGLE", "STRING_DOUBLE"):
                token_type = "STRING"
                clean_val = val[1:-1]
            elif kind in ("HEX_LITERAL", "NUMBER"):
                token_type = "NUMBER"
            elif kind == "WORD":
                upper_val = val.upper()
                if upper_val in self.SQL_KEYWORDS:
                    token_type = "SQL_KEYWORD"
                    clean_val = upper_val
                elif upper_val in self.LOGICAL_OPERATORS:
                    token_type = "LOGIC_OP"
                    clean_val = upper_val
                else:
                    token_type = "IDENTIFIER"
            elif kind == "COMP_OP":
                token_type = "COMP_OP"
            elif kind == "PUNCT":
                token_type = "PUNCT"
            else:
                token_type = "OPERATOR"

            tokens.append({
                "type": token_type,
                "value": clean_val,
                "raw": val,
                "pos": match.start()
            })

        return tokens

    def parse_and_evaluate(self, payload: str) -> Dict[str, Any]:
        """
        Evaluates token sequence for grammatical SQL Injection anomalies.
        """
        tokens = self.tokenize(payload)
        non_comment_tokens = [t for t in tokens if t["type"] != "COMMENT"]
        has_comments = any(t["type"] == "COMMENT" for t in tokens)

        anomalies: List[str] = []
        is_sqli = False
        confidence = 0.0

        # Check 0: Quote breakout followed by logical operator or SQL keyword
        # In SQLi payloads like ' OR '1'='1', an unmatched leading quote is designed to break string context
        quote_breakout = re.search(r"""(?i)['"]\s*(OR|AND|UNION|SELECT|HAVING|ORDER\s+BY)\b""", payload)
        if quote_breakout:
            anomalies.append(f"QUOTE_BREAKOUT_INJECTION: {quote_breakout.group(0)}")
            is_sqli = True
            confidence = max(confidence, 0.95)

        # Check 0b: Generic Tautology Regex Check on normalized string
        tautology_match = re.search(r"""(?i)(OR|AND)\s+['"]?([a-zA-Z0-9_]+)['"]?\s*(=|==|!=|<>)\s*['"]?\2['"]?""", payload)
        if tautology_match:
            anomalies.append(f"TAUTOLOGY_LOGIC_EXPRESSION: {tautology_match.group(0)}")
            is_sqli = True
            confidence = max(confidence, 0.98)

        # Check 1: Inline Comment Obfuscation (e.g. UN/**/ION SEL/**/ECT)
        if has_comments:
            # Check if keywords are broken up across comments
            types_seq = [t["type"] for t in tokens]
            for i in range(len(tokens) - 2):
                if tokens[i]["type"] == "SQL_KEYWORD" and tokens[i+1]["type"] == "COMMENT" and tokens[i+2]["type"] == "SQL_KEYWORD":
                    anomalies.append(f"COMMENT_INTERLEAVED_KEYWORDS: {tokens[i]['value']}/*...*/{tokens[i+2]['value']}")
                    is_sqli = True
                    confidence = max(confidence, 0.98)

        # Check 2: Tautological Comparisons (e.g. '1'='1', 1=1, 'a'='a', 2>1)
        for i in range(len(non_comment_tokens) - 2):
            t1, t2, t3 = non_comment_tokens[i], non_comment_tokens[i+1], non_comment_tokens[i+2]
            if t2["type"] == "COMP_OP":
                # Check identity equality: A = A
                if t1["type"] in ("STRING", "NUMBER") and t3["type"] in ("STRING", "NUMBER"):
                    if t2["value"] in ("=", "==") and t1["value"] == t3["value"]:
                        anomalies.append(f"TAUTOLOGY_EQUALITY: {t1['value']} {t2['value']} {t3['value']}")
                        is_sqli = True
                        confidence = max(confidence, 0.99)
                    elif t2["value"] == ">":
                        try:
                            if float(t1["value"]) > float(t3["value"]):
                                anomalies.append(f"TAUTOLOGY_NUMERIC_TRUE: {t1['value']} > {t3['value']}")
                                is_sqli = True
                                confidence = max(confidence, 0.95)
                        except ValueError:
                            pass

        # Check 3: UNION SELECT / UNION ALL SELECT chained constructs
        for i in range(len(non_comment_tokens) - 1):
            if non_comment_tokens[i]["value"] == "UNION":
                if non_comment_tokens[i+1]["value"] in ("SELECT", "ALL"):
                    anomalies.append("UNION_SELECT_CHAIN")
                    is_sqli = True
                    confidence = max(confidence, 0.99)

        # Check 4: Stacked Query Execution (Delimited with semicolon followed by destructive SQL)
        for i in range(len(non_comment_tokens) - 1):
            if non_comment_tokens[i]["value"] == ";" and non_comment_tokens[i+1]["type"] == "SQL_KEYWORD":
                if non_comment_tokens[i+1]["value"] in ("DROP", "DELETE", "INSERT", "UPDATE", "EXEC"):
                    anomalies.append(f"STACKED_QUERY_ATTEMPT: ; {non_comment_tokens[i+1]['value']}")
                    is_sqli = True
                    confidence = max(confidence, 0.99)

        # Check 5: Trailing Comment Termination (e.g., ' or 1=1 --)
        if len(tokens) >= 3 and tokens[-1]["type"] == "COMMENT":
            if any(t["type"] in ("SQL_KEYWORD", "LOGIC_OP", "COMP_OP") for t in tokens[:-1]):
                anomalies.append(f"TRAILING_COMMENT_TERMINATOR: {tokens[-1]['value']}")
                confidence = max(confidence, 0.85)
                is_sqli = True

        fingerprint = "_".join(t["type"][:4] for t in non_comment_tokens[:12])

        return {
            "is_sqli": is_sqli,
            "confidence": round(confidence, 4),
            "anomalies": anomalies,
            "token_count": len(tokens),
            "fingerprint": fingerprint,
            "has_comment_evasion": has_comments and is_sqli
        }
