# Research Workflow Forge｜Agent 入口 v0.15

> **轻量导航与最小权限摘要**。与 PD-RW 联用时，PD-RW/用户负责科研选题、主张和授权；RWF 只提供合法 DEV 执行、独立复算与技术建议。按任务只读一份 Skill，不把本入口变成第二套科研工作流。

## 0. 最短读取顺序与来源

1. 先识别原始用户授权和科研归属。PD-RW 项目从真实项目路径/STATE 的 `RESEARCH_RECORD_REF`、`PAPER_BLUEPRINT_REF` 定位已有 `RESEARCH_RECORD.md` 当前快照、必要 `PAPER_BLUEPRINT.md` 的 `SEC_ID`；再查相关真实 Run/协议。仅需要对接时读 [PD_RW_DUAL_DOCUMENT_HANDOFF.md](docs/PD_RW_DUAL_DOCUMENT_HANDOFF.md)。
2. 独立 RWF 项目从 `STATE.json`、有效 Run、Task 和当前阻碍恢复；不存在的记录不编造，旧项目不强制迁移。
3. 冷启动/规则变化时核实际 Git commit 和已读文件：`RULE_REPO | RULE_COMMIT | LOADED_FILES`；本地非 Git 复制件或无法确认远端时记 `RULE_VERSION_UNVERIFIED`，不自称最新。已确认版本与任务不变就复用，不重复通读。
4. 仅当阻碍涉及共享执行/授权合同才读 [Execution Policy](docs/EXECUTION_POLICY.md) **相关节**或 [NEXT_ACTION_POLICY](docs/NEXT_ACTION_POLICY.md)；仅检查工件协议才读 [Artifact Contract](docs/ARTIFACT_CONTRACT.md)。仓库索引 [REPO_MAP.md](docs/REPO_MAP.md) 只在不知文件位置时查。

## 1. 不可越过的边界

- **权威与授权**：重大 Task 改变、下载、安装、CPU/GPU、SEALED/CONFIRMATION、项目 STOP/PIVOT、付费、外传及投稿须由用户实际授权；RWF 的工具结果不能授权科研决策。见 [NEXT_ACTION_POLICY](docs/NEXT_ACTION_POLICY.md)。
- **科研**：JCR **Q2+** 潜力（优先 Q1）不是 DEV 分数或期刊元数据直接证明；简单 Champion 是公平比较对象，不是复杂机制前置阶梯。`novelty_check` 只做来源预检，`opportunity_review` 只建议证据行动；见 [HIGH_VALUE_RESEARCH_ENGINEERING](docs/HIGH_VALUE_RESEARCH_ENGINEERING.md)。CI 不能证明真实科研能力。
- **写作**：`PAPER_BLUEPRINT.md` 可以规划 H1/H2；投稿标题、摘要和正文默认 `WRITING_LOCKED`，须成果总结经用户审查并另行明确授权。RWF 不生成第三套科研记忆。
- **图片**：只有**用户明确要求绘制/修改具体图片**才执行绘图、重绘或预览；图像授权与写作/实验权限相互独立。获授权才读 [Figure QA Contract](docs/FIGURE_QA_CONTRACT.md) / [Figure Style](docs/FIGURE_STYLE_SYSTEM.md)。

## 2. 当前阻碍 → 一项 Skill

| 目标 | 仅加载当前 Skill；补充专业规则按需 |
|---|---|
| 方向/文献/数据库 | `01_search`；数据证据才补 `02_evidence_data` |
| 科学 Task/可辨识假说 | `03_problem_design` |
| 合法 DEV 协议/强简单基线 | `04_feasibility` |
| 算法/机制编码 | `05_algorithm` |
| 负 Run、修复、止损 | `06_decision`；需要科学价值回收读 [SCIENCE_RESULT_HARVEST.md](docs/SCIENCE_RESULT_HARVEST.md) 或 [POST_ALGORITHM_SCIENCE_AUDIT.md](docs/POST_ALGORITHM_SCIENCE_AUDIT.md) |
| 独立确认建议 | `07_confirmation`，SEALED 仍单独授权 |

研究方向的不同前提比较沿用 `BREADTH_SCAN → DEEP_FALSIFICATION → COMPETING_CHOICE`，不自动选第一个可行课题。**Load only the skill** needed for the current blocker. 七个 Skills 是能力目录，不是强制七阶段；不要预读全部 Skills、长篇执行政策或 vendor 源码。

## 3. 最短交接

只输出新增证据和路径、协议/关键不确定性、技术建议与 AUTH；必要时同步原 `RESEARCH_RECORD.md` 或 `PAPER_BLUEPRINT.md` 相应字段。重大创新主张和科研路线由 PD-RW/用户判断，真实测评另按受测版本和外部证据进行。后续规则优先合并现有权威文件，不在入口继续堆叠。
