"""Append-only JSONL logger for guardrail audit + agent traces.
Writes to a writable directory chosen by env or auto-detected so we don't
crash on serverless read-only filesystems.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

_DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR = Path(os.getenv("DENDRITE_LOG_DIR", str(_DEFAULT_LOG_DIR)))

try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _WRITABLE = os.access(LOG_DIR, os.W_OK)
except OSError:
    _WRITABLE = False

if not _WRITABLE:
    LOG_DIR = Path("/tmp/dendrite-logs")
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        _WRITABLE = os.access(LOG_DIR, os.W_OK)
    except OSError:
        _WRITABLE = False


def _append(name: str, payload: dict[str, Any]) -> None:
    if not _WRITABLE:
        return  # silently no-op in fully read-only environments
    payload = {"ts": time.time(), **payload}
    path = LOG_DIR / f"{name}.jsonl"
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        pass


def audit(payload: dict[str, Any]) -> None:
    _append("guardrail_audit", payload)


def trace(payload: dict[str, Any]) -> None:
    _append("agent_trace", payload)
