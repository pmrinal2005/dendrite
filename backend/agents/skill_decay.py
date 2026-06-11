"""
🕐 Skill Decay (Reticular Formation).

Mathematical Ebbinghaus modelling — almost no LLM cost.
Retention = exp(-t / S), S = stability ~ original study depth × active use.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from ..core import config, mirl
from ..models.schemas import AgentOutput


@dataclass
class DecayInput:
    learner_id: str
    certification: str
    days_since_cert: int
    days_since_last_active_use: int
    original_score: float   # 0..100


def _retention(days_inactive: int, stability_days: float) -> float:
    if stability_days <= 0:
        return 0.0
    return math.exp(-days_inactive / stability_days)


def compute(records: Iterable[DecayInput]) -> AgentOutput:
    routing = mirl.Routing(1, config.TIER1_MODEL, "instant")  # math only
    summary = []
    for r in records:
        # Stronger original score → more stability; active use slows decay.
        stability = max(7.0, r.original_score * 1.0 + (90 - min(r.days_since_last_active_use, 90)))
        ret = _retention(r.days_since_cert, stability)
        status = "ok"
        if ret < 0.6 and r.days_since_last_active_use > 60:
            status = "refresh_recommended"
        if ret < 0.4:
            status = "critical"
        summary.append({
            "learner_id": r.learner_id,
            "certification": r.certification,
            "retention_pct": round(ret * 100, 1),
            "status": status,
            "days_inactive": r.days_since_last_active_use,
        })
    return AgentOutput(
        agent="skill_decay",
        tier=routing.tier,
        confidence=0.95,           # deterministic math
        content=f"Decay assessed for {len(summary)} record(s).",
        extra={"records": summary},
    )
