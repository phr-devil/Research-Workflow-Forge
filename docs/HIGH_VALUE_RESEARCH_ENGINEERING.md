# High-value scientific search and mechanism design · existing Skills 01–06

**Purpose:** strengthen scientific importance, data discriminability, competing hypotheses and high-upside algorithm mechanisms **without adding a Skill, mandatory gate, autonomous training permission, state enum or manuscript-writing workflow**. When PD-RW is used it owns the research opportunity/Q2 decision; its [high-value scientific design](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/HIGH_VALUE_RESEARCH_DESIGN.md) governs the scientific choices. Forge contributes technical preflight and evidence-linked experiments. Global [execution policy](EXECUTION_POLICY.md), [next-action policy](NEXT_ACTION_POLICY.md) and `WRITING_LOCKED` remain binding.

**Decision owner:** PD-RW or the researcher chooses the scientific question using importance, named-neighbor difference, discriminability and evidence potential. RWF may check the source-bound [science handoff](../adapters/science_handoff.py), but its `opportunity_review` ranks **experiment-action feasibility only**. Its `recommended` is `null` until `--selected-hypothesis-id` is supplied. The source packet and its SHA receipts cannot prove a research problem's quality or that training is authorized. Never make a cross-hypothesis problem recommendation simply because an action is cheaper.

**Three internal checks without three extra user turns:** new opportunity search uses `BREADTH_SCAN → DEEP_FALSIFICATION → COMPETING_CHOICE` within the user's scope. Finding a trainable dataset or one plausible gap is not yet a scientifically selected question; challenge it with a genuinely different failure premise or record a limited, negative contrasting search. Novelty remains unverified until closest original/counterevidence are reviewed. Search effort scales with *decision-changing* unknowns, not fixed paper counts or endless Agent discussions. The authority and decision history remain in PD-RW's [Search Discovery](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/SEARCH_DISCOVERY.md), optionally checked structurally by `core.search_choice_review`—not a science ranker.

## 01: question search, not dataset-and-model shopping

Adapt [STORM](https://github.com/stanford-oval/storm) multi-perspective questions + [PaperQA2](https://github.com/Future-House/paper-qa) original full-text checking. One Agent can consider: real consequence/demand, physical/measurement limitations, and limitations of named strongest methods. At most 1–3 distinct scientific opportunities; preserve counterexamples/reasons literature may **already cover** the purported contribution. RAG/metadata and GitHub stars do not prove novelty.

Minimal opportunity packet: `QUESTION_IMPORTANCE | NAMED_NEIGHBOR + READ_STATUS | UNANSWERED_KNOWLEDGE | WHAT_SUCCESS_TEACHES | CHEAPEST_DISCRIMINATOR | ELIGIBLE_DATA/UNKNOWN | Q2_ANALOG/UNKNOWN`. PaperQA-style evidence is optional; do not auto-index whole libraries, download papers, spawn agents, generate manuscript text or rank by an invented acceptance score.

**`PRE_DOWNLOAD_SCIENCE_FIT` for the proposed D1:** inspect official public metadata for variables/truth, independent group crossing, possible confounding, legal information, confirmation path, license and volume before declaring the *scientific* D1 choice. `OFFICIAL_METADATA_SUPPORTS` is not a scientific PASS; `UNKNOWN` permits provisional planning but not a claim of data suitability; `OFFICIAL_METADATA_CONTRADICTS` triggers re-framing or a comparison to saved alternative topics before large downloads. Real DEV analysis only after separately authorized full required data acquisition, manifest checks and sealed isolation. Theory/proof research checks proof obligations/parameter ranges instead.

## 02: candidate data as scientific instruments

Before choosing the principal dataset, sketch the **smallest discriminability matrix**:

`CLAIM | ALTERNATIVE | FACTORS_TO_DISTINGUISH | INDEPENDENT_GROUP_UNIT | OBSERVED_CROSSING | LABEL/TRUTH + LEGAL_INFO | CONFIRM_ELIGIBILITY | UNRESOLVED_CONFOUND`.

- A large labeled dataset can train a model yet fail to separate device from subject, experiment day from class, or intervention from collection protocol. Treat `CONFOUNDED/UNIDENTIFIABLE` for the proposed mechanism as a **claim/scope restriction**, not blanket dataset rejection or a universal failure of all predictive Tasks.
- Crossed factor counts are descriptive only; adequate independent group replication, label comparability, measurement validity, exposure history, legal time direction and other confounders still need expert judgment. Missing metadata → `UNKNOWN`, not `PASS`.
- Reuse official dataset descriptions before downloads. Once necessary data are authorized and `DATA_ACQUIRED_VERIFIED`, conduct legal **DEV-only** data observation. Do not read SEALED_CONFIRM, use a selected external dataset as untouched confirmation, or turn pre-task exploratory slices into pre-registered findings. Theory/simulation tasks use parameter contrast/counterexample coverage instead of requiring a downloaded dataset.
- Existing `core.data_access` / `tools.data_audit` are data integrity tools, **not** scientific identification auditors. No new capability claim is attached to them.

**Feedback to selection**: when valid DEV evidence refutes the discovery-stage assumptions, return the allowed factual evidence to PD-RW and re-examine saved contrasting opportunities; do not silently pivot the main scientific Task or authorize new dataset/download/GPU. Retain the original data and negative evidence. Avoid treating sunk download costs as a reason to keep training an unsupported mechanism.

## 03: hypotheses that really compete

An idea is ready for a decisive probe when its **primary explanation and strongest realistic alternative predict different outcomes under a legal, matched comparator**. Minimal Agent-authored card:

`IMPORTANT_QUESTION | SOURCE/NEAREST_ORIGINAL | CLAIM | ALTERNATIVE | DISTINCT_PREDICTION | LEGAL_INFORMATION | DATA_CONFOUNDING | BASELINE | MINIMUM_DISCRIMINATOR | POS/NEG/INVALID | COST/AUTH`.

- If both stories explain the same F1 gain, they are **not distinguished** by it. Use targeted controls (model capacity, K/label budget, training data, sensor position, time, confounding, normalization, measurement) when appropriate.
- Some high-value papers demonstrate **new capability, measurement validity, efficiency or generalization boundary**, not causally identified mechanisms. Do not require a pretend causal DAG for every Task. Scope the claim to functional evidence where causal identification is absent.
- `adapters.hypothesis_bank` remains the single existing machine-readable 1–3 hypothesis ledger. `adapters.opportunity_review` is **an action/feasibility triage only**, not a novelty/Q2 score. Original papers and scientific discriminability are human/Agent assessed and must remain `UNVERIFIED` where source/conditions are missing.

## 04–05: high-upside mechanism search and finite budget

Adapt [RD-Agent](https://github.com/microsoft/RD-Agent) hypothesis→implementation→experiment→feedback, [AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) distinct mechanism branches, and [Optuna](https://github.com/optuna/optuna) adaptive pruning. Reuse present Champion and one active Challenger by default; **up to three candidate ideas does not authorize three training runs**.

Candidate levers: legal new information / representation or physical inductive bias / optimization-calibration / reliability-decision / real cost-performance constraint. Each needs:
`BASELINE_FAILURE | NEW_LEVER | DISTINCT_PREDICTION_VS_SIMPLE | POSITIVE_CONTROL_IF_RELEVANT | FIXED_DEV_EVALUATOR | BUDGET | IF_TEST_POS/NEG/INVALID`.
If data cannot identify the proposed cause, first reframe claim or collect legitimate new independent evidence **only with real user authorization**.

- Choose the cheapest **decision-changing** probe; a genuine new temporal/physical representation can justify complexity when there is evidence it addresses an identifiable bottleneck. Do not mistake a poor short training run for algorithmic impossibility.
- Only use automatic tuning/pruning **inside existing authorized DEV budget** and with recorded selection history; no silent extra dependencies or holdout-adaptive HPO. Preserve honest strongest matched-information baselines and report negatives.
- Distinguish a **high-upside scientific result** from a lucky best seed, a tuned metric, or SHAP-style attribution. Mechanistic claims require appropriate distinguishable evidence; all causal claims still need justified identification assumptions.
- Maintain independent confirmations and scoped Q2 claims. A valid small claim is an asset but **not project success** absent verified, important Q2+ contribution. Q1 is preferred if marginal research cost and additional value warrant it.

**Late-discovered science / contribution extraction:** reuse Run and experiment feedback through [SCIENCE_RESULT_HARVEST.md](SCIENCE_RESULT_HARVEST.md) at high-information decision points. Before accepting the first narrow Claim, compare up to 3 different, source-linked scientific candidates and record adverse effects; deciding the scientific Claim belongs to PD-RW/user. Separate research-summary articulation improvement from a real evidence gap; avoid a new expensive model when verified evidence is simply underexplained.

## 06: scientific value feedback, not paper-first premature STOP

When `RUN_RESULT / NO_GAIN / TASK_BLOCKED` occurs, evaluate **what knowledge the Run adds, whether a distinct lever remains and what is the cheapest decisive Q2-relevant action**. A first invalid or negative Pilot is not project failure. `Q2_POTENTIAL_SUPPORTED` requires PD-RW/source-backed scientific review; `opportunity_review` and Run status never certify it. Allow an informative second bounded pilot under **existing real authorization** if it changes the Claim, not simply to hunt for significance.

**Response format:** in-scope legitimate technical choice or strong recommendation → one succinct copy-ready Agent instruction grounded in current receipts; major Task pivot, additional budget/compute/data/sealed access, project STOP, paper writing → recommendation and user options only, no executable prompt. `WRITING_LOCKED` unless user reviewed research summary and separately authorized this manuscript.

**Token/effort limit:** no automatic extra agents, knowledge graphs, polished figures, comprehensive systematic review, compulsory dataset count, new platform/runtime or long reports. Load only the relevant Skill and this guide when the stage actually needs increased scientific value. Record one short `SCIENTIFIC_DELTA | SOURCE | UNANSWERED_ALTERNATIVE | MOST_INFORMATIVE_NEXT_ACTION | AUTH/COST` handoff.
