# Research Workflow Forge | v0.4

**科研工作流不是固定关卡，而是证据驱动的研究循环。**

Forge: 01 Search → 02 Evidence/Data → 03 Problem Design ↔ 04 Feasibility → 05 Algorithm ↔ 06 Decision → 07 Independent Confirmation. An Orchestrator routes the *current* blocker; previously valid sources/runs are reused.

**Current implementation:** public multi-source paper metadata retrieval (ResearchStudio vendor), source-linked **unverified** novelty precheck, bounded non-executing experiment plan (ARIS-inspired), evidence-linked event history, Run comparability rules and tests. **Not implemented:** automatic novel problem generation, full-text novelty judgment, automated CPU/GPU training, scientific confirmation, publication. Successful tests do not prove scientific quality.

## v0.4 changes

- **State integrity:** explicit TASK_PIVOT and PROTOCOL_REVISED decisions, input/output receipts, cross-platform event locks and selection history. Old Champions are retired on task/protocol changes, while historical Runs persist.
- **Research search:** historical papers no longer excluded by a silent four-year default; protect distinct known DOIs, and treat top results as screening candidates rather than verified nearest work.
- **Real read-only checks:** DEV-only CSV/data-manifest preflight, candidate Run history, executable structural route fixtures and Windows CI.
- **Copied reference Skills:** Superpowers debugging and verification-on-completion (MIT), loaded only for relevant engineering defects.

Practical migration and exact commands: [docs/UPGRADE_V04.md](docs/UPGRADE_V04.md). These changes do NOT add an autonomous trainer, an AI verified-novelty system, or a scientific success-rate guarantee.

## Install / verify (Python 3.10+)

```powershell
git clone https://github.com/phr-devil/Research-Workflow-Forge.git
cd Research-Workflow-Forge
python -m pip install -e ".[paper-search]"
python -m unittest discover -s tests -v
python vendor/researchstudio/paper_search/scripts/selftest_postprocess.py
python vendor/researchstudio/paper_search/scripts/selftest_runtime.py
```

Optional OpenReview backend requires `python -m pip install -e ".[openreview]"` and any upstream provider credentials. Crossref, OpenAlex, arXiv, DBLP, Semantic Scholar are available through provider-specific code and subject to network/API limits.

## Research opportunity → task → experiment, without fabricated results

```powershell
python -m core.cli init --dir projects/demo --project-id demo --goal "Sensor cross-device generalization"

# Real public paper metadata search; execute only when public outbound retrieval is authorized.
python -m adapters.researchstudio_search --query "wearable inertial sensor cross device generalization" --query "sensor domain shift calibration" --sources open_alex crossref arxiv --limit 6 --out projects/demo/EVIDENCE.json
python -m core.cli validate --kind evidence --file projects/demo/EVIDENCE.json
python -m core.cli record --dir projects/demo --event SEARCH_READY --artifact projects/demo/EVIDENCE.json --note "Public metadata only, not novelty proof"
```

Use [03 Problem Design](skills/03_problem_design/SKILL.md) to create a *real* `projects/demo/TASK.json` grounded in specific dataset/legal inputs/metric/split. `templates/TASK.json` is a placeholder and must not be treated as actual research. A DRAFT Task may be prepared before its protocol is known. Only an ACTIVE Task is eligible for experiment planning.

To register an actually completed ACTIVE Task before an experiment handoff:

```powershell
python -m core.cli record --dir projects/demo --event TASK_DEFINED --artifact projects/demo/TASK.json --note "Verified real task and evaluation protocol"
```

```powershell
# Four-axis precheck (never declares the proposed novelty true)
python -m adapters.novelty_check --task projects/demo/TASK.json --evidence projects/demo/EVIDENCE.json --mechanism "Our proposed mechanism" --difference "Its falsifiable expected scientific difference" --out projects/demo/NOVELTY.json

# After real Task data/protocol is complete and status=ACTIVE:
python -m adapters.experiment_plan --task projects/demo/TASK.json --novelty-review projects/demo/NOVELTY.json --hypothesis "Model B should improve group-level performance under a legal split" --evaluator-ref "frozen-evaluator-v1" --gpu-hours-max 0.5 --positive "Verify effect and alternative explanation" --negative "Diagnose convergence and residual mechanism" --out projects/demo/EXPERIMENT.json
python -m core.cli record --dir projects/demo --event EXPERIMENT_PLAN_READY --artifact projects/demo/EXPERIMENT.json --note "Planning only; no fitting authorized"
```

The novelty review carries Task/Evidence SHA-256 fingerprints; a changed Task is rejected as stale when used for experiment planning. The generated plan contains a **PLAN_ONLY** status and grants **no** CPU/GPU fitting, data transfer or sealed confirmation authority. A shell pipeline does not automatically promote an unverified Task to ACTIVE.

## Evidence and control

- [AGENTS.md](AGENTS.md) is the one short entry: read only the current [Skill](skills/03_problem_design/SKILL.md).
- `python -m core.cli route --dir projects/demo --event NO_GAIN`: no training; returns a Skill suggestion.
- `python -m core.cli compare --champion A.json --challenger B.json --metric macro_F1`: accepts only comparable VALID **development** Runs.
- `python -m core.cli history --dir projects/demo`: detects event log/STATE disagreement.
- `core.cli record` with no `--artifact` saves a note **without** advancing scientific phase.
- Untouched confirmation data, distinct user execution authorization, legitimate true labels, strong fair baselines, named nearest work and claim-specific independent evidence are never optional for formal claims.

## Files and upstream sources

| Component | Role |
| --- | --- |
| [skills/](skills/) | Seven short, conditionally loaded AI research capabilities |
| [adapters/researchstudio_search.py](adapters/researchstudio_search.py) | Executes vendored upstream source workers, produces Forge evidence JSON |
| [adapters/novelty_check.py](adapters/novelty_check.py) | Metadata-linked four-axis novelty questions; **UNVERIFIED** |
| [adapters/experiment_plan.py](adapters/experiment_plan.py) | Converts ACTIVE Task to bounded PLAN_ONLY ExperimentSpec |
| [vendor/](vendor/) | Pinned, unmodified upstream reference code/docs and their licenses |
| [core/](core/) | Event router, artifact contracts, state and dev Run comparison |
| [tests/](tests/) | Offline regression tests and vendored source tests |
| [SOURCES.md](SOURCES.md) / [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | Exact provenance, commit IDs, copying boundaries and licenses |
| [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md) | Remaining execution integration and scientific benchmark |

All vendored sources and adapted docs remain optional and are **not loaded into the Agent context by default**. Imported Skills from ARIS/ResearchStudio include upstream-specific instructions; Forge Skills, local authorizations, task contracts and actual tooling take priority. No upstream Skill is permitted to invent a run or override a user's permission boundary.

Forge itself remains unlicensed pending maintainer selection; individual MIT-licensed upstream copies remain under their preserved licenses.
