import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.fact_checker import FactChecker

def test_simple_fact():
    fc = FactChecker()
    out = fc.check_claim("The capital of France is Paris.")
    assert out["claim_type"] in {"Factual", "Mixed", "Opinion", "Unverifiable"}
    assert "verdict" in out and out["verdict"] in {"True", "False", "Mixed", "Uncertain"}
