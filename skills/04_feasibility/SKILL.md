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

**Optional three-part diagnostic:** distinguish (1) ideal correctability/Oracle room, (2) predecision identifiability under legal observable inputs, and (3) practical gain after label/calibration cost against matched-information simple strategies. Only invoke on mechanisms such as dynamic gating/active calibration that show an Oracle-to-policy gap; **unknown** input identifiability is not automatic STOP or proof of unlearnability. No fitting without actual authorization.


**v0.8按任务取正确评价器**：分类、回归和事件主张不能混用口径。多受试者回归应指定group_mean或pooled；一次事件触发必须锁定完整episode、事件定义及真实触发容差，避免真值邻域取argmax。无可验证未来输入边界时只把外部工件当算术复算，不能声称在线因果部署通过。

**v0.9 reuse, no extra gate:** Prefer `python -m tools.feasibility_probe --project PROJECT --candidate C [--reference B --metric FROZEN_METRIC]` to retraining when trusted DEV Run predictions already exist. Inspect group residuals and fair matched-reference gain; without reference output UNKNOWN. Candidate residual ≠ achievable headroom; no-info control must be trained only from training groups, not test labels. Classification/regression slices are descriptive; do not invent Oracle/event slices. No compulsory figure.
