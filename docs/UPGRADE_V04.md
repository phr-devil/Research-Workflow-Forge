# v0.4 | Scoped pivots, evidence receipts and search correctness

This is a compatible controller upgrade, NOT a seven-gate pipeline. JSON schema_version remains 0.1; state can have additional receipt fields. No training or scientific outcome is claimed.

## Task/protocol lifecycle

1. Register an actual ACTIVE Task: python -m core.cli record --dir projects/demo --event TASK_DEFINED --artifact projects/demo/tasks/T1.json --note "Real protocol"
2. Forge records active_task_path, SHA-256, canonical task fingerprint, and protocol ID. When later recording a review, plan or Run, Forge checks the original file and Task version again.
3. For an existing v0.3 state lacking a bound task path, re-register the *original* ACTIVE Task with TASK_DEFINED. This retires the old best_valid_run_id; old evidence remains in history.
4. For a task change, write a *new* ACTIVE Task file and a decision artifact of type TASK_PIVOT (different task ID) or PROTOCOL_REVISED (same task ID; changed protocol). Include old/new IDs, actual SHA-256 of the new Task file, reason, supporting evidence and original user-approval reference. This reference is NOT a grant of permission and must be independently checked.
5. Record the transition: python -m core.cli record --dir projects/demo --event TASK_PIVOT --artifact projects/demo/DECISION.json --note "Scoped pivot with evidence"
6. Never overwrite the original Task to conceal a change, and never erase negative Runs. A transition resets only the active Champion pointer. Old Runs stay visible in the journal and are ineligible for comparison under the new protocol.

Check state: python -m core.cli check-task --dir projects/demo
Selection trail: python -m core.cli selection --dir projects/demo
Candidate trail: python -m core.cli journal --dir projects/demo
Event consistency: python -m core.cli history --dir projects/demo

All event writes acquire a Windows/POSIX process lock. If the event log and STATE disagree after a crash, the controller stops for recovery rather than claiming a clean state.

## Search and novelty

- Search starts at 1900 by default so older foundational work is not excluded by a silent four-year default. User-supplied --start-year narrows explicitly.
- The Forge adapter reuses ResearchStudio ranking, with conservative DOI-conflict protection in adapters/paper_merge.py; the vendored source stays unchanged.
- EVIDENCE includes source failures, DOI collisions, searched years and a NON_EXHAUSTIVE coverage disclaimer.
- NOVELTY candidates are for *screening*, never certified closest predecessors. The output includes omitted record IDs. Manually choose named papers by repeated --candidate-id arguments.
- Full-text nearest-method reviews and source-corroborated claim comparisons remain necessary before any novelty conclusion.

## Read-only development-data preflight

    python -m tools.data_audit --manifest projects/demo/DATA_MANIFEST.json --out projects/demo/DATA_AUDIT.json
    python -m tools.data_audit --dev-csv projects/demo/dev.csv --group-col subject --label-col activity --id-col sample_id

Only an explicitly designated DEV CSV is inspected; no sealed file is read by this helper. No normalization, parameter fitting or algorithm training is performed. The preflight cannot prove the scientific protocol correct.

## Execution boundaries

v0.4 has no autonomous GPU/CPU fitting runner, no independently confirmed scientific novelty and no empirical workflow success-rate comparison. Deterministic routing fixtures in evals/ are software regression tests only. Do not interpret a structural PASS as scientific success.
