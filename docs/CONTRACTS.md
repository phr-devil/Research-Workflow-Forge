# Contracts — structural checks vs scientific truth

The implementation is [core/contracts.py](../core/contracts.py) (schema_version \`0.1\`, backward compatible with existing draft templates). Validators check structure only: no new model, source or paper is **scientifically verified** by passing them.

| Kind | Required content / special rules |
| --- | --- |
| state | project_id, goal, phase, next_action, evidence_refs[], authorization_refs[]; optional active_task_id, best_valid_run_id, last_event_id |
| evidence | query, retrieved_at, verification=METADATA_ONLY, sources_checked[], source_errors[], **nonempty** records[]; records have ID/title/source provenance |
| dataset | datasets[] with official source URL, group unit, label status, role DEV/EXTERNAL_REPLICATION/STRESS/PIVOT_RESERVE/SEALED_CONFIRM; theoretical empty datasets require proof_path |
| task | task_id, question, status DRAFT/ACTIVE/FROZEN; ACTIVE/FROZEN require protocol, metric, group_split, holdout_policy, baseline, legal_inputs[], data_refs[], nearest_work[] |
| experiment | experiment_id, task_id, hypothesis, evaluator_ref, **dev/validation only**, finite nonnegative gpu_hours_max, positive/negative result decisions |
| run | run_id, task_id, protocol_id, dataset/code/evaluator versions, split, status, metrics{}, artifact_refs[]; VALID additionally requires nonempty numeric metrics, raw artifact refs, group_split, sample_ids_hash and legal_inputs[] |
| claim | claim_id, task_id, statement, status, evidence_run_ids[], nearest_work[]; CONFIRMED requires both nonempty and confirmation/frozen protocol refs (still NOT proof of genuineness) |

The new [core/comparison.py](../core/comparison.py) rejects purported improvement if either run is not VALID, if either uses sealed split, or if task/protocol/data/evaluator/group/sample/input differs. Only score *difference* is calculated, without CIs or assertions of originality.

## Evidence-linked handoff

\`core.cli route\` returns a skill suggestion and never modifies any state. \`core.cli record\` without \`--artifact\` logs a note but **does not advance project phase**. With an appropriately typed local project artifact it checks the shape, hashes the exact bytes, records ARTIFACT_STRUCTURAL_ONLY, moves the suggested phase and stores the evidence pointer. This is not a statement that a claim, permission or execution is valid.

For SEARCH_READY: \`evidence\`; DATA_READY: \`dataset\`; TASK_DEFINED: active \`task\`; BASELINE_VALID: VALID dev \`run\`; RUN_RESULT / NO_GAIN: \`run\`; RUN_INVALID: INVALID \`run\`; CLAIM_CANDIDATE / CONFIRM_REQUEST: CANDIDATE \`claim\`. Other events are note-only unless a real typed handoff is later designed. All artifacts must live inside the active project directory.

The append-only \`EVENTS.jsonl\` includes event ID and SHA-256; \`STATE.json\` holds last_event_id. \`core.cli history\` detects interrupted state/log updates; recovery is manual, not hidden. **Neither structural references nor STATE authorization_refs grant consent.**

Only an actually authorized tool-backed Agent may download, fit CPU/GPU models, spend money, send external data, run sealed confirmation or submit. No code for these actions exists in this repository yet.
