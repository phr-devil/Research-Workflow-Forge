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

**Handoff:** short opportunity shortlist with source/version IDs, distinguishing risk, assets and `next_probe`; route to 02 if resource eligibility is unknown, else to 03.
