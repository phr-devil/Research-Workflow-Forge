# Research Workflow Forge

A modular, evidence-first AI research workflow. **v0.1 is a tested scaffold, not an autonomous research system.**

## Concept

```text
                        AGENTS.md → Orchestrator
                                  |
       +--------------------------+------------------------+
       v                                                   v
 Opportunity Engine                               Development Engine
 01 Search → 02 Evidence/Data                    04 Feasibility → 05 Algorithm
                    |                                      |
              03 Problem Design ---------------------------+
                    ^                                      |
                    +--------- 06 Decision/Repair/Pivot <--+
                                   |
                              07 Confirmation
                                   |
                     Evidence / Task / Run / Claim
```

The seven capabilities are **event-triggered, not mandatory sequential gates**. Start from the genuine current research blocker, reuse prior verified evidence, and avoid repeating previous stages.

## First use

```bash
python -m unittest discover -s tests -v
python -m core.cli init --dir projects/sensor-study --project-id sensor-study --goal "Find a reproducible sensor-generalization task"
python -m core.cli route --dir projects/sensor-study --event NEW_DIRECTION
python -m core.cli record --dir projects/sensor-study --event SEARCH_READY --note "Evidence sources identified; no training performed"
python -m core.cli validate --kind task --file templates/TASK.json
```

Python >=3.10, no runtime dependencies. The CLI **only routes, checks artifact shapes and saves local state**; it does not search, train, download or grant permissions.

## Modules

| Skill | Purpose | Main handoff |
| --- | --- | --- |
| [01 Search](skills/01_search/SKILL.md) | Search papers, code, datasets and concrete bottlenecks | Opportunity shortlist |
| [02 Evidence & Data](skills/02_evidence_data/SKILL.md) | Verify primary sources, labels, datasets and confirmation eligibility | Evidence/data manifest |
| [03 Problem Design](skills/03_problem_design/SKILL.md) | Form one feasible and falsifiable research task | TaskSpec |
| [04 Feasibility](skills/04_feasibility/SKILL.md) | Protect legal evaluator/splits, establish baseline and cheap probe | ExperimentSpec |
| [05 Algorithm](skills/05_algorithm/SKILL.md) | Write/debug/compare model code; preserve real runs | RunRecord |
| [06 Decision](skills/06_decision/SKILL.md) | Repair, continue, narrow or pivot at evidence-supported scope | Decision |
| [07 Confirmation](skills/07_confirmation/SKILL.md) | Freeze protocol and verify independent contribution | ClaimRecord |

## Architecture and provenance

- [AGENTS.md](AGENTS.md): short AI entry and routing.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): responsibilities and event transitions.
- [docs/CONTRACTS.md](docs/CONTRACTS.md): five structural data contracts and their scientific limits.
- [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md): incremental roadmap and verification plan.
- [SOURCES.md](SOURCES.md): upstream projects, pinned commits, licenses and what was adapted.
- [adapters/README.md](adapters/README.md) and [tools/README.md](tools/README.md): *planned* real integrations (not falsely claimed installed).

## Scientific and safety policy

Exploration admits reasonable falsifiable unknowns; first negative Pilot != project failure. Good performance != scientific novelty. The final claim requires named nearest work, fairly tuned baselines and eligible untouched independent evaluation. Preserve run/source/code/data versions. Downloads, CPU/GPU fitting, expenses, external transfer, sealed testing and submissions require separately verified real user authorization: a STATE file cannot grant permission.

No external source code is copied into v0.1. The repo is currently unlicensed pending a maintainer decision; see [SOURCES.md](SOURCES.md).