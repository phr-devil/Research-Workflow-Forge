"""HypoRefine-style research idea ledger: source receipts, NOT hypothesis discovery by itself.

Seed extraction reads independently verified DEV Runs only. Agent-authored ideas
remain hypotheses, even when linked to genuine data observations and paper metadata.
No fitting, external code, paper claims, or sealed data access is performed.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from core.contracts import ContractError, validate
from core.receipts import check_receipt, fingerprint_file, resolve_project_file

BANK_VERSION = "research-hypothesis-bank-v1"
SEED_VERSION = "research-observation-seeds-v1"
INFO = {"UNKNOWN", "PLAUSIBLE", "OBSERVED_AVAILABLE", "BLOCKED"}
BASELINE = {"UNKNOWN", "MATCHED_BASELINE_PRESENT", "BASELINE_DOMINATED"}
COST = {"UNKNOWN", "LOW", "MEDIUM", "HIGH"}
ASSESSMENTS = {"SUPPORTS_EXPECTED_PATTERN", "CONTRADICTS_EXPECTED_PATTERN", "INCONCLUSIVE"}


def _text(obj: dict, key: str) -> str:
    val = obj.get(key)
    if not isinstance(val, str) or not val.strip() or len(val) > 3000:
        raise ContractError(f"{key} must be nonempty text (max 3000 chars)")
    return val.strip()


def _rel(project: Path, path: Path) -> str:
    resolved = path.resolve()
    if not resolved.is_file() or not resolved.is_relative_to(project.resolve()):
        raise ContractError("source must be an existing project-contained file")
    return resolved.relative_to(project.resolve()).as_posix()


def _load_json(project: Path, path: Path) -> dict:
    _rel(project, path)
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ContractError("expected JSON object")
    return obj


def _receipt(project: Path, path: Path) -> dict:
    return {"ref": _rel(project, path), "sha256": fingerprint_file(path)}


def _write_new(path: Path, obj: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    return path


def make_observation_seeds(project: Path, candidate_run: Path,
                           reference_run: Path | None = None,
                           *, metric: str | None = None) -> dict:
    """Derive a *question* from measured errors; never invent mechanism or headroom."""
    from tools.feasibility_probe import diagnose_feasibility
    project = project.resolve()
    c_path = resolve_project_file(project, _rel(project, candidate_run))
    r_path = (resolve_project_file(project, _rel(project, reference_run))
              if reference_run is not None else None)
    diagnostic = diagnose_feasibility(project, c_path, r_path, metric=metric)
    result = {
        "format": SEED_VERSION, "task_id": diagnostic["task_id"],
        "protocol_id": diagnostic["protocol_id"],
        "candidate_run": _receipt(project, c_path),
        "reference_run": _receipt(project, r_path) if r_path else None,
        "metric": metric,
        "diagnostic": diagnostic,
        "seeds": [],
        "status": "DEV_OBSERVATION_NOT_SCIENTIFIC_CONFIRMATION",
    }
    if diagnostic["residual_structure"] == "DESCRIPTIVE_DEV_ONLY":
        result["seeds"].append({
            "seed_id": "S_GROUP_ERRORS",
            "observation": "Verified DEV predictions have descriptive independent-group errors",
            "evidence": diagnostic["worst_groups_exploratory"],
            "question": "Are group-specific errors repeatable and correctable under legal predecision inputs?",
            "limitations": "Post-selection group descriptions, not correctability or independent replication",
        })
    paired = diagnostic.get("paired_evidence")
    if paired:
        result["seeds"].append({
            "seed_id": "S_MATCHED_COMPARISON",
            "observation": diagnostic["signal_evidence"],
            "evidence": paired,
            "question": "Which independent groups or conditions distinguish this result from a matched reference?",
            "limitations": "DEV comparison, not novelty, causal identification or strong-baseline certification",
        })
    if not result["seeds"]:
        result["seeds"].append({
            "seed_id": "S_NEEDS_EVALUABLE_SIGNAL",
            "observation": "No supported group residual slice or matched DEV comparison",
            "evidence": None,
            "question": "What legal observation or properly evaluated baseline is required next?",
            "limitations": "No evidence of learnability or lack thereof",
        })
    return result


def validate_bank(bank: dict) -> dict:
    if not isinstance(bank, dict) or bank.get("format") != BANK_VERSION:
        raise ContractError("unsupported hypothesis bank version")
    cards = bank.get("hypotheses")
    if not isinstance(cards, list) or not 1 <= len(cards) <= 3:
        raise ContractError("hypothesis bank requires 1-3 candidate ideas")
    if not isinstance(bank.get("sources"), dict):
        raise ContractError("missing evidence source receipts")
    ids = set()
    seed_ids = {x["seed_id"] for x in bank.get("observation_seeds", [])
                if isinstance(x, dict) and isinstance(x.get("seed_id"), str)}
    sources = bank["sources"]
    for c in cards:
        if not isinstance(c, dict):
            raise ContractError("candidate must be an object")
        cid = _text(c, "hypothesis_id")
        if cid in ids:
            raise ContractError("duplicate hypothesis ID")
        ids.add(cid)
        for k in ("research_question", "mechanism", "strongest_alternative",
                  "distinct_prediction", "minimum_test",
                  "if_positive", "if_negative", "legal_information"):
            _text(c, k)
        if c.get("legal_information_status") not in INFO:
            raise ContractError("invalid legal information status")
        if c.get("baseline_status") not in BASELINE:
            raise ContractError("invalid baseline status")
        if c.get("test_cost") not in COST:
            raise ContractError("invalid bounded test cost")
        if c.get("novelty_status") != "UNVERIFIED":
            raise ContractError("metadata/idea card cannot self-certify novelty")
        if c.get("status") not in {"HYPOTHESIZED", "EXPLORATORY_RUN_RECORDED"}:
            raise ContractError("bank cannot self-confirm hypotheses")
        if not isinstance(c.get("source_seed_ids"), list) or not isinstance(c.get("paper_record_ids"), list):
            raise ContractError("missing source IDs")
        if c["source_seed_ids"] and ("seeds" not in sources or
                                      not set(c["source_seed_ids"]).issubset(seed_ids)):
            raise ContractError("source_seed_ids lack existing verified seed references")
        if c["paper_record_ids"] and "literature" not in sources:
            raise ContractError("paper_record_ids lack literature evidence")
        if c.get("uses_data_note") and "data_note" not in sources:
            raise ContractError("data note source is missing")
        if not isinstance(c.get("uses_data_note"), bool):
            raise ContractError("uses_data_note must be boolean")
        if not isinstance(c.get("run_feedback"), list):
            raise ContractError("run_feedback must be a list")
    return bank


def create_bank(project: Path, cards_path: Path, *,
                seed_path: Path | None = None, literature_path: Path | None = None,
                data_note_path: Path | None = None) -> dict:
    """Link at most three AI-authored hypotheses to verifiable receipts, not invented facts."""
    project = project.resolve()
    raw = _load_json(project, cards_path)
    candidates = raw.get("candidates")
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 3:
        raise ContractError("supply 1-3 agent-authored candidate cards")
    if not any((seed_path, literature_path, data_note_path)):
        raise ContractError("at least one independent source pointer is needed")
    seeds, papers = {}, {}
    sources = {"cards": _receipt(project, cards_path)}
    task_context = None
    if seed_path is not None:
        seed = _load_json(project, seed_path)
        if seed.get("format") != SEED_VERSION:
            raise ContractError("unknown seed format")
        c = seed.get("candidate_run")
        r = seed.get("reference_run")
        if not isinstance(c, dict):
            raise ContractError("observation seed lacks verified candidate source")
        c_path = resolve_project_file(project, c["ref"])
        check_receipt(c_path, c["sha256"])
        r_path = None
        if r is not None:
            r_path = resolve_project_file(project, r["ref"])
            check_receipt(r_path, r["sha256"])
        # Recompute from original verified Run; reject forged/tampered summary.
        recomputed = make_observation_seeds(project, c_path, r_path, metric=seed.get("metric"))
        if recomputed != seed:
            raise ContractError("seed summary does not match original verified DEV Run(s)")
        sources["seeds"] = _receipt(project, seed_path)
        seeds = {row["seed_id"]: row for row in seed["seeds"]}
        task_context = (seed["task_id"], seed["protocol_id"])
    if literature_path is not None:
        evidence = _load_json(project, literature_path)
        validate("evidence", evidence)
        sources["literature"] = _receipt(project, literature_path)
        papers = {r["record_id"]: r for r in evidence["records"]}
    if data_note_path is not None:
        sources["data_note"] = _receipt(project, data_note_path)
    hypotheses = []
    used = set()
    for card in candidates:
        if not isinstance(card, dict):
            raise ContractError("candidate card must be an object")
        hid = _text(card, "hypothesis_id")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", hid) or hid in used:
            raise ContractError("duplicate/unsafe hypothesis ID")
        used.add(hid)
        seed_ids = card.get("source_seed_ids", [])
        paper_ids = card.get("paper_record_ids", [])
        note = card.get("uses_data_note", False)
        if not isinstance(seed_ids, list) or not all(isinstance(x, str) and x in seeds for x in seed_ids):
            raise ContractError("unknown observation seed IDs")
        if not isinstance(paper_ids, list) or not all(isinstance(x, str) and x in papers for x in paper_ids):
            raise ContractError("unknown paper record IDs")
        if not isinstance(note, bool) or (note and data_note_path is None):
            raise ContractError("data note source not available")
        if not seed_ids and not paper_ids and not note:
            raise ContractError("every hypothesis needs at least one source-backed pointer")
        info_status = card.get("legal_information_status", "UNKNOWN")
        baseline_status = card.get("baseline_status", "UNKNOWN")
        cost = card.get("test_cost", "UNKNOWN")
        candidate = {
            "hypothesis_id": hid,
            "research_question": _text(card, "research_question"),
            "mechanism": _text(card, "mechanism"),
            "strongest_alternative": _text(card, "strongest_alternative"),
            "distinct_prediction": _text(card, "distinct_prediction"),
            "minimum_test": _text(card, "minimum_test"),
            "if_positive": _text(card, "if_positive"),
            "if_negative": _text(card, "if_negative"),
            "legal_information": _text(card, "legal_information"),
            "legal_information_status": info_status,
            "baseline_status": baseline_status,
            "test_cost": cost,
            "source_seed_ids": list(dict.fromkeys(seed_ids)),
            "paper_record_ids": list(dict.fromkeys(paper_ids)),
            "uses_data_note": note,
            "task_id": card.get("task_id"),
            "protocol_id": card.get("protocol_id"),
            "novelty_status": "UNVERIFIED",
            "status": "HYPOTHESIZED", "run_feedback": [],
        }
        if candidate["task_id"] is not None and not isinstance(candidate["task_id"], str):
            raise ContractError("task_id must be text or null")
        if candidate["protocol_id"] is not None and not isinstance(candidate["protocol_id"], str):
            raise ContractError("protocol_id must be text or null")
        if task_context and (candidate["task_id"] not in (None, task_context[0]) or
                             candidate["protocol_id"] not in (None, task_context[1])):
            raise ContractError("idea Task/Protocol mismatches verified DEV observation")
        hypotheses.append(candidate)
    bank = {
        "format": BANK_VERSION,
        "status": "HYPOTHESIS_BANK_UNVERIFIED",
        "sources": sources,
        "source_truth": {
            "data_run": "METRICS_RECOMPUTED_DEV_ONLY" if seeds else "NOT_AVAILABLE",
            "data_note": "AGENT_NOTE_NOT_RECOMPUTED" if data_note_path else "NOT_AVAILABLE",
            "literature": "METADATA_ONLY" if papers else "NOT_AVAILABLE",
        },
        "observation_seeds": list(seeds.values()),
        "hypotheses": hypotheses,
        "revision": 0,
        "parent_bank_sha256": None,
        "limitations": [
            "Idea generation and source linkage are not hypothesis truth, novelty or publication success",
            "Dev residuals do not establish achievable headroom or causal mechanism",
            "Metadata-only papers do not establish nearest-work non-overlap",
            "No model fitting, external Agent execution or sealed confirmation",
        ],
    }
    return validate_bank(bank)



def verify_bank_sources(project: Path, bank: dict) -> None:
    """Reject stale original Run data, modified seed snapshots and missing paper IDs."""
    validate_bank(bank)
    project = project.resolve()
    for src in bank["sources"].values():
        check_receipt(resolve_project_file(project, src["ref"]), src["sha256"])
    if "seeds" in bank["sources"]:
        seed = _load_json(project, resolve_project_file(project, bank["sources"]["seeds"]["ref"]))
        c = seed.get("candidate_run")
        r = seed.get("reference_run")
        if not isinstance(c, dict):
            raise ContractError("seed missing original DEV Run receipt")
        candidate = resolve_project_file(project, c["ref"])
        check_receipt(candidate, c["sha256"])
        reference = None
        if r is not None:
            reference = resolve_project_file(project, r["ref"])
            check_receipt(reference, r["sha256"])
        if seed != make_observation_seeds(project, candidate, reference, metric=seed.get("metric")):
            raise ContractError("source DEV observation has changed; new hypothesis bank needed")
        if seed["seeds"] != bank["observation_seeds"]:
            raise ContractError("bank seed IDs/results differ from original observations")
    if "literature" in bank["sources"]:
        papers = _load_json(project, resolve_project_file(project, bank["sources"]["literature"]["ref"]))
        validate("evidence", papers)
        allowed = {row["record_id"] for row in papers["records"]}
        for idea in bank["hypotheses"]:
            if not set(idea["paper_record_ids"]).issubset(allowed):
                raise ContractError("bank references unknown literature IDs")

def record_run_feedback(project: Path, bank_path: Path, hypothesis_id: str,
                        run_path: Path, assessment: str) -> dict:
    """Append verified DEV Run evidence in a NEW bank version; never auto-confirm."""
    from core.run_integrity import load_verified_run
    project = project.resolve()
    if assessment not in ASSESSMENTS:
        raise ContractError("unknown, self-declared assessment")
    bank = validate_bank(_load_json(project, bank_path))
    # Source receipts remain stable; stale Run/metadata cannot silently advance.
    verify_bank_sources(project, bank)
    target = next((x for x in bank["hypotheses"] if x["hypothesis_id"] == hypothesis_id), None)
    if target is None:
        raise ContractError("hypothesis ID not in bank")
    ref = _rel(project, run_path)
    run, _ = load_verified_run(project, run_path.resolve())
    if run["status"] != "VALID" or run["split"] not in {"dev", "validation"}:
        raise ContractError("only verified development Runs may inform hypothesis feedback")
    if target.get("task_id") not in (None, run["task_id"]) or target.get("protocol_id") not in (None, run["protocol_id"]):
        raise ContractError("run Task/Protocol mismatch: create a new task-scoped bank revision")
    if any(x["run_id"] == run["run_id"] for x in target["run_feedback"]):
        raise ContractError("duplicate Run feedback; preserve the existing receipt")
    copy = json.loads(json.dumps(bank))
    selected = next(x for x in copy["hypotheses"] if x["hypothesis_id"] == hypothesis_id)
    selected["task_id"], selected["protocol_id"] = run["task_id"], run["protocol_id"]
    selected["run_feedback"].append({
        "run_id": run["run_id"], "run": _receipt(project, run_path),
        "assessment_by_agent": assessment,
        "verified_dev_metrics": run["metrics"],
        "evidence_scope": "DEV_METRIC_RECOMPUTED_NOT_MECHANISM_CONFIRMED",
    })
    selected["status"] = "EXPLORATORY_RUN_RECORDED"
    copy["revision"] += 1
    copy["parent_bank_sha256"] = fingerprint_file(bank_path)
    return validate_bank(copy)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evidence-linked hypothesis seeds/bank, no scientific confirmation")
    sub = parser.add_subparsers(dest="action", required=True)
    s = sub.add_parser("seed")
    s.add_argument("--project", type=Path, required=True)
    s.add_argument("--candidate-run", type=Path, required=True)
    s.add_argument("--reference-run", type=Path)
    s.add_argument("--metric")
    s.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("build")
    b.add_argument("--project", type=Path, required=True)
    b.add_argument("--cards", type=Path, required=True)
    b.add_argument("--seeds", type=Path)
    b.add_argument("--literature", type=Path)
    b.add_argument("--data-note", type=Path)
    b.add_argument("--out", type=Path, required=True)
    f = sub.add_parser("feedback")
    f.add_argument("--project", type=Path, required=True)
    f.add_argument("--bank", type=Path, required=True)
    f.add_argument("--hypothesis-id", required=True)
    f.add_argument("--run", type=Path, required=True)
    f.add_argument("--assessment", choices=sorted(ASSESSMENTS), required=True)
    f.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        project = args.project.resolve()
        output = args.out.resolve()
        if output == project or not output.is_relative_to(project):
            raise ContractError("output must be project-contained")
        if args.action == "seed":
            result = make_observation_seeds(project, args.candidate_run, args.reference_run, metric=args.metric)
        elif args.action == "build":
            result = create_bank(project, args.cards, seed_path=args.seeds,
                                 literature_path=args.literature, data_note_path=args.data_note)
        else:
            result = record_run_feedback(project, args.bank, args.hypothesis_id,
                                         args.run, args.assessment)
        _write_new(output, result)
        print(json.dumps({"output": str(output), "status": result["status"],
                          "hypotheses": len(result.get("hypotheses", [])),
                          "training_performed": False, "novelty_confirmed": False}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"hypothesis bank failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
