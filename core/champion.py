"""AIDE-inspired evidence-verified selection, with explicit metric direction.

A positive development score is not scientific novelty or independent effect.
"""
from __future__ import annotations
from pathlib import Path
import json
import os
from uuid import uuid4
from datetime import datetime, timezone
from core.comparison import compare_runs
from core.contracts import ContractError, validate
from core.receipts import check_state_task, resolve_project_file
from core.run_integrity import load_verified_run
from core.state import load_state, save_state
from core.locking import file_lock

def preview_champion(project: Path, candidate_path: Path) -> dict:
    state = load_state(project / "STATE.json")
    task = check_state_task(project, state)
    if task is None:
        raise ContractError("No active Task")
    candidate, candidate_sha = load_verified_run(project, candidate_path)
    if candidate["status"] != "VALID":
        raise ContractError("Only valid Runs can become Champions")
    if candidate["split"] not in {"dev", "validation"}:
        raise ContractError("Sealed runs cannot be Champions for iterative development")
    if candidate["task_id"] != task["task_id"] or candidate["protocol_id"] != task["protocol_id"]:
        raise ContractError("Candidate does not match active task/protocol")
    metric = task["metric"]
    direction = task.get("metric_direction")
    if direction not in {"maximize", "minimize"}:
        raise ContractError("Set metric_direction=maximize|minimize in ACTIVE Task before selecting Champion")
    if metric not in candidate["metrics"]:
        raise ContractError("Candidate lacks Task's specified metric")
    current_ref = state.get("best_valid_run_path")
    if not current_ref:
        decision = "FIRST_VERIFIED_CHAMPION"
        comparison = None
    else:
        existing_path = resolve_project_file(project, current_ref)
        existing, oldsha = load_verified_run(project, existing_path)
        if oldsha != state.get("best_valid_run_sha256"):
            raise ContractError("Current Champion receipt changed")
        comparison = compare_runs(existing, candidate, metric,
                                  lower_is_better=(direction == "minimize"))
        decision = "PROMOTE" if comparison["improvement_direction_delta"] > 0 else "KEEP_CURRENT"
    return {"decision": decision, "candidate": candidate["run_id"],
            "candidate_relpath": candidate_path.resolve().relative_to(project.resolve()).as_posix(),
            "candidate_sha256": candidate_sha, "comparison": comparison,
            "metric": metric, "direction": direction,
            "scientific_claim_confirmed": False}

def promote_champion(project: Path, candidate_path: Path) -> dict:
    project = project.resolve()
    with file_lock(project / ".forge-state.lock"):
        # Cannot write if event/state history is interrupted.
        from core.state import history_status
        if not history_status(project)["consistent"]:
            raise RuntimeError("State/event history inconsistent; recover first")
        result = preview_champion(project, candidate_path)
        if result["decision"] in {"FIRST_VERIFIED_CHAMPION", "PROMOTE"}:
            state = load_state(project / "STATE.json")
            at, event_id = datetime.now(timezone.utc).isoformat(), uuid4().hex
            event = {
                "event_id": event_id, "at": at, "event": "CHAMPION_SELECTED",
                "note": result["decision"] + ": raw evidence and metric direction checked",
                "record_level": "RAW_ARTIFACT_HASHES_VERIFIED",
                "artifact_path": result["candidate_relpath"],
                "artifact_sha256": result["candidate_sha256"],
                "from_task": {"task_id": state["active_task_id"], "protocol_id": state["active_protocol_id"]},
                "to_task": {"task_id": state["active_task_id"], "protocol_id": state["active_protocol_id"]},
                "suggestion": {"event": "CHAMPION_SELECTED", "phase": state["phase"],
                               "next_action": state["next_action"]},
                "selection": result,
            }
            with (project / "EVENTS.jsonl").open("a", encoding="utf-8") as log:
                log.write(json.dumps(event, ensure_ascii=False) + "\n")
                log.flush()
                os.fsync(log.fileno())
            state["best_valid_run_id"] = result["candidate"]
            state["best_valid_run_path"] = result["candidate_relpath"]
            state["best_valid_run_sha256"] = result["candidate_sha256"]
            state["last_event_id"], state["updated_at"] = event_id, at
            save_state(project / "STATE.json", state)
        return result
