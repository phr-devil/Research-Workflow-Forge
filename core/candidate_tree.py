"""AIDE-inspired parent/child run lineage over the existing versioned Journal.

Pure structure check: does not assign scientific merit or call a coding agent.
"""
from __future__ import annotations
from pathlib import Path
from core.journal import candidate_journal

KINDS = {"DRAFT", "DEBUG", "IMPROVE", "UNSPECIFIED"}

def candidate_tree(project: Path) -> dict:
    data = candidate_journal(project)
    nodes = {r["run_id"]: r for r in data["runs"] if r["current_protocol"]}
    issues = list(data["warnings"])
    if len(nodes) != sum(1 for r in data["runs"] if r["current_protocol"]):
        issues.append("Duplicate run_id in current protocol")
    for key, run in nodes.items():
        parent = run.get("parent_run_id")
        kind = str(run.get("branch_kind", "UNSPECIFIED")).upper()
        if kind not in KINDS:
            issues.append(f"{key}: invalid branch kind {kind}")
        if parent and (parent == key or parent not in nodes):
            issues.append(f"{key}: missing or self-parent reference")
        if kind in {"DEBUG", "IMPROVE"} and not parent:
            issues.append(f"{key}: DEBUG/IMPROVE requires a valid parent")
    for key in nodes:
        seen, ptr = set(), key
        while ptr and ptr in nodes:
            if ptr in seen:
                issues.append(f"{key}: candidate parent cycle")
                break
            seen.add(ptr)
            ptr = nodes[ptr].get("parent_run_id")
    return {"task_id": data["active_task_id"], "protocol_id": data["active_protocol_id"],
            "candidates": list(nodes.values()), "issues": sorted(set(issues)),
            "status": "NEEDS_REPAIR" if issues else "STRUCTURAL_PASS",
            "notes": "Lineage and raw references are not measured performance evidence"}
