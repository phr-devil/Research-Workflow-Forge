# Research Workflow Forge · v0.15

**No automatic figures:** diagnostic charts, evidence plots, journal images, algorithm diagrams and previews are generated **only when the user explicitly asks to draw/modify specified images**. See [figure policy](docs/FIGURE_QA_CONTRACT.md).

**Two-file PD-RW handoff:** RWF supplies real Run/experiment and negative-result evidence for the project's RESEARCH_RECORD.md, and selectively updates PAPER_BLUEPRINT.md H1/H2 evidence planning only when relevant, without starting manuscript prose or image drawing. See [dual-document collaboration](docs/PD_RW_DUAL_DOCUMENT_HANDOFF.md).

An evidence-first research workflow with **one controller, three engines, seven on-demand Skills**. Starting point: the current blocker. **Primary outcome before writing authorization is defensible independent scientific evidence with a credible JCR Q2+ submission-potential route (Q1 preferred), not a cheap specialist-journal manuscript at any level**, not the largest model gain or breakthrough. PD-RW remains the optional scientific/venue controller; Forge verifies evidence and proposes the next necessary experiment, not a guarantee of publication.

**Previously hidden science and contribution clarity:** [SCIENCE_RESULT_HARVEST.md](docs/SCIENCE_RESULT_HARVEST.md) integrates existing Skills 05–07. Meaningful DEV results and negative Runs may contain unexplored boundaries, scientific heterogeneity and resource tradeoffs; before project close or expensive retraining, inventory at most three genuine Claim candidates. Distinguish `ARTICULATION_GAP` (research evidence insufficiently explained) from `EVIDENCE_GAP` (proof lacking). Writing lock remains in force.

**Scientific choice ≠ cheap experimental action**: PD-RW (or the human researcher without PD-RW) decides the important scientific question. `adapters.opportunity_review` sorts only feasible NEXT EVIDENCE ACTIONS; without a prior selected hypothesis it returns **no recommended research problem**. With `--selected-hypothesis-id` it suggests an action within that chosen hypothesis. `adapters.science_handoff` checks project-local DEV/public source SHA receipts but does **not** verify the science, Q2, user authorization or training provenance. [Design guide](docs/HIGH_VALUE_RESEARCH_ENGINEERING.md).

**v0.12 evidence-first default**: first verify legal data/evaluator and existing baseline; favor the smallest falsifiable observation or simple correction, preserve a trustworthy simple reference, and escalate model complexity only for a distinct unresolved mechanism or deployment requirement. Separate viable signal, reliable performance and independent scientific novelty. This is a routing preference, not another gate; a complex model can be justified from physical/temporal needs. RWF executes/diagnoses evidence, while PD-RW remains the optional scientific decision lead.

**v0.13 incremental-paper rule:** one evidence-backed, falsifiable improvement relative to the most relevant named prior work can justify a paper candidate: targeted accuracy, speed/memory/energy or label-cost tradeoff, a reproducible boundary/failure pattern, or a meaningful combination of existing ideas. Do not require global SOTA, a novel backbone, multiple independent contributions, or blanket multi-dataset wins. Keep fair comparators, uncertainty, honest negative outcomes and claim-matched independent confirmation; paper acceptance remains unproven.

**v0.14 small-discovery candidate (not Q2 success):** a valid negative challenger, narrowly positive result or efficiency/label-cost tradeoff must be screened for one evidence-backed incremental Claim *before* abandoning the research branch. RWF reports the evidence/gaps; when PD-RW is used, it owns the optional S/A/B/C manuscript-potential and stretch/target/fallback journal matching ([venue strategy](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/VENUE_STRATEGY.md)). Neither a journal tier nor an IF estimate is an automatic STOP/GO rule; do not invent acceptance probabilities or new CLI states.

**v0.15 Q2 evidence-completion priority:** after a verified DEV result or decisive negative Pilot, check whether the independent Claim can become competitive with actual JCR Q2+ published analogs (Q1 preferred), with reasonable, claim-matched evidence. A modest result is an exploratory scientific asset, not automatic research success. Prioritize decisive baseline/confirmation/cost measurements over another network when they better close the Q2 gap. While defining a topic, inexpensive lookup of 1–3 *actually published* analogous papers can calibrate article scope; do not grade journals or impose SOTA in initial discovery. This is Agent guidance, not a new CLI state or permission.

**First-stage search upgrade (no extra conversation rounds):** [Skill 01](skills/01_search/SKILL.md) now challenges the first viable question through different-premise opportunities and strongest original counterevidence; [Skill 02](skills/02_evidence_data/SKILL.md) documents `PRE_DOWNLOAD_SCIENCE_FIT` from official metadata, while [Skill 03](skills/03_problem_design/SKILL.md) returns DEV contradictions to the saved alternative shortlist. The scientific preference stays with PD-RW/user; no auto-download, fit, sealed review or paper drafting permission is added.

**High-value scientific discovery/algorithms:** [HIGH_VALUE_RESEARCH_ENGINEERING](docs/HIGH_VALUE_RESEARCH_ENGINEERING.md) strengthens existing Skills 01–06: important questions → data discriminability → competing predictions → high-upside mechanisms → decisive tests. No extra stage, compulsory Agent or automatic training.

**Research success criterion:** an evidence-backed scientific Claim with credible **JCR Q2-or-higher journal publication potential** counts as success; **Q1 is preferable**, and actual acceptance/publication is not required. Ordinary specialist-journal feasibility and `DRAFTABLE` are only candidates, not success. Scope, category-year, nearest papers and validation matter more than impact-factor thresholds; see [shared policy](docs/EXECUTION_POLICY.md) and [PD-RW goal](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/Q2_PUBLICATION_GOAL.md).

**Next-step decision routing:** [NEXT_ACTION_POLICY](docs/NEXT_ACTION_POLICY.md): give a ready-to-copy Agent instruction for authorized in-scope technical actions; for user-owned decisions, provide recommendation and options, never an early execution prompt.

**Mandatory manuscript writing lock:** scientific results, DRAFTABLE and the early PAPER_BLUEPRINT.md H1/H2 planning **do not authorize manuscript prose**. RESEARCH_RECORD.md and outline/section-intent bullets may be updated while research proceeds; to draft formal title, abstract, manuscript sections or full paper, first produce a research-results summary, obtain the user's explicit review, then a separate explicit writing instruction. Image generation remains independently opt-in. See [Execution Policy](docs/EXECUTION_POLICY.md) § Research memory / outline planning versus manuscript writing lock.

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

**External models and larger datasets:** [EXTERNAL_MODEL_EVIDENCE.md](docs/EXTERNAL_MODEL_EVIDENCE.md) describes separately authorized Codex/WorkBuddy training, streamed read-only artifact integrity checks and existing bounded DEV evaluation import. No new arbitrary-code executor or automatic scientific confirmation.

**Completed algorithm, better science (optional):** [post-algorithm science audit](docs/POST_ALGORITHM_SCIENCE_AUDIT.md) adapts WILDS/DomainBed group evaluation, SHAP/Captum/DoWhy hypothesis-and-refutation and Cleanlab/Evidently data checks into a low-cost `reuse → distinguish → one bounded test → retain or summarize` route. No new Skill, CLI event, dependency or automatic writing authority.

## Efficient execution defaults

**Load only one Skill** and relevant evidence; reuse verified runs, searches and data. Batch inspect→edit→focused test→repair→record. During exploration **do not generate any image**, including diagnostic charts and previews, unless the user explicitly requests the specified image; keep numeric/text evidence available without plots. Use concise *delta-only* updates instead of repeated reports. Full CI at integration/release, not after every minor edit. A negative Pilot prompts diagnosis, not automatic project STOP. **Never weaken legal splits, permissions, reproducibility or independent confirmation to save tokens.**

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

## v0.10 · 证据驱动的科研假设发现（按需）

将 HypoRefine / ResearchAgent 的**数据—文献联合构思**与 POPPER 的**最小证伪思想**接入现有七个 Skill，不增加默认 Agent 或强制阶段。新 `adapters.hypothesis_bank` 从已独立复算的 DEV Run 提取**描述性问题种子**，再把外部 Agent 撰写的 1–3 条研究假设绑定到原始 Run、文献元数据或明确标注未复算的数据笔记；`adapters.opportunity_review` 只选择下一项证据行动，不声称创新、成功率或论文贡献。已验证 Run 可回写假设的探索反馈，保留旧版本。

使用范例和 JSON 卡片见 [Discovery playbook](docs/DISCOVERY_PLAYBOOK.md)。无真实 Run 也可先走文献/数据笔记入口，合法信息不足保留 UNKNOWN。不复制上游未授权代码，不自动训练、读取封存确认集或调用付费 LLM。**历史科研盲回放仍未执行，工作流有效性 NOT_MEASURED。**

## PD-RW 按需可信指标交接（v0.11）

当 PD-RW 某个关键 DEV Run 需要独立指标复算时，在 RWF 仓库环境运行：

```bash
python -m adapters.pd_rw_bridge --project FORGE_PROJECT --forge-run runs/R/RUN.json --pd-root PD_PROJECT --pd-run runs/R.json --metric macro_F1
```

只处理已由 RWF 重新计算原始 DEV 标签和逐样本预测的 Run。PD-RW Run 与 Forge Run 必须匹配任务/协议/样本/合法输入，且 **原始预测文件的字节 SHA 相同**；不同格式需先在合法开发池生成一致版本，不能仅拷贝成绩。返回 `METRIC_VERIFIED_DEV_ONLY`，不证明训练源码一致、时间因果、强基线公平性或科学独立确认。旧 Run 不强制迁移。更多限制见 `docs/ARTIFACT_CONTRACT.md`。

**v0.11 科研路由补充**：如果同K强简单基线已覆盖候选方法的收益，先寻找不同的可证伪杠杆或科研问题；对昂贵但可检验的机制优先设计低成本判别实验，而非错误地要求重复已完成的基线。
