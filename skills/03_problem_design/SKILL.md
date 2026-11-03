---
name: research-problem-design
description: Form a feasible, falsifiable scientific task and a defensible potential contribution.
---
# 03 | 科学问题与命题构建

**入口**：已有相关证据，但尚不清楚到底研究什么具体 Task；某一模型失败时先进入 06 判断失败层级，不能自动换题。

**借鉴**：IdeaSpark 的瓶颈→创新假设→反证链，ResearchAgent 的问题生成/验证/方法设计分工，ARIS Idea Discovery 的阶段交接。

**执行**：
1. 明确“已观察到什么、现有方法欠缺什么、要证明哪种知识/能力、什么结果会推翻它”，区分真实现象和未经训练的假说。
2. 在最多 1–3 个科学上不同的候选间对照两条独立维度：**可行性**（真值、合法输入、简单基线、数据、算力）与**科学价值**（最近邻差额、机制、能力或规律）。
3. 只查最重要的 1–2 篇具名最近邻和最危险的外部依赖；未知不自动被否决，正式创新性验证留给选定命题与确认阶段。
4. 选一个主任务、按需保留一个失败前提不同的备用问题。L0 基线、L1 实际可行任务、L2 机制、L3 难信息条件只是可选科研任务层级，并非论文等级或必做顺序。
5. 输出可证伪的最廉价初始检查，避免因为提出想法就提前承诺算法效果或论文发表。

**交接**：TASK.json。早期允许 DRAFT 和 UNKNOWN；真正进入 ACTIVE 后才补全 protocol_id、metric、group_split、legal_inputs、baseline、holdout_policy。格式见 docs/CONTRACTS.md。
