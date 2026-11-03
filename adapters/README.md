# Adapters: integrated, optional, and planned

**Real optional upstream-backed search (v0.3):** `python -m adapters.researchstudio_search --query "sensor domain shift" --sources open_alex crossref arxiv --out projects/demo/EVIDENCE.json`. It explicitly calls *vendored ResearchStudio* source_worker and postprocess, retaining provider-level errors and deduped provenance. Install the optional extra: `pip install -e ".[paper-search]"`. OpenReview requires `.[openreview]` and its own credentials. Network-dependent searches are not used in CI; upstream localhost HTTP tests and mocked Forge queries are.

**Legacy fallback** `adapters.literature` still offers OpenAlex + Crossref metadata only. Keep it for compatibility; do not automatically run both backends and waste tokens/API calls.

**Novelty precheck:** `python -m adapters.novelty_check --task TASK.json --evidence EVIDENCE.json --mechanism "..." --difference "..." --out NOVELTY.json`. Actual content identifies nearest metadata **candidates** and constructs an explicitly UNVERIFIED four-axis inspection matrix. Missing full texts means the candidate's novelty is UNKNOWN, not positive.

**Experiment handoff:** `python -m adapters.experiment_plan --task TASK.json --hypothesis "..." --evaluator-ref "..." --gpu-hours-max 0 --positive "..." --negative "..." --out EXPERIMENT.json`. Requires ACTIVE/FROZEN TaskSpec; rejects a stale novelty review Task fingerprint. Never executes CPU/GPU or authorizes sealed confirmation. Uses the ARIS experiment-plan structure selectively, not its auto-run instructions.

**Still NOT integrated:** full IdeaSpark LLM orchestrator, Scoop Check full-text fetcher, PaperQA2, ARIS auto-deploy/experiment bridge, AIDE journal or R&D-Agent coding loop. Do not mistake vendored reference text for executed scientific checks. Original source files, licenses and frozen commits: [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
