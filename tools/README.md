# Planned research tools

**Already implemented:** python -m core.cli (init, route, record, validate) only. These are offline deterministic utilities, not search, experiment, training or confirmation tools.

**Next interfaces:**
- data_audit: official manifest, file integrity, schema, true labels/independent groups, holdout eligibility.
- experiment_runner: fixed evaluator and protected split, bounded authorized execution, actual command/seed/hardware logs, code/dataset/evaluator versions.
- result_tracker: only compare compatible task/protocol metrics, retain negative candidates and group-level predictions, resume from valid state.
- claim_checker: named nearest prior work plus source-backed evidence, frozen protocol and untouched independent units.

Prefer existing verified modules (MLflow/DVC, AIDE journal, PaperQA2) over speculative reimplementation when the concrete need arises. Scientific correctness and human authorization are separate from structural tests.
