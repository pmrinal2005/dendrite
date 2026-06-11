"""
📅 Study Plan Generator (Cerebellum).

Converts a chosen learning path into a 3-variant, capacity-aware study plan
using Work IQ (sim) for cognitive-load budgeting and SM-2 spaced repetition.
"""
from __future__ import annotations

from typing import Any

from ..core import config, mirl
from ..core.config import UserContext
from ..core.foundry_client import chat_json
from ..models.schemas import AgentOutput
from ..services import work_iq_sim, fabric_iq


SYSTEM = """You are the DENDRITE Study Plan Generator.
Build THREE variants (Aggressive / Balanced / Conservative) of a weekly schedule
for the learner.

Apply:
- Interleaving (mix 2-3 topics per session, not block scheduling)
- SM-2 review checkpoints at days 1, 3, 7, 14
- Cognitive-load awareness using the provided WORK_SIGNAL
- Sprint awareness: if meeting_hours_per_week > 20 → reduce mid-week, push to weekends

Return ONLY JSON:
{
  "variants": [
    {"name": "Aggressive"|"Balanced"|"Conservative",
     "total_weeks": int,
     "weekly_hours": number,
     "weekly_schedule": [{"day": str, "time": str, "topics": [str], "hours": number}],
     "sm2_checkpoints": [int],
     "readiness_confidence": number}
  ],
  "confidence": number
}
"""


async def generate_plan(ctx: UserContext, *,
                        learner_id: str, role: str, certification: str,
                        skill_areas: list[str], weeks_available: int | None,
                        employee_id: str | None = None) -> AgentOutput:
    routing = mirl.route(mirl.score_complexity(
        agents_to_coordinate=2, kb_lookups=1,
        learners_in_scope=1, downstream_criticality=3))

    work_signal: dict[str, Any] = {}
    if employee_id:
        work_signal = work_iq_sim.find_optimal_study_windows(
            employee_id, hours_needed=20.0)
    ontology = await fabric_iq.get_ontology_snapshot(ctx)

    user_prompt = (
        f"LEARNER: {learner_id}\nROLE: {role}\nCERT: {certification}\n"
        f"SKILL_AREAS: {', '.join(skill_areas)}\n"
        f"WEEKS_AVAILABLE: {weeks_available or 'flexible'}\n"
        f"WORK_SIGNAL: {work_signal or 'unknown (no employee_id)'}\n"
        f"FABRIC_ONTOLOGY_AVAILABLE: {ontology.get('available')}\n"
    )
    data = await chat_json(ctx, model=routing.model,
                           system=SYSTEM, user=user_prompt, max_tokens=1100)

    return AgentOutput(
        agent="plan_generator",
        tier=routing.tier,
        confidence=float(data.get("confidence", 0.78)),
        content="Three plan variants generated.",
        extra={"variants": data.get("variants", []),
               "work_signal": work_signal},
    )
