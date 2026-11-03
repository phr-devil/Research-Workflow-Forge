# RWF v0.10 · Evidence-linked discovery (read only when Task/idea is missing)

**Purpose:** propose an experiment-worthy scientific question from real data/nearest literature, not generate a title and call it a paper. This is a conditional path through existing Skills 01–04, not a new gate. **No fitting, automatic LLM calls, sealed data, claim confirmation or user authorization** is performed by these adapters.

## Minimal path

1. If a valid DEV Run exists, extract *descriptive* observation seeds; otherwise keep a project-contained raw-data note marked **UNVERIFIED** (or begin with paper metadata):
   \`\`\`bash
   python -m adapters.hypothesis_bank seed --project PROJECT --candidate-run PROJECT/runs/C/RUN.json --reference-run PROJECT/runs/B/RUN.json --metric MAE --out PROJECT/observation-seeds.json
   \`\`\`
   Both Runs must pass existing independent DEV metric verification. With no reference, omit \`--reference-run\` and \`--metric\` when unnecessary. Group error ≠ recoverable signal; no matched reference ≠ task unlearnable.
2. Use existing \`python -m adapters.researchstudio_search --query "specific mechanism" --out PROJECT/papers.json\` if literature evidence is missing; metadata-only evidence cannot certify novelty. The **current Agent** reads only relevant evidence and writes up to three different, falsifiable ideas. Each one states legal predecision information, strongest alternative, differentiating prediction and a cheap experiment.
3. Save the candidate JSON as \`PROJECT/ideas.json\` (below), then build source-bound hypothesis bank:
   \`\`\`bash
   python -m adapters.hypothesis_bank build --project PROJECT --cards PROJECT/ideas.json --seeds PROJECT/observation-seeds.json --literature PROJECT/papers.json --out PROJECT/HYPOTHESES_v1.json
   python -m adapters.opportunity_review --project PROJECT --bank PROJECT/HYPOTHESES_v1.json --out PROJECT/OPPORTUNITIES_v1.json
   \`\`\`
   Omit either \`--seeds\` or \`--literature\` if absent. Alternatively attach \`--data-note PROJECT/data-notes.txt\` as **agent narrative, not an independently verified data effect**. Source IDs in idea cards must match exactly those in the seed/metadata bundles.
4. Use the cheapest result-changing next probe in the existing Task/Experiment process. When a **genuine independently verified DEV** Run exists (not merely a self-reported score), append versioned feedback:
   \`\`\`bash
   python -m adapters.hypothesis_bank feedback --project PROJECT --bank PROJECT/HYPOTHESES_v1.json --hypothesis-id H01 --run PROJECT/runs/R2/RUN.json --assessment INCONCLUSIVE --out PROJECT/HYPOTHESES_v2.json
   \`\`\`
   Assessment is a declared interpretation: \`SUPPORTS_EXPECTED_PATTERN\`, \`CONTRADICTS_EXPECTED_PATTERN\`, or \`INCONCLUSIVE\`. **Never** overwrite v1. A changed legal K, Task or protocol requires a new task-scoped version, not a silent success of the previous experiment.

## Minimum idea card, produced by the Agent (not automatically invented by this script)

\`\`\`json
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
\`\`\`

\`source_seed_ids\` or \`paper_record_ids\` may be empty when only the other is available; for data-note-only candidates set \`uses_data_note: true\`. All examples are **illustrative**. Do not fabricate a paper record ID or claim the example mechanism is true.

## Review semantics / safety

- \`adapters.opportunity_review\` sorts by **next evidence action**, not estimated scientific success: first identify blocked information, absent DEV signal, untested legitimate inputs, strong-matched-baseline need, or a bounded discriminator. No fake numerical priority score or publication probability. Missing information is \`UNKNOWN\`, not automatic STOP.
- Observation seeds link to independently recomputed Run receipts but are selected DEV descriptions; **not** independent scientific discovery, headroom bound, causality or novelty. Paper metadata is **METADATA_ONLY** until original nearest work is read.
- Real experiments remain with authorized Codex/WorkBuddy or existing allowlisted CPU executor. Run/Task/Claim contracts and protected evaluator remain authoritative. Future-scoped causal event semantics require additional provenance; stored predictions alone cannot certify execution.
- Do not force a literature query, GPU Pilot, hypothesis bank or 1–3 candidates for already-certain Tasks; simply resume the existing verified state and next action.
- Historical blind replay and prospective success-rate evaluation are **NOT_MEASURED**. Synthetic unit tests validate engineering behavior only.
