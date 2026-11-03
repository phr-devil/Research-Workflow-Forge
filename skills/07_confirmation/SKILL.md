---
name: research-confirmation
description: Independently test frozen scientific claims without contaminating held-out evidence.
---
# 07 | 独立科学确认与论文证据

**入口**：已有真实开发 Run 支持候选科学 Claim，且存在未被研究搜索污染的独立确认路径。可提前规划，但未经额外真实授权不得运行封存确认实验。

**借鉴**：ResearchStudio Scoop Check 的具名最近邻差额，ARIS 的 experiment-audit/citation-audit，AutoResearchClaw 的 paper verifier，与 AutoResearch 评价器隔离思想。

**执行**：
1. 冻结 claim_id、task/protocol/metric、legal_inputs、checkpoint、数据和评价器版本、独立统计单位、选择过的任务/切片/指标历史。
2. 根据具名最近邻确定真实独立贡献：新能力、新机制、新规律或真实部署限制。只跑通基线、代理得分提高或模型自评认可，不等于论文贡献。
3. 核持出资源从未参与任务/模型选择且适用于**当前**标签与分组；不能通过重新 seed 或改名重置污染。
4. 只有明确确认授权后才执行冻结评估；公平强基线、适当消融与组级不确定性按 Claim 类型选择。保留失败结果，不挑幸运组/seed。
5. 每项论文陈述追溯到真实原始 Run、来源及代码协议；无独立证据写 CONFIRMATION_UNAVAILABLE 或 INSUFFICIENT，不编造投稿准备度。

**交接**：CLAIM.json 和 Claim→Evidence 记录；结构校验只证明字段完整，不证明科学结论为真。
