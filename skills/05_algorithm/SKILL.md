---
name: research-algorithm-execution
description: Build, debug and compare algorithms with reproducible Runs and bounded iterations.
---
# 05 | Algorithm implementation and feedback

Shared rules: [EXECUTION_POLICY](../../docs/EXECUTION_POLICY.md). Execution requires real Task, protected evaluator, eligible DEV data and actual authorization.

- Work in one coherent **DRAFT → DEBUG / IMPROVE → directed test → record** batch. Diagnose the earliest engineering failure, repair locally and test affected interfaces; do not run unrelated full tests after every edit.
- Preserve task/protocol/data/code/evaluator IDs, raw stdout/predictions, SHA receipts, candidate parent and negative Runs. No cherry-picked seed or evaluator changes disguised as improvement.
- Current **bounded** engine: `python -m tools.experiment_runner` for opt-in grouped DEV dummy/logistic/forest; no arbitrary Agent-produced code or GPU. Then `core.cli record`, `core.cli compare` and explicit `core.cli champion`. `core.cli candidates` shows lineage, not a complete AIDE executor.
- More runs are justified only by a different mechanism, unfair baseline, inadequate convergence, uncertainty or another decision-changing reason. A valid negative routes to 06 rather than endless hyperparameter churn.

**Handoff:** real RunRecord / NOT_RUN, compatible Champion comparison, mechanism-level observation and next discriminating action.
