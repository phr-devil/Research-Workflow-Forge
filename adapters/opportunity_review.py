"""Transparent, ordinal research opportunity triage (no fictitious success probabilities)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from adapters.hypothesis_bank import validate_bank, verify_bank_sources, _load_json, _write_new
from core.receipts import check_receipt, resolve_project_file

ORDER = {"BOUNDED_TEST_CANDIDATE": 0,
         "MATCHED_BASELINE_FIRST": 1,
         "LEGAL_INFORMATION_PROBE": 2,
         "CHECK_ORIGINAL_DATA_SIGNAL": 3,
         "VERIFY_DATA_SIGNAL": 4,
         "REVISE_ILLEGAL_INFORMATION_PREMISE": 5}


def review_opportunities(project: Path, bank: dict) -> dict:
    project = project.resolve()
    validate_bank(bank)
    verify_bank_sources(project, bank)
    rows = []
    for idea in bank["hypotheses"]:
        has_verified_data = bool(idea["source_seed_ids"])
        has_note = idea["uses_data_note"]
        has_papers = bool(idea["paper_record_ids"])
        legal = idea["legal_information_status"]
        baseline = idea["baseline_status"]
        if legal == "BLOCKED":
            route = "REVISE_ILLEGAL_INFORMATION_PREMISE"
        elif not has_verified_data:
            route = "CHECK_ORIGINAL_DATA_SIGNAL" if has_note else "VERIFY_DATA_SIGNAL"
        elif legal == "UNKNOWN":
            route = "LEGAL_INFORMATION_PROBE"
        elif baseline == "UNKNOWN":
            route = "MATCHED_BASELINE_FIRST"
        else:
            route = "BOUNDED_TEST_CANDIDATE"
        if idea["test_cost"] == "HIGH" and route == "BOUNDED_TEST_CANDIDATE":
            route = "MATCHED_BASELINE_FIRST"
        rows.append({
            "hypothesis_id": idea["hypothesis_id"],
            "next_action": route,
            "data_evidence": ("VERIFIED_DEV_DIAGNOSTIC" if has_verified_data else
                              "UNRECOMPUTED_DATA_NOTE" if has_note else "NONE"),
            "literature_evidence": "METADATA_ONLY" if has_papers else "NONE",
            "legal_information": legal,
            "baseline_status": baseline,
            "declared_test_cost": idea["test_cost"],
            "novelty": "UNVERIFIED",
            "scientific_status": idea["status"],
            "next_probe": idea["minimum_test"],
            "if_positive": idea["if_positive"], "if_negative": idea["if_negative"],
            "warnings": ["Independent validation and named nearest full-text review required before formal Claim"],
        })
    rows.sort(key=lambda r: (ORDER[r["next_action"]],
                             {"LOW":0,"MEDIUM":1,"UNKNOWN":2,"HIGH":3}[r["declared_test_cost"]],
                             r["hypothesis_id"]))
    return {
        "status": "ORDINAL_REVIEW_ONLY",
        "recommended": rows[0]["hypothesis_id"],
        "candidates": rows,
        "interpretation": "Next evidence action, NOT rank of novelty/paper probability. Unknown is not automatic STOP.",
        "authorization": "NOT_GRANTED",
        "research_success_rate": "NOT_MEASURED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review hypothesis bank without training or automated claims")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        project = args.project.resolve()
        out = args.out.resolve()
        if not out.is_relative_to(project) or out == project:
            raise ValueError("output must be project-contained")
        result = review_opportunities(project, _load_json(project, args.bank))
        _write_new(out, result)
        print(json.dumps({"recommended": result["recommended"], "review": str(out),
                          "training_performed": False, "science_confirmed": False}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"opportunity review failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
