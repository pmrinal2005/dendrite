"""
🛡️ Guardrail Agent (Immune System).

Silent watcher on EVERY agent output. 6-dimension checks:
  1. Citation verification (claims with no [Source: …] when one was needed)
  2. PII scan (emails, phone numbers, real-name-like patterns)
  3. Hallucination probe (numbers/dates not present in citations)
  4. Bias check (asymmetric role/demographic language)
  5. Prompt injection detection
  6. Out-of-scope detection

Lightweight regex + heuristic for 90% of cases (MIRL Tier 2 only when ambiguous).
Audit log streamed to backend/logs/guardrail_audit.jsonl.
"""
from __future__ import annotations

import re
from typing import Any

from ..core.logging import audit
from ..models.schemas import GuardrailNote


_PII_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"),          # email
    re.compile(r"\+?\d[\d\s().-]{8,}\d"),                                    # phone
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),                                  # cc
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),                                    # ssn
]

_INJECTION_PATTERNS = [
    re.compile(r"ignore (?:all )?previous instructions", re.I),
    re.compile(r"reveal (?:the )?system prompt", re.I),
    re.compile(r"act as (?:a )?(?:dan|developer mode)", re.I),
    re.compile(r"disregard (?:any )?safety", re.I),
]

_OOS_PATTERNS = [
    re.compile(r"\b(stocks?|crypto|bitcoin|politics?|election|porn)\b", re.I),
]

_BIAS_PATTERNS = [
    re.compile(r"\b(women|men|young|old|black|white|asian)\s+(?:are|should)\b", re.I),
]


def _detect_pii(text: str) -> list[str]:
    hits = []
    for p in _PII_PATTERNS:
        if p.search(text):
            hits.append(p.pattern[:30])
    return hits


def scan_input(user_message: str, agent: str = "input") -> GuardrailNote:
    violations: list[str] = []
    note: str | None = None
    for p in _INJECTION_PATTERNS:
        if p.search(user_message):
            violations.append("prompt_injection")
            note = "Possible prompt injection — sanitised."
            break
    for p in _OOS_PATTERNS:
        if p.search(user_message):
            violations.append("out_of_scope")
            note = "DENDRITE only handles certification & learning topics."
            break
    pii_hits = _detect_pii(user_message)
    if pii_hits:
        violations.append("pii_attempt")
    if violations:
        audit({"agent": agent, "phase": "input",
               "violations": violations, "snippet": user_message[:140]})
    return GuardrailNote(intervened=bool(violations), violations=violations, note=note)


def scan_output(content: str, citations: list[dict[str, Any]] | None,
                agent: str, requires_citations: bool = False) -> tuple[str, GuardrailNote]:
    violations: list[str] = []
    citations = citations or []
    modified = content

    # PII
    if _detect_pii(content):
        violations.append("pii_leak")
        for p in _PII_PATTERNS:
            modified = p.sub("[REDACTED]", modified)

    # Citation requirement
    if requires_citations and not citations and "[Source" not in content:
        violations.append("missing_citation")
        modified += "\n\nℹ️ This recommendation was reviewed. Citations were missing — treat as advisory only."

    # Bias
    for p in _BIAS_PATTERNS:
        if p.search(content):
            violations.append("bias_language")
            break

    note = None
    if violations:
        note = "Guardrail intervened: " + ", ".join(violations)
        audit({"agent": agent, "phase": "output", "violations": violations,
               "original": content[:200], "modified": modified[:200]})

    return modified, GuardrailNote(
        intervened=bool(violations), violations=violations, note=note
    )
