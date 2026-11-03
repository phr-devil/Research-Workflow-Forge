"""Local project state and append-only event notes, no external actions."""
from __future__ import annotations
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from core.contracts import SCHEMA_VERSION, validate_state
from core.router import route

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def initial_state(project_id: str, goal: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", project_id):
        raise ValueError("project_id must be 1-80 letters/digits/_/-")
    if not goal.strip():
        raise ValueError("goal is required")
    return {"schema_version": SCHEMA_VERSION, "project_id": project_id, "goal": goal,
            "phase": "DISCOVERY", "active_task_id": None, "best_valid_run_id": None,
            "evidence_refs": [], "authorization_refs": [],
            "next_action": "Define research scope and gather verifiable evidence",
            "updated_at": utcnow()}

def save_state(path: Path, state: dict) -> None:
    validate_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".state-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def load_state(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return validate_state(json.load(f))

def record_event(directory: Path, event: str, note: str) -> dict:
    if not note.strip():
        raise ValueError("nonempty note required")
    path = directory / "STATE.json"
    state = load_state(path)
    suggestion = route(state, event)
    state["phase"] = suggestion["phase"]
    state["next_action"] = suggestion["next_action"]
    state["updated_at"] = utcnow()
    save_state(path, state)
    with (directory / "EVENTS.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": state["updated_at"], "event": event,
                            "note": note, "suggestion": suggestion}, ensure_ascii=False) + "\n")
    return suggestion
