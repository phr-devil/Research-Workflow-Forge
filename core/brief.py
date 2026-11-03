"""Small project handoff summary; never reads model logs or reports inferred costs."""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from core.state import load_state

def project_brief(directory: Path, recent: int = 2) -> dict:
    if type(recent) is not int or not 0 <= recent <= 5:
        raise ValueError("recent must be an integer from 0 to 5")
    state = load_state(directory / "STATE.json")
    recent_events = deque(maxlen=recent or 1)
    last_event_id = None
    path = directory / "EVENTS.jsonl"
    if path.exists():
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    event_id = entry.get("event_id")
                    if not isinstance(event_id, str) or not event_id:
                        raise ValueError("Malformed event history: missing event_id")
                    last_event_id = event_id
                    if recent:
                        recent_events.append({
                            "event": entry.get("event"),
                            "evidence": entry.get("artifact_path"),
                            "record_level": entry.get("record_level"),
                            "note": str(entry.get("note") or "")[:160],
                        })
    return {
        "project_id": state["project_id"],
        "phase": state["phase"],
        "active_task_id": state.get("active_task_id"),
        "active_protocol_id": state.get("active_protocol_id"),
        "champion_run_id": state.get("best_valid_run_id"),
        "next_action": state["next_action"][:240],
        "event_history_consistent": last_event_id == state.get("last_event_id"),
        "recent_events": list(recent_events) if recent else [],
        "evidence_level": "STATE_AND_EVENT_POINTERS_ONLY",
        "token_gpu_cost": "NOT_MEASURED",
    }
