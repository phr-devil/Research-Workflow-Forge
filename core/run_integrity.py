"""Check raw Run evidence before any scientific Champion promotion.

Existing v0.4 structural Run files remain readable but do NOT earn VERIFIED
status without an exact, current raw-artifact digest manifest.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from core.contracts import ContractError, validate
from core.receipts import resolve_project_file

MAX_ARTIFACTS = 32
MAX_ARTIFACT_BYTES = 250_000_000

def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def validate_run_evidence(project: Path, run: dict) -> dict:
    validate("run", run)
    if run["status"] == "NOT_RUN":
        raise ContractError("NOT_RUN has no raw execution evidence")
    refs = run["artifact_refs"]
    hashes = run.get("artifact_hashes")
    if (not isinstance(hashes, dict) or not refs or set(hashes) != set(refs)
            or len(refs) > MAX_ARTIFACTS or len(refs) != len(set(refs))):
        raise ContractError("Run needs exact artifact_hashes mapping for every artifact_refs entry")
    if not any(str(ref).endswith(".json") or str(ref).endswith(".log") for ref in refs):
        raise ContractError("Run must retain a raw log or prediction JSON")
    artifacts = []
    for ref in refs:
        if not isinstance(ref, str):
            raise ContractError("artifact_ref must be a project-relative string")
        expected = hashes[ref]
        if not isinstance(expected, str) or len(expected) != 64:
            raise ContractError("artifact SHA-256 must be 64 hex characters")
        path = resolve_project_file(project, ref)
        if path.stat().st_size > MAX_ARTIFACT_BYTES:
            raise ValueError("raw Run artifact is too large for integrity check")
        observed = _sha_file(path)
        if observed.lower() != expected.lower():
            raise ContractError(f"Run artifact hash mismatch: {ref}")
        artifacts.append({"path": ref, "sha256": observed})
    return {"integrity": "RAW_ARTIFACT_HASHES_VERIFIED", "run_id": run["run_id"],
            "artifacts": artifacts,
            "limitations": "Hashes do not prove model correctness, dataset legitimacy, or independent confirmation"}

def load_verified_run(project: Path, run_path: Path) -> tuple[dict, str]:
    target = run_path.resolve()
    base = project.resolve()
    if not target.is_relative_to(base):
        raise ValueError("Run must be located under project")
    raw = target.read_bytes()
    obj = validate("run", json.loads(raw.decode("utf-8")))
    validate_run_evidence(base, obj)
    return obj, hashlib.sha256(raw).hexdigest()
