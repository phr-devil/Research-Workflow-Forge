# Current architecture · v0.15

## One controller, three engines, seven callable Skills

- **Controller** `core/router.py`, `core/state.py`, `core/receipts.py`: evidence-linked versioned events, task/protocol transitions, no external action on routing. `core.cli brief` reports only current pointers and recent event deltas.
- **Discovery**: 01 sourced paper/data opportunities → 02 official labels/group/role verification → 03 falsifiable Task and viable fallback. ResearchStudio search is **metadata-only**; IdeaSpark/Scoop Check are reference rubrics, not autonomous novelty confirmation.
- **Development**: 04 immutable evaluation and credible, preferably simple, reference → 05 smallest decision-changing Draft/Debug/Improve, then justified complexity escalation, with actual Run receipt, evaluator/data versions and explicit Champion. Current CPU executor is allowlisted, not general Agent code; typed regression and single-emission event DEV evaluations accept independently verified prediction receipts (not arbitrary code execution).
- **Decision/confirmation**: 06 diagnose at Run/mechanism/Task/Claim scope; repair/pivot preserving evidence. 07 checks independent paper contribution and untouched confirmation, **not automated yet**.

A narrow, reproducible incremental capability, cost/accuracy tradeoff, or new failure boundary may proceed toward a paper candidate without global SOTA or a new backbone. The existing Claim/confirmation contracts remain unchanged; this is a decision rule rather than a new machine state.

**v0.15 paper-first handoff:** `RUN_RESULT`, `NO_GAIN`, and `TASK_BLOCKED` route through the existing Decision Skill and now explicitly prompt a narrow paper-opportunity review before model escalation or abandoning the Task. The route **does not** automatically review literature, assert manuscript readiness, train, confirm or submit; PD-RW remains the optional paper/venue controller.

The route follows the current blocker: `NO_GAIN` → 06 → back to 05 if a different mechanism remains; `TASK_PIVOT` → 03; `CLAIM_CANDIDATE` → 07. **No mandatory linear seven-stage gate.**

## Persistent artifacts and boundaries

`STATE.json` holds current pointers; `EVENTS.jsonl` contains append-only evidence-linked transitions; Task/Experiment/Run/Claim contracts live in `core/contracts.py`. `DATA_MANIFEST.json` and `DATA_ACCESS.jsonl` protect eligible DEV use; raw Run logs/predictions retain SHA digests. Version changes retire incompatible Champions without erasing negative results. Sealed confirmation and user authorization are independent protected gates.

A compact status is **not** a verified result. Paper novelty requires original full text and named predecessors; strong independent confirmation is outside the current runtime.

**How agents work efficiently:** [EXECUTION_POLICY.md](EXECUTION_POLICY.md). This file documents only system structure. Source attribution: [SOURCES.md](../SOURCES.md). Historical migrations: [UPGRADE_V04.md](UPGRADE_V04.md), [UPGRADE_V05.md](UPGRADE_V05.md).


**v0.10 optional discovery adapter (no additional controller):** `adapters.hypothesis_bank` extracts descriptive seeds from verified DEV receipts and binds 1–3 Agent-authored hypotheses to hashed data-note / literature metadata / seed pointers. `adapters.opportunity_review` selects a transparent next evidence action; new DEV Run feedback creates an immutable bank revision. The seven Skills, STATE/Event contracts and external-Agent execution boundaries remain unchanged.

**v0.11 evidence interoperability:** optional `adapters.pd_rw_bridge` reuses the existing Forge verified DEV Run loader and compares original prediction bytes to PD-RW artifacts. It is a read-only subprocess boundary rather than a second controller or merged state schema. Ordinal opportunity review also distinguishes baseline-dominated mechanisms from high-cost but distinct hypotheses.
