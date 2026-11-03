---
name: research-algorithm-execution
description: Implement, debug and compare algorithms with traceable actual execution.
---
# 05 | 算法实现与自主实验

**入口**：已具备真实 Task、合法 evaluator、有效基线或待补基线及已批准的执行范围。此 Skill 不自行授予训练权限。

**借鉴**：ARIS Experiment Bridge 的实验计划→代码→Sanity→Run 交接；AIDE 的 draft/debug/improve 节点和 Journal；R&D-Agent 的研究↔开发反馈；AutoResearch 的评价器隔离思想。

**执行**：
1. 只读相关 Task/Run/代码和必要测试。固定 task_id、protocol_id、dataset_version、evaluator_version；将允许修改的模型代码与受保护评价器、split 分开。
2. DRAFT 编写可运行最小代码；DEBUG 定位最早异常、最小修复和定向回归；IMPROVE 在同一合法评价条件下比较 Champion 和一个有独立机制假说的 Challenger。
3. 先 Sanity，再根据真实现象开展合理规模训练与公平比较；只有当规模、收敛或统计不足可能改变判断时增加 GPU。无需默认多 Agent、全量消融或漂亮的图表。
4. 记录准确命令、代码 commit、原始日志、逐样本/组级预测、训练预算、错误与所有有效或负结果。禁止挑最好 seed 或改变评价器挽救成绩。
5. 将 RUN_RESULT、NO_GAIN、RUN_INVALID、CODE_FAILURE 送到 06。没有真实执行必须明确 NOT_RUN，不能填入模拟指标。

**交接**：可复现代码与 RunRecord（VALID/INVALID/INCONCLUSIVE/NOT_RUN）及下一个具有信息价值的实验假设。

**自动可比性检查（已实现）**：保存含真实 raw log 指针和合法输入/分组/样本集指纹的 VALID Run JSON 后，运行 `python -m core.cli compare --champion A.json --challenger B.json --metric macro_F1`；最小化误差指标加 `--lower-is-better`。不允许通过不同数据切片、评价器、输入条件或封存集改写“增益”。仅报告开发集差值，不把它冒充显著性或论文贡献。
