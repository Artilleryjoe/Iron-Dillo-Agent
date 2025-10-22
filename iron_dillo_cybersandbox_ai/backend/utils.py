"""Utility helpers and mini security workflows for the Cybersandbox."""

from __future__ import annotations

import ipaddress
import re
from typing import List

IOC_PATTERNS = {
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "url": re.compile(r"https?://[\w\-./?%&=#:]+", re.IGNORECASE),
    "md5": re.compile(r"\b[a-f0-9]{32}\b", re.IGNORECASE),
    "sha256": re.compile(r"\b[a-f0-9]{64}\b", re.IGNORECASE),
}

HEADER_PATTERN = re.compile(r"^([A-Za-z0-9\-]+):\s*(.+)$")


def extract_iocs(text: str) -> List[dict]:
    """Return a list of unique indicators of compromise discovered in the text."""

    indicators = []
    seen = set()
    for indicator_type, pattern in IOC_PATTERNS.items():
        for match in pattern.findall(text):
            value = match.strip()
            if indicator_type == "ipv4":
                try:
                    ipaddress.IPv4Address(value)
                except ipaddress.AddressValueError:
                    continue
            key = (indicator_type, value.lower())
            if key in seen:
                continue
            seen.add(key)
            indicators.append({"type": indicator_type, "value": value})
    return indicators


def parse_email_headers(raw_headers: str) -> List[dict]:
    """Parse simple RFC 5322-style headers into structured data."""

    entries = []
    for line in raw_headers.splitlines():
        match = HEADER_PATTERN.match(line.strip())
        if match:
            entries.append({"header": match.group(1), "value": match.group(2)})
    return entries


def summarize_logs(text: str) -> dict:
    """Produce lightweight heuristics about a log snippet without an LLM."""

    lines = [line for line in text.splitlines() if line.strip()]
    total = len(lines)
    status_counts = {}
    for line in lines:
        match = re.search(r"\s(\d{3})\s", line)
        if match:
            status = match.group(1)
            status_counts[status] = status_counts.get(status, 0) + 1
    highlight = None
    if status_counts:
        common_status = max(status_counts, key=status_counts.get)
        highlight = f"Most common status code: {common_status} ({status_counts[common_status]} hits)"
    return {
        "lines": total,
        "status_counts": status_counts,
        "highlight": highlight,
    }


__all__ = ["extract_iocs", "parse_email_headers", "summarize_logs"]
