"""Unit tests for Iron Dillo Cybersecurity Buddy utilities."""

from __future__ import annotations

import random

import pytest

from buddy_facts import get_random_fact, list_facts
from tools import RAGStore, assess_risk, get_compliance_guide, get_security_tip


def test_get_security_tip_returns_actions():
    result = get_security_tip("Individuals", "identity")
    assert result["audience"] == "individuals"
    assert result["topic"] == "identity"
    assert result["actions"]
    assert any("credit" in action.lower() for action in result["actions"])


def test_get_security_tip_invalid_audience():
    with pytest.raises(ValueError):
        get_security_tip("contractors", "identity")


def test_get_compliance_guide_includes_checklist():
    guide = get_compliance_guide("hipaa")
    assert guide["standard"] == "hipaa"
    assert len(guide["checklist"]) == 5


def test_assess_risk_computes_level():
    report = assess_risk(
        audience="small_businesses",
        impact="high",
        likelihood="likely",
        description="Remote access left enabled on old firewall",
    )
    assert report.level == "high"
    assert report.score == 9
    assert any("Remote access".lower() in item.lower() for item in report.recommendations)


def test_rag_store_search_returns_matches():
    store = RAGStore()
    store.add_document(
        title="NIST access control",
        content="Implement least privilege for Tyler and Lindale offices.",
        tags=["nist", "access"],
    )
    store.add_document(
        title="Patch management",
        content="Keep firmware current on irrigation controllers.",
        tags=["patching", "scada"],
    )

    results = store.search("Tyler least privilege")
    assert len(results) == 1
    assert results[0].title == "NIST access control"


def test_get_random_fact_avoids_previous_fact():
    rng = random.Random(0)
    first_fact = get_random_fact(rng=rng)
    second_fact = get_random_fact(rng=rng, avoid=[first_fact])
    assert first_fact != second_fact
    assert first_fact in list_facts()
    assert second_fact in list_facts()
