"""Append-only JSONL logger for guardrail audit + agent traces."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def _append(name: str, payload: dict[str, Any]) -> None:
    payload = {"ts": time.time(), **payload}
    path = LOG_DIR / f"{name}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def audit(payload: dict[str, Any]) -> None:
    _append("guardrail_audit", payload)


def trace(payload: dict[str, Any]) -> None:
    _append("agent_trace", payload)
