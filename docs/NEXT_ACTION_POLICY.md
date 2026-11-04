# Next-action output contract · user vs Agent

**Applies to every Forge entry/Skill/decision handoff**, including optional PD-RW collaboration. This is an **answer format and authority policy**, not a new router event, autonomous executor, permission token or writing unlock. Respect [EXECUTION_POLICY](EXECUTION_POLICY.md), the real user's authorization and manuscript lock.

## Choose owner BEFORE formatting the next response

- `AGENT_DECIDABLE`: legitimate existing authorization covers the technical step and scope/cost/Task/holdout boundaries do not change; Agent may choose the best read-only investigation, ordinary code fix, valid rerun of authorized DEV work, fair comparator or evidence check.
- `STRONG_RECOMMENDATION`: evidence makes one in-scope technical action clearly preferable; proceed with a **direct next-agent instruction**, not an unnecessary user question. Strength of recommendation **never** creates authorization.
- `USER_DECISION_REQUIRED`: any additional or ambiguous permission (download/install/fit/GPU/confirm-sealed), funding/spending/external upload, a substantial Task/research-goal change, project-level HOLD/STOP, author choice of venue/submission, user review of research-results summary or new manuscript-writing authorization. If scientifically plausible alternatives require human values or scope tradeoffs, ask the user. A user-authorized project scope may already encompass normal local Task-specific repairs; do not re-request it.

## Two exclusive response contracts

**A: Agent-decided/in-scope** — `DECISION+EVIDENCE` followed by **one concise, copy-ready NEXT_AGENT_INSTRUCTION** for Codex/WorkBuddy/Agent, grounded in current Run/artifacts and real authorization. Include objective, protected data/sealed/writing rules, affected modules, minimal decisive test, output verification and only the necessary findings. Let Agent handle related fixes continuously rather than fixed tiny task batches. No redundant repo-wide reading or huge reports. If there is genuinely no next work: `NO_NEXT_ACTION`, no filler instruction.

**B: User decision required** — `RECOMMENDATION+REASON | OPTIONS (usually 2–3 with cost/risk) | USER_CHOICE_NEEDED`. **Do not output a Codex/WorkBuddy/Agent execution instruction, training command or draft prompt yet.** Only after the user chooses and grants any missing permission in an actual new message may the next reply issue an executable instruction.

## Representative cases

| Case | Contract |
|---|---|
| Existing fully authorized DEV run has a clear code fault | A: targeted repair/verification Agent instruction |
| Read-only original Run/nearest-paper audit to check Q2 potential | A: concise audit Agent instruction |
| New sealed confirmation or unapproved GPU budget is highly recommended | B: reason and user options, NO execution prompt |
| Scientific evidence supports ending the entire project or pivoting primary Task | B: recommend and present choices, NO project-STOP/pivot prompt |
| Research-results summary awaiting user review, or writing authorization absent | B: user choices, never manuscript drafting instruction |
| Both reviewed summary and explicit manuscript-writing instruction verified | A only for that authorized manuscript scope |

**Do not confuse:** scientific recommendation ≠ approval; `Q2_POTENTIAL_SUPPORTED` ≠ manuscript-writing permission; PASSed structural contract ≠ scientific confirmation. Preserve the user's choice as provenance. No extra machine status or compulsory decision form.
