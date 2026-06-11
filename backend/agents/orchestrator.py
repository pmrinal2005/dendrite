"""
🧠 Meta-Orchestrator (Prefrontal Cortex).

Parses intent, runs the state machine, dispatches to sub-agents, calls
Critic when confidence < gate, runs Guardrail on every output, persists trace.
"""
from __future__ import annotations

from typing import Any

from ..core import config, mirl
from ..core.config import UserContext
from ..core.foundry_client import chat_json
from ..core.logging import trace as log_trace
from ..models.schemas import AgentOutput, ChatRequest, ChatResponse, GuardrailNote
from . import (assessment, critic, engagement, guardrail, manager_insights,
               path_curator, plan_generator, skill_decay, meta_learning)


INTENT_SYSTEM = """Classify the user message into ONE intent.
Return JSON: {"intent": "<one of below>", "confidence": number}.

Intents:
- curate_path     → wants a learning path
- generate_plan   → wants a study plan
- nudge           → wants engagement / motivation
- assessment     → asking for a quiz / assessment
- score          → submitting answers
- manager_view    → manager-level question about a team
- skill_decay     → asking about knowledge freshness / decay
- general         → anything else
"""


async def classify(ctx: UserContext, message: str) -> tuple[str, float]:
    routing = mirl.Routing(1, config.TIER1_MODEL, "instant")
    try:
        data = await chat_json(ctx, model=routing.model,
                               system=INTENT_SYSTEM, user=message,
                               max_tokens=120)
        return data.get("intent", "general"), float(data.get("confidence", 0.6))
    except Exception:
        return "general", 0.5


async def _maybe_critique(ctx: UserContext, out: AgentOutput) -> AgentOutput:
    if out.confidence >= config.CONFIDENCE_GATE:
        return out
    review = await critic.critique(
        ctx, agent_name=out.agent,
        original=out.content, original_conf=out.confidence,
        context_hint=str(out.extra)[:600])
    return AgentOutput(
        agent=out.agent,
        tier=out.tier,
        confidence=review.confidence,
        content=review.content,
        citations=out.citations,
        extra={**out.extra, "critic_verdict": review.extra.get("verdict"),
               "critic_reasoning": review.extra.get("reasoning")},
    )


async def handle(ctx: UserContext, req: ChatRequest) -> ChatResponse:
    trace: list[AgentOutput] = []
    guard_input = guardrail.scan_input(req.message, agent="orchestrator")
    if guard_input.intervened and "out_of_scope" in guard_input.violations:
        return ChatResponse(
            reply=guard_input.note or "Out of scope.",
            state="REJECTED", trace=[], guardrail=guard_input, citations=[])

    intent, _conf = await classify(ctx, req.message)
    state = "INTAKE"
    citations = []
    reply = ""
    guard_out = GuardrailNote()

    if intent == "curate_path":
        state = "CURATION"
        out = await path_curator.curate(
            ctx,
            role=req.role or "Cloud Engineer",
            certification=req.target_certification or "AZ-204",
            weeks_available=req.weeks_available)
        out = await _maybe_critique(ctx, out)
        modified, guard_out = guardrail.scan_output(
            out.content, [c.model_dump() for c in out.citations],
            agent="path_curator", requires_citations=True)
        out.content = modified
        trace.append(out)
        citations = out.citations
        reply = _format_paths(out)

    elif intent == "generate_plan":
        state = "PLANNING"
        out = await plan_generator.generate_plan(
            ctx,
            learner_id=req.learner_id or "L-1001",
            role=req.role or "Cloud Engineer",
            certification=req.target_certification or "AZ-204",
            skill_areas=["API Development", "Azure Functions", "Storage"],
            weeks_available=req.weeks_available,
            employee_id=_employee_for(req.learner_id))
        out = await _maybe_critique(ctx, out)
        modified, guard_out = guardrail.scan_output(
            out.content, None, agent="plan_generator")
        out.content = modified
        trace.append(out)
        reply = _format_plan(out)

    elif intent == "nudge":
        state = "ACTIVE_LEARNING"
        out = await engagement.nudge(
            ctx, learner_id=req.learner_id or "L-1001",
            employee_id=_employee_for(req.learner_id),
            recent_pattern=None)
        modified, guard_out = guardrail.scan_output(
            out.content, None, agent="engagement")
        out.content = modified
        trace.append(out)
        reply = out.content

    elif intent == "skill_decay":
        out = skill_decay.compute([
            skill_decay.DecayInput(
                learner_id=req.learner_id or "L-1001",
                certification=req.target_certification or "AZ-204",
                days_since_cert=120, days_since_last_active_use=70,
                original_score=78),
        ])
        modified, guard_out = guardrail.scan_output(
            out.content, None, agent="skill_decay")
        out.content = modified
        trace.append(out)
        reply = f"{out.content}\n\n" + "\n".join(
            f"• {r['certification']} — retention {r['retention_pct']}% ({r['status']})"
            for r in out.extra["records"])

    elif intent == "manager_view":
        state = "ROUTING"
        out = await manager_insights.insights(
            ctx, query=req.message, team_id="TEAM-A",
            team_signals=[
                {"role": "Cloud Engineer", "cert": "AZ-204",
                 "practice_score_avg": 67, "hours_studied": 18, "outcome": "Fail"},
                {"role": "DevOps Engineer", "cert": "AZ-400",
                 "practice_score_avg": 82, "hours_studied": 24, "outcome": "Pass"},
                {"role": "Data Engineer", "cert": "DP-203",
                 "practice_score_avg": 74, "hours_studied": 20, "outcome": "Pass"},
            ])
        out = await _maybe_critique(ctx, out)
        modified, guard_out = guardrail.scan_output(
            out.content, None, agent="manager_insights")
        out.content = modified
        trace.append(out)
        reply = _format_manager(out)

    else:
        # General → light reasoning Tier 1
        routing = mirl.Routing(1, config.TIER1_MODEL, "instant")
        from ..core.foundry_client import chat
        ans = await chat(ctx, model=routing.model,
                         system=("You are DENDRITE, a cognitive co-pilot for "
                                 "enterprise certification learning. Be concise."),
                         user=req.message, max_tokens=350)
        out = AgentOutput(agent="orchestrator_general", tier=routing.tier,
                          confidence=0.7, content=ans)
        modified, guard_out = guardrail.scan_output(
            ans, None, agent="orchestrator_general")
        out.content = modified
        trace.append(out)
        reply = modified

    # async reflection (cheap)
    reflection = meta_learning.reflect()
    if reflection.extra.get("hints"):
        trace.append(reflection)

    for t in trace:
        log_trace({"agent": t.agent, "tier": t.tier,
                   "confidence": t.confidence})

    return ChatResponse(reply=reply, state=state, trace=trace,
                        guardrail=guard_out, citations=citations)


# ---------- formatting helpers ----------
def _format_paths(out: AgentOutput) -> str:
    paths = out.extra.get("paths", [])
    if not paths:
        return out.content or "No grounded learning path could be produced."
    lines = ["**📚 Learning Path Options**"]
    if out.content:
        lines.append(f"_{out.content}_")
    for p in paths:
        lines.append(
            f"\n**{p.get('name')}** — {p.get('weeks')} weeks · "
            f"effort {p.get('effort')}/5 · risk {p.get('risk')}/5 · "
            f"synergy {p.get('synergy')}/5 · "
            f"readiness ~{int(float(p.get('readiness_confidence', 0))*100)}%")
        for m in p.get("modules", [])[:6]:
            lines.append(f"  • {m.get('title')}  *[Source: {m.get('source_id')}]*")
    return "\n".join(lines)


def _format_plan(out: AgentOutput) -> str:
    variants = out.extra.get("variants", [])
    if not variants:
        return "No plan variants could be generated."
    lines = ["**📅 Three Study Plan Variants**"]
    for v in variants:
        lines.append(
            f"\n**{v.get('name')}** — {v.get('total_weeks')} weeks · "
            f"{v.get('weekly_hours')} h/week · "
            f"readiness ~{int(float(v.get('readiness_confidence', 0))*100)}%")
        for s in v.get("weekly_schedule", [])[:5]:
            lines.append(f"  • {s.get('day')} {s.get('time')} — "
                         f"{', '.join(s.get('topics', []))} ({s.get('hours')}h)")
    return "\n".join(lines)


def _format_manager(out: AgentOutput) -> str:
    summary = out.content or "Manager view ready."
    rr = out.extra.get("risk_radar", [])
    bf = out.extra.get("bus_factor_alerts", [])
    actions = out.extra.get("recommended_actions", [])
    lines = [f"**📊 Manager Insights**\n{summary}"]
    if rr:
        lines.append("\n**Workforce Risk Radar**")
        for r in rr:
            lines.append(f"  • {r['certification']}: "
                         f"urgency {r['urgency']:.2f} · readiness {r['readiness']:.2f} · "
                         f"{r['learners_at_risk']}/{r['total_learners']} at risk")
    if bf:
        lines.append("\n**Bus Factor Alerts**")
        lines += [f"  ⚠️ {b}" for b in bf]
    if actions:
        lines.append("\n**Recommended Actions**")
        lines += [f"  → {a}" for a in actions]
    return "\n".join(lines)


def _employee_for(learner_id: str | None) -> str | None:
    # Synthetic: L-1001 ↔ EMP-001, L-1002 ↔ EMP-002
    if not learner_id:
        return None
    mapping = {"L-1001": "EMP-001", "L-1002": "EMP-002"}
    return mapping.get(learner_id)
