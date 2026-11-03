"""Read-only AIDE-inspired candidate lineage from original project event receipts.

Does not select a scientific winner, execute code, or train a model.
"""
from __future__ import annotations
import json
from pathlib import Path

from core.contracts import validate
from core.receipts import check_receipt, resolve_project_file
from core.state import load_state

def candidate_journal(project: Path) -> dict:
    state = load_state(project / "STATE.json")
    target_task = state.get("active_task_id")
    target_protocol = state.get("active_protocol_id")
    records, warnings = [], []
    log = project / "EVENTS.jsonl"
    if not log.exists():
        return {"active_task_id": target_task, "runs": [], "warnings": []}
    for row in log.read_text(encoding="utf-8").splitlines():
        if not row.strip():
            continue
        event = json.loads(row)
        if event.get("event") not in {"BASELINE_VALID", "RUN_RESULT", "NO_GAIN", "RUN_INVALID"}:
            continue
        rel, sha = event.get("artifact_path"), event.get("artifact_sha256")
        if not rel or not sha:
            warnings.append(f"{event['event_id']}: note-only, not run evidence")
            continue
        try:
            file = resolve_project_file(project, rel)
            check_receipt(file, sha)
            run = validate("run", json.loads(file.read_text(encoding="utf-8")))
            is_active = (run["task_id"] == target_task and run["protocol_id"] == target_protocol)
            records.append({"run_id": run["run_id"], "event_id": event["event_id"],
                            "task_id": run["task_id"], "protocol_id": run["protocol_id"],
                            "status": run["status"], "split": run["split"],
                            "metrics": run["metrics"], "artifact": rel,
                            "current_protocol": is_active,
                            "parent_run_id": run.get("parent_run_id"),
                            "branch_kind": run.get("branch_kind", "UNSPECIFIED")})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            warnings.append(f"{event['event_id']}: unusable run receipt ({type(exc).__name__})")
    return {"active_task_id": target_task, "active_protocol_id": target_protocol,
            "runs": records, "warnings": warnings,
            "notes": "Old and negative runs are retained; no automatic scientific novelty ranking"}
