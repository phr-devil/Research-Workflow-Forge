"""Read-only PD-RW handoff: attest *same raw predictions* using Forge's DEV verifier.

This is not a Python package import of PD-RW (both repositories have a 'core'
package). Never train or open sealed data; never infer causal execution or novelty.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from core.contracts import ContractError
from core.receipts import resolve_project_file
from core.run_integrity import load_verified_run

REQUIRED_SAME = (
    "task_id", "protocol_id", "dataset_version", "evaluator_version",
    "split", "group_split", "sample_ids_hash",
)
LEGAL_CONDITIONS = (
    "level_id", "k_unit", "support_query_policy",
    "k_target_labels", "inference_visible_info",
)


def _inside(root: Path, path: Path | str) -> Path:
    root = root.resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ContractError("PD-RW source path missing or outside authorized root")
    return target


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def verify_pd_rw_handoff(
    forge_project: Path, forge_run_path: Path, pd_root: Path,
    pd_run_path: Path, metric: str,
) -> dict:
    """Trust Forge's re-evaluation, then check PD points to the *same* samples."""
    forge_project, pd_root = forge_project.resolve(), pd_root.resolve()
    pd_path = _inside(pd_root, pd_run_path)
    pd = json.loads(pd_path.read_text(encoding="utf-8"))
    if not isinstance(pd, dict):
        raise ContractError("PD-RW Run must be an object")
    forge_path = (forge_run_path if forge_run_path.is_absolute()
                  else forge_project / forge_run_path)
    forge, forge_sha = load_verified_run(forge_project, forge_path)
    if any(r.get("status") != "VALID" or r.get("split") not in {"dev", "validation"}
           for r in (pd, forge)):
        raise ContractError("Only VALID development Runs can be verified")
    mismatches = [key for key in REQUIRED_SAME if not pd.get(key)
                  or pd.get(key) != forge.get(key)]
    if sorted(pd.get("legal_inputs", [])) != sorted(forge.get("legal_inputs", [])):
        mismatches.append("legal_inputs")
    for key in LEGAL_CONDITIONS:
        if pd.get(key) != forge.get(key):
            mismatches.append(key)
    if mismatches:
        raise ContractError("NOT_COMPARABLE: " + ", ".join(mismatches))
    pd_metrics = pd.get("metrics")
    if not isinstance(pd_metrics, dict) or not isinstance(forge.get("metrics"), dict):
        raise ContractError("missing metrics")
    a, b = pd_metrics.get(metric), forge["metrics"].get(metric)
    if (isinstance(a, bool) or isinstance(b, bool)
            or not isinstance(a, (int, float)) or not isinstance(b, (int, float))
            or not math.isfinite(a) or not math.isfinite(b)
            or not math.isclose(a, b, rel_tol=0, abs_tol=1e-6)):
        raise ContractError("RECOMPUTED_METRIC_MISMATCH: " + metric)
    refs = pd.get("artifact_refs")
    spec = forge.get("metric_spec")
    if not isinstance(refs, dict) or not isinstance(spec, dict):
        raise ContractError("missing raw prediction references")
    pd_prediction = refs.get("predictions")
    forge_prediction = spec.get("predictions_ref")
    if not isinstance(pd_prediction, str) or not isinstance(forge_prediction, str):
        raise ContractError("missing raw prediction references")
    pred_pd = _inside(pd_root, pd_prediction)
    pred_forge = resolve_project_file(forge_project, forge_prediction)
    if _sha(pred_pd) != _sha(pred_forge):
        raise ContractError("PREDICTION_BYTES_MISMATCH: PD-RW and Forge need identical raw predictions")
    return {
        "status": "METRIC_VERIFIED_DEV_ONLY",
        "pd_run_sha256": _sha(pd_path),
        "forge_run_sha256": forge_sha,
        "prediction_sha256": _sha(pred_pd),
        "metric": metric,
        "recomputed_value": b,
        "protocol_field_coverage": (
            "FULL" if all(k in pd and k in forge for k in LEGAL_CONDITIONS)
            else "PARTIAL_LEGACY"),
        "limitations": "DEV arithmetic verified; legal training provenance, future-input causality, fairness, novelty and independent confirmation NOT verified",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Independently verify a PD-RW DEV Run via RWF")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--forge-run", type=Path, required=True)
    parser.add_argument("--pd-root", type=Path, required=True)
    parser.add_argument("--pd-run", type=Path, required=True)
    parser.add_argument("--metric", required=True)
    args = parser.parse_args(argv)
    try:
        result = verify_pd_rw_handoff(
            args.project, args.forge_run, args.pd_root, args.pd_run, args.metric)
    except (ContractError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"PD-RW handoff verification failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
