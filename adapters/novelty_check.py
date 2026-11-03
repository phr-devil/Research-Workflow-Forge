"""Evidence-linked novelty PRECHECK; deliberately does not judge originality.

Adapts ResearchStudio Scoop Check's four-axis decomposition and primary-paper
comparison contract. Metadata alone cannot establish overlap or novelty.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from adapters.literature import write_bundle
from core.contracts import validate

def fingerprint(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")).hexdigest()

def prepare_review(task: dict, evidence: dict, *, mechanism: str,
                   expected_difference: str, top_n: int = 3) -> dict:
    validate("task", task)
    validate("evidence", evidence)
    if not mechanism.strip() or not expected_difference.strip():
        raise ValueError("Mechanism and its falsifiable proposed difference are required")
    if type(top_n) is not int or not 1 <= top_n <= 5:
        raise ValueError("top_n must be 1..5")
    nearest = []
    for row in evidence["records"][:top_n]:
        nearest.append({"record_id": row["record_id"], "title": row["title"],
                        "doi": row.get("doi"), "url": row.get("url"),
                        "source_providers": row["sources"],
                        "fulltext_review": "NOT_DONE",
                        "overlap_verdict": "UNKNOWN",
                        "differentiating_evidence": None})
    return {
        "schema_version": "0.1", "task_id": task["task_id"], "status": "UNVERIFIED",
        "origin": "Scoop Check four-axis decomposition adapted, not upstream execution",
        "input_fingerprints": {"task": fingerprint(task), "evidence": fingerprint(evidence)},
        "claimed_contribution": {
            "problem_framing": task["question"],
            "core_mechanism": mechanism.strip(),
            "key_insight": expected_difference.strip(),
            "application_and_boundary": task.get("application_domain") or "UNKNOWN"},
        "closest_candidates": nearest,
        "scientific_questions": [
            "Read full original nearest papers, not only metadata or abstracts",
            "Compare same task/legal inputs, algorithm mechanism, independent truth and evaluation",
            "Name a minimum defensible difference, or mark COVERED/UNKNOWN",
            "Specify one real experiment distinguishing the new hypothesis from the strongest simple alternative",
        ],
        "what_is_not_verified": ["Novelty", "Independence of contribution", "Feasibility", "Model improvement"]
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare source-linked novelty questions, not a novelty verdict")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--mechanism", required=True)
    parser.add_argument("--difference", required=True)
    parser.add_argument("--top-n", type=int, default=3)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        task = json.loads(args.task.read_text(encoding="utf-8"))
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        result = prepare_review(task, evidence, mechanism=args.mechanism,
                                expected_difference=args.difference, top_n=args.top_n)
        if args.out.exists():
            parser.error("output already exists; choose a new versioned output path")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"state": result["status"], "review": str(args.out),
                          "nearest_candidates": len(result["closest_candidates"]),
                          "claim_confirmed": False}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, json.JSONDecodeError, KeyError) as exc:
        parser.exit(2, f"novelty precheck failed: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
