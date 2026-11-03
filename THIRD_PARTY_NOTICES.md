# Third-party code / documentation notices (v0.3)

**ResearchStudio** — https://github.com/microsoft/ResearchStudio
- Pinned commit: `063f10088af49909e1a4a7ea8d29efe19633f34e`
- License: MIT; original LICENSE preserved at `vendor/researchstudio/LICENSE` (Copyright (c) 2026 Happy).
- Copied **unchanged**: `ResearchStudio-Idea/skills/paper_search/SKILL.md`, `references/programmatic_api.md`, scripts `search_papers.py`, `source_worker.py`, `postprocess.py`, `_http_runtime.py`, `_env.py`, 6 provider connectors (arxiv, crossref, dblp, open_alex, openreview, semantic_scholar), `selftest_postprocess.py`, `selftest_runtime.py`, `skills/scoop_check/SKILL.md`, `scripts/fetch_paper.sh`, and `skills/idea_spark/references/` files `anti-patterns.md`, `intake-routing.md`, `relevance-partition-rubric.md`, `pattern-summary-rubric.md`. All are mirrored under `vendor/researchstudio/`.
- We **did not copy** the giant IdeaSpark `run.py` pipeline, quality engines, LaTeX/PDF renderers, model prompts or unrelated connectors. Forge-original `adapters/researchstudio_search.py` calls the vendored source workers and postprocess; `adapters/novelty_check.py` adapts the idea behind four-axis checks but does not copy upstream source.
- Scope: upstream Paper Search provides metadata, not independent novelty verification. The original IdeaSpark `anti-patterns.md` contains dataset- and venue-specific empirical priors, **not general research rejection criteria**. `fetch_paper.sh` is upstream reference only and may require Bash/Unix tools; not automatically executed on Windows.

**ARIS / Auto-claude-code-research-in-sleep** — https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep
- Pinned commit: `2927b40b2ea37774de53763338c5e8f91a7601e6`
- License: MIT; preserved at `vendor/aris/LICENSE` (Copyright (c) 2026 wanshuiyin).
- Copied **unchanged**: `skills/experiment-plan/SKILL.md` to `vendor/aris/experiment-plan/SKILL.md`.
- Forge-original `adapters/experiment_plan.py` selectively adapts claim-to-evidence experimental planning, without adopting ARIS's default Reviewer/GPU authorizations, model provider assumptions or fixed experiment counts.

**Other projects** listed in [SOURCES.md](SOURCES.md) are architectural inspirations, **not included or installed**. Copying additional upstream files requires a new provenance entry, the exact upstream revision and any LICENSE/NOTICE obligations. This repository's own distribution license has not yet been selected; upstream MIT permissions do not imply blanket licensing of unrelated project code.
