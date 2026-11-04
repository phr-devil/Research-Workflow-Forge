"""Read-only streamed SHA-256 verification for externally produced DEV artifacts.

This is not a model runner or scientific evaluator. It does not bypass the
size/manifest/holdout limits of the normal Forge DEV metric verifier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from core.contracts import ContractError

MAX_FILES = 32
CHUNK_BYTES = 1024 * 1024
KINDS = {"source", "predictions", "log", "checkpoint", "configuration"}


def verify_external_artifacts(project: Path, manifest: dict) -> dict:
    """Verify project-contained files and expected hashes without loading RAM."""
    if not isinstance(manifest, dict) or manifest.get("split") not in {"dev", "validation"}:
        raise ContractError("Only an explicitly declared DEV/validation artifact manifest is permitted")
    entries = manifest.get("artifacts")
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_FILES:
        raise ContractError("artifacts must be a nonempty list of at most 32 records")
    root = project.resolve(strict=True)
    if not root.is_dir():
        raise ContractError("project must be a directory")
    observed = []
    unique = set()
    for row in entries:
        if not isinstance(row, dict):
            raise ContractError("artifact entry must be an object")
        rel, kind, expected = row.get("path"), row.get("kind"), row.get("sha256")
        if not isinstance(rel, str) or not rel.strip():
            raise ContractError("artifact needs a path")
        p = Path(rel)
        if p.is_absolute() or ".." in p.parts:
            raise ContractError("Only project-relative, non-traversing artifact paths allowed")
        if kind not in KINDS:
            raise ContractError("unsupported artifact kind")
        if not isinstance(expected, str) or len(expected) != 64 or any(
            c not in "0123456789abcdefABCDEF" for c in expected
        ):
            raise ContractError("expected SHA-256 must be exactly 64 hexadecimal characters")
        path = (root / p).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ContractError("artifact must exist inside project; symlink escapes denied")
        canonical = path.relative_to(root).as_posix()
        if canonical in unique:
            raise ContractError("duplicate artifact path")
        unique.add(canonical)
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(CHUNK_BYTES), b""):
                h.update(chunk)
        actual = h.hexdigest()
        if actual.lower() != expected.lower():
            raise ContractError("external artifact hash mismatch: " + canonical)
        observed.append({"path": canonical, "kind": kind, "bytes": path.stat().st_size,
                         "sha256": actual})
    return {"status": "ARTIFACT_HASHES_VERIFIED_ONLY", "split": manifest["split"],
            "artifacts": observed, "scientific_confirmation": False,
            "metric_verification": False, "training_execution_attested": False,
            "note": "External training origin, legal data, protected split and metrics "
                    "require separate original user authorization and DEV evaluation."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True,
                        help="read-only expected hashes for project-local DEV output files")
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    print(json.dumps(verify_external_artifacts(args.project, payload),
                     indent=2, ensure_ascii=False))
