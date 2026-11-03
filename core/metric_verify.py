"""Independently recompute classification metrics against manifest-bound DEV truth.

The labels are loaded from a SHA-pinned DEV CSV, NOT from the Run author's
prediction JSON. This is a cooperative integrity verifier, not an OS sandbox.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
from core.contracts import ContractError
from core.data_access import bind_dev_dataset
from core.receipts import check_receipt, resolve_project_file

FORMAT = "forge-dev-classification-v1"
MAX_PREDICTIONS = 50000
SUPPORTED = {"macro_F1", "balanced_accuracy"}

def sample_hash(ids: list[object]) -> str:
    return hashlib.sha256(json.dumps(sorted(ids), ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()

def _scores(truth: list[str], predictions: list[str], labels: list[str]) -> dict:
    # Same mathematical definition as sklearn's macro F1 and balanced accuracy
    # (for finite classification labels; zero_division=0).
    f1, recalls = [], []
    for label in labels:
        tp=sum(y==label and p==label for y,p in zip(truth,predictions))
        fp=sum(y!=label and p==label for y,p in zip(truth,predictions))
        fn=sum(y==label and p!=label for y,p in zip(truth,predictions))
        f1.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.0)
        if tp+fn:
            recalls.append(tp/(tp+fn))
    return {"macro_F1": sum(f1)/len(f1), "balanced_accuracy": sum(recalls)/len(recalls)}

def verify_metrics(project: Path, run: dict, *, check_reported: bool = True) -> dict:
    spec=run.get("metric_spec")
    if isinstance(spec,dict) and spec.get("format") in {"forge-dev-regression-v1", "forge-dev-event-v1"}:
        from core.metric_extensions import verify_extended_metrics
        return verify_extended_metrics(project,run,check_reported=check_reported)
    if not isinstance(spec,dict) or spec.get("format")!=FORMAT:
        raise ContractError("Run metrics UNRECOMPUTED: missing trusted metric_spec")
    required=("predictions_ref", "manifest_ref", "manifest_sha256", "dataset_id")
    for k in required:
        if not isinstance(spec.get(k),str) or not spec[k].strip():
            raise ContractError("metric_spec missing " + k)
    manifest_path=resolve_project_file(project,spec["manifest_ref"])
    check_receipt(manifest_path,spec["manifest_sha256"])
    data_path,ds=bind_dev_dataset(project,manifest_path,spec["dataset_id"],purpose="EVALUATE_DEV")
    if ds["sha256"].lower()!=run["dataset_version"].lower():
        raise ContractError("Run dataset version disagrees with independently loaded DEV dataset")
    if spec["predictions_ref"] not in run["artifact_refs"]:
        raise ContractError("predictions_ref is not a hashed raw Run artifact")
    pred_path=resolve_project_file(project,spec["predictions_ref"])
    raw=json.loads(pred_path.read_text(encoding="utf-8"))
    if not isinstance(raw,list) or not 1<=len(raw)<=MAX_PREDICTIONS:
        raise ContractError("predictions must be a bounded, nonempty list")
    by_row={}
    for p in raw:
        if not isinstance(p,dict) or type(p.get("row_index")) is not int or p["row_index"]<0:
            raise ContractError("prediction row_index must be a nonnegative integer")
        if p["row_index"] in by_row:
            raise ContractError("duplicate prediction row_index")
        if not isinstance(p.get("prediction"),str) or not p["prediction"]:
            raise ContractError("missing classification prediction")
        by_row[p["row_index"]]=p
    group_col=ds.get("group_column")
    label_col=ds.get("label_column")
    sample_col=ds.get("sample_id_column")
    if not all(isinstance(x,str) and x for x in (group_col,label_col)):
        raise ContractError("independent evaluator needs explicit group/label column")
    expected_split=f"group-shuffle:{group_col}:seed=42:test=0.25"
    if run.get("group_split") != expected_split:
        raise ContractError("Unverified grouping: use the frozen evaluator split")
    observations={}
    all_groups=[]
    all_labels=[]
    with data_path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not {group_col,label_col}.issubset(reader.fieldnames):
            raise ContractError("trusted DEV data missing group/label columns")
        if sample_col and sample_col not in reader.fieldnames:
            raise ContractError("sample_id_column missing from DEV data")
        for i,row in enumerate(reader):
            full_group=(row[group_col] or "").strip()
            full_label=(row[label_col] or "").strip()
            if not full_group or not full_label:
                raise ContractError("DEV contains missing label/group; split is invalid")
            all_groups.append(full_group)
            all_labels.append(full_label)
            if i not in by_row:
                continue
            y=(row[label_col] or "").strip()
            group=(row[group_col] or "").strip()
            if not y or not group:
                raise ContractError("trusted label/group is missing")
            sample=(row[sample_col] or "").strip() if sample_col else i
            if sample_col and not sample:
                raise ContractError("trusted sample ID is missing")
            observations[i]=(y,group,sample)
    if len(observations)!=len(by_row):
        raise ContractError("prediction references out-of-range DEV rows")
    from sklearn.model_selection import GroupShuffleSplit
    split=GroupShuffleSplit(n_splits=1,test_size=0.25,random_state=42)
    _, frozen_test=next(split.split(list(range(len(all_groups))), all_labels, all_groups))
    if set(by_row) != set(map(int, frozen_test)):
        raise ContractError("PREDICTIONS_NOT_ON_FROZEN_DEV_SPLIT: cherry-picking or wrong fold")
    indices=sorted(by_row)
    truth,pred=[],[]
    for i in indices:
        saved=by_row[i]
        y,group,stable_id=observations[i]
        if saved.get("truth") != y or saved.get("group") != group:
            raise ContractError("prediction truth/group disagrees with independent DEV source")
        if sample_col and saved.get("sample_id")!=stable_id:
            raise ContractError("prediction sample ID disagrees with independent DEV source")
        truth.append(y)
        pred.append(saved["prediction"])
    samples=[observations[i][2] for i in indices]
    if len(set(samples))!=len(samples):
        raise ContractError("duplicate trusted sample IDs")
    if run["sample_ids_hash"]!=sample_hash(samples):
        raise ContractError("sample_ids_hash does not match trusted DEV test identities")
    classes=sorted(set(truth)|set(pred))
    computed=_scores(truth,pred,classes)
    if set(run["metrics"]) - SUPPORTED:
        raise ContractError("unsupported metrics in verified Run; use a registered evaluator")
    for name,value in run["metrics"].items():
        if check_reported and not math.isclose(float(value),computed[name],abs_tol=1e-6,rel_tol=0):
            raise ContractError(f"RECOMPUTED_METRIC_MISMATCH {name}: reported={value}, actual={computed[name]}")
    if not run["metrics"]:
        raise ContractError("empty Run metric map")
    return {"integrity":"METRICS_RECOMPUTED_FROM_DEV", "n_samples":len(indices),
            "trusted_dataset_sha256":ds["sha256"],"computed":computed,
            "note":"Verified metric arithmetic and DEV labels; not scientific novelty or independent holdout"}
