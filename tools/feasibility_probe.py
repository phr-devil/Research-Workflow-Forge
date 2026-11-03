"""Small evidence-only DEV feasibility diagnostic (no model fitting).

Accepts only Run files that pass Forge's independent metric verifier. Reports
descriptive residuals on already-selected DEV groups; not a learnability proof
or a new training/test split. Access to DEV is recorded by the existing loader.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

from core.comparison import compare_runs
from core.contracts import ContractError
from core.metric_verify import FORMAT as CLASSIFICATION_FORMAT
from core.receipts import resolve_project_file
from core.run_integrity import load_verified_run

REGRESSION_FORMAT = "forge-dev-regression-v1"
EVENT_FORMAT = "forge-dev-event-v1"
MAX_GROUPS_TO_SHOW = 3


def _group_losses(project: Path, run: dict) -> tuple[dict[str, list[tuple[int, float]]], str]:
    fmt = run["metric_spec"]["format"]
    if fmt == CLASSIFICATION_FORMAT:
        ref = run["metric_spec"]["predictions_ref"]
        raw = json.loads(resolve_project_file(project, ref).read_text(encoding="utf-8"))
        grouped = defaultdict(list)
        # Trusted ground truth/group identity was independently checked by
        # load_verified_run immediately before this function.
        for row in raw:
            grouped[row["group"]].append((row["row_index"],
                                          float(row["prediction"] != row["truth"])))
        return dict(grouped), "classification_error_rate"
    if fmt == REGRESSION_FORMAT:
        # Reuses pinned-group, SHA-verified independent labels.
        from core.metric_extensions import _setup, _truth
        _, items, predictions, _ = _setup(project, run)
        grouped = defaultdict(list)
        for row_index, (group, _, raw_target) in items.items():
            expected = _truth(raw_target, event=False)
            predicted = predictions[row_index]["prediction"]
            if type(predicted) not in (int, float) or not math.isfinite(predicted):
                raise ContractError("nonfinite regression prediction in verified Run")
            grouped[group].append((row_index, abs(predicted - expected)))
        return dict(grouped), "absolute_error"
    if fmt == EVENT_FORMAT:
        return {}, "NOT_APPLICABLE_FOR_EVENT_EVALUATION"
    raise ContractError("Unsupported metric receipt format")


def diagnose_feasibility(project: Path, candidate_path: Path,
                         reference_path: Path | None = None, *, metric: str | None = None) -> dict:
    """Read existing original Run receipts; never trains, searches or accesses sealed data."""
    project = project.resolve()
    candidate, _ = load_verified_run(project, candidate_path)
    if candidate["status"] != "VALID" or candidate["split"] not in {"dev", "validation"}:
        raise ContractError("Only validated development Runs are eligible")
    losses, error_unit = _group_losses(project, candidate)
    n_groups = len(losses)
    n_samples = sum(len(rows) for rows in losses.values())
    grouped = [
        {"group": group, "n": len(rows),
         "mean_loss": sum(loss for _, loss in rows) / len(rows)}
        for group, rows in sorted(losses.items())
    ]
    # A descriptive error profile is NOT a provable performance ceiling.
    overall = (sum(g["mean_loss"] for g in grouped) / n_groups if n_groups else None)
    worst = sorted(grouped, key=lambda row: (-row["mean_loss"], row["group"]))[:MAX_GROUPS_TO_SHOW]
    output = {
        "status": "VERIFIED_DEV_RECEIPTS_ANALYZED",
        "data_validity": "HASHED_DEV_AND_METRIC_ARITHMETIC_ONLY",
        "task_id": candidate["task_id"],
        "protocol_id": candidate["protocol_id"],
        "candidate": candidate["run_id"],
        "evidence_ref": candidate_path.resolve().relative_to(project).as_posix(),
        "reference": None,
        "evaluation_type": candidate["metric_spec"]["format"],
        "n_independent_groups": n_groups,
        "n_query_samples": n_samples,
        "signal_evidence": "UNKNOWN_WITHOUT_MATCHED_REFERENCE",
        "simple_baseline": "NOT_VERIFIED_AS_SIMPLE_OR_WELL_TUNED",
        "residual_structure": "DESCRIPTIVE_DEV_ONLY" if n_groups >= 2 else "INSUFFICIENT_GROUPS_OR_UNSUPPORTED",
        "remaining_error": {
            "measure": error_unit,
            "group_macro_mean": overall,
            "theoretical_attainable_gain": "UNKNOWN",
            "note": "Residual error is observable, not a proof of algorithmic headroom",
        },
        "worst_groups_exploratory": worst,
        "paired_evidence": None,
        "recommended_next_check": "VERIFY_A_MATCHED_SIMPLE_REFERENCE_OR_A_NEW_DISTINCT_MECHANISM",
        "limitations": [
            "Exploratory DEV-only slices; no independent scientific confirmation or novelty inference",
            "A reference Run is not proven to be a simple/strong/no-information baseline",
            "No oracle or achievable upper bound is inferred from observed residuals",
            "Model training conditions, causal inputs and tuning parity require separate evidence",
        ],
        "data_access": "DEV_AUDIT_APPEND_ONLY_NO_FIT",
    }
    if reference_path is None:
        return output
    reference, _ = load_verified_run(project, reference_path)
    if reference["status"] != "VALID" or reference["split"] not in {"dev", "validation"}:
        raise ContractError("Reference must be a valid development Run")
    metric_names = set(candidate["metrics"]) & set(reference["metrics"])
    if not metric_names:
        raise ContractError("No shared verified metric")
    if metric is None:
        if len(metric_names) != 1:
            raise ContractError("Multiple verified metrics; supply the frozen Task metric with --metric")
        metric = next(iter(metric_names))
    if metric not in metric_names:
        raise ContractError("Requested metric missing from matched verified Runs")
    # This checks frozen data/protocol/information/metric receipts, not self-reports.
    comparison = compare_runs(reference, candidate, metric,
                              lower_is_better=metric in {"MAE", "RMSE", "false_alarm_rate"})
    output["reference"] = reference["run_id"]
    output["paired_evidence"] = {
        "metric": metric,
        "directional_delta": comparison["improvement_direction_delta"],
        "scientific_claim_confirmed": False,
    }
    delta = comparison["improvement_direction_delta"]
    output["signal_evidence"] = (
        "DEV_IMPROVEMENT_OVER_REFERENCE_OBSERVED" if delta > 0 else
        "NO_DEV_IMPROVEMENT_OVER_REFERENCE_OBSERVED" if delta < 0 else
        "DEV_TIE_WITH_REFERENCE"
    )
    earlier, earlier_unit = _group_losses(project, reference)
    if error_unit == earlier_unit and losses and earlier:
        if set(losses) != set(earlier):
            raise ContractError("Reference and candidate have different held-out groups")
        by_group = []
        for group in sorted(losses):
            c = dict(losses[group])
            b = dict(earlier[group])
            if set(c) != set(b):
                raise ContractError("Reference and candidate differ in held-out sample IDs")
            by_group.append(sum(b[k] - c[k] for k in c) / len(c))
        output["paired_evidence"]["group_loss_change"] = {
            "improved": sum(value > 1e-12 for value in by_group),
            "degraded": sum(value < -1e-12 for value in by_group),
            "tied": sum(abs(value) <= 1e-12 for value in by_group),
            "n_groups": len(by_group),
            "note": "Post-selection, descriptive only; not a significance test",
        }
        output["recommended_next_check"] = (
            "EXAMINE_MECHANISM_IN_PAIRED_GROUP_ERRORS_AND_VALIDATE_ON_ELIGIBLE_GROUPS"
            if delta > 0 else
            "CHECK_LEGAL_INFORMATION_OR_A_DISTINCT_FAILURE_PREMISE_BEFORE_MORE_COMPLEXITY"
        )
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verified DEV feasibility diagnostic; never trains")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--metric", help="Explicit frozen Task metric when Runs contain multiple metrics")
    parser.add_argument("--out", type=Path, help="Optional NEW project-contained evidence JSON; never overwritten")
    args = parser.parse_args(argv)
    try:
        result = diagnose_feasibility(args.project, args.candidate, args.reference, metric=args.metric)
        if args.out is not None:
            path = args.out.resolve()
            if not path.is_relative_to(args.project.resolve()):
                raise ValueError("Evidence output must be project-contained")
            with path.open("x", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                f.write("\n")
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        parser.exit(2, f"feasibility diagnostic failed: {exc}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
