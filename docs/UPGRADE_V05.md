# v0.5 — From structural guidance to bounded DEV evidence

## P0 repaired

- Data gate: core/data_access.py binds manifest DEV role, explicit local_path, SHA256 and dataset_id. Refuses aliases to declared SEALED_CONFIRM and non-DEV entries; logs attempted DEV access. tools.data_audit CLI rejects unbound CSV.
- Raw Run integrity: core/run_integrity.py checks every referenced log/prediction file under the project against its SHA256. Older structural-only Run references do not count as verified baseline events; migrate by preserving genuine original artifacts and adding hashes, never fabricating logs.
- Champion: core/champion.py compares only development VALID runs with verified raw receipts, matching task/protocol/dataset/evaluator/group/samples/legal inputs, and explicit Task metric_direction. BASELINE_VALID never silently promotes. Applying writes CHAMPION_SELECTED to EVENTS and an updated STATE receipt.
- Recovery: core/recovery.py previews interrupted events and can replay exactly one unambiguous SHA-valid event with STATE backup. Multiple events, missing/changed artifacts or Champion interruption need manual reconciliation; it is not a transactional database.
- Candidate parent graph: core/candidate_tree.py checks DRAFT, DEBUG, IMPROVE relations; has no scientific selection authority.

## P1 small real development vertical slice

- tools/experiment_runner.py is a constrained local CPU grouped classifier runner: sklearn dummy, logistic, forest; max 10k rows and 64 numeric features, fixed group-disjoint split, train-only scaling/imputation, frozen evaluator source fingerprint, exact prediction/log SHA evidence. A permission flag is necessary but not sufficient: agents must verify the original user's actual authorization.
- No arbitrary Python/shell execution, LLM generation, GPU, external data download, sealed evaluation, statistical significance inference or guaranteed strong baseline. Tests use tiny SYNTHETIC datasets only.
- Grouped development Pilot does not replace task-specific scientific verification, parameter fair tuning, or independent external confirmation.

## Next

Add trusted official dataset metadata and task-specific split audits; integrate a permissioned Codex/WorkBuddy backend behind the existing protected evaluator, with raw execution and actual wall-clock budget enforcement; add full-text paper-to-claim evidence and same-budget prospective workflow evaluations.
