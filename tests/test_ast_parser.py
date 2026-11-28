"""
tests/test_ast_parser.py
Unit tests for Grammar-Aware AST Lexer & SQL Syntax Parser.
"""

import pytest
from src.ast_parser import SQLASTLexer

@pytest.fixture
def lexer():
    return SQLASTLexer()

def test_benign_traffic_clean(lexer):
    clean_samples = [
        "product_name=laptop&category=electronics",
        "id=105&action=view",
        "search=machine+learning+algorithms",
        "email=user@company.com"
    ]
    for s in clean_samples:
        res = lexer.parse_and_evaluate(s)
        assert not res["is_sqli"], f"False positive on clean input: {s}"
        assert len(res["anomalies"]) == 0

def test_tautology_detection(lexer):
    tautologies = [
        "' OR '1'='1",
        "admin' OR 1=1 --",
        "' OR 'a'='a'",
        "id=105 OR 2>1"
    ]
    for t in tautologies:
        res = lexer.parse_and_evaluate(t)
        assert res["is_sqli"], f"Failed to detect tautology: {t}"
        assert res["confidence"] >= 0.90
        assert any("TAUTOLOGY" in a for a in res["anomalies"])

def test_comment_interleaved_evasion(lexer):
    obfuscated = [
        "1 UNION/**/SELECT password FROM users",
        "id=1 UNION/*inline*/ALL/*clean*/SELECT 1,2,3",
    ]
    for o in obfuscated:
        res = lexer.parse_and_evaluate(o)
        assert res["is_sqli"], f"Failed to detect comment evasion: {o}"
        assert res["has_comment_evasion"]

def test_stacked_query_detection(lexer):
    stacked = "id=10; DROP TABLE customers; --"
    res = lexer.parse_and_evaluate(stacked)
    assert res["is_sqli"]
    assert any("STACKED_QUERY" in a for a in res["anomalies"])
