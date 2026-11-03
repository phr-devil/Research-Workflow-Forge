---
name: research-feasibility
description: Establish legal evaluation, credible baseline and minimum informative pilot.
---
# 04 | Feasibility and evaluation contract

Shared rules: [EXECUTION_POLICY](../../docs/EXECUTION_POLICY.md). Start from an existing Task/Run where possible.

- Freeze the real evaluation rule: label, independence unit, group/time split, legal observation, train-only preprocessing, metric and evaluator version. Protect sealed confirmation.
- Reuse legitimate existing baseline Runs; compare fairly tuned strong alternatives when performance is claimed. Check for label ambiguity, leakage, group heterogeneity, undertraining and feasible performance headroom with the cheapest valid probes.
- Separate ENABLEMENT / BASELINE / MECHANISM experiments. Oracle and synthetic checks are diagnostics, not deployed gains. A first negative Pilot triggers bounded diagnosis, not automatic abandonment.
- `adapters.experiment_plan` creates `PLAN_ONLY` ExperimentSpec with evaluator, DEV split, falsifiable hypothesis, permitted budget and positive/negative decision. It **does not train**. The optional `tools.experiment_runner` fits only allowlisted CPU classifiers on manifest-bound DEV with actual user approval.

**Handoff:** verified evaluator/baseline or NOT_RUN, experiment contract and one discriminating next experiment. No unnecessary figures.
