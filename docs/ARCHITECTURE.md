# Architecture: one controller, three engines, seven capabilities

## Design, not a rigid seven-step pipeline

- **Controller (core/router.py + State):** maps a real event to one skill; preserves project continuity and constraints. It is deterministic and **does not** call LLMs, GitHub, web, GPUs or other external tools.
- **A | Opportunity Engine:** 01 search, 02 primary evidence/data resources, 03 falsifiable scientific problem. Free exploration with explicit UNKNOWNs; narrow to one actual primary Task without prematurely requiring a positive model result.
- **B | Development Engine:** 04 evaluator/data validity/credible baseline, 05 code + experiment. Protected protocol/split and writable model scopes; Champion/Challenger with real execution traces.
- **C | Decision & Confirmation:** 06 scoped repair/continue/pivot, 07 frozen independent claim assessment. A mechanism failure may return to 05; a task-level blocker may return to 03/01 while reusing legitimate data/assets.

## Event graph

NEW_DIRECTION → 01 → SEARCH_READY → 02 → DATA_READY → 03 → TASK_DEFINED → 04 → BASELINE_VALID → 05

05 → RUN_RESULT / NO_GAIN / CODE_FAILURE / RUN_INVALID → 06 → 05 (repair/next mechanism), or → 03 (new actual Task)

06 / 05 → CLAIM_CANDIDATE → 07 (plan only) → real approval + eligible sealed evidence → independent confirmation

Any event can occur first if the corresponding genuine state already exists. The CLI route command never claims the implied inputs were produced; scientific Agent must inspect actual records.

## Shared evidence, not repeated reports

- ResearchState: latest project pointers and suggested action; authorization_refs are **pointers only**.
- EvidenceRecord / DataManifest (future structured adapters): original URLs, DOI, version, exact supported claim and dataset role/eligibility.
- TaskSpec: task_id, legal observation, outcome, independent unit, group split, metric, baseline, named nearest work and optional task levels.
- ExperimentSpec: immutable evaluator reference, dev split, hypothesis, max cost and expected distinguishing outcomes.
- RunRecord: code/data/evaluator/protocol versions, real stdout/metrics/predictions, status and exact compute cost.
- ClaimRecord: original scientific contribution and nearest-work difference, actual supporting runs, independent verification and limitations.

See [CONTRACTS.md](CONTRACTS.md). A version change can invalidate comparability/novelty/evidence, but must not erase real historical failures. Sealed data cannot be used for selecting tasks/algorithms.

## Why these modules

ResearchStudio supplies a model of **source-backed, version-aware idea design**; ARIS and AutoResearchClaw show handoff contracts; AIDE gives **auditable candidate branches**, R&D-Agent gives **feedback-driven new hypotheses**, AutoResearch suggests **evaluator isolation**; PaperQA2 is an optional citation source. This composition is a proposed architecture, **not experimentally proven superior**. Compare with chapters 08/10 under equal budgets.

## v0.2 real handoffs and research safeguards

The optional `adapters.literature` module retrieves raw OpenAlex/Crossref **metadata** with query/timestamp/provider provenance. Only a real source file can satisfy SEARCH_READY structurally. Stage events with note alone do not advance STATE. Handoffs hash local artifacts, require active task IDs for real Run/Claim events, and record a last_event_id to detect interrupted state writes. These are shape-level checks, not a scientific or authorization oracle. `core.comparison.compare_runs` rejects incomparable and sealed development candidates.
