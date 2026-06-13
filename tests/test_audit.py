from pathlib import Path

from token_alias_tail_audit.audit import ALLOWED_VERDICTS, FORBIDDEN_PHRASES


def test_forbidden_claims_are_specific_strings():
    assert "score-tail always hurts" in FORBIDDEN_PHRASES
    assert "token models are bad" in FORBIDDEN_PHRASES


def test_allowed_verdicts_are_exactly_the_prompt_set():
    assert set(ALLOWED_VERDICTS) == {
        "paper-worthy v1",
        "needs stronger learned model",
        "needs benchmark validation",
        "redesign required",
    }


def test_repo_has_readme():
    assert Path("README.md").exists()

