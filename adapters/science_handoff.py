"""Read-only PD-RW scientific-decision handoff (separate from DEV metric bridge).

Checks evidence-file receipts and minimal hypothesis/contrast fields.
Does NOT rank scientific importance, attest original literature, authorize work,
execute code, inspect sealed data or certify Q2 potential.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from core.contracts import ContractError
from core.receipts import check_receipt, resolve_project_file

REQUIRED = (
    "format", "task_id", "research_question", "importance_rationale",
    "named_nearest_original", "claimed_knowledge_delta", "strongest_alternative",
    "distinct_prediction", "data_discriminability_limitations",
    "independent_group_unit", "legal_information_contract",
    "next_discriminating_test", "pd_rw_scientific_choice",
    "authorization_reference",
)
ROLES = {"DEV", "PUBLIC_METADATA"}


def review_science_handoff(project: Path, packet: dict) -> dict:
    if not isinstance(packet, dict) or packet.get("format") != "pd-rw-science-handoff-v1":
        raise ContractError("unsupported PD-RW science handoff")
    for key in REQUIRED:
        if not isinstance(packet.get(key), str) or not packet[key].strip():
            raise ContractError("missing nonempty scientific handoff field: " + key)
    evidence = packet.get("source_receipts")
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 8:
        raise ContractError("1..8 DEV/public metadata source receipts required")
    root = project.resolve(strict=True)
    if not root.is_dir():
        raise ContractError("project must be a directory")
    verified = []
    seen = set()
    for item in evidence:
        if not isinstance(item, dict) or item.get("role") not in ROLES:
            raise ContractError("science handoff forbids sealed source roles")
        ref, digest = item.get("path"), item.get("sha256")
        if not isinstance(ref, str) or not ref.strip():
            raise ContractError("source needs a project-relative path")
        if not isinstance(digest, str) or len(digest) != 64 or any(
                c not in "0123456789abcdefABCDEF" for c in digest):
            raise ContractError("source needs a SHA256 receipt")
        try:
            file = resolve_project_file(root, ref)
            if not file.is_file() or file.stat().st_size > 8 * 1024 * 1024:
                raise ContractError("science reference must be an existing bounded DEV/public metadata file")
            check_receipt(file, digest.lower())
        except (ValueError, OSError) as exc:
            raise ContractError("invalid or changed source receipt: " + ref) from exc
        if file in seen:
            raise ContractError("duplicate science source receipt")
        seen.add(file)
        verified.append({"role": item["role"],
                         "path": file.relative_to(root).as_posix(),
                         "sha256": digest.lower()})
    return {
        "status": "SCIENCE_HANDOFF_FILE_HASHES_VERIFIED_ONLY",
        "task_id": packet["task_id"],
        "pd_rw_scientific_choice_declared": packet["pd_rw_scientific_choice"],
        "source_receipts": verified,
        "research_problem_selected_by_forge": False,
        "scientific_value_ranked_by_forge": False,
        "journal_quartile_verified": False,
        "q2_potential_verified": False,
        "original_user_authorization_verified": False,
        "independent_confirmation_performed": False,
        "next_action": "CHECK ORIGINAL USER AUTHORIZATION AND USE RELEVANT SKILL",
        "note": ("Source hashes only. Paper truth, sufficient independent groups, "
                 "causal identification, scientific priority and permissions require "
                 "separate original review; do not substitute Forge cheap-probe order.")
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    args = parser.parse_args(argv)
    project = args.project.resolve()
    src = args.packet.resolve()
    if not src.is_relative_to(project) or not src.is_file():
        parser.error("packet must be an existing file under --project")
    result = review_science_handoff(project, json.loads(src.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
