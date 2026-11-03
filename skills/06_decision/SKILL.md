---
name: research-decisions
description: Diagnose failures at their correct scope and choose repair, continue or pivot.
---
# 06 | Decision, repair and pivot

Shared rules: [EXECUTION_POLICY](../../docs/EXECUTION_POLICY.md). Read original Run receipts before interpreting summaries.

- Distinguish INVALID (broken protocol/leakage), INCONCLUSIVE (insufficient evidence), real negative at mechanism level, Task infeasibility and Claim novelty failure.
- **Scope-specific cause map:** ENGINEERING_ERROR → repair affected code/data/evaluator; SIGNAL_LIMITATION → inspect predecision legal information and Task; MECHANISM_FAILURE → HOLD challenger while preserving verified simple reference; NOVELTY_FAILURE → revisit independent scientific gap (PD-RW if applicable); CONFIRMATION_FAILURE → narrow Claim or plan new independent evidence. These are reasoning labels, not new CLI enum values. Do not treat a simple method's valid success as proof of paper novelty or a complex model's loss as proof the entire data area is unusable. Retain valid old evidence; do not elevate model-score improvement into scientific novelty.
- **Do not misclassify incremental novelty:** a fair simple reference matching the challenger is a negative result for that mechanism, but may still support a new efficiency, calibration-cost or boundary Claim. If one modest, specific and reproducible contribution survives nearest-work comparison, route to the minimum paper-evidence path rather than require larger model gains. If it only reproduces known results, retain the engineering asset without implying a paper.
- **Narrow-paper escape before stopping a valid branch:** if a hard mechanism fails but reliable baseline/residuals expose a reproducible, previously unanswered *narrow* effect or real label/compute-cost advantage, route that as `PAPER_CANDIDATE_WITH_GAPS` (narrative shorthand, **not** a CLI/event value) and name the single cheapest decisive test. A small result can warrant professional/specialty-journal consideration; lack of global SOTA or a new backbone is not STOP. If the finding is a post-hoc slice, merely known or not identifiable from legal information, preserve it as exploratory/engineering rather than claiming publication readiness. Do not repeat novelty review without new evidence.
- Pick CONTINUE, REPAIR, NARROW, HOLD or real PIVOT according to the *new information obtainable per remaining cost*. One negative Pilot ≠ project STOP; repeated experiments with the same falsified premise and no discriminatory value should stop.
- Ordinary bugs: reproduce → root cause → targeted fix → verify, autonomously within authorized scope. For a **scientific** negative, don't invoke engineering-debug loops to inflate scores. Superpowers debugging Skill is an optional reference only.
- Task and protocol transitions require versioned `TASK_PIVOT` / `PROTOCOL_REVISED` decisions; old Champion is retired, negative history preserved. `core.cli recover` previews/repairs only a safe one-event interruption.

**Handoff:** failure_scope, cited new evidence, decision, smallest next probe, possible outcomes and any genuine permission blocker.

**APACE→SAFE-Gait failure lesson:** when a policy has theoretical Oracle room but consistently fails fixed/random controls, diagnose hidden-information/indistinguishable-action premises before changing network complexity. If a *realistically available* K-shot calibration observation changes the information condition, propose a distinct versioned Task, retain original negative evidence, recheck same-K baselines and independent confirmation eligibility. If no genuinely different information or mechanism exists, do not relabel a superficial pivot as progress. Case (optional): https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/LESSONS/SAFE_GAIT_APACE.md.


**v0.8失败归因**：CRIA式真值邻域择优属于评价失效，优先隔离INVALID；RISC-Sense式subject-mean与pooled差异属于评价合同不同；APACE式K改变属于新任务与合法信息条件。保留真实简单基线而不自动宣称论文价值。

**Failure triage with the v0.9 feasibility summary:** invalid labels/evaluator → repair affected evidence; undertraining/fairness deficit → bounded equal-budget anchor; candidate not better than matched simple reference → inspect residual structure, legal new information or genuinely different failure premise; heterogeneous positive DEV results → narrow only with new validation. Negative Pilot or UNKNOWN does **not** auto-STOP the project. Do not keep searching the same falsified lever without information gain.

**v0.10 science feedback:** For a real verified DEV result, `python -m adapters.hypothesis_bank feedback --project PROJECT --bank BANK.json --hypothesis-id H01 --run RUN.json --assessment INCONCLUSIVE --out BANK_v2.json` creates a new evidence-linked revision. Assessments are Agent interpretations, not machine-certified effects. On an invalid evaluator first repair the Run; on a plausible negative probe revise premise or fallback at the correct scope; on positive DEV gains still compare strong alternatives/nearest work and eligible independent confirmation.
