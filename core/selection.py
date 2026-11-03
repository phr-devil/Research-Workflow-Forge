"""Reconstruct research-task selection history from append-only event logs.

The log is the source of truth; never erase unsuccessful branches or relabel a
development dataset as sealed after it influenced task selection.
"""
from __future__ import annotations
import json
from pathlib import Path

def selection_history(project: Path) -> dict:
    changes = []
    log = project / "EVENTS.jsonl"
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if item["event"] in {"TASK_DEFINED", "TASK_PIVOT", "PROTOCOL_REVISED"} and item.get("record_level") == "ARTIFACT_STRUCTURAL_ONLY":
                changes.append({
                    "event_id": item["event_id"], "at": item["at"],
                    "event": item["event"], "from": item.get("from_task"),
                    "to": item.get("to_task"),
                    "decision": item.get("artifact_path"),
                })
    return {"selection_events": changes, "task_or_protocol_selection_count": len(changes),
            "confirmation_note": "Selection history is necessary for holdout eligibility; it does not prove a split was untouched"}
