"""
Model Intelligence Routing Layer (MIRL).

5 tiers. Score a task on complexity (0-100) and route to the cheapest model
that can still reason adequately.

Tier 1 — Phi-4-mini-instruct       (instant, near-free)
Tier 2 — gpt-4o-mini                (CoT, cheap)
Tier 3 — gpt-4.1-mini               (interleaved, mid)
Tier 4 — o4-mini                    (deep reasoning, sparingly)
Tier 5 — Swarm parallel             (fan-out across tiers, merge w/ Tier 3)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from . import config


Tier = Literal[1, 2, 3, 4, 5]


@dataclass
class Routing:
    tier: Tier
    model: str
    reasoning_mode: str   # 'instant' | 'cot' | 'interleaved' | 'deep' | 'swarm'


def score_complexity(
    *,
    agents_to_coordinate: int = 1,
    kb_lookups: int = 0,
    learners_in_scope: int = 1,
    downstream_criticality: int = 1,   # 1 (low) … 5 (org-wide)
) -> int:
    """Normalise to 0-100."""
    raw = (
        agents_to_coordinate * 6
        + kb_lookups * 5
        + min(learners_in_scope, 50)
        + downstream_criticality * 8
    )
    return max(0, min(100, raw))


def route(score: int) -> Routing:
    if score < 15:
        return Routing(1, config.TIER1_MODEL, "instant")
    if score < 35:
        return Routing(2, config.TIER2_MODEL, "cot")
    if score < 60:
        return Routing(3, config.TIER3_MODEL, "interleaved")
    if score < 85:
        return Routing(4, config.TIER4_MODEL, "deep")
    return Routing(5, config.TIER3_MODEL, "swarm")


def escalate(current: Routing) -> Routing:
    """Bump one tier up — used after a failed confidence gate."""
    tier = min(4, current.tier + 1)  # type: ignore[assignment]
    model_map = {1: config.TIER1_MODEL, 2: config.TIER2_MODEL,
                 3: config.TIER3_MODEL, 4: config.TIER4_MODEL}
    mode_map = {1: "instant", 2: "cot", 3: "interleaved", 4: "deep"}
    return Routing(tier, model_map[tier], mode_map[tier])  # type: ignore[arg-type]
