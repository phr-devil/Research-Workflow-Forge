# Trusted DEV metric and external-agent handoff · v0.7

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
