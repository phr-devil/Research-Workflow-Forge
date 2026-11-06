# Research Workflow Forge｜Agent 入口 v0.15

> **这是导航与权限摘要，不是第二个科研主控。** 在与 PD-RW 共同工作时，以 PD-RW 的科研选择/用户授权为准；RWF 负责可复核 DEV 工件、机制验证及必要的科研实验建议。完整规则在 [Execution Policy](docs/EXECUTION_POLICY.md)，按需读相关段落，不把所有专题和历史同时加载。

## 0. 最短读取顺序（新 Agent / 跨会话）

1. 确定**当前用户请求及原始授权**，确认是 PD-RW 项目还是独立 RWF 项目。用户原始许可优先于本地 STATE 或任何 handoff。
2. **PD-RW 项目**：先读 `RESEARCH_RECORD.md` 首页当前状态/最佳 Run/重要失败/下一步；论文相关任务再读 `PAPER_BLUEPRINT.md` 构思快照与相关 `SEC_ID`。之后核原始 STATE/Run/任务协议，必要时使用 [two-file handoff](docs/PD_RW_DUAL_DOCUMENT_HANDOFF.md)；RWF 不建第三套科研日记。
3. **独立 RWF 项目**：先读 `STATE.json`（或 `python -m core.cli brief --dir PROJECT`）→ 当前有效 Run/Task 与权限 → 当前阻碍需要的单个 Skill。旧版工件照常复用，未证实的来源/运行状态不升级。
4. 只有遇到具体规则/机制问题才读相应 [Execution Policy](docs/EXECUTION_POLICY.md)、[Artifact Contract](docs/ARTIFACT_CONTRACT.md)、[Science Handoff](adapters/science_handoff.py) 或专业文档。真实原始 Run/协议优于摘要；哈希/结构通过不自动证明科学有效。

## 1. 不可越过的边界

- **授权**：[NEXT_ACTION_POLICY](docs/NEXT_ACTION_POLICY.md) 将授权内技术执行与用户必须决策的下载、安装、CPU/GPU、SEALED/CONFIRMATION、重大 Task 改变、HOLD/STOP、投稿、外传和付费分开。保存的许可字段或 Agent 建议不是原始用户授权。
- **科研与 Q2 目标**：追求真实证据支持的 JCR Q2+ 投稿潜力（优先 Q1），不保证录用；DEV 增益、廉价实验和期刊元信息都不是独立科学确认。PD-RW 拥有科研选择和选刊判断，RWF 的廉价下一 Probe 排序不能替代。见 [HIGH_VALUE_RESEARCH_ENGINEERING](docs/HIGH_VALUE_RESEARCH_ENGINEERING.md)。
- **写作**：允许更新 `PAPER_BLUEPRINT.md` 的 H1/H2 及逐节要点；论文正式标题、摘要、章节正文和初稿仍 `WRITING_LOCKED`，须用户审查真实科研成果总结后**另行明确授权**。参见 [Execution Policy](docs/EXECUTION_POLICY.md)；蓝图或 Run 不授权写稿。
- **图片**：**只在用户明确要求绘制/修改具体图片时**才可调用绘图、重绘、预览或导出；科技图表、诊断图与稿件图一律不自动生成。获授权时读 [Figure QA Contract](docs/FIGURE_QA_CONTRACT.md) 与 [Figure Style](docs/FIGURE_STYLE_SYSTEM.md)。
- **工具边界**：RWF 不自带通用自主编码 Agent、GPU 执行器或独立论文确认器。只有可复算的合法 DEV 预测/指标才能据实验证；外部代码、日志和 JSON 声明不自动成为已验证 Run，封存集不得用于开发。

## 2. 当前阻碍 → 只加载相关 Skill

| 目标 | Skill / 按需专题 |
| --- | --- |
| 研究方向/文献/数据 | `01_search`，按需 `02_evidence_data`；未知方向先 `BREADTH_SCAN → DEEP_FALSIFICATION → COMPETING_CHOICE`，比较不同失败前提，不能只选第一个可行题目 |
| 科学 Task 与可辨识假设 | `03_problem_design`，按需 `docs/HIGH_VALUE_RESEARCH_ENGINEERING.md` |
| DEV 协议、简单基线/评估 | `04_feasibility` |
| 算法编码/误差与机制实验 | `05_algorithm` |
| 负结果、修复、收窄或转向 | `06_decision`；按需 [Science Result Harvest](docs/SCIENCE_RESULT_HARVEST.md) 或 [Post-Algorithm Audit](docs/POST_ALGORITHM_SCIENCE_AUDIT.md) |
| 独立科学主张/确认方案 | `07_confirmation`，按真实 SEALED 权限；PD-RW 负责最终主张决策 |

既有有效 Run 直接续做，不重新开选题、下载或重复训练；强简单基线和可区分的科学预言优先于盲目复杂化。七个 Skills 是能力，不是七次强制审批。**Load only the skill needed for the current blocker**；不要预读所有 Skills、vendor 源码或实验历史。

## 3. 增量输出与交接

仅交付**真实新增证据 + 原始路径/协议/状态 + 决策或 UNKNOWN + 一项下一行动及权限依赖**。有意义的实验和失败补进 PD-RW 的 RESEARCH_RECORD.md；科学主张确有变化才更新 PAPER_BLUEPRINT.md 相应 SEC_ID。保留原本 RWF Run/STATE/ledger/bridge 及源数据，不重复堆砌日志、不新增 CLI 状态或自动生成稿件图片。其余技术约束见 [Architecture](docs/ARCHITECTURE.md) · [Contracts](docs/CONTRACTS.md) · [Sources](SOURCES.md)。
