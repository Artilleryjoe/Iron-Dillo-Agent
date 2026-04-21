"""Risk score and confidence normalization."""

from __future__ import annotations

from .schemas import Classification, ConfidenceBand, Score, SeverityBand

_BASE_SCORE = {
    SeverityBand.LOW: 25,
    SeverityBand.MEDIUM: 50,
    SeverityBand.HIGH: 75,
    SeverityBand.CRITICAL: 90,
}


def calculate_score(classification: Classification, completeness: float) -> Score:
    base_value = _BASE_SCORE[classification.severity]
    domain_bonus = min(len(classification.affected_domains) * 2, 10)
    control_bonus = min(len(classification.likely_controls), 5)
    value = max(0, min(100, base_value + domain_bonus + control_bonus))

    if completeness >= 0.8:
        confidence = ConfidenceBand.HIGH
    elif completeness >= 0.5:
        confidence = ConfidenceBand.MEDIUM
    else:
        confidence = ConfidenceBand.LOW

    if value >= 85:
        band = SeverityBand.CRITICAL
    elif value >= 70:
        band = SeverityBand.HIGH
    elif value >= 45:
        band = SeverityBand.MEDIUM
    else:
        band = SeverityBand.LOW

    return Score(value=value, band=band, confidence=confidence)


__all__ = ["calculate_score"]
