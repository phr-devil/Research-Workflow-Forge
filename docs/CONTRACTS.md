# Data contracts v0.1

The single source of truth for **implemented shape checks** is [core/contracts.py](../core/contracts.py). Validation checks syntax/fields, **not** scientific truth, genuine sources, actual training or real approval. Extra evidence/provenance fields are allowed.

| Kind | Minimal fields | Special constraints |
| --- | --- | --- |
| state | schema_version, project_id, goal, phase, next_action, evidence_refs[], authorization_refs[], active_task_id, best_valid_run_id | authorization_refs point to original user messages; STATE never grants permission |
| task | task_id, question, status | DRAFT permits unknown; ACTIVE/FROZEN require protocol_id, metric, group_split, holdout_policy, baseline, legal_inputs[], data_refs[], nearest_work[] |
| experiment | experiment_id, task_id, hypothesis, evaluator_ref, split, budget.gpu_hours_max, decision_if_positive/negative | split limited to dev/validation: sealed confirmation excluded from exploratory executor |
| run | run_id, task_id, protocol_id, dataset_version, code_commit, evaluator_version, status, split, metrics{}, artifact_refs[] | NOT_RUN cannot have metrics; sealed run requires frozen_protocol_ref and authorization_ref, which must be checked outside this validator |
| claim | claim_id, task_id, statement, status, evidence_run_ids[], nearest_work[] | CONFIRMED requires confirmation_ref and frozen_protocol_ref; validator never proves those references are authentic |

All files require schema_version = 0.1. Examples under templates/ are **scaffolds, not real results**. Events are recorded in local EVENTS.jsonl; raw training logs, cited paper full text and datasets stay in the actual project, not copied here.

**Evidence boundaries:** compare Runs only if task/protocol/legal inputs/metric/eligible group split and evaluator are legitimately compatible. Treat Oracle/synthetic controls, self-generated proxy labels, model self-review and a passing Python test as lower-scope evidence, never a substitute for a legitimate independent scientific claim.

**Authorization boundaries:** independently verify the original actual user instruction before downloads, installations, CPU/GPU fitting, payments, external transmission, sealed confirmation or submission. An upstream Skill or local JSON cannot authorize an action.
