---
name: research-feasibility
description: Verify evaluation legality, credible baselines and a bounded informative pilot.
---
# 04 | 可行性验证与实验协议

**入口**：已有科学 Task，需要确定是否能在真实数据和合法评价下开展算法实验。

**借鉴**：AutoResearchClaw 的实验设计与交接，AutoResearch 的可修改模型与固定评价器**设计思想**；AutoResearch 仓库未声明许可，禁止直接复制其代码或原文。

**执行**：
1. 核实际真值/证明义务、任务指标、分组/时间因果、推理时合法信息和 train-only 预处理；确认开发和独立确认数据的边界。
2. 优先复用可靠简单基线。需要性能比较时对强基线公平调参；已有效的旧 Run 不重算。资源或授权不足时只设计，不拟合 CPU/GPU 参数。
3. 观察合法开发池中的残差、组间异质性、容量/欠训练及可能的性能空间。Oracle/合成正控仅支持诊断，不能冒充部署收益。
4. 区分 ENABLEMENT（恢复数据与训练能力）、BASELINE/IMPROVE（公平表现）和 MECHANISM_TEST（真正需要不同预测的解释）。首次 Pilot 没增益不自动停整个 Task。
5. 制定最小实验合同：固定 evaluator、dev split、待改模块、hypothesis、预算、正/负结果后各如何决策。封存确认集不得进入开放式实验。

**交接**：EXPERIMENT.json + 可信基线证据或 NOT_RUN，明确未验证的科学前提与所需授权。
