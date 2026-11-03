# Research Workflow Forge · AI entry (v0.6)

**Read once:** [Execution Policy](docs/EXECUTION_POLICY.md), current project `STATE.json` (or `python -m core.cli brief --dir PROJECT`), and **only the Skill needed for the current blocker**. Do not preload all Skills, previous version notes, vendor code, papers or historical logs. Existing verified evidence takes precedence over repeating work.

| Need | Skill |
| --- | --- |
| Discover direction, papers, datasets | `01_search` → optional `02_evidence_data` |
| Design/replace a falsifiable Task | `03_problem_design` |
| Validate evaluator, baseline and DEV | `04_feasibility` |
| Implement/debug/compare a model | `05_algorithm` |
| Diagnose, repair, narrow or pivot | `06_decision` |
| Independent scientific Claim | `07_confirmation` |

**Shared efficiency, output, plotting, tests, autonomy, permissions and scientific boundaries:** [docs/EXECUTION_POLICY.md](docs/EXECUTION_POLICY.md). Do not repeat these rules inside Skills. The seven Skills are **capabilities, not seven compulsory approvals**.

**Tool truth:** metadata search works; novelty precheck is UNVERIFIED; experiment planning is PLAN_ONLY; DEV audit and bounded opt-in CPU grouped pilots run on manifest-bound data; Run/Champion and recovery utilities verify receipts. There is **no general autonomous coding Agent, GPU executor or independent paper confirmation** yet. A JSON authorization reference or CLI flag is not actual user permission.

**Result:** concise new evidence, evidence path, next decision and any real blocker. Save raw logs in the project, not in chat. [Architecture](docs/ARCHITECTURE.md) · [Contracts](docs/CONTRACTS.md) · [Source provenance](SOURCES.md).
