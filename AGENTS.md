# Research Workflow Forge · AI entry (v0.15)

**Default goal:** finish the smallest evidence-backed manuscript suitable for a real specialist journal; new model complexity is optional. At a credible Run/negative Pilot or before costly model escalation/HOLD/PIVOT, use `06_decision` to ask whether an existing narrow Claim only needs a decisive fair comparison or independent evidence. If yes, prioritize paper-critical experiments and hand off `ONE_CLAIM | CORE_RUN | GAP_1-3 | NEXT_REQUIRED_TEST | VENUE_ANALOGS_IF_KNOWN` to PD-RW, without asserting acceptance or scientific confirmation. When task design requires it, inspect 1–3 recent published analogous studies cheaply; formal journal matching belongs to PD-RW.

**Read once:** [Execution Policy](docs/EXECUTION_POLICY.md), current project `STATE.json` (or `python -m core.cli brief --dir PROJECT`), and **only the Skill needed for the current blocker**. Do not preload all Skills, previous version notes, vendor code, papers or historical logs. Existing verified evidence takes precedence over repeating work.

| Need | Skill |
| --- | --- |
| Discover direction, papers, datasets | `01_search` → optional `02_evidence_data` |
| Design/replace a falsifiable Task | `03_problem_design` |
| Validate evaluator, baseline and DEV | `04_feasibility` |
| Implement/debug/compare a model | `05_algorithm` |
| Diagnose, repair, narrow or pivot | `06_decision` |
| Independent scientific Claim | `07_confirmation` |

**Default sequence:** inspect current valid Run and Task → reuse or establish a legal, reasonably tuned simple reference → identify a reproducible error/signal and its cheapest falsifying test → escalate architecture only if a distinct lever/prediction or actual deployment constraint requires it. A simple success is not novelty; a complex failure is not Task failure. No second state ledger or compulsory skill chain.

**Incremental-claim route:** when a credible result exists, assess a single concrete paper contribution under the actual task constraints rather than demanding a new architecture or global SOTA. Quantify any cost/accuracy tradeoff, inspect the nearest named paper(s), and pass a narrow Claim plus missing evidence to `07_confirmation` when appropriate. A draftable candidate is not independently confirmed; these are narrative rules, not new CLI statuses.

**Small-result publication routing:** before HOLD/PIVOT after a valid model-level negative, consider whether a real effect, efficiency tradeoff, less costly calibration, robust failure boundary or meaningful known-method combination supports one narrow new Claim. If so, preserve evidence and hand a one-line paper candidate + missing confirmation to PD-RW; paper tiers are advisory, *not* Forge machine statuses or a reason to train larger models. For journal matching, PD-RW's optional [venue strategy](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/VENUE_STRATEGY.md) is authoritative.

**Shared efficiency, output, plotting, tests, autonomy, permissions and scientific boundaries:** [docs/EXECUTION_POLICY.md](docs/EXECUTION_POLICY.md). Do not repeat these rules inside Skills. The seven Skills are **capabilities, not seven compulsory approvals**.

**Tool truth:** metadata search works; novelty precheck is UNVERIFIED; experiment planning is PLAN_ONLY; DEV audit and bounded opt-in CPU grouped pilots run on manifest-bound data; Run/Champion and recovery utilities verify receipts. There is **no general autonomous coding Agent, GPU executor or independent paper confirmation** yet. A JSON authorization reference or CLI flag is not actual user permission.

**Result:** concise new evidence, evidence path, next decision and any real blocker. Save raw logs in the project, not in chat. [Architecture](docs/ARCHITECTURE.md) · [Contracts](docs/CONTRACTS.md) · [Source provenance](SOURCES.md).

**v0.7 performance trust rule:** only `core.metric_verify` / `load_verified_run` can certify DEV metrics; a hashed log or self-reported RUN.metrics cannot become Champion. Event ledger requires verified chained history; legacy logs use explicit `migrate-ledger` (preview first). Sealed Runs are prohibited in development events. External Agent code is **not executed by Forge**; ingest only original DEV predictions through `adapters.agent_bridge`. See `docs/ARTIFACT_CONTRACT.md` when needed; do not read by default.

**按需低成本机制诊断（v0.9）**：当已有可信 DEV Run、拟开发复杂机制时，可调用 `tools.feasibility_probe` 读取既有预测，检查独立组误差和同协议配对差值；残差≠可达增益，无匹配参照≠无信号。此工具不是模型训练、科研确认或必须执行的前置审批。按需读 `tools/README.md`，不要重复预加载全部文档。

**v0.10 discovery (only when Task is unknown or research hypothesis changes):** inspect existing DEV observation via `adapters.hypothesis_bank seed` (no fit), then let the current Agent draft at most 1–3 distinct, falsifiable hypotheses anchored to those seeds and/or existing paper metadata. `hypothesis_bank build` checks receipt/source IDs; `adapters.opportunity_review` proposes one cheap evidence action. After an actual verified DEV Run, `hypothesis_bank feedback` creates a new version. Start with [discovery playbook](docs/DISCOVERY_PLAYBOOK.md) only when needed; no extra mandatory Skill, second controller or multi-agent debate.

**v0.11 optional PD-RW handoff:** for a key external DEV Run, use `adapters.pd_rw_bridge` only when the original PD-RW and Forge prediction bytes and task/legal metadata can be matched; it calls the existing independent Forge verifier and returns a DEV arithmetic receipt. Never reformat merely to copy model scores, claim attested training provenance, or load PD-RW's `core` in-process. See [artifact contract](docs/ARTIFACT_CONTRACT.md) on demand.
