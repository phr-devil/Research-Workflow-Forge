# Tools · current execution boundaries (v0.9)

- `core.cli`: versioned Task/Run/Champion, immutable evidence hashes and dev-metric recomputation, history and branch recovery.
- `tools.data_audit`: manifest-bound DEV integrity and label/group check, not training or sealed confirmation.
- `tools.experiment_runner`: optional real grouped CPU DEV classification fit (dummy/logistic/forest), only under actual user permission. Does not run arbitrary Agent source.
- `tools.feasibility_probe`: **no fitting**, uses independently verified DEV Run predictions to report group error/residual and optional matched-reference paired gain. Does not declare learnability/Oracle, scientific novelty or attainable headroom. Reading DEV logs data access; `--out` writes a fresh report only when requested.
- `core.action_output`: optional human-vs-Agent output-mode preflight; flags alone never prove user authorization or execute actions. Follow [NEXT_ACTION_POLICY](../docs/NEXT_ACTION_POLICY.md).
- `adapters.agent_bridge`, `adapters.typed_agent_bridge`: import external classification/regression/event predictions under trusted DEV evaluator; external training/sandbox provenance is **not attested**.
- `adapters.researchstudio_search`: optional network paper metadata lookup, **not full-text novelty verification**; `adapters.novelty_check` is UNVERIFIED screening; `adapters.experiment_plan` is PLAN_ONLY.
- Offline checks: `python -m unittest discover -s tests -v` plus vendored ResearchStudio selftests.

**No** autonomous arbitrary Agent code executor, independently protected sealed evaluation service, user authorization from JSON, automatically proven novelty or publication engine. See [execution policy](../docs/EXECUTION_POLICY.md), [artifact contract](../docs/ARTIFACT_CONTRACT.md), and [PD-RW diagnostic interpretation](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/FEASIBILITY_ENVELOPE.md).

Typical diagnostic:

```bash
python -m tools.feasibility_probe --project PROJECT --candidate PROJECT/runs/C/RUN.json --reference PROJECT/runs/B/RUN.json --metric macro_F1 --out PROJECT/FEASIBILITY_ENVELOPE.json
```

Without a reference it reports **UNKNOWN signal**, not failure. A reference is not independently guaranteed to be an appropriate dummy/strong baseline; inspect implementation, K, legal information, tuning parity and selection history separately. No automatic scientific STOP/GO or charts.
