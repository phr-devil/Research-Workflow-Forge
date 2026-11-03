"""Recover one interrupted event append only after verifying its source receipt.

Conservative: a missing STATE, multiple unmatched events, corrupted artifacts,
or stale task evidence require manual recovery. Does not silently replay a Run.
"""
from __future__ import annotations
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from core.locking import file_lock
from core.receipts import fingerprint
from core.state import (_bind_task, _checked_artifact, _next_task,
                        history_status, load_state, save_state)

def _plan(project: Path) -> tuple[dict, dict | None]:
    state = load_state(project / "STATE.json")
    path = project / "EVENTS.jsonl"
    events = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []
    ids = [item.get("event_id") for item in events]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate event IDs: manual recovery required")
    last = state.get("last_event_id")
    if not events and last is None:
        return {"status": "CLEAN", "pending": 0}, None
    if last is None:
        offset = 0
    elif last in ids:
        offset = ids.index(last) + 1
    else:
        raise ValueError("State event pointer is missing from log; manual recovery required")
    pending = events[offset:]
    if not pending:
        if last != (ids[-1] if ids else None):
            raise ValueError("Cannot reconcile state and event history")
        return {"status": "CLEAN", "pending": 0}, None
    if len(pending) != 1:
        raise ValueError("Multiple pending events: manual recovery required")
    event = pending[0]
    if event.get("event") == "CHAMPION_SELECTED":
        raise ValueError("Interrupted Champion selection requires manual receipt review")
    linked = None
    if event.get("artifact_path"):
        target = (project / event["artifact_path"]).resolve()
        linked = _checked_artifact(project, event["event"], target)
        if linked[2] != event.get("artifact_sha256"):
            raise ValueError("Pending event artifact hash changed")
    if event.get("record_level") == "ARTIFACT_STRUCTURAL_ONLY" and linked is None:
        raise ValueError("Missing structural event artifact")
    if event.get("record_level") == "ROUTING_NOTE_ONLY" and linked is not None:
        raise ValueError("Note-only event unexpectedly has an artifact")
    suggestion = event.get("suggestion", {})
    if (not isinstance(suggestion, dict) or
            suggestion.get("event") != event.get("event")):
        raise ValueError("Pending event routing metadata is inconsistent")
    changed = dict(state)
    if linked is not None:
        obj, rel, sha = linked
        changed["phase"] = suggestion["phase"]
        changed["next_action"] = suggestion["next_action"]
        changed["evidence_refs"] = list(state["evidence_refs"]) + [f"{rel}@sha256:{sha}"]
        if event["event"] == "TASK_DEFINED":
            if changed.get("active_task_path"):
                raise ValueError("Cannot replay re-registration without manual review")
            _bind_task(changed, obj, rel, sha)
        elif event["event"] in {"TASK_PIVOT", "PROTOCOL_REVISED"}:
            new_task = _next_task(project, state, obj)
            _bind_task(changed, *new_task)
            changed["evidence_refs"].append(f"{new_task[1]}@sha256:{new_task[2]}")
        # No automatic Champion promotion during event recovery.
        if event["event"] == "CHAMPION_SELECTED":
            raise ValueError("Champion promotion requires explicit reconciliation")
        if event["event"] == "EXPERIMENT_PLAN_READY":
            from core.receipts import check_state_task
            task = check_state_task(project, state)
            if obj.get("task_fingerprint") != fingerprint(task):
                raise ValueError("Pending experimental plan is stale")
    changed["updated_at"], changed["last_event_id"] = event["at"], event["event_id"]
    return {"status": "REPLAYABLE_ONE_EVENT", "pending": 1,
            "event_id": event["event_id"], "event": event["event"]}, changed

def recover(project: Path, *, apply: bool = False) -> dict:
    project = project.resolve()
    with file_lock(project / ".forge-state.lock"):
        summary, reconstructed = _plan(project)
        if not apply or reconstructed is None:
            return {**summary, "applied": False}
        backup = project / ("STATE.recovery-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + ".json")
        shutil.copy2(project / "STATE.json", backup)
        save_state(project / "STATE.json", reconstructed)
        if not history_status(project)["consistent"]:
            raise RuntimeError("Recovery did not reconcile log and STATE; inspect backup")
        return {**summary, "applied": True, "state_backup": str(backup)}
