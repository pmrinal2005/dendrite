"""
🔔 Engagement Agent (Motor Cortex + Amygdala).

Generates a contextually-timed, emotionally-calibrated nudge using Work IQ
signals and 4-state emotional register (Engaged / Neutral / Fatigued / Disengaged).
"""
from __future__ import annotations

from ..core import config, mirl
from ..core.config import UserContext
from ..core.foundry_client import chat_json
from ..models.schemas import AgentOutput
from ..services import work_iq_sim


SYSTEM = """You are the DENDRITE Engagement Agent.
Produce ONE short nudge for the learner (max 60 words).

Adapt tone to the emotional register:
- engaged   → celebratory + stretch challenge
- neutral   → standard coaching
- fatigued  → supportive, lower pressure
- disengaged → curiosity hook + re-motivation

Use the WORK_SIGNAL to pick a realistic window. Mention cognitive recovery if fatigued.

Return ONLY JSON:
{
  "register": "engaged"|"neutral"|"fatigued"|"disengaged",
  "nudge": string,
  "suggested_time": string,
  "micro_retrieval_question": string,
  "confidence": number
}
"""


async def nudge(ctx: UserContext, *, learner_id: str,
                employee_id: str | None, recent_pattern: str | None) -> AgentOutput:
    routing = mirl.route(mirl.score_complexity(
        agents_to_coordinate=1, kb_lookups=0,
        learners_in_scope=1, downstream_criticality=1))

    work_signal = work_iq_sim.find_optimal_study_windows(
        employee_id, hours_needed=4.0) if employee_id else {}
    cog_state = work_iq_sim.cognitive_state(employee_id) if employee_id else "unknown"

    user = (f"LEARNER: {learner_id}\n"
            f"COGNITIVE_STATE: {cog_state}\n"
            f"RECENT_PATTERN: {recent_pattern or 'no recent data'}\n"
            f"WORK_SIGNAL: {work_signal}\n")
    data = await chat_json(ctx, model=routing.model,
                           system=SYSTEM, user=user, max_tokens=400)

    return AgentOutput(
        agent="engagement",
        tier=routing.tier,
        confidence=float(data.get("confidence", 0.82)),
        content=data.get("nudge", ""),
        extra={
            "register": data.get("register"),
            "suggested_time": data.get("suggested_time"),
            "micro_retrieval_question": data.get("micro_retrieval_question"),
            "work_signal": work_signal,
            "cognitive_state": cog_state,
        },
    )
