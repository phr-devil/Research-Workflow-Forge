# Research Workflow Forge | v0.2

**面向 AI 的科研工作流**：信息搜索 → 证据/数据 → 科学问题 → 强基线 → 代码实验 → 诊断转向 → 独立确认。七项是**按需调用能力**，不是七个必过门槛。目标：高可行性、可反驳的科学贡献和可复现证据。

An evidence-first modular research workflow with **real public literature-metadata search**, deterministic event routing, artifact-linked state history and safe development-run comparison. **Not yet an autonomous coding/training agent. No research success claims have been validated.**

## Quick start (Python >= 3.10; standard library runtime)

\`\`\`bash
python -m unittest discover -s tests -v
python -m core.cli init --dir projects/demo --project-id demo --goal "Identify a sensor-generalization research opportunity"
python -m core.cli route --dir projects/demo --event NEW_DIRECTION

# Explicitly query OpenAlex + Crossref metadata; public network required:
python -m adapters.literature --query "wearable inertial sensor cross-device generalization" --limit 6 --out projects/demo/EVIDENCE.json
python -m core.cli validate --kind evidence --file projects/demo/EVIDENCE.json

# Link a real structural artifact (not a note alone) to advance the suggested stage:
python -m core.cli record --dir projects/demo --event SEARCH_READY --artifact projects/demo/EVIDENCE.json --note "Public metadata retrieved; full-text novelty unverified"
python -m core.cli history --dir projects/demo
\`\`\`

If network fails, no papers are invented. \`OPENALEX_API_KEY\` is optional for keyless small queries; no key or credential is logged. **Metadata != full text, proof of novelty, availability of datasets or permission for further actions.** The provider adapter has mocked HTTP unit tests; actual API connectivity depends on the running environment.

### Compare real developer runs (not paper confirmation)

\`\`\`bash
python -m core.cli compare --champion projects/demo/runs/A.json --challenger projects/demo/runs/B.json --metric macro_F1
# Add --lower-is-better for an error metric such as RMSE
\`\`\`

Only VALID **development** runs with matching task/protocol/data/evaluator/group/sample/inputs can be compared. Refuses sealed runs and mismatched inputs. A positive delta is **not** independent scientific evidence.

### Router and recovery

- \`python -m core.cli route --dir projects/demo --event NO_GAIN\`: advice only, no experimental action.
- \`python -m core.cli record ... --event NO_GAIN --note "Observed negative pilot"\`: writes a **ROUTING_NOTE_ONLY** record; does **not** advance scientific phase.
- \`python -m core.cli record ... --event RUN_RESULT --artifact projects/demo/RUN.json --note "Valid Run logged"\`: checks structure and file hash, then sets *suggested next phase*. This is **ARTIFACT_STRUCTURAL_ONLY**, not a verified scientific conclusion.
- \`python -m core.cli history --dir projects/demo\`: detects a mismatch between last persisted event and state (e.g., interrupted write).

Raw Run logs and legitimate training approvals are still checked by the execution Agent. Neither the CLI nor any file automatically grants GPU/CPU fitting, download, spending, sealed-test or submission permission.

## Three engines, seven skills

| Engine | Skills | Purpose |
| --- | --- | --- |
| Opportunity | [01 Search](skills/01_search/SKILL.md), [02 Evidence/Data](skills/02_evidence_data/SKILL.md), [03 Problem](skills/03_problem_design/SKILL.md) | Find source-backed problems, reliable assets and plausible distinct contributions |
| Development | [04 Feasibility](skills/04_feasibility/SKILL.md), [05 Algorithm](skills/05_algorithm/SKILL.md) | Legal baselines, testable implementation and experiment comparison |
| Decision/Confirmation | [06 Decision](skills/06_decision/SKILL.md), [07 Confirmation](skills/07_confirmation/SKILL.md) | Repair without premature STOP; confirm only with independent evidence |

Core entry: [AGENTS.md](AGENTS.md). Design: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Exact artifact shapes: [docs/CONTRACTS.md](docs/CONTRACTS.md). Roadmap: [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md). Upstream/commit/license ledger: [SOURCES.md](SOURCES.md).

## Scientific boundaries

- Exploration allows falsifiable UNKNOWNs, and one negative Pilot is not a project-wide STOP. A valid failure only affects its evidence-supported scope.
- Software PASS != learnable task != new independent scientific contribution. Use genuinely comparable tuned baselines, legal label/group splits and an untouched eligible confirmation resource.
- Preserve raw outputs, protocol/data/code versions and negative runs. The event file records structural pointers, not actual permission or proof.
- The optional upstream components PaperQA2, ARIS, AIDE, R&D-Agent and ResearchStudio are **reference architectures only** until separately integrated and tested. No upstream source files were copied into this repository.

The repository has not selected a distribution license; see [SOURCES.md](SOURCES.md).
