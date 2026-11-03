---
name: research-opportunity-search
description: Discover evidence-backed scientific opportunities within the user-defined scope.
---
# 01 | 信息搜索与科研机会发现

**入口**：用户提出新研究方向、需要寻找科学问题；已有真实 Task/Run 时不要重新从头搜索。研究范围由用户本轮指令决定，不默认某个领域。

**借鉴**：Microsoft ResearchStudio 的 Paper Search / IdeaSpark（多源搜索→瓶颈），Stanford STORM（不同学科与应用视角），GPT Researcher 的研究子问题规划。这里只复用方法，不假称已集成外部工具。

**执行**：
1. 将范围分解为应用需求、真实失败现象、可检验理论/物理问题、现有算法、可用数据和评价方式。针对领域/问题/方法机制构造少量互补查询。
2. 优先读取论文原文、官方数据库、基线代码和相关综述；按 DOI/版本去重，区分 OBSERVED / HYPOTHESIZED / UNVERIFIED。标题相似不能直接判断论文已覆盖某机制。
3. 保留 1–3 个**不同失败前提**的研究机会，记关键最近邻、已有证据、最低验证路径、最大未知、为何优先；没有足够证据时诚实标 UNKNOWN。
4. 当资料缺口阻碍判断时交给 02；已有足够资源可交给 03。探索阶段不要求完整论文级查新，不按固定次数无限检索。

**交接**：精简机会清单，每项包含 question、primary_sources、nearest_work、available_assets、critical_unknown、next_probe。只输出实际发现，不生成没有科研价值的图表。来源和许可见 SOURCES.md。

**已实现的最小检索入口**：`python -m adapters.literature --query "specific research problem" --limit 6 --out projects/ID/EVIDENCE.json`。OpenAlex/Crossref 仅返回公开元数据、DOI、标题与来源；处理 429/部分失败、去重与来源版本。**不可直接据标题声称新颖性**，对于真正进入命题的主候选仍需查原文及官方代码。没有联网时标 FAILED，不编造记录。后续用 `core.cli validate --kind evidence` 检查格式。

**v0.3 实际检索入口（优先）：** `python -m adapters.researchstudio_search --query "问题表述" --query "关键机制或失效" --sources open_alex crossref arxiv --limit 6 --out projects/ID/EVIDENCE.json`。封装上游 ResearchStudio 的来源 Worker 与去重逻辑；多源失败逐项记录，若没有有效论文不可称搜索通过。旧 `adapters.literature` 仅作为兼容备选。阅读上游 `vendor/researchstudio/paper_search/SKILL.md` 只在调试检索或需要额外 API 时，不默认加载。仍需核查原论文而非仅使用标题/摘要。
