"""Independent arithmetic for pinned-group regression and one-event-per-episode DEV predictions.

This checks declared labels, split, group/sample identity and metric arithmetic.
It CANNOT attest that an external model genuinely operated causally.
"""
from __future__ import annotations
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from core.contracts import ContractError
from core.data_access import bind_dev_dataset
from core.receipts import check_receipt, resolve_project_file

REGRESSION_FORMAT = "forge-dev-regression-v1"
EVENT_FORMAT = "forge-dev-event-v1"
FORMATS = {REGRESSION_FORMAT, EVENT_FORMAT}
MAX_ROWS = 50000


def _finite(x: object, name: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (float, int)):
        raise ContractError(name + " must be a finite number")
    if not math.isfinite(float(x)):
        raise ContractError(name + " must be a finite number")
    return float(x)


def _truth(raw: str, *, event: bool) -> float | None:
    if event and raw.strip().upper() in {"", "NONE", "NULL"}:
        return None
    try:
        number = float(raw)
    except (ValueError, TypeError) as exc:
        raise ContractError("trusted DEV target is not numeric") from exc
    if not math.isfinite(number):
        raise ContractError("trusted DEV target is non-finite")
    return number


def _setup(project: Path, run: dict):
    from core.metric_verify import sample_hash
    spec = run.get("metric_spec")
    if not isinstance(spec, dict) or spec.get("format") not in FORMATS:
        raise ContractError("unsupported extended metric format")
    required = ("predictions_ref", "manifest_ref", "manifest_sha256", "dataset_id",
                "split_ref", "split_sha256")
    for field in required:
        if not isinstance(spec.get(field), str) or not spec[field].strip():
            raise ContractError("metric_spec missing " + field)
    manifest_path = resolve_project_file(project, spec["manifest_ref"])
    split_path = resolve_project_file(project, spec["split_ref"])
    check_receipt(manifest_path, spec["manifest_sha256"])
    check_receipt(split_path, spec["split_sha256"])
    data_path, ds = bind_dev_dataset(project, manifest_path, spec["dataset_id"],
                                     purpose="EVALUATE_DEV")
    if ds["sha256"].lower() != run["dataset_version"].lower():
        raise ContractError("DEV source hash does not match Run dataset_version")
    if run["group_split"] != "pinned-groups:" + spec["split_sha256"].lower():
        raise ContractError("Run group_split must bind pinned split manifest")
    if spec["predictions_ref"] not in run["artifact_refs"]:
        raise ContractError("predictions must be in hashed Run artifacts")
    split = json.loads(split_path.read_text(encoding="utf-8"))
    train, dev = split.get("train_groups"), split.get("dev_groups")
    if not all(isinstance(x, list) and x and all(isinstance(v, str) and v for v in x)
               and len(set(x)) == len(x) for x in (train, dev)):
        raise ContractError("pinned split requires nonempty unique train/dev groups")
    if set(train) & set(dev):
        raise ContractError("train/dev independent groups overlap")
    group_col, label_col = ds.get("group_column"), ds.get("label_column")
    id_col = ds.get("sample_id_column")
    if not all(isinstance(x, str) and x for x in (group_col, label_col, id_col)):
        raise ContractError("typed metrics require trusted group, target and sample_id columns")
    items = {}
    all_groups = set()
    with data_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not {group_col,label_col,id_col}.issubset(reader.fieldnames):
            raise ContractError("trusted DEV CSV lacks group, label or sample IDs")
        for index, row in enumerate(reader):
            group, sid = (row[group_col] or "").strip(), (row[id_col] or "").strip()
            if not group or not sid:
                raise ContractError("empty independent group or sample ID")
            all_groups.add(group)
            if group in dev:
                items[index] = (group, sid, (row[label_col] or "").strip())
    if all_groups != set(train) | set(dev):
        raise ContractError("pinned group split does not cover complete DEV dataset")
    if not items or len(items) > MAX_ROWS:
        raise ContractError("empty/oversized independent DEV query set")
    ids = [v[1] for v in items.values()]
    if len(ids) != len(set(ids)):
        raise ContractError("duplicate trusted DEV sample IDs")
    if run["sample_ids_hash"] != sample_hash(ids):
        raise ContractError("Run sample identity hash mismatch")
    preds_path = resolve_project_file(project, spec["predictions_ref"])
    preds = json.loads(preds_path.read_text(encoding="utf-8"))
    if not isinstance(preds, list) or len(preds) != len(items):
        raise ContractError("predictions do not match complete frozen DEV query set")
    by_index = {}
    for p in preds:
        if not isinstance(p, dict) or type(p.get("row_index")) is not int or p["row_index"] < 0:
            raise ContractError("prediction requires integer row_index")
        if p["row_index"] in by_index:
            raise ContractError("duplicate prediction row_index")
        by_index[p["row_index"]] = p
    if set(by_index) != set(items):
        raise ContractError("predictions do not match complete frozen DEV query set")
    return spec, items, by_index, ds


def _regression(items: dict, predictions: dict, aggregation: str) -> tuple[dict, dict]:
    if aggregation not in {"group_mean", "pooled"}:
        raise ContractError("regression aggregation must be group_mean/pooled")
    groups = defaultdict(list)
    for index, (group, _, raw) in items.items():
        y = _truth(raw, event=False)
        p = _finite(predictions[index].get("prediction"), "prediction")
        groups[group].append((p - y) ** 2)
    # Recover absolute residuals before aggregating (square-root of squared errors).
    if aggregation == "group_mean":
        mae = sum(sum(math.sqrt(x) for x in rs)/len(rs) for rs in groups.values()) / len(groups)
        rmse = sum(math.sqrt(sum(rs)/len(rs)) for rs in groups.values()) / len(groups)
    else:
        all_sq = [x for rs in groups.values() for x in rs]
        mae = sum(math.sqrt(x) for x in all_sq)/len(all_sq)
        rmse = math.sqrt(sum(all_sq)/len(all_sq))
    group_mae = {g:sum(math.sqrt(x) for x in rs)/len(rs) for g,rs in groups.items()}
    return {"MAE":mae, "RMSE":rmse}, group_mae


def _events(items: dict, predictions: dict, tol: float, mode: str) -> tuple[dict, dict]:
    if mode != "SINGLE_EMISSION_PER_EPISODE":
        raise ContractError("event evaluator requires explicit single-emission protocol")
    if not (0 < tol <= 30):
        raise ContractError("event tolerance must be >0 and <=30 seconds")
    hits, events, alarms = 0, 0, 0
    group_summary = defaultdict(lambda: {"episodes":0,"events":0,"hits":0,"alarms":0})
    for index, (group, _, raw) in items.items():
        truth = _truth(raw, event=True)
        p = predictions[index]
        # Must be a single output, not a truth-centered score window or candidate list.
        if set(p) != {"row_index", "trigger_time_s"}:
            raise ContractError("event prediction must be one row_index and one trigger_time_s only")
        trigger = p["trigger_time_s"]
        if trigger is not None:
            trigger = _finite(trigger, "trigger_time_s")
            if trigger < 0:
                raise ContractError("trigger time must be nonnegative")
        good = truth is not None and trigger is not None and abs(trigger - truth) <= tol
        if truth is not None:
            events += 1
            group_summary[group]["events"] += 1
        if good:
            hits += 1
            group_summary[group]["hits"] += 1
        elif trigger is not None:
            alarms += 1
            group_summary[group]["alarms"] += 1
        group_summary[group]["episodes"] += 1
    if events == 0:
        raise ContractError("no true events: event recall undefined")
    return {"event_recall":hits/events,"false_alarm_rate":alarms/len(items)}, dict(group_summary)


def verify_extended_metrics(project: Path, run: dict, *, check_reported: bool = True) -> dict:
    import math
    project = project.resolve()
    spec, items, predictions, ds = _setup(project, run)
    if spec["format"] == REGRESSION_FORMAT:
        computed, detail = _regression(items, predictions, spec.get("aggregation"))
        metric_type = "REGRESSION"
    else:
        computed, detail = _events(items, predictions, _finite(spec.get("tolerance_s"), "tolerance_s"),
                                   spec.get("prediction_mode"))
        metric_type = "EVENT_SINGLE_EMISSION_ARITHMETIC"
    if not run["metrics"] or set(run["metrics"]) - set(computed):
        raise ContractError("unsupported or missing verified metrics")
    for name, reported in run["metrics"].items():
        if check_reported and not math.isclose(float(reported), computed[name], abs_tol=1e-6, rel_tol=0):
            raise ContractError("RECOMPUTED_METRIC_MISMATCH: " + name)
    return {"integrity":"METRICS_RECOMPUTED_FROM_DEV", "metric_type":metric_type,
            "n_samples":len(items), "n_groups":len(detail),
            "trusted_dataset_sha256":ds["sha256"],"computed":computed,
            "group_detail":detail,
            "limitations":"Metric arithmetic verified; no source-code execution attestation, causal trace proof or independent holdout"}
