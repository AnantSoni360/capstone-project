"""
tests/test_adversarial_fuzzer.py
Unit tests for Automated Adversarial Mutation Fuzzer & WAF Resilience Engine.
"""

import pytest
from src.adversarial_fuzzer import AdversarialMutationFuzzer

@pytest.fixture
def fuzzer():
    return AdversarialMutationFuzzer(seed=42)

def test_case_randomization(fuzzer):
    base = "SELECT * FROM users"
    mutated = fuzzer.mutate_case_randomization(base)
    assert mutated.lower() == base.lower()
    assert mutated != base  # Non-deterministic mixed casing

def test_sql_comment_splicing(fuzzer):
    base = "UNION SELECT password"
    mutated = fuzzer.mutate_sql_comment_splicing(base)
    assert "/**/" in mutated

def test_url_double_encoding(fuzzer):
    base = "admin' OR 1=1"
    mutated = fuzzer.mutate_url_double_encoding(base)
    assert "%2527" in mutated

def test_whitespace_jitter(fuzzer):
    base = "SELECT password FROM accounts"
    mutated = fuzzer.mutate_whitespace_jitter(base)
    assert any(sub in mutated for sub in ["%09", "%0a", "+", "/**/"])

def test_tautology_substitution(fuzzer):
    base = "admin' OR 1=1 --"
    mutated = fuzzer.mutate_tautology_substitution(base)
    assert any(identity in mutated for identity in ["2>1", "'a'='a'", "5=5", "100>50", "'x'='x'"])

def test_generate_all_mutations(fuzzer):
    base = "admin' UNION SELECT credit_card FROM users --"
    mutations = fuzzer.generate_all_mutations(base)
    assert len(mutations) >= 8
    for m in mutations:
        assert "operator" in m
        assert "mutated_payload" in m
        assert len(m["mutated_payload"]) > 0

def test_audit_waf_resilience_mock(fuzzer):
    base = "' OR 1=1 --"
    # Mock inspection function
    def mock_inspect(payload):
        return {"verdict": "BLOCK", "threat_score": 0.95}

    audit = fuzzer.audit_waf_resilience(base, mock_inspect)
    assert audit["total_mutations_tested"] >= 8
    assert audit["blocked_or_flagged_count"] == audit["total_mutations_tested"]
    assert audit["resilience_percentage"] == 100.0
