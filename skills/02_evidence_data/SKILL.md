---
name: research-evidence-data
description: Audit literature claims, dataset compatibility and independent-evaluation eligibility.
---
# 02 | 文献证据与数据库建设

**入口**：需要核实关键论文、官方数据来源、标签/分组、下载和确认集的合法使用。纯理论任务改用证明或仿真验证路线，不强制下载数据库。

**借鉴**：PaperQA2 的全文证据检索与出处关联，ResearchStudio Paper Search / Scoop Check 的原论文与创新碰撞核查。

**执行**：
1. 对关键最近邻核任务、部署时合法输入、评价、数据版本、限制及创新差额。每条论断引用明确的来源 DOI/URL/版本，不用模型知识代替已核全文。
2. 数据组合按用途选择：DEV 开发、EXTERNAL_REPLICATION 外部复现、STRESS 困难条件、PIVOT_RESERVE 转题备用、SEALED_CONFIRM 独立确认。不机械要求固定数据集数；不同库必须能支持实际目标。
3. 核官方许可、必要文件与容量、独立标签、受试者/设备/时间分组、跨库可比性及完整性。保留下载来源、版本与哈希/CRC（如提供）。
4. 被用来挑任务、数据切片、机制或超参的样本不能继续假装是未接触的确认集；为后续新任务重新判断确认资格。
5. 下载、安装、外传、CPU/GPU 拟合等行为必须得到真实用户授权；权限不足输出下载清单和 WAITING_FOR_AUTH，不执行。

**交接**：EVIDENCE 及 DATA_MANIFEST，记角色、来源、许可、标签/group、可用性、确认资格与阻碍；不把文件完整性当科学任务有效性。

**元数据边界**：`EVIDENCE.json` 中的 `METADATA_ONLY` 仅证明某提供者返回了检索条目；不等于已阅读论文全文或核实创新。输入 `DATA_MANIFEST.json` 时明确官方 URL、group_unit、label_status 与 DEV/SEALED_CONFIRM 等角色；检索时使用过的切片不得在确认时重新宣称从未接触。

**v0.5 mandatory DEV interface**: when a local file will be read or fitted, manifest must include dataset_id, role, local_path, SHA-256 and independent group unit. Bind reads with core.data_access; a registered SEALED_CONFIRM alias is refused. Record access attempts. Do not claim that path+hash alone proves true labels or scientific compatibility.
