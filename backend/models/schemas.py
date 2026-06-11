from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# ---------- chat ----------
class ChatRequest(BaseModel):
    message: str
    learner_id: Optional[str] = None
    role: Optional[str] = None
    target_certification: Optional[str] = None
    weeks_available: Optional[int] = None
    persona: Literal["learner", "manager"] = "learner"


class Citation(BaseModel):
    doc: str
    section: Optional[str] = None
    excerpt: Optional[str] = None


class AgentOutput(BaseModel):
    agent: str
    tier: int
    confidence: float = Field(ge=0.0, le=1.0)
    content: str
    citations: list[Citation] = []
    extra: dict[str, Any] = {}


class GuardrailNote(BaseModel):
    intervened: bool = False
    violations: list[str] = []
    note: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    state: str
    trace: list[AgentOutput]
    guardrail: GuardrailNote
    citations: list[Citation] = []


# ---------- assessment ----------
class AssessmentRequest(BaseModel):
    certification: str
    skill_areas: list[str]
    num_questions: int = 5


class Question(BaseModel):
    id: str
    skill_area: str
    difficulty: float = Field(ge=0.0, le=1.0)
    prompt: str
    options: list[str]
    correct_index: int
    citation: Citation
    rationale: str


class AssessmentResponse(BaseModel):
    questions: list[Question]
    trace: list[AgentOutput]
    guardrail: GuardrailNote


class AnswerSubmission(BaseModel):
    question_id: str
    chosen_index: int
    confidence: float = Field(ge=0.0, le=1.0)


class ScoringRequest(BaseModel):
    certification: str
    answers: list[AnswerSubmission]
    questions: list[Question]


class WeaknessFingerprint(BaseModel):
    skill_area: str
    mastery_pct: float
    state: Literal["strong", "borderline", "gap", "dangerous_gap"]


class ScoringResponse(BaseModel):
    readiness_pct: float
    knowledge_temperature: Literal["hot", "warm", "cold"]
    fingerprint: list[WeaknessFingerprint]
    next_action: str
    socratic_followups: list[str]
    trace: list[AgentOutput]
    guardrail: GuardrailNote


# ---------- manager ----------
class ManagerRequest(BaseModel):
    query: str
    team_id: Optional[str] = "TEAM-A"


class RiskCell(BaseModel):
    certification: str
    urgency: float
    readiness: float
    learners_at_risk: int
    total_learners: int


class ManagerResponse(BaseModel):
    summary: str
    risk_radar: list[RiskCell]
    bus_factor_alerts: list[str]
    coverage_map: dict[str, float]
    recommended_actions: list[str]
    trace: list[AgentOutput]
    guardrail: GuardrailNote


# ---------- system ----------
class HealthResponse(BaseModel):
    ok: bool
    version: str
    mirl_models: dict[str, str]
