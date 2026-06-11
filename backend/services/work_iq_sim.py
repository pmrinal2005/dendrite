"""
Work IQ — synthetic simulator.

Work IQ is currently restricted to specific M365 tenants. To keep DENDRITE
fully demoable, we expose a simulator that reads ONLY the synthetic JSON
the challenge brief supplies (data/synthetic/work-signals.json).

Everywhere we surface output from this module we label it as SIMULATED.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parent.parent.parent / "data" / "synthetic"


def _load_signals() -> list[dict[str, Any]]:
    with (DATA / "work-signals.json").open() as f:
        return json.load(f)


def get_work_signal(employee_id: str) -> dict[str, Any] | None:
    for s in _load_signals():
        if s["employee_id"] == employee_id:
            return {**s, "_source": "Work IQ Simulator (synthetic)"}
    return None


def find_optimal_study_windows(employee_id: str, hours_needed: float) -> dict[str, Any]:
    sig = get_work_signal(employee_id)
    if not sig:
        return {
            "available_hours_per_week": 0,
            "windows": [],
            "_source": "Work IQ Simulator (synthetic)",
            "note": f"No signal for {employee_id}",
        }
    focus = sig["focus_hours_per_week"]
    slot = sig["preferred_learning_slot"]
    # Distribute up to half of focus hours to study, capped by hours_needed
    weekly_budget = min(hours_needed, focus * 0.5)
    windows = []
    if weekly_budget > 0:
        # Spread across Mon/Wed/Fri by default; shift to Tue/Thu if meeting heavy
        days = (["Tue", "Thu", "Sat"]
                if sig["meeting_hours_per_week"] > 20 else ["Mon", "Wed", "Fri"])
        per_day = round(weekly_budget / len(days), 2)
        time_block = "09:00-10:30" if slot.lower() == "morning" else "14:00-15:30"
        windows = [{"day": d, "time": time_block, "hours": per_day} for d in days]
    return {
        "available_hours_per_week": round(weekly_budget, 2),
        "preferred_slot": slot,
        "meeting_load": sig["meeting_hours_per_week"],
        "windows": windows,
        "_source": "Work IQ Simulator (synthetic)",
    }


def cognitive_state(employee_id: str) -> str:
    sig = get_work_signal(employee_id)
    if not sig:
        return "unknown"
    m = sig["meeting_hours_per_week"]
    if m > 20:
        return "fatigued"
    if m > 14:
        return "recovering"
    return "fresh"
