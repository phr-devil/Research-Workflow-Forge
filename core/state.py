"""Project state and attributable event history; no external research execution."""
from __future__ import annotations
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from core.contracts import SCHEMA_VERSION, ContractError, validate, validate_state
from core.router import route

# These represent structural *handoff evidence*, never scientific certification.
EVENT_KINDS = {
    "SEARCH_READY": "evidence",
    "DATA_READY": "dataset",
    "TASK_DEFINED": "task",
    "BASELINE_VALID": "run",
    "RUN_RESULT": "run",
    "NO_GAIN": "run",
    "RUN_INVALID": "run",
    "CLAIM_CANDIDATE": "claim",
    "CONFIRM_REQUEST": "claim",
}

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def initial_state(project_id: str, goal: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", project_id):
        raise ValueError("project_id must be 1-80 letters/digits/_/-")
    if not goal.strip():
        raise ValueError("goal is required")
    return {"schema_version": SCHEMA_VERSION, "project_id": project_id, "goal": goal,
            "phase": "DISCOVERY", "active_task_id": None, "best_valid_run_id": None,
            "evidence_refs": [], "authorization_refs": [], "last_event_id": None,
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

def _checked_artifact(directory: Path, event: str, artifact: Path) -> tuple[dict, str, str]:
    kind = EVENT_KINDS.get(event)
    if not kind:
        raise ValueError(f"{event} does not take an evidence artifact; route or note only")
    base = directory.resolve()
    target = artifact.resolve()
    if not target.is_relative_to(base):
        raise ValueError("artifact must live inside project directory for reproducibility")
    raw = target.read_bytes()
    if len(raw) > 2_000_000:
        raise ValueError("handoff artifact is unexpectedly large")
    obj = validate(kind, json.loads(raw.decode("utf-8")))
    if event == "TASK_DEFINED" and obj["status"] not in {"ACTIVE", "FROZEN"}:
        raise ContractError("TASK_DEFINED requires ACTIVE or FROZEN Task")
    if event == "BASELINE_VALID" and (obj["status"] != "VALID" or obj["split"] == "sealed"):
        raise ContractError("BASELINE_VALID needs actual VALID development Run")
    if event in {"RUN_RESULT", "NO_GAIN"} and obj["status"] not in {"VALID", "INCONCLUSIVE"}:
        raise ContractError(f"{event} requires VALID/INCONCLUSIVE Run; this does not prove relative gain")
    if event == "RUN_INVALID" and obj["status"] != "INVALID":
        raise ContractError("RUN_INVALID requires INVALID Run")
    if event in {"CLAIM_CANDIDATE", "CONFIRM_REQUEST"} and obj["status"] != "CANDIDATE":
        raise ContractError("claim request must refer to a candidate, not self-assert confirmation")
    return obj, target.relative_to(base).as_posix(), hashlib.sha256(raw).hexdigest()

def record_event(directory: Path, event: str, note: str, artifact: Path | None = None) -> dict:
    if not note.strip() or len(note) > 1200:
        raise ValueError("note must contain concise actual observations (1..1200 chars)")
    state_path = directory / "STATE.json"
    state = load_state(state_path)
    suggestion = route(state, event)
    linked = None
    if artifact is not None:
        linked = _checked_artifact(directory, event, artifact)
    if linked:
        candidate_task = linked[0].get("task_id")
        active_task = state.get("active_task_id")
        if candidate_task and active_task and candidate_task != active_task:
            raise ContractError("artifact task_id disagrees with active task; explicit task change required")
        if event in {"BASELINE_VALID", "RUN_RESULT", "NO_GAIN", "RUN_INVALID",
                     "CLAIM_CANDIDATE", "CONFIRM_REQUEST"} and not active_task:
            raise ContractError("cannot record a Run/Claim as project progress before an active Task is defined")
    at, event_id = utcnow(), uuid4().hex
    # Event is a user/agent-reported observation with an optional shape-checked file.
    record = {"event_id": event_id, "at": at, "event": event, "note": note,
              "record_level": "ARTIFACT_STRUCTURAL_ONLY" if linked else "ROUTING_NOTE_ONLY",
              "artifact_path": linked[1] if linked else None,
              "artifact_sha256": linked[2] if linked else None,
              "suggestion": suggestion}
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "EVENTS.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    # A note alone must not upgrade project phase or falsely certify research progress.
    if linked:
        state["phase"] = suggestion["phase"]
        state["next_action"] = suggestion["next_action"]
        state["evidence_refs"].append(f"{linked[1]}@sha256:{linked[2]}")
        obj = linked[0]
        if event == "TASK_DEFINED":
            state["active_task_id"] = obj["task_id"]
        if event == "BASELINE_VALID":
            state["best_valid_run_id"] = obj["run_id"]
    state["updated_at"] = at
    state["last_event_id"] = event_id
    save_state(state_path, state)
    return {**suggestion, "record_level": record["record_level"],
            "state_phase": state["phase"], "event_id": event_id,
            "artifact_sha256": record["artifact_sha256"]}

def history_status(directory: Path) -> dict:
    """Detect a crash between append-only event log and atomic state update."""
    state = load_state(directory / "STATE.json")
    path = directory / "EVENTS.jsonl"
    last_id = None
    if path.exists():
        with path.open(encoding="utf-8") as f:
            for row in f:
                if row.strip():
                    last_id = json.loads(row)["event_id"]
    return {"consistent": state.get("last_event_id") == last_id,
            "state_last_event_id": state.get("last_event_id"), "log_last_event_id": last_id,
            "note": "Mismatch requires manual recovery; do not silently claim restored results"}
