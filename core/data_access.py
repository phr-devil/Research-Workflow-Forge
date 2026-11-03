"""Manifest-bound DEV access; no sealed files are read, even for hashing.

This is a cooperative safety boundary for Forge tools, NOT a security sandbox.
Arbitrary user programs and third-party agents must be separately restricted.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from core.contracts import ContractError, validate
from core.locking import file_lock
from core.receipts import fingerprint

PURPOSES = {"AUDIT_DEV", "FIT_DEV", "EVALUATE_DEV", "INSPECT_DEV"}
MAX_DATA_BYTES = 200_000_000

def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def bind_dev_dataset(project: Path, manifest_path: Path, dataset_id: str, *,
                     purpose: str, record_access: bool = True) -> tuple[Path, dict]:
    """Validate declared role/path/hash, then read ONLY declared DEV dataset.

    The manifest may contain absolute user-owned paths so datasets need not be
    copied into the project. Never inspect a declared sealed path for a digest.
    """
    if purpose not in PURPOSES:
        raise ValueError("Invalid development-only access purpose")
    project = project.resolve()
    manifest_path = manifest_path.resolve()
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = validate("dataset", json.loads(manifest_path.read_text(encoding="utf-8")))
    rows = manifest["datasets"]
    if len([x for x in rows if x["dataset_id"] == dataset_id]) != 1:
        raise ContractError("dataset_id missing or duplicated in manifest")
    entry = next(x for x in rows if x["dataset_id"] == dataset_id)
    if entry["role"] != "DEV":
        raise PermissionError("Only DEV data may be accessed by this tool")
    if purpose == "FIT_DEV" and entry["label_status"] != "VERIFIED":
        raise ContractError("FIT_DEV requires verified labels")
    raw = entry.get("local_path")
    sha = entry.get("sha256")
    if not isinstance(raw, str) or not raw.strip() or not isinstance(sha, str) or len(sha) != 64:
        raise ContractError("DEV dataset requires an explicit local_path and SHA-256")
    path = Path(raw).expanduser()
    path = (path if path.is_absolute() else project / path).resolve()
    if not path.is_file():
        raise FileNotFoundError("DEV file is not present at manifest path")
    if any(
        x["role"] != "DEV" and x.get("local_path") and
        (Path(x["local_path"]).expanduser() if Path(x["local_path"]).is_absolute()
         else project / x["local_path"]).resolve() == path
        for x in rows
    ):
        raise PermissionError("File path aliases a non-DEV dataset")
    if any(x["role"] == "SEALED_CONFIRM" and x.get("sha256", "").lower() == sha.lower() for x in rows):
        raise PermissionError("DEV digest aliases a SEALED_CONFIRM dataset")
    if path.stat().st_size > MAX_DATA_BYTES:
        raise ValueError("DEV file exceeds v0.5 preflight limit")
    # Access is logged before hashing/opening the DEV file.
    if record_access:
        with file_lock(project / ".forge-data-access.lock"):
            with (project / "DATA_ACCESS.jsonl").open("a", encoding="utf-8") as log:
                log.write(json.dumps({
                    "at": datetime.now(timezone.utc).isoformat(),
                    "dataset_id": dataset_id, "purpose": purpose,
                    "manifest_fingerprint": fingerprint(manifest),
                    "local_path": str(path), "declared_sha256": sha,
                    "status": "ATTEMPTED_DEV_ACCESS",
                }, ensure_ascii=False) + "\n")
    observed = _sha_file(path)
    if observed.lower() != sha.lower():
        raise ValueError("DEV dataset hash mismatch; no results may be trusted")
    return path, dict(entry)
