---
name: research-algorithm-execution
description: Build, debug and compare algorithms with reproducible Runs and bounded iterations.
---
# 05 | Algorithm implementation and feedback

Shared rules: [EXECUTION_POLICY](../../docs/EXECUTION_POLICY.md). Execution requires real Task, protected evaluator, eligible DEV data and actual authorization.

- Work in one coherent **DRAFT → DEBUG / IMPROVE → directed test → record** batch. Diagnose the earliest engineering failure, repair locally and test affected interfaces; do not run unrelated full tests after every edit.
- Preserve task/protocol/data/code/evaluator IDs, raw stdout/predictions, SHA receipts, candidate parent and negative Runs. No cherry-picked seed or evaluator changes disguised as improvement.
- Current **bounded** engine: `python -m tools.experiment_runner` for opt-in grouped DEV dummy/logistic/forest; no arbitrary Agent-produced code or GPU. Then `core.cli record`, `core.cli compare` and explicit `core.cli champion`. `core.cli candidates` shows lineage, not a complete AIDE executor.
- More runs are justified only by a different mechanism, unfair baseline, inadequate convergence, uncertainty or another decision-changing reason. A valid negative routes to 06 rather than endless hyperparameter churn.

**Handoff:** real RunRecord / NOT_RUN, compatible Champion comparison, mechanism-level observation and next discriminating action.

**v0.7:** Reject self-reported metric improvements: standard predictions must be independently re-evaluated against a SHA-pinned DEV source/frozen group split. External Codex/WorkBuddy scripts may produce predictions in separately controlled workspaces, then `adapters.agent_bridge` imports them without execution. `core.cli compare` now requires `--dir`; Champion preview includes provisional group-bootstrap uncertainty. Details only if needed: `docs/ARTIFACT_CONTRACT.md`.


**v0.8真实实证**：支持在SHA固定DEV组清单上核回归/事件预测的原始标签、样本覆盖及指标。不同K、合法预测时点、聚合口径或事件容差不属于公平Challenger比较；负Pilot优先复核评价/训练/可辨识性，再决定独立新机制。内置训练器仍只含有限分类CPU基线；不能虚称支持任意GPU Agent自主训练。

**Before expensive new mechanism (only when evidence exists):** identify an observed baseline failure, legitimate information/inductive-bias/optimization lever, and a distinct prediction testable with the smallest authorized run. If the model merely has more parameters, do not invent a new science hypothesis. Reuse verified group residual summary; if performance rises, still test fair strong simple alternatives and independent group/Task conditions.

**v0.10 hypothesis→Run:** On an evidence-supported candidate, link `hypothesis_id` to the existing Task/Experiment IDs and parent Run; keep exact protected evaluator and legal inputs. Do not substitute model-size variation for a distinguishing prediction. The separate Agent runs only authorized work; once a DEV Run has independently verified receipts, register exploration feedback in a NEW hypothesis-bank version, not as confirmed mechanism evidence.
