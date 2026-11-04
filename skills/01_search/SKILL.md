---
name: research-opportunity-search
description: Find source-backed research opportunities and candidate assets within current scope.
---
# 01 | Research opportunity search

Shared execution rules: [EXECUTION_POLICY](../../docs/EXECUTION_POLICY.md). Invoke only when direction, evidence or opportunity is missing; **do not re-search a proven Task/Run by default**.

- Build complementary searches around the problem, observed failures, mechanism, legal evaluation and available datasets. Reuse verified sources and distinguish `OBSERVED / HYPOTHESIZED / UNKNOWN`.
- Prefer a small set of candidates with **different failure premises**; identify key closest methods, dataset/label prospects, the critical unknown and the cheapest discriminating next check. Search historic foundations as needed, not an arbitrary paper count.
- Executable metadata entry: `python -m adapters.researchstudio_search --query "problem" --query "mechanism" --out projects/ID/EVIDENCE.json`. Upstream ResearchStudio deduplicates/ranks; Forge records source failures and DOI conflicts. Older `adapters.literature` is fallback only.
- Title/abstract search is **not** a full-text novelty verdict. Read original nearest papers only when a real decision depends on them.

**High-value opportunity discovery (only if new problem/novelty is unresolved):** use [HIGH_VALUE_RESEARCH_ENGINEERING](../../docs/HIGH_VALUE_RESEARCH_ENGINEERING.md) §01. Borrow STORM's complementary questions about real consequence, measurement/physics limits and strongest method failure; borrow PaperQA2's original-paper-backed contradiction search. For each of at most 3 different premises, state`IMPORTANT_QUESTION | NAMED_NEAREST_GAP | WHAT_SUCCESS_TEACHES | STRONGEST_COUNTEREVIDENCE | CHEAP_DISCRIMINATOR | Q2_ANALOG_OR_UNKNOWN`. A short shortlist beats a giant literature dump; not every novelty hypothesis merits training. Never treat metadata/absence of papers as original full-text verification.

**Handoff:** short opportunity shortlist with source/version IDs, distinguishing risk, assets and `next_probe`; route to 02 if resource eligibility is unknown, else to 03.

**v0.10 targeted literature-to-problem search:** For each genuine observed failure or predecision information constraint, search nearest methods by (a) actual Task and legal input/K, (b) claimed mechanism and its simple alternative, and (c) same failure symptom in another field. Use `adapters.researchstudio_search` once per new uncertainty; feed exact `record_id` into the hypothesis bank. Metadata only raises candidates, never verifies novelty; reread full original nearest paper if a publication decision hinges on overlap. No repeated wide scans after credible evidence exists.
