"""Input/output fingerprints and source receipts, adapted from ResearchStudio.

Receipts establish structural provenance, not scientific truth or consent.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def fingerprint(obj: dict) -> str:
    return digest_bytes(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8"))

def fingerprint_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())

def resolve_project_file(project: Path, rel: str) -> Path:
    base = project.resolve()
    if not rel or Path(rel).is_absolute():
        raise ValueError("Expected nonempty project-relative path")
    target = (base / rel).resolve()
    if target == base or not target.is_relative_to(base):
        raise ValueError("Artifact escapes project directory")
    return target

def check_receipt(path: Path, expected_sha256: str) -> None:
    if fingerprint_file(path) != expected_sha256:
        raise ValueError(f"Input artifact changed since last accepted receipt: {path.name}")

def check_state_task(project: Path, state: dict) -> dict | None:
    rel = state.get("active_task_path")
    if not rel:
        if state.get("active_task_id"):
            raise ValueError("Active task is missing a versioned TaskSpec; re-register TASK_DEFINED")
        return None
    task_file = resolve_project_file(project, rel)
    check_receipt(task_file, state["active_task_sha256"])
    from core.contracts import validate
    task = validate("task", json.loads(task_file.read_text(encoding="utf-8")))
    if (task.get("task_id") != state.get("active_task_id") or
            task.get("protocol_id") != state.get("active_protocol_id") or
            fingerprint(task) != state.get("active_task_fingerprint")):
        raise ValueError("Active TaskSpec no longer matches state receipt")
    return task
