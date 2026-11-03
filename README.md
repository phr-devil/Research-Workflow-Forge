# Research Workflow Forge v0.5

Modular evidence-first research workflow: opportunity → data/evidence → falsifiable Task → baseline → algorithm iteration ↔ scoped decision → independent scientific confirmation. Skills are non-linear capabilities.

**Implemented:** vendored ResearchStudio multi-provider metadata search; UNVERIFIED novelty precheck; PLAN_ONLY experiment planning; versioned Task/Run states and pivots; manifest-bound DEV access; SHA-verified raw Run artifacts; explicit evidence-backed Champion selection; one-event crash recovery; AIDE-style candidate lineage; optional CPU-only grouped dummy/logistic/forest development runner.

**Not implemented:** an autonomous Codex/WorkBuddy coding backend, unrestricted algorithm research, GPU execution, full-paper novelty assessment, external independent confirmation, proven paper success-rate improvement.

## Install and test

    git clone https://github.com/phr-devil/Research-Workflow-Forge.git
    cd Research-Workflow-Forge
    python -m pip install -e ".[paper-search,runner]"
    python -m unittest discover -s tests -v

## Real project flow (requires real data and authorization)

1. Use core.cli init to create project STATE; run adapters.researchstudio_search for actual paper metadata; complete Task and DATA_MANIFEST from official datasets and real legal inputs.
2. Register ACTIVE Task with core.cli record --event TASK_DEFINED --artifact PROJECT/TASK.json.
3. Read-only audit must use --manifest and --dataset-id. DEV manifest requires local_path, SHA256, source_url, role=DEV, group_unit, group_column, label_column, label_status=VERIFIED for fitting and numeric feature_columns.
4. Only with actual user approval, run tools.experiment_runner --project PROJECT --manifest PROJECT/DATA_MANIFEST.json --dataset-id D --model dummy --run-id R1 --allow-cpu-fit; this performs a REAL bounded local CPU fit on registered DEV data. It cannot run an arbitrary Agent-produced program.
5. Register the output runs/R1/RUN.json with core.cli record --event BASELINE_VALID; this validates raw SHA receipts but does not automatically mark the model best.
6. Preview best-model selection with core.cli champion --dir PROJECT --candidate PROJECT/runs/R1/RUN.json. Add --apply to commit selection. The active Task must explicitly specify metric_direction=maximize or minimize.
7. Run a Challenger (logistic or forest), optionally with --parent-run-id R1 after registering the baseline, and compare same DEV protocol with core.cli compare. Inspect core.cli journal and candidates for parentage and failures.
8. For an interrupted event use core.cli recover --dir PROJECT (preview), then --apply only if one safe verified event can be replayed. Independent paper confirmation is a separate scientific task.

DataAccess logs DEV access before reading; the tools are cooperative protections, not an OS security sandbox. Synthetic CI fits are engineering tests, not scientific results. Raw outputs, negative candidates and source provenance are retained.

Docs: AGENTS.md, docs/CONTRACTS.md, docs/ARCHITECTURE.md, docs/UPGRADE_V05.md, SOURCES.md, THIRD_PARTY_NOTICES.md.
