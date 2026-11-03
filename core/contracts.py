"""Versioned structural contracts. Passing != scientific evidence or approval."""
from __future__ import annotations
import math
from typing import Any

SCHEMA_VERSION = "0.1"
PHASES = {"DISCOVERY", "EVIDENCE", "PROBLEM", "FEASIBILITY", "ALGORITHM", "DECISION", "CONFIRMATION"}
RUN_STATUSES = {"VALID", "INVALID", "INCONCLUSIVE", "NOT_RUN"}
TASK_STATUSES = {"DRAFT", "ACTIVE", "FROZEN"}
CLAIM_STATUSES = {"CANDIDATE", "INSUFFICIENT", "CONFIRMED"}
DATA_ROLES = {"DEV", "EXTERNAL_REPLICATION", "STRESS", "PIVOT_RESERVE", "SEALED_CONFIRM"}

class ContractError(ValueError):
    """Invalid artifact shape: no assertion about scientific truth."""

def _object(value: Any) -> dict:
    if not isinstance(value, dict):
        raise ContractError("expected JSON object")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ContractError(f"schema_version must be {SCHEMA_VERSION}")
    return value

def _text(value: dict, *keys: str) -> None:
    for key in keys:
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ContractError(f"{key} must be nonempty string")

def _list(value: dict, *keys: str) -> None:
    for key in keys:
        if not isinstance(value.get(key), list):
            raise ContractError(f"{key} must be list")

def _enum(value: dict, key: str, options: set[str]) -> None:
    if value.get(key) not in options:
        raise ContractError(f"{key} must be one of {sorted(options)}")

def validate_state(value: Any) -> dict:
    obj = _object(value)
    _text(obj, "project_id", "goal", "next_action")
    _enum(obj, "phase", PHASES)
    _list(obj, "evidence_refs", "authorization_refs")
    for key in ("active_task_id", "best_valid_run_id", "last_event_id"):
        if obj.get(key) is not None and not isinstance(obj[key], str):
            raise ContractError(f"{key} must be string or null")
    return obj

def validate_evidence(value: Any) -> dict:
    obj = _object(value)
    _text(obj, "query", "retrieved_at")
    _enum(obj, "verification", {"METADATA_ONLY"})
    _list(obj, "sources_checked", "source_errors", "records")
    if not obj["records"]:
        raise ContractError("evidence records are empty: cannot certify SEARCH_READY")
    for r in obj["records"]:
        if not isinstance(r, dict):
            raise ContractError("evidence record must be object")
        _text(r, "record_id", "title")
        _enum(r, "verification", {"METADATA_ONLY"})
        _list(r, "sources")
        if not r["sources"]:
            raise ContractError("evidence record must include provider provenance")
    return obj

def validate_dataset(value: Any) -> dict:
    obj = _object(value)
    _list(obj, "datasets")
    if not obj["datasets"]:
        _text(obj, "proof_path")  # theory/simulation instead of static dataset
    for ds in obj["datasets"]:
        if not isinstance(ds, dict):
            raise ContractError("dataset entry must be object")
        _text(ds, "dataset_id", "source_url", "group_unit")
        _enum(ds, "role", DATA_ROLES)
        _enum(ds, "label_status", {"VERIFIED", "UNKNOWN", "NOT_APPLICABLE"})
    return obj

def validate_task(value: Any) -> dict:
    obj = _object(value)
    _text(obj, "task_id", "question")
    _enum(obj, "status", TASK_STATUSES)
    if obj["status"] in {"ACTIVE", "FROZEN"}:
        _text(obj, "protocol_id", "metric", "group_split", "holdout_policy", "baseline")
        _list(obj, "legal_inputs", "data_refs", "nearest_work")
        if not obj["legal_inputs"]:
            raise ContractError("active task must identify legal prediction-time inputs")
    return obj

def validate_experiment(value: Any) -> dict:
    obj = _object(value)
    _text(obj, "experiment_id", "task_id", "hypothesis", "evaluator_ref",
          "decision_if_positive", "decision_if_negative")
    _enum(obj, "split", {"dev", "validation"})
    budget = obj.get("budget")
    if not isinstance(budget, dict):
        raise ContractError("budget must be object")
    cap = budget.get("gpu_hours_max")
    if isinstance(cap, bool) or not isinstance(cap, (int, float)) or not math.isfinite(cap) or cap < 0:
        raise ContractError("budget.gpu_hours_max must be nonnegative finite number")
    return obj

def validate_run(value: Any) -> dict:
    obj = _object(value)
    _text(obj, "run_id", "task_id", "protocol_id", "dataset_version",
          "code_commit", "evaluator_version")
    _enum(obj, "status", RUN_STATUSES)
    _enum(obj, "split", {"dev", "validation", "sealed"})
    if not isinstance(obj.get("metrics"), dict):
        raise ContractError("metrics must be object")
    _list(obj, "artifact_refs")
    if obj["status"] == "NOT_RUN" and obj["metrics"]:
        raise ContractError("NOT_RUN cannot declare metrics")
    if obj["status"] != "NOT_RUN" and not obj["artifact_refs"]:
        raise ContractError("recorded run requires raw log or artifact reference")
    if obj["status"] == "VALID":
        _text(obj, "group_split", "sample_ids_hash")
        _list(obj, "legal_inputs")
        if not obj["legal_inputs"] or not obj["metrics"]:
            raise ContractError("VALID requires legal inputs and measured metrics")
        for name, metric in obj["metrics"].items():
            if not isinstance(name, str) or not name.strip():
                raise ContractError("metric name must be nonempty")
            if isinstance(metric, bool) or not isinstance(metric, (int, float)) or not math.isfinite(metric):
                raise ContractError("VALID metrics must be finite numbers")
    if obj["split"] == "sealed":
        _text(obj, "frozen_protocol_ref", "authorization_ref")
    return obj

def validate_claim(value: Any) -> dict:
    obj = _object(value)
    _text(obj, "claim_id", "task_id", "statement")
    _enum(obj, "status", CLAIM_STATUSES)
    _list(obj, "evidence_run_ids", "nearest_work")
    if obj["status"] == "CONFIRMED":
        _text(obj, "confirmation_ref", "frozen_protocol_ref")
        if not obj["evidence_run_ids"] or not obj["nearest_work"]:
            raise ContractError("confirmed claims require evidence runs and named nearest work")
    return obj

VALIDATORS = {"state": validate_state, "evidence": validate_evidence,
              "dataset": validate_dataset, "task": validate_task,
              "experiment": validate_experiment, "run": validate_run,
              "claim": validate_claim}

def validate(kind: str, obj: Any) -> dict:
    if kind not in VALIDATORS:
        raise ContractError(f"unknown artifact kind: {kind}")
    return VALIDATORS[kind](obj)
