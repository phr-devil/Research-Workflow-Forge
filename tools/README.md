# Research tools — actual execution boundaries

- Offline: `core.cli` init/route/record/history/validate/compare; non-executing state and experiment shape checks.
- Explicit public network: `adapters.researchstudio_search` (vendored multi-provider ResearchStudio Worker + dedup), optional older `adapters.literature` (OpenAlex/Crossref).
- Offline research handoff: `adapters.novelty_check` (UNVERIFIED prior-art matrix), `adapters.experiment_plan` (PLAN_ONLY, authorized resource cap only as input data).
- Vendored unit checks: upstream ResearchStudio postprocess/runtime selftests; local Python unit tests under `tests/`.

**Not implemented:** official dataset integrity acquisition, full-text verified novelty analysis, training/inference runner, AIDE candidate search loop, protected independent scientific confirmation, automated research-paper generation. Do not claim these exist from upstream Skill references.

Follow the current user's scope/authorization, preserve real sources/negative Runs. Do not create decorative images or tests of irrelevant modules. Details in `docs/BUILD_PLAN.md`.

**v0.4 read-only utilities:** `python -m tools.data_audit --manifest ...` and `--dev-csv DEV.csv --group-col GROUP --label-col LABEL` check official-source metadata and local DEV integrity without training or sealed reading. `core.cli selection`, `journal`, `check-task` inspect versioned state/Run history. Model fitting, fair baseline optimization and actual independent effect estimation remain future integrations.

**v0.5 functional update:** tools.data_audit CLI now enforces Manifest-bound local DEV access. tools.experiment_runner is an optional real grouped CPU DEV pilot (sklearn dummy/logistic/forest; fit opt-in and real user authorization required), emitting raw prediction/log digests. core.cli champion explicitly chooses among verified comparable Runs; candidates and recover are auditable offline utilities. No general agent code execution, GPU training, sealed evaluation or paper claims are implemented.
