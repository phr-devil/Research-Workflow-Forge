---
name: research-confirmation
description: Confirm a frozen independent scientific claim using eligible evidence.
---
# 07 | Scientific confirmation

Shared rules: [EXECUTION_POLICY](../../docs/EXECUTION_POLICY.md). Enter only on a real candidate claim with eligible independent evaluation; it may be planned early but cannot run sealed resources without actual approval.

- Freeze claim, task, code/data/evaluator, checkpoint, legal inputs, metric, group independence and prior selection history before confirmation.
- Read full named nearest papers and compare the **actual scoped contribution**, not only method novelty, title or metadata overlap. One credible incremental Claim is sufficient to justify scientific confirmation; global SOTA, a brand-new architecture, all-positive metrics and multi-dataset dominance are not generic requirements. Select strongest *relevant* fair baselines, report all relevant adverse outcomes, group-level uncertainty, and only the ablation/cost/physical checks needed to substantiate that Claim. Efficiency and label-cost contributions must disclose predictive tradeoffs and actual resource measurement.
- Examine DATA_ACCESS and Task selection history: merely renaming a split or changing seeds cannot restore untouched holdout status. Preserve failed confirmations.
- Separate **DEV effect**, independent confirmation and genuine paper-level novelty. Structural passes, synthetic fixtures, Oracle, and model reviews do not prove scientific Claims.

**Handoff:** ClaimRecord pointing to actual source/Run receipts and limits, or INSUFFICIENT / CONFIRMATION_UNAVAILABLE. An eligible untouched within-dataset group may confirm a carefully restricted Claim; external datasets become necessary when the claim genuinely spans datasets/domains or the original confirmation resource is ineligible. Forge still does **not** execute independent scientific confirmation autonomously. Publication figures only after results justify them.

**v0.7:** SEALED Run ingestion through BASELINE_VALID/RUN_RESULT/NO_GAIN/RUN_INVALID is refused. This is fail-closed development bookkeeping, NOT a completed independent-confirmation service. No JSON authorization_ref alone can grant permission to inspect a sealed dataset. The full execution boundary must be separate from the Agent's DEV workspace.

**Narrow Claims:** multi-target/direction/dataset outcomes may support a restricted effect or credible boundary but cannot be repackaged as universal gain through post-hoc cherry-picking. Preserve entire search/selection history, negative targets and direction reversals; require eligible independent confirmation and named nearest-work comparison. Individually trained dataset-specific models are not evidence that weights transferred across platforms.
