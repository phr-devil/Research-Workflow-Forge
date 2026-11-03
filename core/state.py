"""Evidence-linked task state, scoped pivots, and append-only event history."""
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
from core.locking import file_lock
from core.receipts import check_receipt, check_state_task, fingerprint, resolve_project_file
from core.router import route

EVENT_KINDS = {
    "SEARCH_READY": "evidence",
    "DATA_READY": "dataset",
    "NOVELTY_PRECHECK_READY": "novelty",
    "TASK_DEFINED": "task",
    "TASK_PIVOT": "decision",
    "PROTOCOL_REVISED": "decision",
    "EXPERIMENT_PLAN_READY": "experiment",
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
            "phase": "DISCOVERY", "active_task_id": None, "active_protocol_id": None,
            "active_task_path": None, "active_task_sha256": None,
            "active_task_fingerprint": None, "best_valid_run_id": None,
            "evidence_refs": [], "authorization_refs": [], "last_event_id": None,
            "next_action": "Define research scope and gather verifiable evidence",
            "updated_at": utcnow()}

def save_state(path: Path, state: dict) -> None:
    validate_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".state-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def load_state(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return validate_state(json.load(f))

def _checked_artifact(directory: Path, event: str, artifact: Path) -> tuple[dict, str, str]:
    kind = EVENT_KINDS.get(event)
    if not kind:
        raise ValueError(f"{event} does not take an artifact; route or note only")
    base = directory.resolve()
    target = artifact.resolve()
    if target == base or not target.is_relative_to(base):
        raise ValueError("artifact must live inside project directory")
    raw = target.read_bytes()
    if len(raw) > 2_000_000:
        raise ValueError("handoff artifact is unexpectedly large")
    obj = validate(kind, json.loads(raw.decode("utf-8")))
    if event == "EXPERIMENT_PLAN_READY" and obj.get("status") != "PLAN_ONLY":
        raise ContractError("EXPERIMENT_PLAN_READY requires non-executed PLAN_ONLY")
    if event == "TASK_DEFINED" and obj["status"] not in {"ACTIVE", "FROZEN"}:
        raise ContractError("TASK_DEFINED requires ACTIVE or FROZEN Task")
    if event == "BASELINE_VALID" and (obj["status"] != "VALID" or obj["split"] == "sealed"):
        raise ContractError("BASELINE_VALID needs VALID development Run")
    if event in {"RUN_RESULT", "NO_GAIN"} and obj["status"] not in {"VALID", "INCONCLUSIVE"}:
        raise ContractError(f"{event} needs VALID/INCONCLUSIVE Run; not proof of gain")
    if event == "RUN_INVALID" and obj["status"] != "INVALID":
        raise ContractError("RUN_INVALID requires INVALID Run")
    if event in {"CLAIM_CANDIDATE", "CONFIRM_REQUEST"} and obj["status"] != "CANDIDATE":
        raise ContractError("claim request must be CANDIDATE")
    if event in {"TASK_PIVOT", "PROTOCOL_REVISED"} and obj["decision_type"] != event:
        raise ContractError("decision_type does not match transition event")
    return obj, target.relative_to(base).as_posix(), hashlib.sha256(raw).hexdigest()

def _next_task(directory: Path, state: dict, decision: dict) -> tuple[dict, str, str]:
    if not state.get("active_task_id"):
        raise ContractError("transition needs an existing active Task")
    if (decision["from_task_id"] != state["active_task_id"] or
            decision["from_protocol_id"] != state.get("active_protocol_id")):
        raise ContractError("decision refers to stale task or protocol")
    new_path = resolve_project_file(directory, decision["new_task_path"])
    check_receipt(new_path, decision["new_task_sha256"])
    new = validate("task", json.loads(new_path.read_text(encoding="utf-8")))
    if new["status"] not in {"ACTIVE", "FROZEN"}:
        raise ContractError("transition target must be ACTIVE/FROZEN Task")
    if new["task_id"] != decision["to_task_id"] or new["protocol_id"] != decision["to_protocol_id"]:
        raise ContractError("target TaskSpec mismatches decision")
    if decision["decision_type"] == "TASK_PIVOT" and new["task_id"] == state["active_task_id"]:
        raise ContractError("TASK_PIVOT needs a different task_id")
    if decision["decision_type"] == "PROTOCOL_REVISED" and (
        new["task_id"] != state["active_task_id"] or
        new["protocol_id"] == state["active_protocol_id"]):
        raise ContractError("PROTOCOL_REVISED must retain task_id and change protocol_id")
    return new, new_path.relative_to(directory.resolve()).as_posix(), decision["new_task_sha256"]

def _bind_task(state: dict, task: dict, path: str, sha: str) -> None:
    state["active_task_id"] = task["task_id"]
    state["active_protocol_id"] = task["protocol_id"]
    state["active_task_path"] = path
    state["active_task_sha256"] = sha
    state["active_task_fingerprint"] = fingerprint(task)
    # History remains in EVENTS, but a changed protocol must not carry a Champion.
    state["best_valid_run_id"] = None
    state["best_valid_run_path"] = None
    state["best_valid_run_sha256"] = None

def history_status(directory: Path) -> dict:
    state = load_state(directory / "STATE.json")
    log = directory / "EVENTS.jsonl"
    last_id = None
    if log.exists():
        with log.open(encoding="utf-8") as f:
            for row in f:
                if row.strip():
                    last_id = json.loads(row)["event_id"]
    valid = state.get("last_event_id") == last_id
    return {"consistent": valid, "state_last_event_id": state.get("last_event_id"),
            "log_last_event_id": last_id,
            "note": "Mismatch needs recovery before new events; do not silently overwrite history"}

def record_event(directory: Path, event: str, note: str, artifact: Path | None = None) -> dict:
    if not note.strip() or len(note) > 1200:
        raise ValueError("note must contain observations (1..1200 chars)")
    with file_lock(directory / ".forge-state.lock"):
        state_path = directory / "STATE.json"
        state = load_state(state_path)
        if not history_status(directory)["consistent"]:
            raise RuntimeError("Event log and STATE disagree; recover before recording new evidence")
        suggestion = route(state, event)
        linked = _checked_artifact(directory, event, artifact) if artifact is not None else None
        next_task = None
        current = {"task_id": state.get("active_task_id"),
                   "protocol_id": state.get("active_protocol_id")}
        if linked:
            obj, rel, sha = linked
            if event in {"BASELINE_VALID", "RUN_RESULT", "NO_GAIN", "RUN_INVALID"}:
                from core.run_integrity import validate_run_evidence
                validate_run_evidence(directory, obj)
            proposed = obj.get("task_id")
            if proposed and state.get("active_task_id") and proposed != state["active_task_id"]:
                raise ContractError("artifact task_id disagrees with active task; explicit task change required")
            if event == "TASK_DEFINED":
                if state.get("active_task_id"):
                    if obj["task_id"] != state["active_task_id"]:
                        raise ContractError("Existing task differs: use TASK_PIVOT")
                    # Upgrade pre-v0.4 STATE records by explicitly re-registering
                    # the original Task. Old Champion cannot survive this migration.
                    if state.get("active_task_path"):
                        bound = check_state_task(directory, state)
                        if fingerprint(bound) != fingerprint(obj):
                            raise ContractError("Existing task differs: use PROTOCOL_REVISED")
            elif event in {"TASK_PIVOT", "PROTOCOL_REVISED"}:
                check_state_task(directory, state)
                next_task = _next_task(directory, state, obj)
            elif event in {"NOVELTY_PRECHECK_READY", "EXPERIMENT_PLAN_READY",
                           "BASELINE_VALID", "RUN_RESULT", "NO_GAIN", "RUN_INVALID",
                           "CLAIM_CANDIDATE", "CONFIRM_REQUEST"}:
                if not state.get("active_task_id"):
                    raise ContractError("cannot record a Run/Claim as project progress before an active Task is defined")
                task = check_state_task(directory, state)
                if proposed and proposed != task["task_id"]:
                    raise ContractError("artifact task_id disagrees with active task")
                if event in {"EXPERIMENT_PLAN_READY", "BASELINE_VALID",
                             "RUN_RESULT", "NO_GAIN", "RUN_INVALID"}:
                    if obj.get("protocol_id") != task["protocol_id"]:
                        raise ContractError("artifact protocol_id mismatches active Task")
                    if event == "EXPERIMENT_PLAN_READY" and obj.get("task_fingerprint") != fingerprint(task):
                        raise ContractError("stale experimental plan: Task changed after planning")
                if event == "NOVELTY_PRECHECK_READY":
                    if obj["input_fingerprints"]["task"] != fingerprint(task):
                        raise ContractError("stale novelty review: Task changed")
            # SEARCH_READY/DATA_READY have no current-task requirement.

        at, event_id = utcnow(), uuid4().hex
        after = ({"task_id": next_task[0]["task_id"], "protocol_id": next_task[0]["protocol_id"]}
                 if next_task else ({"task_id": linked[0]["task_id"], "protocol_id": linked[0]["protocol_id"]}
                                     if linked and event == "TASK_DEFINED" else current))
        record = {"event_id": event_id, "at": at, "event": event, "note": note,
                  "record_level": "ARTIFACT_STRUCTURAL_ONLY" if linked else "ROUTING_NOTE_ONLY",
                  "artifact_path": linked[1] if linked else None,
                  "artifact_sha256": linked[2] if linked else None,
                  "from_task": current, "to_task": after, "suggestion": suggestion}
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "EVENTS.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        if linked:
            state["phase"] = suggestion["phase"]
            state["next_action"] = suggestion["next_action"]
            state["evidence_refs"].append(f"{linked[1]}@sha256:{linked[2]}")
            if event == "TASK_DEFINED" and not state.get("active_task_path"):
                _bind_task(state, linked[0], linked[1], linked[2])
            elif next_task:
                _bind_task(state, *next_task)
                state["evidence_refs"].append(f"{next_task[1]}@sha256:{next_task[2]}")
        state["updated_at"], state["last_event_id"] = at, event_id
        save_state(state_path, state)
        return {**suggestion, "record_level": record["record_level"],
                "state_phase": state["phase"], "event_id": event_id,
                "artifact_sha256": record["artifact_sha256"]}
