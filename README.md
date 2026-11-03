# Research Workflow Forge · v0.9

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


**v0.8：新增可信DEV评价格式**：固定组清单下支持回归MAE/RMSE和单发事件定位的算术复算、源数据绑定与实验可比性保护。详细协议见[ARTIFACT_CONTRACT.md](docs/ARTIFACT_CONTRACT.md)。分类v0.7继续兼容；复杂模型仍由外部Agent执行，因果在线性与源码真实性不能仅由预测工件证明。


外部Codex/WorkBuddy的回归或事件预测可用`python -m adapters.typed_agent_bridge` 导入；程序只复核合法DEV分组、标签、样本与指标，不运行Agent源码或证明真实因果执行。用法见[工件合同](docs/ARTIFACT_CONTRACT.md)。

## v0.9 · 真实信号与剩余空间画像

新增按需、无训练的 `tools.feasibility_probe`：仅分析已通过 Forge 独立指标重算的开发集预测；按独立组报告错误结构，使用**同任务、同协议、同合法信息**的可信参考 Run 计算配对增量。**不会**把残差比例当理论可达上限，也不会因负增益决定项目 STOP 或因正增益宣布论文成功。分类错误率和回归绝对误差提供描述性切片；事件任务暂不生成伪造的切片诊断。现有 Task/Run 已知时可直接复用。

```bash
python -m tools.feasibility_probe --project PROJECT --candidate PROJECT/runs/C/RUN.json --reference PROJECT/runs/B/RUN.json --metric macro_F1 --out PROJECT/FEASIBILITY_ENVELOPE.json
```

`--reference` 和 `--out` 可省略；含多项指标的 Run 比较需指定任务的 `--metric`。可将输出交给 [PD-RW 的可行性判读](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/FEASIBILITY_ENVELOPE.md)。不新建默认审批、训练或绘图步骤。
