"""Deterministic event router; no code execution or implied authorization."""
from __future__ import annotations
from dataclasses import dataclass
from core.contracts import validate_state

@dataclass(frozen=True)
class Route:
    phase: str
    skill: str
    next_action: str
    handoff: str

ROUTES: dict[str, Route] = {
    "NEW_DIRECTION": Route("DISCOVERY", "skills/01_search/SKILL.md", "Build source-backed opportunity map", "OPPORTUNITIES"),
    "SEARCH_READY": Route("EVIDENCE", "skills/02_evidence_data/SKILL.md", "Check primary literature and dataset roles", "EVIDENCE_AND_DATA_MANIFEST"),
    "DATA_READY": Route("PROBLEM", "skills/03_problem_design/SKILL.md", "Form one scientific task and reserve", "TASK"),
    "NOVELTY_PRECHECK_READY": Route("PROBLEM", "skills/03_problem_design/SKILL.md", "Compare primary nearest papers and refine falsifiable task", "NOVELTY"),
    "TASK_DEFINED": Route("FEASIBILITY", "skills/04_feasibility/SKILL.md", "Audit protocol and plan simplest valid baseline", "EXPERIMENT_PLAN"),
    "EXPERIMENT_PLAN_READY": Route("ALGORITHM", "skills/05_algorithm/SKILL.md", "Review experiment and real authorization; do not assume fitting is approved", "EXPERIMENT_PLAN"),
    "BASELINE_VALID": Route("ALGORITHM", "skills/05_algorithm/SKILL.md", "Develop traceable Champion and Challenger", "RUN"),
    "RUN_RESULT": Route("DECISION", "skills/06_decision/SKILL.md", "Interpret result and choose next evidence-producing action", "DECISION"),
    "NO_GAIN": Route("DECISION", "skills/06_decision/SKILL.md", "Diagnose fairness, capacity, mechanism and alternatives", "DECISION"),
    "RUN_INVALID": Route("DECISION", "skills/06_decision/SKILL.md", "Isolate invalid evidence and repair", "DECISION"),
    "CODE_FAILURE": Route("DECISION", "skills/06_decision/SKILL.md", "Reproduce earliest error, repair and verify", "DECISION"),
    "TASK_BLOCKED": Route("DECISION", "skills/06_decision/SKILL.md", "Reframe or seek genuinely different task", "DECISION"),
    "CLAIM_CANDIDATE": Route("CONFIRMATION", "skills/07_confirmation/SKILL.md", "Freeze claim/protocol and plan independent verification", "CLAIM_EVIDENCE"),
    "CONFIRM_REQUEST": Route("CONFIRMATION", "skills/07_confirmation/SKILL.md", "Check real approval and untouched confirmation resources", "CLAIM_EVIDENCE"),
}

def route(state: dict, event: str) -> dict:
    validate_state(state)
    if event not in ROUTES:
        raise ValueError(f"unknown event {event}; valid: {', '.join(sorted(ROUTES))}")
    dest = ROUTES[event]
    warnings = []
    if event in {"BASELINE_VALID", "RUN_RESULT", "NO_GAIN", "CLAIM_CANDIDATE", "CONFIRM_REQUEST"} and not state.get("active_task_id"):
        warnings.append("No active_task_id: verify real TaskSpec/protocol")
    if event in {"CLAIM_CANDIDATE", "CONFIRM_REQUEST"}:
        warnings.append("Planning only: verify frozen protocol, eligible untouched holdout and separate real authorization")
    warnings.append("STATE authorization_refs are pointers, NOT permission; check the original user instruction")
    return {"event": event, "phase": dest.phase, "skill": dest.skill,
            "next_action": dest.next_action, "handoff": dest.handoff,
            "warnings": warnings, "executes_external_action": False}
