# Source provenance and integration ledger

Last checked: **2026-11-03**, default branches on public GitHub. Exact pinned commits listed below. This scaffold is **originally written** using selectively adapted mechanisms: **no third-party source code, full Skill text, datasets or model weights have been copied in v0.1**. Do not assume an upstream component has been installed or verified merely because it appears in this ledger.

| Capability used in our framework | Verified upstream path / commit | Declared repo license | Reuse boundary |
| --- | --- | --- | --- |
| Search, bottleneck, novelty verification | [ResearchStudio / ResearchStudio-Idea/skills](https://github.com/microsoft/ResearchStudio/tree/063f10088af49909e1a4a7ea8d29efe19633f34e/ResearchStudio-Idea/skills) (063f1008) | MIT | IdeaSpark, Paper Search, Scoop Check; adapt source-grounded inquiry and version-specific audits, not all mandatory checks |
| Multi-view questions | [STORM / knowledge_storm](https://github.com/stanford-oval/storm/tree/fb951af7744dab086e34962e9bc6fe878e145f83/knowledge_storm) (fb951af7) | MIT | Multiple research perspectives; originally for content synthesis, not proof of scientific originality |
| PDF/full-text evidence | [PaperQA2 / src/paperqa](https://github.com/Future-House/paper-qa/tree/c692d0dfeac4a0296599f7fe21a253a58b7ac12a/src/paperqa) (c692d0df) | Apache-2.0 | Evidence retrieval with citation traces; optional integration |
| Problem and method decomposition | [ResearchAgent / code/pipelines/agents](https://github.com/JinheonBaek/ResearchAgent/tree/babb49b51ebfcebedc39ccde12c9785be7bef46c/code/pipelines/agents) (babb49b5) | **Not declared** | Architectural concept only; no copied source |
| Skill handoff, ideation, coding | [ARIS / skills](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/2927b40b2ea37774de53763338c5e8f91a7601e6/skills) (2927b40b) | MIT | idea-discovery, experiment-bridge, audit patterns; do not import mandatory multi-model reviews or automatic GPU deployment |
| Experiment planning / recovery | [AutoResearchClaw / researchclaw/pipeline](https://github.com/aiming-lab/AutoResearchClaw/tree/be4ba4755bf1b52220f25e13b2293b5956590070/researchclaw/pipeline) (be4ba475) | MIT | Stage contracts, experiment diagnosis/repair; not copying the whole 23-stage pipeline |
| Research ↔ developer feedback | [R&D-Agent / rdagent/core](https://github.com/microsoft/RD-Agent/tree/484776c211e4fbbeef03e0ec00d6bbee7362a4f4/rdagent/core) (484776c2) | MIT | Proposal / evolving framework / evaluation concepts, not automatically integrated |
| Candidate trees and journal | [AIDE / aide](https://github.com/WecoAI/aideml/tree/ad73d227af481bea3de06f884f41b2993dd6453a/aide) (ad73d227) | MIT | Draft/debug/improve candidate history; validation metrics != independent novelty |
| Fixed evaluator / editable training | [AutoResearch / program.md](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md) (228791fb) | **Not declared** | Design idea only. **No code/prose may be copied without license/permission** |
| Future behavior evaluation | [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai/tree/c3360cea51762b3b2411f0d471da33de418724ba) (c3360cea) | MIT | Dataset/solver/scorer for future real Agent evaluations; not integrated |

Other inspiration: [GPT Researcher](https://github.com/assafelovic/gpt-researcher) for question-based retrieval. It is **not a dependency in v0.1**.

## Direct import rules

Before copying or linking any upstream file: verify its **exact** commit, file-level and repository license, LICENSE/NOTICE, transitive dependencies, data/security policy and what is actually needed. Record upstream path, local destination, modification and necessary attributions. A GitHub Star count is not evidence of correctness. Dataset, paper and model licensing are distinct from code licensing.

This new repository has **no distribution LICENSE yet**: maintainer must select one; the above licenses do not automatically license this new work.
