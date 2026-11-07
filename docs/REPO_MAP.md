# RWF 仓库职责与按需入口（INDEX_ONLY）

**定位**：RWF 提供工具和可复核证据，不是 PD-RW 的另一个科研主控。仓库不搬动既有文件，不重建项目 STATE/Run，也不增加绘图、写稿、下载或训练授权。Agent 已知当前文件时直接读取，不把本地图作为强制读取步骤。

| 当前需要什么 | 原始权威文档/代码 | 备注 |
|---|---|---|
| RWF 研究执行及权限 | [EXECUTION_POLICY](EXECUTION_POLICY.md)、[NEXT_ACTION_POLICY](NEXT_ACTION_POLICY.md) | 与 PD-RW 联用时仍服从 PD-RW 总控及用户真实授权 |
| Task/Run/工件合同 | [ARTIFACT_CONTRACT](ARTIFACT_CONTRACT.md)、[CONTRACTS](CONTRACTS.md)、[core/](../core/README.md) | 仅在处理相应协议时加载 |
| 七个研究 Skill | [skills/](../skills/01_search/SKILL.md)、[AGENTS](../AGENTS.md) | 一次按阻碍选一个，不通读全部 |
| PD-RW 科研记录交接 | [PD_RW_DUAL_DOCUMENT_HANDOFF](PD_RW_DUAL_DOCUMENT_HANDOFF.md) | 不创建第三份科研日志 |
| 科研数据图 | [FIGURE_STYLE_SYSTEM](FIGURE_STYLE_SYSTEM.md)、[FIGURE_QA_CONTRACT](FIGURE_QA_CONTRACT.md) | 图像用户单独明确授权后才可生成 |
| 已授权论文数据图执行 | [figure_templates](../tools/figure_templates.py)、[figure_qa](../tools/figure_qa.py)、[figure_theme_pdrw](../styles/figure_theme_pdrw.json) | 按需读对应 API；主题不迁移旧项目 |
| 对外工具或跨项目桥接 | [adapters/](../adapters/pd_rw_bridge.py) | 不等于授予新的科学或数据权限 |
| 纯离线回归验证 | [tests/](../tests/test_figure_style.py) | 只能证明对应静态/行为合同，不证明科研与视觉结果 |

**权威边界**：科研选择和论文/图像许可由 PD-RW 与实际用户请求决定；RWF 的 `tools/` 实现和 `docs/` 接口是执行/验证能力。不要将一个规则同时复制成两份可独立修改的权威文件。CI 保持不自动绘制图片、不运行未经授权的科研实验。
