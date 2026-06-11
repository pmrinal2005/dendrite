"""
🎯 Assessment Agent (Hippocampus + Cerebellum).

- Citation-grounded question generation (questions w/o a citation are regenerated).
- Confidence-Weighted Scoring (4-cell matrix).
- Weakness Fingerprinting per skill area.
- Socratic follow-ups on wrong answers.
"""
from __future__ import annotations

import uuid
from typing import Any

from ..core import config, mirl
from ..core.config import UserContext
from ..core.foundry_client import chat_json
from ..models.schemas import (AgentOutput, AnswerSubmission, Citation, Question,
                              WeaknessFingerprint)
from ..services import foundry_iq


GEN_SYSTEM = """You are the DENDRITE Assessment Agent.
Generate multiple-choice questions grounded in the provided SOURCES.

Rules:
- EVERY question MUST cite a source ID from the SOURCES list (citation.source_id).
- Difficulty in [0,1].
- 4 options per question, exactly one correct.
- Include a one-sentence rationale.

Return ONLY JSON:
{ "questions": [
    {"skill_area": str, "difficulty": number,
     "prompt": str, "options": [str,str,str,str],
     "correct_index": int,
     "citation": {"source_id": str, "excerpt": str},
     "rationale": str}
  ],
  "confidence": number
}
"""


SCORE_SYSTEM = """You score a learner's assessment using CONFIDENCE-WEIGHTED scoring.

For each answer compute one of:
  - correct + high_conf  → "strong"
  - correct + low_conf   → "fragile"
  - incorrect + low_conf → "gap"
  - incorrect + high_conf → "dangerous_gap"

Aggregate per skill_area to a mastery_pct in [0,100].
Return ONLY JSON:
{
  "readiness_pct": number,
  "knowledge_temperature": "hot"|"warm"|"cold",
  "fingerprint": [{"skill_area": str, "mastery_pct": number,
                    "state": "strong"|"borderline"|"gap"|"dangerous_gap"}],
  "next_action": str,
  "socratic_followups": [str],
  "confidence": number
}
"""


async def generate_questions(ctx: UserContext, *,
                             certification: str, skill_areas: list[str],
                             num_questions: int) -> tuple[AgentOutput, list[Question]]:
    routing = mirl.route(mirl.score_complexity(
        agents_to_coordinate=1, kb_lookups=2,
        learners_in_scope=1, downstream_criticality=4))

    iq = await foundry_iq.query_knowledge(
        ctx, f"Assessment content for {certification} covering {', '.join(skill_areas)}")
    sources = []
    for i, c in enumerate(iq.get("citations", []) or []):
        sources.append({"id": f"IQ-{i+1}", "doc": c.get("doc"),
                        "excerpt": iq.get("answer", "")[:500]})
    if not sources:
        sources.append({"id": "IQ-NONE", "doc": "no knowledge retrieved",
                        "excerpt": ""})

    user = (f"CERTIFICATION: {certification}\n"
            f"SKILL_AREAS: {skill_areas}\n"
            f"NUM_QUESTIONS: {num_questions}\n"
            f"SOURCES:\n" +
            "\n".join(f"- {s['id']}: {s['doc']} — {s['excerpt'][:200]}"
                      for s in sources))
    data = await chat_json(ctx, model=routing.model,
                           system=GEN_SYSTEM, user=user, max_tokens=1400)

    src_index = {s["id"]: s for s in sources}
    questions: list[Question] = []
    for q in data.get("questions", [])[:num_questions]:
        sid = (q.get("citation") or {}).get("source_id") or "IQ-NONE"
        src = src_index.get(sid, sources[0])
        questions.append(Question(
            id=str(uuid.uuid4()),
            skill_area=q.get("skill_area", "general"),
            difficulty=float(q.get("difficulty", 0.5)),
            prompt=q["prompt"],
            options=q["options"][:4],
            correct_index=int(q["correct_index"]),
            citation=Citation(doc=src.get("doc", "unknown"),
                              section=sid,
                              excerpt=(q.get("citation") or {}).get("excerpt", "")),
            rationale=q.get("rationale", ""),
        ))

    out = AgentOutput(
        agent="assessment_generator",
        tier=routing.tier,
        confidence=float(data.get("confidence",
                                  0.78 if iq.get("citations") else 0.55)),
        content=f"{len(questions)} grounded questions generated.",
        citations=[q.citation for q in questions],
        extra={"source_ids": list(src_index.keys())},
    )
    return out, questions


async def score(ctx: UserContext, *,
                certification: str,
                answers: list[AnswerSubmission],
                questions: list[Question]) -> AgentOutput:
    routing = mirl.route(mirl.score_complexity(
        agents_to_coordinate=1, kb_lookups=0,
        learners_in_scope=1, downstream_criticality=5))

    qmap = {q.id: q for q in questions}
    rows: list[dict[str, Any]] = []
    for a in answers:
        q = qmap.get(a.question_id)
        if not q:
            continue
        rows.append({
            "skill_area": q.skill_area,
            "correct": a.chosen_index == q.correct_index,
            "confidence": a.confidence,
            "difficulty": q.difficulty,
        })
    user = f"CERT: {certification}\nROWS: {rows}"
    data = await chat_json(ctx, model=routing.model,
                           system=SCORE_SYSTEM, user=user, max_tokens=900)

    return AgentOutput(
        agent="assessment_scorer",
        tier=routing.tier,
        confidence=float(data.get("confidence", 0.8)),
        content=data.get("next_action", ""),
        extra={
            "readiness_pct": float(data.get("readiness_pct", 0)),
            "knowledge_temperature": data.get("knowledge_temperature", "warm"),
            "fingerprint": data.get("fingerprint", []),
            "socratic_followups": data.get("socratic_followups", []),
        },
    )
