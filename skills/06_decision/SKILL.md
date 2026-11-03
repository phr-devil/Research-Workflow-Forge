---
name: research-decisions
description: Diagnose failures at their correct scope and choose repair, continue or pivot.
---
# 06 | Decision, repair and pivot

Shared rules: [EXECUTION_POLICY](../../docs/EXECUTION_POLICY.md). Read original Run receipts before interpreting summaries.

- Distinguish INVALID (broken protocol/leakage), INCONCLUSIVE (insufficient evidence), real negative at mechanism level, Task infeasibility and Claim novelty failure. Retain valid old evidence; do not elevate model-score improvement into scientific novelty.
- Pick CONTINUE, REPAIR, NARROW, HOLD or real PIVOT according to the *new information obtainable per remaining cost*. One negative Pilot ≠ project STOP; repeated experiments with the same falsified premise and no discriminatory value should stop.
- Ordinary bugs: reproduce → root cause → targeted fix → verify, autonomously within authorized scope. For a **scientific** negative, don't invoke engineering-debug loops to inflate scores. Superpowers debugging Skill is an optional reference only.
- Task and protocol transitions require versioned `TASK_PIVOT` / `PROTOCOL_REVISED` decisions; old Champion is retired, negative history preserved. `core.cli recover` previews/repairs only a safe one-event interruption.

**Handoff:** failure_scope, cited new evidence, decision, smallest next probe, possible outcomes and any genuine permission blocker.
