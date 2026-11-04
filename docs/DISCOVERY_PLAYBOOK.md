# RWF v0.10 · Evidence-linked discovery (read only when Task/idea is missing)

**Purpose:** propose an experiment-worthy scientific question from real data/nearest literature, not generate a title and call it a paper. This is a conditional path through existing Skills 01–04, not a new gate. **No fitting, automatic LLM calls, sealed data, claim confirmation or user authorization** is performed by these adapters.

**Science-value-oriented opportunity selection:** prefer a consequential, legally testable question with a credible new knowledge/ability difference and claim-matched evidence; protect feasible narrow successes, but do not rank trivial small score improvements ahead of stronger, realistic Q2-relevant discoveries merely because they are easier. When it changes selection, inspect 1–3 recent actually published analogous studies and their specific core tests (rather than citation counts, impact factor or abstract similarity alone). Record a one-line plausible narrow manuscript Claim and decisive missing evidence; mark `PAPER_VENUE_REFERENCE_UNKNOWN` if no reliable source. Do not use assumed journal quality as a Task elimination rule.

**High-value default (overrides legacy “small contribution is enough” wording)**: see [HIGH_VALUE_RESEARCH_ENGINEERING](HIGH_VALUE_RESEARCH_ENGINEERING.md). Before selecting the easiest hypothesis, ask what important knowledge successful verification would add, what closest original paper already knows, and whether available data separately vary the factors needed to reject a simple alternative. Prefer an evidence-backed high-value, feasible Claim over a trivial F1 increase; do not assume more ambitious always means higher value. Existing `hypothesis_bank` and `opportunity_review` are **source/cost/next-action helpers**, NOT scientific-ranking engines; `Q2_POTENTIAL_SUPPORTED` requires separate credible original-work/confirmation/venue review.

**No automatic first-opportunity selection**: without a previously selected scientific question, perform a short breadth coverage / closest-original falsification / distinct-premise comparison before concluding D1. Only PD-RW or the user chooses the research problem; `opportunity_review` estimates cheap next evidence actions **after** that choice. The PD-RW optional `core.search_choice_review` reports structural omissions only; `SEARCH_PARTIAL` and `PREFERRED_PROVISIONAL` are acceptable honest outcomes when critical originals or D1 scientific fit are still UNKNOWN. Do not convert a provisional preference into a verified Q2 innovation or automatic download permission.

## Minimal path

**Evidence-first discovery default:** before proposing an architecture, seek the smallest verifiable question: a repeatable between-condition effect, a residual correctable by legal low-cost feedback, or the condition where a strong simple method fails. Physical theory or concrete deployment constraints may justify another start. Distinguish legal signal, reliable result, and novelty relative to named predecessors. Use the smallest falsifiable probe; do not force complexity or claim that a simple positive DEV result is a publishable discovery.

1. If a valid DEV Run exists, extract *descriptive* observation seeds; otherwise keep a project-contained raw-data note marked **UNVERIFIED** (or begin with paper metadata):
   ```bash
   python -m adapters.hypothesis_bank seed --project PROJECT --candidate-run PROJECT/runs/C/RUN.json --reference-run PROJECT/runs/B/RUN.json --metric MAE --out PROJECT/observation-seeds.json
   ```
   Both Runs must pass existing independent DEV metric verification. With no reference, omit `--reference-run` and `--metric` when unnecessary. Group error ≠ recoverable signal; no matched reference ≠ task unlearnable.
2. Use existing `python -m adapters.researchstudio_search --query "specific mechanism" --out PROJECT/papers.json` if literature evidence is missing; metadata-only evidence cannot certify novelty. The **current Agent** reads only relevant evidence and writes up to three different, falsifiable ideas. Each one states legal predecision information, strongest alternative, differentiating prediction and a cheap experiment.
3. Save the candidate JSON as `PROJECT/ideas.json` (below), then build source-bound hypothesis bank:
   ```bash
   python -m adapters.hypothesis_bank build --project PROJECT --cards PROJECT/ideas.json --seeds PROJECT/observation-seeds.json --literature PROJECT/papers.json --out PROJECT/HYPOTHESES_v1.json
   python -m adapters.opportunity_review --project PROJECT --bank PROJECT/HYPOTHESES_v1.json --out PROJECT/OPPORTUNITIES_v1.json
# Once PD-RW/user has chosen a scientific hypothesis, add --selected-hypothesis-id H01 to get the next evidence action for THAT hypothesis. Without selection, recommended=null and no scientific topic is auto-selected.
   ```
   Omit either `--seeds` or `--literature` if absent. Alternatively attach `--data-note PROJECT/data-notes.txt` as **agent narrative, not an independently verified data effect**. Source IDs in idea cards must match exactly those in the seed/metadata bundles.
4. Use the cheapest result-changing next probe in the existing Task/Experiment process. When a **genuine independently verified DEV** Run exists (not merely a self-reported score), append versioned feedback:
   ```bash
   python -m adapters.hypothesis_bank feedback --project PROJECT --bank PROJECT/HYPOTHESES_v1.json --hypothesis-id H01 --run PROJECT/runs/R2/RUN.json --assessment INCONCLUSIVE --out PROJECT/HYPOTHESES_v2.json
   ```
   Assessment is a declared interpretation: `SUPPORTS_EXPECTED_PATTERN`, `CONTRADICTS_EXPECTED_PATTERN`, or `INCONCLUSIVE`. **Never** overwrite v1. A changed legal K, Task or protocol requires a new task-scoped version, not a silent success of the previous experiment.

## Minimum idea card, produced by the Agent (not automatically invented by this script)

```json
{
  "candidates": [
    {
      "hypothesis_id": "H01",
      "research_question": "Does a repeatable subject residual persist across conditions?",
      "mechanism": "Subject-specific offset may transfer",
      "strongest_alternative": "Label prevalence/condition imbalance explains the residual",
      "distinct_prediction": "The effect persists under matched train-only preprocessing and label strata",
      "minimum_test": "Paired legal DEV group/condition baseline vs simple residual offset",
      "if_positive": "Narrow to a potentially repeatable condition-specific capability",
      "if_negative": "Retain a negative mechanism result and investigate alternate signals",
      "legal_information": "Only predecision sensor features; target calibration labels unavailable",
      "legal_information_status": "UNKNOWN",
      "baseline_status": "UNKNOWN",
      "test_cost": "LOW",
      "source_seed_ids": ["S_GROUP_ERRORS"],
      "paper_record_ids": ["REPLACE_WITH_REAL_SEARCH_RECORD_ID"]
    }
  ]
}
```

`source_seed_ids` or `paper_record_ids` may be empty when only the other is available; for data-note-only candidates set `uses_data_note: true`. All examples are **illustrative**. Do not fabricate a paper record ID or claim the example mechanism is true.

## Review semantics / safety

- `adapters.opportunity_review` sorts by **next evidence action** only; `recommended=null` until a valid prior `--selected-hypothesis-id` is provided. `selected_research_problem=NOT_SELECTED_BY_FORGE` is always preserved. It cannot select the science target, which belongs to PD-RW/user. It does not rank expected research value, Q2 potential or acceptance. Its action advice is advisory, **not a user authorization**. For this stage, before proposing any extra model, first check the named comparison and strongest alternative. Existing heuristic: first identify blocked information, absent DEV signal, untested legitimate inputs, strong-matched-baseline need, or a bounded discriminator. No fake numerical priority score or publication probability. Missing information is `UNKNOWN`, not automatic STOP.
- Observation seeds link to independently recomputed Run receipts but are selected DEV descriptions; **not** independent scientific discovery, headroom bound, causality or novelty. Paper metadata is **METADATA_ONLY** until original nearest work is read.
- Real experiments remain with authorized Codex/WorkBuddy or existing allowlisted CPU executor. Run/Task/Claim contracts and protected evaluator remain authoritative. Future-scoped causal event semantics require additional provenance; stored predictions alone cannot certify execution.
- Do not force a literature query, GPU Pilot, hypothesis bank or 1–3 candidates for already-certain Tasks; simply resume the existing verified state and next action.
- Historical blind replay and prospective success-rate evaluation are **NOT_MEASURED**. Synthetic unit tests validate engineering behavior only.

## Incremental paper examples (concepts, not performance thresholds)
- [LTSF-Linear (AAAI 2023)](https://github.com/cure-lab/LTSF-Linear): testing the assumed need for complex architectures can itself produce scientific insight.
- [MiniRocket (KDD 2021)](https://doi.org/10.1145/3447548.3467231): a meaningful speed–accuracy tradeoff is different from claiming universally better accuracy.
- [iTransformer (ICLR 2024)](https://github.com/thuml/iTransformer): reorganizing existing components may be useful when supported by comparisons and explanation.
These are **illustrative patterns**, not automatic novelty certification or acceptance guarantees. Only inspect the particular original paper when it is a genuine closest neighbor; do not preload them on every run.

## Decision quality over hypothesis-card count

Before an expensive new mechanism, use the strongest valid simple reference and the actual legal predecision inputs to ask what distinct residual behavior the mechanism predicts. Prefer one falsifiable low-cost probe with a specified response to positive, negative and invalid observations; keep at most one active challenger sharing the same failure premise. A negative DEV Pilot updates the mechanism, not the entire scientific area. The hypothesis bank is optional: existing clear Task/Run evidence must not be rewrapped into cards. Do not infer an objective success probability from ordinal opportunity routes.

**v0.11 research routing fix:** when a matched simple baseline already dominates the idea, route to `DISTINCT_LEVER_OR_PIVOT_REVIEW` rather than repeatedly requesting the same baseline. A high-cost otherwise testable idea routes to `REDUCE_COST_OR_FIND_CHEAPER_DISCRIMINATOR`; neither route automatically rejects the Task or fabricates a success probability.
