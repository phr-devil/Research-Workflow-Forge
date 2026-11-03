---
name: research-evidence-data
description: Verify decisive literature and actual dataset roles, labels and provenance.
---
# 02 | Evidence and data

Shared rules: [EXECUTION_POLICY](../../docs/EXECUTION_POLICY.md). Invoke when critical source, usable ground truth or independent validation eligibility is uncertain; theoretical work may use proof/simulation instead of a dataset.

- Check **original** references, named nearest methods, deployment-time legal inputs, labels and independent groups. Metadata and model summaries do not establish an actual mechanism or novelty.
- Assign data roles for a purpose: DEV, EXTERNAL_REPLICATION, STRESS, PIVOT_RESERVE, SEALED_CONFIRM. Use only as many datasets as needed; preserve exact source, version, license, label, grouping and hashes.
- Before opening a local DEV file, use manifest-bound `core.data_access`. Read-only preflight: `python -m tools.data_audit --project PROJECT --manifest MANIFEST.json --dataset-id D --group-col GROUP --label-col LABEL`. The tool cannot prove scientific label validity or untouched confirmation.
- Preserve search/data-access history across pivots; task/model selection exposure may make a purported holdout ineligible.

**Handoff:** concise evidence + data manifest, decisive unknown, resource role and legal next action. Download/fitting remain permission-controlled by the shared policy.
