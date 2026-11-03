# Active research contracts · schema_version 0.1

**Source of truth:** [core/contracts.py](../core/contracts.py). Passing a shape check does *not* validate real labels, provenance, scientific truth or user authorization.

| Artifact | Purpose and additional checks |
| --- | --- |
| `STATE.json` | project goal, current Task/protocol, evidence refs, Champion pointers and last event |
| `EVIDENCE.json` | primary metadata provider, DOI/URL/version, source failures; metadata never proves novelty |
| `DATA_MANIFEST.json` | DEV/SEALED roles, official source, labels/group units; local DEV file identity/role/hash checked by `core.data_access` |
| `TASK.json` | DRAFT may contain UNKNOWN; ACTIVE requires protocol, metric, independent split, legal inputs, baseline and holdout policy |
| `EXPERIMENT.json` | positive/negative decisions, evaluator, DEV-only split and bounded plan; `PLAN_ONLY` never authorizes fitting |
| `RUN.json` | dataset/code/evaluator/protocol, status/metric; actual Run promotion requires all raw artifact hashes and compatible groups/samples/inputs |
| `CLAIM.json` | novelty and original evidence links; independent confirmation, not development-only score |
| `DECISION.json` | evidence-backed Task pivot/protocol revision, old/new IDs and original user approval *reference* |

`EVENTS.jsonl` is append-only; a **note-only event does not advance** scientific phase. The controller checks versioned artifact receipts. `DATA_ACCESS.jsonl` records DEV accesses; `core.cli journal/selection/candidates` reconstruct history. `core.cli champion --apply` separately selects a better comparable Run; `BASELINE_VALID` alone never does. `core.cli recover` can replay only one unambiguous SHA-backed event, otherwise requires manual review.

Structural tests, metadata, synthetic fixtures and a positive DEV score do not confirm scientific claims. Real original-paper novelty and untouched eligible holdouts remain separate prerequisites. Shared execution/Token/output defaults live only in [EXECUTION_POLICY.md](EXECUTION_POLICY.md); version-specific details in [UPGRADE_V04](UPGRADE_V04.md) and [UPGRADE_V05](UPGRADE_V05.md).

## v0.7 receipt extensions

VALID classification Runs for trustworthy performance need a `metric_spec` with format, predictions_ref, manifest_ref/sha256, and dataset_id. Every row_index, truth, group and optional stable sample_id is checked against independently SHA-pinned DEV ground truth and the frozen grouped evaluation split. Only macro_F1/balanced_accuracy are supported. STATE stores ledger_length/head_digest; EVENTS stores seq/prev_digest/event_digest. CLI compare verifies files, not bare JSON. Historical nonconforming Runs remain viewable but are not trusted for promotion. See `docs/ARTIFACT_CONTRACT.md` and `docs/UPGRADE_V07.md`.
