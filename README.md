# Research Workflow Forge · v0.7

An evidence-first research workflow with **one controller, three engines, seven on-demand Skills**. Starting point: the current scientific/engineering blocker, not a mandatory 7-step sequence. Optimize for **verified research progress per actual total resource cost**, not document count, number of Agent calls, or plots.

## Quick use

```powershell
git clone https://github.com/phr-devil/Research-Workflow-Forge.git
cd Research-Workflow-Forge
python -m pip install -e ".[paper-search,runner]"
python -m unittest discover -s tests -v
python -m core.cli init --dir projects/demo --project-id demo --goal "Evaluate a valid research task"
python -m core.cli brief --dir projects/demo
python -m core.cli route --dir projects/demo --event NEW_DIRECTION
```

To resume an existing project, run `python -m core.cli brief --dir PROJECT --recent 2`, read only the cited active Task/Run and current relevant Skill, then execute a **coherent, authorized batch** of work. A brief is state pointers, not scientific verification.

## Engines and actual implementation

| Engine | Skills | Current tool boundary |
| --- | --- | --- |
| Discovery | 01 Search · 02 Evidence/Data · 03 Problem | Multi-provider literature **metadata**, verified DEV roles, **UNVERIFIED** novelty precheck |
| Development | 04 Feasibility · 05 Algorithm | `PLAN_ONLY` experiment contracts; manifest-bound DEV audit; optional grouped CPU dummy/logistic/forest pilot; raw SHA receipts; explicit Champion |
| Decision/Confirmation | 06 Decision · 07 Confirmation | Failure scope, pivot, selection history, safe recovery; independent scientific confirmation **not automated** |

A real CPU fit requires separately verified user permission and `--allow-cpu-fit` on the allowlisted runner; the flag is **not** itself authorization. The tools are cooperative guards, not an arbitrary-code sandbox. No autonomous Codex/WorkBuddy integration, GPU engine, full-text novelty verification, or established improvement in paper success rate.

## Efficient execution defaults

**Load only one Skill** and relevant evidence; reuse verified runs, searches and data. Batch inspect→edit→focused test→repair→record. During exploration skip decorative images and publication figures; make a small diagnostic chart only when needed to decide. Use concise *delta-only* updates instead of repeated reports. Full CI at integration/release, not after every minor edit. A negative Pilot prompts diagnosis, not automatic project STOP. **Never weaken legal splits, permissions, reproducibility or independent confirmation to save tokens.**

The [shared execution policy](docs/EXECUTION_POLICY.md) is authoritative for these defaults. [AGENTS.md](AGENTS.md) is the shortest AI entry; [architecture](docs/ARCHITECTURE.md), [contracts](docs/CONTRACTS.md), and [build plan](docs/BUILD_PLAN.md) describe current behavior, not appended version histories. Prior changes remain under [UPGRADE_V04](docs/UPGRADE_V04.md) and [UPGRADE_V05](docs/UPGRADE_V05.md); upstream copyrights in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

CI uses only synthetic research fixtures and source selftests; passing tests never proves a scientific paper claim.

## v0.7 trustworthy metrics & external Agent handoff

VALID development metrics are now independently recomputed from original manifest-bound DEV labels and a fixed group-held-out split; raw SHA receipts alone cannot certify claimed performance. CHAMPION is exploratory only and displays optional group-bootstrap uncertainty and adaptive-selection count. `compare` now requires `--dir PROJECT` and independently verifies both Run files. Event history is SHA-chained against STATE; legacy projects need explicit `core.cli migrate-ledger` before writing events. Normal development events reject all sealed Runs. The external `adapters.agent_bridge` imports Codex/WorkBuddy/AIDE predictions **without executing arbitrary Agent code**. See [artifact contract](docs/ARTIFACT_CONTRACT.md) and [upgrade guide](docs/UPGRADE_V07.md).

**SAFE-Gait success/failure lesson:** when Oracle gain does not translate into a deployable learned strategy, separate correctability from predecision identifiability and from legal calibration cost. A K=0→K=1 move changes the scientific Task and Claim; do not claim the old task succeeded. Optional evidence-grounded example: [PD-RW APACE→SAFE-Gait lesson](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/LESSONS/SAFE_GAIT_APACE.md). No extra mandatory stage or model training is added.
