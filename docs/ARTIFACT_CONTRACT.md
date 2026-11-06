# Trusted DEV metric and external-agent handoff · v0.8

Reportable DEV metrics are independently recomputed from SHA-bound DEV ground truth. Artifact hashes alone do not verify metrics.

## Standard classification receipt

An ACTIVE Task specifies protocol_id, metric, legal_inputs, group_split and dataset ID. DATA_MANIFEST binds DEV dataset_id, local_path, SHA-256, label_column, group_column and optionally sample_id_column.

VALID Run.json must reference hashed raw artifacts and metric_spec:
- format = forge-dev-classification-v1
- predictions_ref: project-relative hashed predictions.json
- manifest_ref: project-relative DATA_MANIFEST.json
- manifest_sha256: exact manifest hash
- dataset_id: DEV dataset declared in manifest and Task

predictions.json is a list of {row_index:int, group:string, truth:string, prediction:string, sample_id?:string}. row_index identifies the original DEV CSV row. The verifier independently checks truth/group/sample IDs from original DEV CSV. A frozen GroupShuffleSplit(seed=42, test_size=.25) regenerates held-out row IDs; cherry-picked indices are rejected. sample_ids_hash uses canonical sorted true sample IDs (or original row indices when there is no ID column).

Only macro_F1 and balanced_accuracy are supported. Recalculation tolerance is 1e-6; task-specific scientific conclusions remain separate.

## External Agent handoff

1. Codex/WorkBuddy/AIDE runs in a separately secured DEV-only workspace with actual user permission. Forge NEVER executes arbitrary Agent-produced Python.
2. Save actual source and standard predictions JSON under the project.
3. Import: `python -m adapters.agent_bridge --project PROJECT --manifest PROJECT/DATA_MANIFEST.json --dataset-id D --run-id R2 --source-code PROJECT/model.py --predictions PROJECT/predictions.json --measured-wall-seconds 15.2`.
4. Register RUN.json using `python -m core.cli record --dir PROJECT --event RUN_RESULT --artifact PROJECT/runs/R2/RUN.json --note "Verified prediction arithmetic"`.
5. Use `core.cli champion` preview and explicit `--apply` for provisional DEV selection. Compare requires `core.cli compare --dir PROJECT ...`.

This does not prove external code was executed or trained only on DEV, nor that saved source corresponds to predictions. A true OS/container sandbox and execution attestation remain future work. Sealed Runs through development events are rejected. Independent confirmation is unavailable.

## Backward compatibility

V0.6 hashed-log-only Runs remain historical but are not trusted for newly verified metrics/Champion. NEVER invent missing predictions. Legacy projects must preview/apply `core.cli migrate-ledger --dir PROJECT` before new events. Anchoring cannot prove pre-migration history authenticity.

## v0.8｜可信回归与单次事件评价（新增，不替代原分类协议）

注册两种新的只读指标格式：\`forge-dev-regression-v1\`（\`MAE/RMSE\`，\`aggregation=group_mean|pooled\`）与 \`forge-dev-event-v1\`（\`event_recall/false_alarm_rate\`）。新版评价器使用单独 SHA-256 固定的 \`split_ref\` JSON：\`{"train_groups":["A"],"dev_groups":["B"]}\`；两组独立且必须完整覆盖 DEV 数据的所有 groups。Run 的 \`group_split\` 必须等于 \`pinned-groups:<split_sha256>\`。原有分类格式和固定42号分组切分不变、继续兼容。

新\`metric_spec\`包含 \`format,predictions_ref,manifest_ref,manifest_sha256,dataset_id,split_ref,split_sha256\`；DEV 数据必须有非空\`group_column,label_column,sample_id_column\`。回归预测JSON逐行：\`{"row_index":整数,"prediction":有限数}\`。事件数据每行是一个独立 episode，label_column 是真值事件秒数，\`NONE\`/空代表无事件；预测JSON逐行恰一条 \`{"row_index":整数,"trigger_time_s":非负有限数或null}\`。事件\`metric_spec\`另需 \`tolerance_s\` (0,30] 和 \`prediction_mode="SINGLE_EMISSION_PER_EPISODE"\`。不得只选择真值附近的一小段结果或提交多候选事件；查询样本必须完全覆盖已冻结DEV划分。

**边界**：程序可独立核标签、样本覆盖、分组划分、存储原始预测的指标算术；**不能证明**外部Agent真的因果在线推断、从未见过未来数据、只用DEV训练或源码与预测一致。该类主张需额外受保护执行记录和独立科学确认。回归组级MAE/RMSE可使用探索性配对bootstrap；pooled与group_mean不得相互比较，也不将bootstrap当确认检验。Run完整性和外部Agent预测可采用项目既有记录方式后走\`core.cli compare --dir\`或\`core.cli champion\`；v0.7专用\`agent_bridge\`仍仅导入分类，新增类型暂可由外部Agent按本合同写完整签名Run，不能虚称已自动完成任意类型导入。


**v0.8 typed external Agent import**: after creating an ACTIVE Task whose \`group_split\` equals the pinned split SHA, run
\`python -m adapters.typed_agent_bridge --project PROJECT --manifest PROJECT/manifest.json --split PROJECT/split.json --dataset-id D --run-id R --predictions PROJECT/preds.json --source-code PROJECT/model.py --kind regression\`
(or \`--kind event --tolerance-s 0.5\`). The bridge never executes the supplied code; it copies predictions, binds the active Task/DEV labels/split, recomputes metrics, and writes a non-overwriting signed Run. Model execution provenance remains unverified; external agent source and predictions could be inconsistent. The earlier classification \`adapters.agent_bridge\` remains supported.

**Existing-result harvest as optional source evidence:** a PD-RW DEV-only `result_harvest` scientific-inventory JSON may be included as a *source_receipt* in `adapters.science_handoff`, subject to existing SHA/size and DEV/public role checks. Its condition effects, costs and candidate flags are exploratory, and a hash pass does not independently recompute metrics, validate independent groups, identify mechanisms or certify a publication claim. Evidence-level `CONTRIBUTION_EVIDENCE_BRIEF` is never a manuscript artifact. See [SCIENCE_RESULT_HARVEST.md](SCIENCE_RESULT_HARVEST.md).

**PD-RW dual-file evidence handoff:** verified DEV/public Run receipts can be referenced in RESEARCH_RECORD.md and the related PAPER_BLUEPRINT.md H1/H2 plans, via [dual-file handoff](PD_RW_DUAL_DOCUMENT_HANDOFF.md). This does not verify scientific truth, authorize sealed reads or training, unlock manuscript prose or trigger rendering; do not create a competing RWF narrative ledger.


**Pre-download discovery is NOT a metric/Run handoff:** PD-RW's short `SEARCH_HANDOFF` may carry `BREADTH_COVERAGE / STRONGEST_NEIGHBOR+COUNTEREVIDENCE / DIFFERENT_PREMISE_COMPARISON / PRE_DOWNLOAD_SCIENCE_FIT / NEXT_DISCRIMINATING_CHECK` as **public-source claims or UNKNOWN**. `adapters.science_handoff` still expects actual permitted DEV/public source receipts after they exist; do not invent DEV SHA files for an early ChatGPT research search or use a passed hash to grant data access or certify Q2. With no chosen problem, RWF's feasibility rankings cannot choose it. Original user authorization remains decisive.

## PD-RW scientific-choice handoff (separate from metrics)

The optional `adapters.science_handoff` requires an already PD-RW/user-selected Task, important knowledge gap, closest original paper, strongest alternative, distinct prediction, data-confounding limitations, independent-group unit, legal inputs and one or more hash-pinned project-local DEV/public metadata source files. Hash verification is **not** scientific review, originality, Q2 competitiveness, user authorization or independent confirmation. A suggested cheap evidence action cannot override the externally chosen scientific problem. [Example schema](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/SCIENTIFIC_HANDOFF.example.json).

## PD-RW read-only verified DEV handoff

`python -m adapters.pd_rw_bridge --project FORGE_PROJECT --forge-run FORGE_RUN --pd-root PD_PROJECT --pd-run PD_RUN --metric METRIC` independently reloads and recomputes the Forge Run, then checks matched task/protocol/dataset/evaluator/split/group/sample identities, legal inputs, calibration/level fields when present, numerical metrics, and **byte-identical original prediction JSON** referenced by both Runs. Missing calibration fields in both old Runs are reported as `PARTIAL_LEGACY`; unequal or one-sided fields fail. Output is read-only, `METRIC_VERIFIED_DEV_ONLY`, and is not a certificate of source-code execution or scientific confirmation. This is a controlled bridge, not a unified schema or full repository merge.

## Optional figure artifact provenance and QA

Any new figure, preview, redraw or contact sheet **requires the actual user's explicit request to draw the specific images**. Only then may a project use the optional [Figure QA Contract](FIGURE_QA_CONTRACT.md), [example contract](../templates/FIGURE_CONTRACT.example.json) and read-only `tools.figure_qa`. Source hashes and SVG/PNG file validation bind bytes/structure, not user authority, independent source correctness, plotted-value semantics, confirmation or Q2 potential. Figure status never promotes scientific Run/Claim status. No implicit SEALED access, re-training, manuscript drafting or uploads.
