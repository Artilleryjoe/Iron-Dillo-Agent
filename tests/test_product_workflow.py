from iron_dillo.product import GuidedIntake, Scenario, generate_readiness_brief


def test_generate_readiness_brief_returns_normalized_score_and_confidence():
    intake = GuidedIntake(
        scenario=Scenario.PHISHING_CONCERN,
        business_type="retail",
        employee_count_band="11_50",
        critical_systems=["email", "pos"],
        concern="Phishing emails targeting payroll",
        safeguards=["mfa"],
        urgency="high",
        audience="small_businesses",
    )

    brief, response = generate_readiness_brief(intake, include_fact=False)

    assert 0 <= brief.score.value <= 100
    assert brief.score.confidence.value in {"low", "medium", "high"}
    assert "## Next-action handoff" in response.message
    assert response.fact is None
