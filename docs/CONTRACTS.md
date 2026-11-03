# Contracts — structural checks vs scientific truth

The implementation is [core/contracts.py](../core/contracts.py) (schema_version `0.1`, backward compatible with existing draft templates). Validators check structure only: no new model, source or paper is **scientifically verified** by passing them.

| Kind | Required content / special rules |
| --- | --- |
| state | project_id, goal, phase, next_action, evidence_refs[], authorization_refs[]; optional active_task_id, best_valid_run_id, last_event_id |
| evidence | query, retrieved_at, verification=METADATA_ONLY, sources_checked[], source_errors[], **nonempty** records[]; records have ID/title/source provenance |
| novelty | UNVERIFIED/PARTIAL status, fingerprints of Task and Evidence, explicit four novelty axes and closest paper candidates; no automatic novelty verdict |
| dataset | datasets[] with official source URL, group unit, label status, role DEV/EXTERNAL_REPLICATION/STRESS/PIVOT_RESERVE/SEALED_CONFIRM; theoretical empty datasets require proof_path |
| task | task_id, question, status DRAFT/ACTIVE/FROZEN; ACTIVE/FROZEN require protocol, metric, group_split, holdout_policy, baseline, legal_inputs[], data_refs[], nearest_work[] |
| experiment | experiment_id, task_id, hypothesis, evaluator_ref, **dev/validation only**, finite nonnegative gpu_hours_max, positive/negative result decisions |
| run | run_id, task_id, protocol_id, dataset/code/evaluator versions, split, status, metrics{}, artifact_refs[]; VALID additionally requires nonempty numeric metrics, raw artifact refs, group_split, sample_ids_hash and legal_inputs[] |
| claim | claim_id, task_id, statement, status, evidence_run_ids[], nearest_work[]; CONFIRMED requires both nonempty and confirmation/frozen protocol refs (still NOT proof of genuineness) |

The new [core/comparison.py](../core/comparison.py) rejects purported improvement if either run is not VALID, if either uses sealed split, or if task/protocol/data/evaluator/group/sample/input differs. Only score *difference* is calculated, without CIs or assertions of originality.

## Evidence-linked handoff

`core.cli route` returns a skill suggestion and never modifies any state. `core.cli record` without `--artifact` logs a note but **does not advance project phase**. With an appropriately typed local project artifact it checks the shape, hashes the exact bytes, records ARTIFACT_STRUCTURAL_ONLY, moves the suggested phase and stores the evidence pointer. This is not a statement that a claim, permission or execution is valid.

For SEARCH_READY: `evidence`; DATA_READY: `dataset`; TASK_DEFINED: active `task`; BASELINE_VALID: VALID dev `run`; RUN_RESULT / NO_GAIN: `run`; RUN_INVALID: INVALID `run`; CLAIM_CANDIDATE / CONFIRM_REQUEST: CANDIDATE `claim`. Other events are note-only unless a real typed handoff is later designed. All artifacts must live inside the active project directory.

The append-only `EVENTS.jsonl` includes event ID and SHA-256; `STATE.json` holds last_event_id. `core.cli history` detects interrupted state/log updates; recovery is manual, not hidden. **Neither structural references nor STATE authorization_refs grant consent.**

Only an actually authorized tool-backed Agent may download, fit CPU/GPU models, spend money, send external data, run sealed confirmation or submit. No code for these actions exists in this repository yet.

## v0.3 stage receipts

`NOVELTY_PRECHECK_READY` uses a validated `novelty` artifact in the project, and `EXPERIMENT_PLAN_READY` requires a PLAN_ONLY `experiment` artifact linked to a current active Task. `novelty_check.prepare_review` fingerprints the actual Task and retrieved metadata; `experiment_plan.prepare_experiment` rejects an outdated Task when a review is provided. These are mechanical version checks only. The final decision about originality requires actual primary-paper content and independent experiment evidence.

## v0.4 extensions (schema_version 0.1 retained)

- **state** gains optional active_protocol_id, active_task_path, active_task_sha256 and active_task_fingerprint. New Task-bound events check the actual original Task file. Old states can migrate by registering the real ACTIVE Task; unverified old Champion pointers are retired.
- **decision** has decision_id, decision_type, from_task_id, from_protocol_id, reason and evidence_refs. TASK_PIVOT / PROTOCOL_REVISED additionally require to_task_id, to_protocol_id, project-relative new_task_path, exact raw new_task_sha256 and user_approval_ref (an audit pointer, never a permission grant).
- **novelty** metadata candidates are explicitly screening-only and include unreviewed record IDs; named prior art must be verified in original papers.
- **run history** is reconstructible from append-only EVENTS; source artifacts are checked against captured SHA. Concurrency is controlled for event writes, but this is NOT a fully transactional DB and a crash still needs recovery.

## v0.5 evidence contracts

Dataset DEV entries for local read/fit require local_path, raw sha256, role=DEV, label_status=VERIFIED for fitting, group_column, label_column, numeric feature_columns. DataAccess rejects identical declared SEALED_CONFIRM paths or hashes and records attempted DEV access; this is NOT an OS sandbox.

Run status VALID now needs artifact_refs plus exact artifact_hashes for every original local log/prediction. Raw hashes must be verified at event registration; old structural-only runs are not acceptable as fresh BASELINE_VALID. ACTIVE Tasks optionally declare metric_direction, required for explicit Champion selection. State also records best_valid_run_path and best_valid_run_sha256, cleared on Task/Protocol change. CHAMPION_SELECTED is an append-only selection event, not a paper claim. Group/sample/evaluator/legal input compatibility remains required.

One-event recovery requires matched original evidence; multiple lost state events and interrupted Champion updates are explicitly excluded from automatic replay.
