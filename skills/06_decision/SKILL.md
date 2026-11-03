---
name: research-decisions
description: Scope failures and choose repair, improve, pivot or hold based on actual evidence.
---
# 06 | 科研决策、纠错与转向

**入口**：代码错误、负 Pilot、结果反常、共同科学前提失效、论文贡献不足或新投入决策。先读原始 Run，不依赖 STATE 的主观总结。

**借鉴**：AIDE 的候选分支与历史证据保存，ResearchStudio 的版本失效概念，R&D-Agent 的实验反馈，第八章的纠错与第十章的任务转向。

**执行**：
1. 区分 INVALID（泄漏、真值/评价/代码错误）、INCONCLUSIVE（欠训练、统计不足、缺关键对照）及真正有效的正/负结果。代码正常≠任务可学≠科研贡献。
2. 指明受影响层级 RUN / MECHANISM / TASK / AREA_DATA / CLAIM；只撤销失效主张，保留可靠数据、基线和负结果。
3. 普通 Bug 在真实已授权预算内最小复现→修复→定向验证→续做，不逐处重新审批；科学负结果不能当 Bug 无限调参。
4. 可选 CONTINUE、REPAIR、NARROW、真实 UP/DOWN、LATERAL/PIVOT、HOLD。任务改变需新合法协议；不能换架构名、随机种子或数据切片就重置相同失败前提。
5. 对比下一项行动的预期新信息与 GPU/Token/人工总成本。一次负 Pilot 不自动 STOP，但无新判别价值的分支也不能无限续命。实质改题/越权限需用户批准。

**交接**：DECISION，含 evidence_refs、decision_scope、new_observation、next_probe、positive/negative outcomes、cost、authorization_gap、recovery_condition。

**已实现的安全保护**：`core.cli record` 不再因一句“任务完成”而自动升级科研阶段；必须具备结构有效的本地产物，原始内容以 SHA-256 关联。普通 bug 遵循 superpowers 的“复现→根因→定向验证→恢复”思想，但无需强制完整读其所有 Skills；真实结果声称前先有新鲜的测试日志。改变 Task ID 不能静默绑定旧实验。
