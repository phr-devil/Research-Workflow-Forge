"""Bounded, explicitly authorized CPU DEV baseline/Challenger execution.

NOT a general-purpose coding-agent sandbox. No user code, shell, network,
GPU, sealed/test datasets or external actions are executed. sklearn fits are
opt-in, train-only preprocessing, group-disjoint development evaluation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from core.contracts import ContractError, validate
from core.data_access import bind_dev_dataset
from core.receipts import check_state_task, fingerprint_file
from core.metric_verify import FORMAT, sample_hash
from core.run_integrity import validate_run_evidence
from core.state import load_state

MODELS = {"dummy", "logistic", "forest"}
VERSION = "forge-grouped-development-v0.5"
MAX_ROWS, MAX_FEATURES = 10000, 64

def _model(name: str):
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    if name == "dummy":
        return DummyClassifier(strategy="most_frequent")
    if name == "logistic":
        return make_pipeline(SimpleImputer(strategy="median"),
                             StandardScaler(),
                             LogisticRegression(max_iter=400, random_state=42, class_weight="balanced"))
    if name == "forest":
        return make_pipeline(SimpleImputer(strategy="median"),
                             RandomForestClassifier(n_estimators=64, max_depth=8, n_jobs=1,
                                                    random_state=42, class_weight="balanced"))
    raise ValueError("Model outside the constrained allowlist")

def fit_development(project: Path, manifest_file: Path, dataset_id: str,
                    run_id: str, model: str, *,
                    explicit_cpu_fit: bool = False,
                    parent_run_id: str | None = None) -> dict:
    if not explicit_cpu_fit:
        raise PermissionError("CPU fitting denied; requires explicit --allow-cpu-fit and actual user authorization")
    if model not in MODELS:
        raise ValueError("Choose a supported model: dummy, logistic, forest")
    if not run_id.isascii() or not run_id.replace("-", "").replace("_", "").isalnum() or len(run_id) > 64:
        raise ValueError("run_id must be ASCII alphanumeric plus underscore/hyphen, <=64 chars")
    project = project.resolve()
    task = check_state_task(project, load_state(project / "STATE.json"))
    if task is None or task["status"] not in {"ACTIVE", "FROZEN"}:
        raise ContractError("Runner needs an active, SHA-matched Task")
    manifest_file = manifest_file.resolve()
    dataset_path, ds = bind_dev_dataset(project, manifest_file, dataset_id, purpose="FIT_DEV")
    label_col, group_col = ds.get("label_column"), ds.get("group_column")
    features = ds.get("feature_columns")
    if not (isinstance(label_col, str) and label_col and
            isinstance(group_col, str) and group_col and
            isinstance(features, list) and 1 <= len(features) <= MAX_FEATURES and
            all(isinstance(c, str) and c for c in features) and len(set(features)) == len(features)):
        raise ContractError("Manifest needs label_column, group_column, unique numeric feature_columns (1..64)")
    if set(features) & {label_col, group_col} or label_col == group_col:
        raise ContractError("Feature leakage: group/label cannot be predictor")
    if not set(features).issubset(set(task["legal_inputs"])):
        raise ContractError("Predictors must be explicitly allowed by active TaskSpec")
    if parent_run_id:
        from core.journal import candidate_journal
        from core.run_integrity import load_verified_run
        from core.receipts import resolve_project_file
        parents = [r for r in candidate_journal(project)["runs"]
                   if r["run_id"] == parent_run_id and r["current_protocol"]]
        if len(parents) != 1:
            raise ContractError("Parent Run must be uniquely present in current Journal")
        parent, _ = load_verified_run(project, resolve_project_file(project, parents[0]["artifact"]))
        if parent["task_id"] != task["task_id"] or parent["protocol_id"] != task["protocol_id"]:
            raise ContractError("Parent Run belongs to a different Task/protocol")
        if parent["dataset_version"] != ds["sha256"]:
            raise ContractError("Parent Run used a different dataset version")
    rows = []
    with dataset_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        needed = set(features + [label_col, group_col])
        if not reader.fieldnames or not needed.issubset(set(reader.fieldnames)):
            raise ContractError("DEV CSV missing required columns")
        for row in reader:
            if len(rows) >= MAX_ROWS:
                raise ValueError("DEV CSV exceeds bounded CPU fitting limit")
            group, y = (row.get(group_col) or "").strip(), (row.get(label_col) or "").strip()
            if not group or not y:
                raise ContractError("Missing group/label")
            x = []
            for name in features:
                value = (row.get(name) or "").strip()
                try:
                    z = float(value) if value else float("nan")
                except ValueError as exc:
                    raise ContractError("Non-numeric predictor, use prevalidated numeric DEV columns") from exc
                if math.isinf(z):
                    raise ContractError("Infinite predictor value")
                x.append(z)
            rows.append((group, y, x))
    if len(rows) < 12 or len({r[0] for r in rows}) < 4:
        raise ContractError("At least 12 DEV rows and 4 independent groups required")
    from sklearn.metrics import f1_score, balanced_accuracy_score
    from sklearn.model_selection import GroupShuffleSplit
    import sklearn
    groups = [r[0] for r in rows]
    X = [r[2] for r in rows]
    y = [r[1] for r in rows]
    splits = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train_idx, test_idx = next(splits.split(X, y, groups))
    train_idx, test_idx = [int(i) for i in train_idx], [int(i) for i in test_idx]
    if set(groups[i] for i in train_idx) & set(groups[i] for i in test_idx):
        raise AssertionError("Group split leakage")
    if len(set(y[i] for i in train_idx)) < 2 or len(set(y[i] for i in test_idx)) < 2:
        raise ContractError("Group split has insufficient class coverage; do not silently resample")
    clf = _model(model)
    clf.fit([X[i] for i in train_idx], [y[i] for i in train_idx])
    pred = [str(p) for p in clf.predict([X[i] for i in test_idx])]
    truth = [y[i] for i in test_idx]
    macro = float(f1_score(truth, pred, average="macro", zero_division=0))
    bal = float(balanced_accuracy_score(truth, pred))
    predictions = [{"row_index": i, "group": groups[i], "truth": truth[j],
                    "prediction": pred[j]} for j, i in enumerate(test_idx)]
    metrics = {"macro_F1": macro, "balanced_accuracy": bal}
    sample_col = ds.get("sample_id_column")
    if sample_col:
        with dataset_path.open(encoding="utf-8-sig", newline="") as source:
            identifiers = [row.get(sample_col,"").strip() for row in csv.DictReader(source)]
        if len(identifiers) != len(rows) or not all(identifiers) or len(set(identifiers)) != len(identifiers):
            raise ContractError("DEV sample IDs missing/duplicated")
        samples = [identifiers[i] for i in test_idx]
        for row, idx in zip(predictions, test_idx):
            row["sample_id"] = identifiers[idx]
    else:
        samples = test_idx
    sample_fingerprint = sample_hash(samples)
    runner_sha = fingerprint_file(Path(__file__))
    # No arbitrary or LLM-supplied commands may be executed by this runner.
    try:
        manifest_ref = manifest_file.relative_to(project).as_posix()
    except ValueError as exc:
        raise ContractError("Manifest must be under project root for verifiable run receipts") from exc
    record = {
        "schema_version": "0.1", "run_id": run_id,
        "task_id": task["task_id"], "protocol_id": task["protocol_id"],
        "dataset_version": ds["sha256"], "code_commit": "source-sha256:" + runner_sha,
        "evaluator_version": "forge-metric-verify-v1:" + fingerprint_file(Path(__file__).resolve().parents[1]/"core"/"metric_verify.py")[:12], "split": "dev",
        "status": "VALID", "metrics": metrics,
        "group_split": f"group-shuffle:{group_col}:seed=42:test=0.25",
        "sample_ids_hash": sample_fingerprint, "legal_inputs": features,
        "artifact_refs": [], "artifact_hashes": {},
        "metric_spec": {"format": FORMAT, "predictions_ref": f"runs/{run_id}/predictions.json",
                        "manifest_ref": manifest_ref, "manifest_sha256": fingerprint_file(manifest_file),
                        "dataset_id": dataset_id},
        "branch_kind": "IMPROVE" if parent_run_id else "DRAFT",
        "parent_run_id": parent_run_id, "model_family": model,
        "authorization": "CLI_FLAG_ONLY_NOT_USER_PERMISSION",
        "task_fingerprint": __import__("core.receipts", fromlist=["fingerprint"]).fingerprint(task)
    }
    output_dir = project / "runs" / run_id
    if output_dir.exists():
        raise FileExistsError("Run ID already exists; raw results are immutable")
    output_dir.mkdir(parents=True, exist_ok=False)
    def save_artifact(name: str, value: object) -> None:
        rel = f"runs/{run_id}/{name}"
        file = project / rel
        file.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        record["artifact_refs"].append(rel)
        record["artifact_hashes"][rel] = fingerprint_file(file)
    save_artifact("predictions.json", predictions)
    save_artifact("fit_log.json", {
        "model": model, "dataset_id": dataset_id, "manifest_sha256": fingerprint_file(manifest_file),
        "dataset_sha256": ds["sha256"], "task_id": task["task_id"],
        "task_fingerprint": record["task_fingerprint"],
        "model_parameters_repr": repr(clf.get_params(deep=False)),
        "train_groups": sorted({groups[i] for i in train_idx}),
        "test_groups": sorted({groups[i] for i in test_idx}),
        "n_train": len(train_idx), "n_test": len(test_idx),
        "sklearn_version": sklearn.__version__,
        "at": datetime.now(timezone.utc).isoformat(),
        "result_scope": "DEVELOPMENT_PILOT_NOT_PAPER_EVIDENCE"
    })
    validate("run", record)
    validate_run_evidence(project, record)
    run_path = output_dir / "RUN.json"
    run_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"run_path": str(run_path), "metrics": metrics,
            "raw_evidence": record["artifact_refs"],
            "group_disjoint": True, "sealed_data_accessed": False,
            "research_claim_confirmed": False}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Optional bounded CPU DEV grouped pilot, not general code execution")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model", choices=sorted(MODELS), required=True)
    parser.add_argument("--parent-run-id")
    parser.add_argument("--allow-cpu-fit", action="store_true",
                        help="Operator opt-in ONLY; agent must separately verify actual user permission")
    args = parser.parse_args(argv)
    try:
        result = fit_development(args.project, args.manifest, args.dataset_id,
                                 args.run_id, args.model,
                                 explicit_cpu_fit=args.allow_cpu_fit,
                                 parent_run_id=args.parent_run_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, RuntimeError, ValueError, PermissionError, ImportError) as exc:
        parser.exit(2, f"DEV fitting failed: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
