# Trusted DEV metric and external-agent handoff · v0.7

Reportable DEV metrics are independently recomputed from SHA-bound DEV ground truth. Artifact hashes alone do not verify metrics.

## Standard classification receipt

An ACTIVE Task specifies protocol_id, metric, legal_inputs, group_split and dataset ID. DATA_MANIFEST binds DEV dataset_id, local_path, SHA-256, label_column, group_column and optionally sample_id_column.

VALID Run.json must reference hashed raw artifacts and metric_spec:
- format = forge-dev-classification-v1
- predictions_ref: project-relative hashed predictions.json
- manifest_ref: project-relative DATA_MANIFEST.json
- manifest_sha256: exact manifest hash
- dataset_id: DEV dataset declared in manifest and Task

predictions.json is a list of {row_index:int, group:string, truth:string, prediction:string, sample_id?:string}. row_index identifies the original DEV CSV row. The verifier independently checks truth/group/sample IDs from original DEV CSV. A frozen GroupShuffleSplit(seed=42, test_size=.25) regenerates held-out row IDs; cherry-picked indices are rejected. sample_ids_hash uses canonical sorted true sample IDs (or original row indices when there is no ID column).

Only macro_F1 and balanced_accuracy are supported. Recalculation tolerance is 1e-6; task-specific scientific conclusions remain separate.

## External Agent handoff

1. Codex/WorkBuddy/AIDE runs in a separately secured DEV-only workspace with actual user permission. Forge NEVER executes arbitrary Agent-produced Python.
2. Save actual source and standard predictions JSON under the project.
3. Import: `python -m adapters.agent_bridge --project PROJECT --manifest PROJECT/DATA_MANIFEST.json --dataset-id D --run-id R2 --source-code PROJECT/model.py --predictions PROJECT/predictions.json --measured-wall-seconds 15.2`.
4. Register RUN.json using `python -m core.cli record --dir PROJECT --event RUN_RESULT --artifact PROJECT/runs/R2/RUN.json --note "Verified prediction arithmetic"`.
5. Use `core.cli champion` preview and explicit `--apply` for provisional DEV selection. Compare requires `core.cli compare --dir PROJECT ...`.

This does not prove external code was executed or trained only on DEV, nor that saved source corresponds to predictions. A true OS/container sandbox and execution attestation remain future work. Sealed Runs through development events are rejected. Independent confirmation is unavailable.

## Backward compatibility

V0.6 hashed-log-only Runs remain historical but are not trusted for newly verified metrics/Champion. NEVER invent missing predictions. Legacy projects must preview/apply `core.cli migrate-ledger --dir PROJECT` before new events. Anchoring cannot prove pre-migration history authenticity.
