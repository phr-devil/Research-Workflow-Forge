# Post-algorithm science audit · evidence-first, optional

**Purpose:** after an algorithm has a credible champion / stable baseline and another round of model search is being considered, ask whether a *small, falsifiable intervention* could improve the **scientific claim**, not merely its DEV score. This is an optional route through existing Skills 04→05→06→07, **not an eighth Skill, new CLI event/state, autonomous runner, or manuscript writer**. When PD-RW is present, its [post-algorithm audit](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/POST_ALGORITHM_SCIENCE_AUDIT.md) owns novelty, scientific value and venue choices. Always obey [EXECUTION_POLICY](EXECUTION_POLICY.md), especially `WRITING_LOCKED`.

**Minimum publication goal:** prioritize scientifically meaningful, falsifiable upgrades that can turn an existing algorithm into an evidence-backed **JCR Q2+ publication-potential** research result; Q1 is preferable when realistic. Actual journal acceptance is not required. Evaluate novelty and venue fit separately; PD-RW [Q2 policy](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/Q2_PUBLICATION_GOAL.md) owns the final decision. Do not stop at a Q3/Q4-only small-paper exit or overfit research to a journal label.

## Read-only evidence first (no fit, sealed access or new dependencies)

- Reuse a verified `Task`, evaluator/split, selected DEV `Run`, matched-information simple reference, source predictions and current failure history. Check prediction-level receipts (not only a reported score); `core.cli brief`, `core.cli compare` and `tools.feasibility_probe` are *optional existing aids* subject to their actual input contracts.
- Diagnose **only the claim-relevant** error structure: independent group/position/device/time, possible duplicates/label anomalies, distribution change, cost, calibration and robustness. Record group counts, effect and uncertainty when supported. Observations selected after many slices are `EXPLORATORY`, not independently confirmed.
- Compare 1–2 *actual closest* published papers and strongest fair simple substitute. Metadata or SHAP/Captum attribution can suggest a hypothesis but **cannot establish novelty or causality**.
- Choose at most three **different** hypotheses: `OBSERVED_RUN → NEAREST_GAP → COMPETING_EXPLANATION → DISTINCT_PREDICTION → LEGAL_TEST → POS/NEG/INVALID → COST`. If there is no distinct prediction, do not train another backbone.

## Select the smallest decision-changing action

| Mode | Action | Boundaries |
|---|---|---|
| **A: REUSE** | Group-paired error, matched-run re-analysis, data-quality/drift checks; zero fit | Do not label post-hoc slices as established laws; never inspect sealed resources |
| **B: SMALL_DEV** | One authorized matched ablation, simple substitute, calibration-cost curve, real deployment constraint or controlled perturbation | Same task/information/K, fair tuning budget and fixed DEV analysis unit; preserve old Champion and negative Runs. New K/deployment information = versioned Task |
| **C: CONFIRM** | Separate user-authorized claim-matched independent evaluation after freezing method/claim/selection history | No repeated model selection on holdout or laundering DEV as fresh confirmation |

If the first bounded test reveals a distinct scientific direction that can justify reaching Q2+ or materially improving Q1 competitiveness, pursue further **authorized and decision-changing** tests as justified; do not impose a fixed count or endlessly retune.

For claimed mechanisms, define what outcomes the proposed mechanism predicts **differently** from a simpler explanation. Attribution, observational correlations and assumed shifts alone are not causal proof. A diagnostic perturbation must respect physical/data semantics and avoid label leakage. A rejected test can be scientifically useful but is not a stand-alone publishable result.

## Decision & handoff (no auto paper draft)

Route the **next output** per [NEXT_ACTION_POLICY](NEXT_ACTION_POLICY.md): in-scope, already-authorized scientific diagnostics → direct next Agent instruction; additional GPU/sealed access, major project pivot or termination → recommendation+user options, no executable Agent prompt. A strong recommendation never grants itself authorization.

`SOURCE_RUN/PROTOCOL | HYPOTHESIS+NAMED_GAP/UNKNOWN | RELEVANT_GROUP_EFFECT | FAIR_ALTERNATIVE | DISTINGUISHING_TEST+EXPECTED_OUTCOMES | DATA/CONFIRM_ELIGIBILITY | COST/AUTH | NEXT`

- `UPGRADE_PILOT`: one falsifiable inexpensive B test is worth running **only if actually authorized**.
- `EVIDENCE_ONLY`: no new model; complete the crucial fair comparison, uncertainty or confirmation requirement.
- `KEEP_ORIGINAL`: no independently valuable difference, near neighbor already covered it, or cost outweighs value. Freeze credible original and report for research-results summary.
- `UNKNOWN`: missing legal Run, original closest paper, fair comparison, relevant groups, legitimate resources or permission. Resolve smallest missing fact; do not claim success/failure.

Interpret Pilot evidence as `SUPPORTED_DEV_ONLY`, `INCONCLUSIVE`, or `INVALID/REFUTED`; genuine confirmation is separate. Reuse existing Claim/Run records and `hypothesis_bank` if suitable, but do not invent new machine states. **No automatic paper title, outline, section, draft, figure formatting, submission or expensive training.** A research-results summary must be explicitly reviewed by the user and a separate manuscript-writing instruction verified before any writing.

## Public source ideas (conceptual; do not vendor or auto-install)

- [Cleanlab](https://github.com/cleanlab/cleanlab) and [Evidently](https://github.com/evidentlyai/evidently): anomaly/label/drift screening, not ground-truth certification.
- [WILDS](https://github.com/p-lambda/wilds) and [DomainBed](https://github.com/facebookresearch/DomainBed): group shift and proper model-selection protocols; DomainBed is archived as of 2026.
- [SHAP](https://github.com/shap/shap), [Captum](https://github.com/meta-pytorch/captum), [DoWhy](https://github.com/py-why/dowhy): interpretability → testable predictions → assumed identification/refutation; explanations alone are not causality.
- [RobustBench](https://github.com/RobustBench/robustbench), [DVC](https://github.com/treeverse/dvc): standardized evaluation conditions and reproducible data/run provenance, not automatic robustness of every deployment.

**Scope:** these are design references, not runtime integrations, claimed venue outcomes, direct upstream code copies or required installations. Real tool use requires separate data/licensing/dependency and user-permission checks.
