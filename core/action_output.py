"""Advisory next-response gate. No side effects, user-message verification or permission grant.

The Agent must inspect original user authorization; caller-provided booleans are
NOT trusted proof. This helper prevents obvious response-format contradictions.
"""
from __future__ import annotations


def output_mode(*, authorized: bool, user_choice_required: bool = False,
                major_task_change: bool = False, project_stop: bool = False,
                manuscript_work: bool = False, summary_reviewed: bool = False,
                explicit_writing_permission: bool = False,
                has_next_action: bool = True) -> dict:
    fields = locals()
    if any(type(value) is not bool for value in fields.values()):
        raise TypeError("All output-mode conditions must be explicit booleans")
    if not has_next_action:
        return {"mode": "NO_NEXT_ACTION", "agent_instruction_allowed": False,
                "note": "No next step is actually needed"}
    reasons = []
    if not authorized:
        reasons.append("ORIGINAL_USER_AUTHORIZATION_MISSING_OR_UNVERIFIED")
    if user_choice_required or major_task_change or project_stop:
        reasons.append("USER_OWNS_DECISION")
    if manuscript_work and not (summary_reviewed and explicit_writing_permission):
        reasons.append("MANUSCRIPT_WRITING_LOCKED")
    if reasons:
        return {"mode": "USER_DECISION_REQUIRED", "agent_instruction_allowed": False,
                "reason": ",".join(reasons),
                "output": "RECOMMENDATION+REASON | OPTIONS | USER_CHOICE_NEEDED"}
    return {"mode": "AGENT_DECIDABLE", "agent_instruction_allowed": True,
            "output": "DECISION+EVIDENCE | NEXT_AGENT_INSTRUCTION",
            "note": "Only within original, verified user authorization; no action is executed"}
