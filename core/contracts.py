"""Structural contracts; passing validation does NOT prove scientific truth."""
from __future__ import annotations
from typing import Any
SCHEMA_VERSION = "0.1"
PHASES = {"DISCOVERY", "EVIDENCE", "PROBLEM", "FEASIBILITY", "ALGORITHM", "DECISION", "CONFIRMATION"}
RUN_STATUSES = {"VALID", "INVALID", "INCONCLUSIVE", "NOT_RUN"}
TASK_STATUSES = {"DRAFT", "ACTIVE", "FROZEN"}
CLAIM_STATUSES = {"CANDIDATE", "INSUFFICIENT", "CONFIRMED"}

class ContractError(ValueError):
    """Invalid structural contract."""

def _object(obj: Any) -> dict:
    if not isinstance(obj, dict):
        raise ContractError("expected a JSON object")
    if obj.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("schema_version must be 0.1")
    return obj

def _text(obj: dict, *keys: str) -> None:
    for key in keys:
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            raise ContractError(f"{key} must be nonempty string")

def _list(obj: dict, *keys: str) -> None:
    for key in keys:
        if not isinstance(obj.get(key), list):
            raise ContractError(f"{key} must be list")

def _enum(obj: dict, key: str, values: set[str]) -> None:
    if obj.get(key) not in values:
        raise ContractError(f"{key} must be one of {sorted(values)}")

def validate_state(value: Any) -> dict:
    obj = _object(value)
    _text(obj, "project_id", "goal", "next_action")
    _enum(obj, "phase", PHASES)
    _list(obj, "evidence_refs", "authorization_refs")
    for key in ("active_task_id", "best_valid_run_id"):
        if obj.get(key) is not None and not isinstance(obj[key], str):
            raise ContractError(f"{key} must be string or null")
    return obj

def validate_task(value: Any) -> dict:
    obj = _object(value)
    _text(obj, "task_id", "question")
    _enum(obj, "status", TASK_STATUSES)
    if obj["status"] in {"ACTIVE", "FROZEN"}:
        _text(obj, "protocol_id", "metric", "group_split", "holdout_policy", "baseline")
        _list(obj, "legal_inputs", "data_refs", "nearest_work")
    return obj

def validate_experiment(value: Any) -> dict:
    obj = _object(value)
    _text(obj, "experiment_id", "task_id", "hypothesis", "evaluator_ref",
          "decision_if_positive", "decision_if_negative")
    _enum(obj, "split", {"dev", "validation"})
    budget = obj.get("budget")
    if not isinstance(budget, dict):
        raise ContractError("budget must be an object")
    cap = budget.get("gpu_hours_max")
    if isinstance(cap, bool) or not isinstance(cap, (int, float)) or cap < 0:
        raise ContractError("budget.gpu_hours_max must be nonnegative numeric")
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
    return obj

VALIDATORS = {"state": validate_state, "task": validate_task,
              "experiment": validate_experiment, "run": validate_run,
              "claim": validate_claim}

def validate(kind: str, obj: Any) -> dict:
    if kind not in VALIDATORS:
        raise ContractError(f"unknown kind: {kind}")
    return VALIDATORS[kind](obj)
