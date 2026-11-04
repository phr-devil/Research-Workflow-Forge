---
name: research-feasibility
description: Establish legal evaluation, credible baseline and minimum informative pilot.
---
# 04 | Feasibility and evaluation contract

Shared rules: [EXECUTION_POLICY](../../docs/EXECUTION_POLICY.md). Start from an existing Task/Run where possible.

- Freeze the real evaluation rule: label, independence unit, group/time split, legal observation, train-only preprocessing, metric and evaluator version. Protect sealed confirmation.
- Reuse legitimate existing baseline Runs; compare fairly tuned strong alternatives when performance is claimed. Prefer a trusted **simple matched-information reference** and one cheapest decisive probe before planning complex training. Candidate residual, oracle correctability and deployable identifiable gain are separate. Use A=read-only diagnosis, B=authorized lightweight fit, C=authorized expensive model according to decision value, not fixed time quotas. Check for label ambiguity, leakage, group heterogeneity, undertraining and feasible performance headroom with the cheapest valid probes.
- For an incremental paper Claim, choose matched baselines **relevant to that Claim** rather than demand global leaderboard supremacy; e.g. when speed or calibration cost improves, measure both resource cost and any accuracy tradeoff under comparable hardware/protocol. A single dataset may support a narrowly scoped contribution if independent groups and confirmation eligibility are real; cross-domain generalization needs cross-domain evidence.
- Separate ENABLEMENT / BASELINE / MECHANISM experiments. Oracle and synthetic checks are diagnostics, not deployed gains. A first negative Pilot triggers bounded diagnosis, not automatic abandonment.
- `adapters.experiment_plan` creates `PLAN_ONLY` ExperimentSpec with evaluator, DEV split, falsifiable hypothesis, permitted budget and positive/negative decision. It **does not train**. The optional `tools.experiment_runner` fits only allowlisted CPU classifiers on manifest-bound DEV with actual user approval.

**Discriminating-probe feasibility:** where novelty rests on a mechanism, write the two hypotheses' **different expected observations** before deciding which ablation/stratification is worth GPU. Check factor crossing/independent groups and unresolved confounding before attributing location/device/time effect causally; a metadata crossing check is descriptive only. A valid classifier may be useful even if mechanisms are not identified; narrow the Claim and its confirmation accordingly. Follow [HIGH_VALUE_RESEARCH_ENGINEERING](../../docs/HIGH_VALUE_RESEARCH_ENGINEERING.md) §04–05. Never use confirmation data for this decision.

**Handoff:** verified evaluator/baseline or NOT_RUN, experiment contract and one discriminating next experiment. No unnecessary figures.

**Optional three-part diagnostic:** distinguish (1) ideal correctability/Oracle room, (2) predecision identifiability under legal observable inputs, and (3) practical gain after label/calibration cost against matched-information simple strategies. Only invoke on mechanisms such as dynamic gating/active calibration that show an Oracle-to-policy gap; **unknown** input identifiability is not automatic STOP or proof of unlearnability. No fitting without actual authorization.


**v0.8按任务取正确评价器**：分类、回归和事件主张不能混用口径。多受试者回归应指定group_mean或pooled；一次事件触发必须锁定完整episode、事件定义及真实触发容差，避免真值邻域取argmax。无可验证未来输入边界时只把外部工件当算术复算，不能声称在线因果部署通过。

**v0.9 reuse, no extra gate:** Prefer `python -m tools.feasibility_probe --project PROJECT --candidate C [--reference B --metric FROZEN_METRIC]` to retraining when trusted DEV Run predictions already exist. Inspect group residuals and fair matched-reference gain; without reference output UNKNOWN. Candidate residual ≠ achievable headroom; no-info control must be trained only from training groups, not test labels. Classification/regression slices are descriptive; do not invent Oracle/event slices. No compulsory figure.

**v0.10 POPPER-inspired cheap falsification (not POPPER's statistical error control):** Use the chosen hypothesis's `distinct_prediction` versus `strongest_alternative` to design one minimum legal probe. Before GPU scaling, distinguish positive control/correctability, prediction-time identifiability, matched simple baseline and label/K budget *as applicable*. A negative or UNKNOWN result routes to scoped diagnosis; no auto STOP, no sequential Type-I guarantee, no new universal preflight.
