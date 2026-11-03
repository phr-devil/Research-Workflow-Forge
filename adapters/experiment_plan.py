"""Bounded experiment PLAN handoff, adapting the ARIS claim-to-evidence rubric.

Produces no model, training command, scientific claim, resource authorization,
or sealed-test access. The agent must supply a real hypothesis and evaluator.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

from adapters.novelty_check import fingerprint
from core.contracts import validate

def prepare_experiment(task: dict, *, hypothesis: str, evaluator_ref: str,
                       gpu_hours_max: float, positive: str, negative: str,
                       experiment_id: str = "E1", baseline_run_ref: str | None = None,
                       novelty_review: dict | None = None) -> dict:
    validate("task", task)
    if task["status"] not in {"ACTIVE", "FROZEN"}:
        raise ValueError("Activate TaskSpec and valid protocol before planning comparisons")
    for name, value in {"hypothesis": hypothesis, "evaluator_ref": evaluator_ref,
                        "experiment_id": experiment_id, "positive": positive, "negative": negative}.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be nonempty")
    if isinstance(gpu_hours_max, bool) or not isinstance(gpu_hours_max, (int, float)) or not math.isfinite(gpu_hours_max) or gpu_hours_max < 0:
        raise ValueError("GPU budget must be a nonnegative finite number")
    if novelty_review is not None:
        if novelty_review.get("input_fingerprints", {}).get("task") != fingerprint(task):
            raise ValueError("stale novelty review: task content changed")
        if novelty_review.get("task_id") != task["task_id"]:
            raise ValueError("novelty review is for a different task")
    experiment = {
        "schema_version": "0.1", "experiment_id": experiment_id, "task_id": task["task_id"],
        "hypothesis": hypothesis, "evaluator_ref": evaluator_ref,
        "split": "dev", "budget": {"gpu_hours_max": gpu_hours_max},
        "decision_if_positive": positive, "decision_if_negative": negative,
        "status": "PLAN_ONLY", "protocol_id": task["protocol_id"],
        "task_fingerprint": fingerprint(task), "novelty_precheck": novelty_review.get("status") if novelty_review else "NOT_REQUESTED",
        "baseline_run_ref": baseline_run_ref,
        "execution_plan": [
            {"stage": "sanity", "intent": "Verify legal data, protected evaluator and no leakage"},
            {"stage": "baseline", "intent": "Reuse actual credible Run or run permitted baseline; no training authorized here"},
            {"stage": "challenger", "intent": "One meaningful differentiating algorithm experiment within real authorization"},
            {"stage": "analysis", "intent": "Compare group-level metrics, uncertainty, cost and negative outcomes"},
        ],
        "authorization": "NOT_GRANTED_BY_THIS_ARTIFACT"}
    validate("experiment", experiment)
    return experiment

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate non-executable experiment plan from an ACTIVE Task")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--evaluator-ref", required=True)
    parser.add_argument("--gpu-hours-max", type=float, required=True)
    parser.add_argument("--positive", required=True)
    parser.add_argument("--negative", required=True)
    parser.add_argument("--experiment-id", default="E1")
    parser.add_argument("--baseline-run-ref")
    parser.add_argument("--novelty-review", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        task = json.loads(args.task.read_text(encoding="utf-8"))
        novelty = json.loads(args.novelty_review.read_text(encoding="utf-8")) if args.novelty_review else None
        result = prepare_experiment(task, hypothesis=args.hypothesis,
                    evaluator_ref=args.evaluator_ref, gpu_hours_max=args.gpu_hours_max,
                    positive=args.positive, negative=args.negative,
                    experiment_id=args.experiment_id, baseline_run_ref=args.baseline_run_ref,
                    novelty_review=novelty)
        if args.out.exists():
            parser.error("output exists; use a versioned output name")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"status": "PLAN_ONLY", "path": str(args.out), "gpu_hours_max": args.gpu_hours_max,
                          "training_performed": False, "authorization_granted": False},ensure_ascii=False))
        return 0
    except (ValueError, OSError, json.JSONDecodeError, KeyError) as exc:
        parser.exit(2, f"experiment planning failed: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
