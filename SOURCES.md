# Source provenance and integration ledger

Last checked: **2026-11-03**, default branches on public GitHub. Exact pinned commits listed below. v0.3 includes pinned MIT-licensed upstream slices copied unchanged under vendor/, with original license texts and the exact copied-file inventory in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Forge adapters are original. Other source projects remain conceptual references only.

| Capability used in our framework | Verified upstream path / commit | Declared repo license | Reuse boundary |
| --- | --- | --- | --- |
| Search, bottleneck, novelty verification | [ResearchStudio / ResearchStudio-Idea/skills](https://github.com/microsoft/ResearchStudio/tree/063f10088af49909e1a4a7ea8d29efe19633f34e/ResearchStudio-Idea/skills) (063f1008) | MIT | Paper Search is now vendored and exercised by our adapter; selected IdeaSpark references and Scoop Check Skill are mirrored; full IdeaSpark executor is not imported |
| Multi-view questions | [STORM / knowledge_storm](https://github.com/stanford-oval/storm/tree/fb951af7744dab086e34962e9bc6fe878e145f83/knowledge_storm) (fb951af7) | MIT | Multiple research perspectives; originally for content synthesis, not proof of scientific originality |
| PDF/full-text evidence | [PaperQA2 / src/paperqa](https://github.com/Future-House/paper-qa/tree/c692d0dfeac4a0296599f7fe21a253a58b7ac12a/src/paperqa) (c692d0df) | Apache-2.0 | Evidence retrieval with citation traces; optional integration |
| Problem and method decomposition | [ResearchAgent / code/pipelines/agents](https://github.com/JinheonBaek/ResearchAgent/tree/babb49b51ebfcebedc39ccde12c9785be7bef46c/code/pipelines/agents) (babb49b5) | **Not declared** | Architectural concept only; no copied source |
| Skill handoff, ideation, coding | [ARIS / skills](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/2927b40b2ea37774de53763338c5e8f91a7601e6/skills) (2927b40b) | MIT | Experiment Plan Skill is now vendored as a rubric; idea-discovery/experiment-bridge remain reference concepts, not copied or installed |
| Experiment planning / recovery | [AutoResearchClaw / researchclaw/pipeline](https://github.com/aiming-lab/AutoResearchClaw/tree/be4ba4755bf1b52220f25e13b2293b5956590070/researchclaw/pipeline) (be4ba475) | MIT | Stage contracts, experiment diagnosis/repair; not copying the whole 23-stage pipeline |
| Research ↔ developer feedback | [R&D-Agent / rdagent/core](https://github.com/microsoft/RD-Agent/tree/484776c211e4fbbeef03e0ec00d6bbee7362a4f4/rdagent/core) (484776c2) | MIT | Proposal / evolving framework / evaluation concepts, not automatically integrated |
| Candidate trees and journal | [AIDE / aide](https://github.com/WecoAI/aideml/tree/ad73d227af481bea3de06f884f41b2993dd6453a/aide) (ad73d227) | MIT | Draft/debug/improve candidate history; validation metrics != independent novelty |
| Fixed evaluator / editable training | [AutoResearch / program.md](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md) (228791fb) | **Not declared** | Design idea only. **No code/prose may be copied without license/permission** |
| Future behavior evaluation | [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai/tree/c3360cea51762b3b2411f0d471da33de418724ba) (c3360cea) | MIT | Dataset/solver/scorer for future real Agent evaluations; not integrated |

| Root-cause diagnosis / verification | [obra/superpowers](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills) (2ce8aa15) | MIT | Two optional Skills now copied unchanged under vendor/superpowers; error diagnosis and evidence-before-completion; not compulsory in research exploration |
| Progressive Skills loading | [anthropics/skills](https://github.com/anthropics/skills/tree/ca45fc496a3436251f191354091d557da31c15b5) (ca45fc49) | **Repository-level metadata not declared** | Load metadata, then one SKILL, then optional references; conceptual only |

**New provider documentation for original `adapters/literature.py`:** [OpenAlex API](https://help.openalex.org/api/) and [authentication](https://help.openalex.org/api/authentication/); [Crossref REST access](https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication). Public metadata endpoints, no provider code copied. Only a user's explicit CLI invocation causes outbound requests. OpenAlex's free keyless access has limits; optional user-owned API key is read from the environment and transmitted by header, never logged. Crossref is queried sequentially at small volume with no claims of exhaustive review.

Other inspiration: [GPT Researcher](https://github.com/assafelovic/gpt-researcher) for question-based retrieval. It is **not a runtime dependency**.

## Direct import rules

Before copying or linking any upstream file: verify its **exact** commit, file-level and repository license, LICENSE/NOTICE, transitive dependencies, data/security policy and what is actually needed. Record upstream path, local destination, modification and necessary attributions. A GitHub Star count is not evidence of correctness. Dataset, paper and model licensing are distinct from code licensing.

Forge-authored code still has **no distribution LICENSE** selected: maintainer must select one; the above licenses do not automatically license this new work.

**v0.4:** Cross-platform receipt/lock and scoped task transitions are Forge-original, selectively adapting the quality receipt principle from ResearchStudio. Conservative DOI metadata merge uses upstream ResearchStudio lexical ranking but adds Forge conflict safeguards. See [docs/UPGRADE_V04.md](docs/UPGRADE_V04.md).


## v0.10 hypothesis-discovery design references (conceptual reuse only)

- ChicagoHAI/HypoGeniC and HypoRefine: https://github.com/ChicagoHAI/hypothesis-generation — evidence+literature hypothesis refinement patterns; no upstream code copied.
- Baek et al., ResearchAgent, NAACL 2025: https://github.com/JinheonBaek/ResearchAgent — paper/knowledge-grounded problem ideation, compact critical feedback; no code copied or license inferred.
- Stanford POPPER: https://github.com/snap-stanford/POPPER — falsification-first experiment proposals; Forge does not implement POPPER's sequential error-rate guarantees.
- Technion data-to-paper: https://github.com/Technion-Kishony-lab/data-to-paper — traceable data-to-evidence loop; no paper-writing integration or code copied.
- MOOSE-Chem: https://github.com/ZonglinY/MOOSE-Chem — cross-domain inspiration considered as an occasional human/Agent idea source, not an automatic novelty generator.
- ScienceAgentBench: https://github.com/OSU-NLP-Group/ScienceAgentBench — real execution benchmarking inspiration; historical blind replay not yet performed.
