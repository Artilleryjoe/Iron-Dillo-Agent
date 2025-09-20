"""Fun armadillo and pangolin trivia to keep briefings engaging."""

from __future__ import annotations

import random
from typing import Iterable, Sequence

_FACTS: Sequence[str] = (
    "Armadillos can hold their breath for over six minutes, letting them cross creeks around Lindale without a bridge.",
    "The nine-banded armadillo is the only mammal besides humans known to regularly give birth to quadruplets.",
    "Pangolins roll into a ball using scales made of keratin—the same material in human fingernails.",
    "In Texas folklore, armadillos were once called 'hillbilly speed bumps,' but Iron Dillo proves they can be cybersecurity heroes.",
    "Armadillos have a natural resistance to some infections, inspiring resilient network designs.",
)


def list_facts() -> Sequence[str]:
    """Return all currently loaded facts."""

    return tuple(_FACTS)


def get_random_fact(*, rng: random.Random | None = None, avoid: Iterable[str] | None = None) -> str:
    """Return a random fact, optionally avoiding repeats from the `avoid` collection."""

    rng = rng or random
    avoided = set(fact.strip() for fact in avoid or [])
    candidates = [fact for fact in _FACTS if fact not in avoided]

    if not candidates:
        candidates = list(_FACTS)

    return rng.choice(candidates)


__all__ = ["get_random_fact", "list_facts"]
