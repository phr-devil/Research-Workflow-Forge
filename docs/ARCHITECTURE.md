# Current architecture · v0.6

## One controller, three engines, seven callable Skills

- **Controller** `core/router.py`, `core/state.py`, `core/receipts.py`: evidence-linked versioned events, task/protocol transitions, no external action on routing. `core.cli brief` reports only current pointers and recent event deltas.
- **Discovery**: 01 sourced paper/data opportunities → 02 official labels/group/role verification → 03 falsifiable Task and viable fallback. ResearchStudio search is **metadata-only**; IdeaSpark/Scoop Check are reference rubrics, not autonomous novelty confirmation.
- **Development**: 04 immutable evaluation and credible baseline → 05 Draft/Debug/Improve with actual Run receipt, evaluator/data versions and explicit Champion. Current CPU executor is allowlisted, not general Agent code.
- **Decision/confirmation**: 06 diagnose at Run/mechanism/Task/Claim scope; repair/pivot preserving evidence. 07 checks independent paper contribution and untouched confirmation, **not automated yet**.

The route follows the current blocker: `NO_GAIN` → 06 → back to 05 if a different mechanism remains; `TASK_PIVOT` → 03; `CLAIM_CANDIDATE` → 07. **No mandatory linear seven-stage gate.**

## Persistent artifacts and boundaries

`STATE.json` holds current pointers; `EVENTS.jsonl` contains append-only evidence-linked transitions; Task/Experiment/Run/Claim contracts live in `core/contracts.py`. `DATA_MANIFEST.json` and `DATA_ACCESS.jsonl` protect eligible DEV use; raw Run logs/predictions retain SHA digests. Version changes retire incompatible Champions without erasing negative results. Sealed confirmation and user authorization are independent protected gates.

A compact status is **not** a verified result. Paper novelty requires original full text and named predecessors; strong independent confirmation is outside the current runtime.

**How agents work efficiently:** [EXECUTION_POLICY.md](EXECUTION_POLICY.md). This file documents only system structure. Source attribution: [SOURCES.md](../SOURCES.md). Historical migrations: [UPGRADE_V04.md](UPGRADE_V04.md), [UPGRADE_V05.md](UPGRADE_V05.md).
