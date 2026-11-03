"""Comparable development-run metrics; never infer scientific novelty."""
from __future__ import annotations
from core.contracts import ContractError, validate

REQUIRED_SAME = ("task_id", "protocol_id", "dataset_version",
                 "evaluator_version", "split", "group_split", "sample_ids_hash")

def compare_runs(champion: dict, challenger: dict, metric: str, *, lower_is_better: bool = False) -> dict:
    validate("run", champion)
    validate("run", challenger)
    if champion["status"] != "VALID" or challenger["status"] != "VALID":
        raise ContractError("both runs must be VALID; repair/inconclusive is not comparable")
    if champion["split"] == "sealed" or challenger["split"] == "sealed":
        raise ContractError("sealed confirmation is never an iterative tuning comparator")
    differences = [field for field in REQUIRED_SAME if champion.get(field) != challenger.get(field)]
    if sorted(champion["legal_inputs"]) != sorted(challenger["legal_inputs"]):
        differences.append("legal_inputs")
    if differences:
        raise ContractError("NOT_COMPARABLE: mismatched " + ", ".join(differences))
    if metric not in champion["metrics"] or metric not in challenger["metrics"]:
        raise ContractError(f"metric {metric!r} missing from either run")
    a, b = champion["metrics"][metric], challenger["metrics"][metric]
    delta = b-a
    improvement = -delta if lower_is_better else delta
    return {"comparison_status": "DEVELOPMENT_ONLY",
            "task_id": champion["task_id"], "protocol_id": champion["protocol_id"],
            "champion": champion["run_id"], "challenger": challenger["run_id"],
            "metric": metric, "champion_value": a, "challenger_value": b,
            "raw_delta": delta, "improvement_direction_delta": improvement,
            "direction": "minimize" if lower_is_better else "maximize",
            "scientific_claim_confirmed": False,
            "notes": "Effect uncertainty, fair tuning, literature novelty and independent confirmation require separate evidence"}
