# AI Research Execution Policy · v0.6

This file is the **single shared source** for execution efficiency. Read it once per research session; each Skill adds only its specific task. Requirements are defaults unless scientific correctness, actual permissions or the user's instruction require otherwise.

## Scope and context
- Start from the current **blocker**, not stage 01. Read `AGENTS.md`, the actual project `STATE.json`, relevant source/Run receipts, and **one** Skill. Load other files only to resolve a named dependency.
- Prefer `python -m core.cli brief --dir PROJECT` for a compact project snapshot. It reports pointers, **not** scientific verification. Reuse prior valid experiments, data audits, downloads, code and paper evidence; invalidate stale versions rather than recomputing everything.
- State uncertainties as UNKNOWN, not automatic STOP. An exploration Pilot may be negative without falsifying the Task. Distinguish code error, invalid evaluation, weak mechanism, infeasible Task and unsupported Claim.

## Autonomous work and cost
- Choose the **largest coherent authorized batch**: inspect → implement → directed test → repair → save evidence → decide. Do not stop after every small step or repeatedly ask for already supplied details.
- Match work to its expected information gain. Use a minimal informative baseline/probe first; increase GPU/iterations/review depth only when results may change a scientific decision. Reuse cached results and limit redundant Agent reviews; do not mandate multi-Agent voting.
- Track measured resources when available (elapsed time, GPU, API/Token usage). **Never invent Token or compute costs** from an absent log. Total research value matters more than apparent task-count efficiency.
- During development, run focused tests for affected code and relevant interfaces. Run full CI at integration/release or when a shared invariant changed; preserve safety-critical tests regardless of cost. Avoid repeating unchanged tests without a concrete reason.

## Outputs and visuals
- **No automatic plots, polished figures, slide decks, decorative diagrams, or publication formatting** during exploratory work. Make a minimal diagnostic figure only if it tests a hypothesis or changes the decision. Publication-quality figures follow accepted, verified results.
- Do not generate a Markdown report after every command or Skill. Preserve raw logs/artifacts where they are produced. Default human-facing update is **delta-only**: `RESULT` (new fact), `EVIDENCE` (file/run), `DECISION`, `NEXT`; add `BLOCKER` / `COST` only if material and known. No duplicate narrative, pasted logs, or fake completion estimates.
- Longer summaries are reserved for real decision boundaries, recovery, handoff or final scientific evidence; document only what cannot be reconstructed from code, source and receipts.

## Scientific and permission gates (never optimized away)
- Protect legitimate labels, group splits, legal inference inputs, evaluator/Task versions and untouched independent confirmation. Keep negative Runs and selection history. Strong/fair baselines and evidence-backed novelty remain required for formal Claims.
- First negative Pilot ≠ project STOP. Repair bounded engineering faults automatically inside actual authorization. Continue only with a discriminating mechanism test; pivot when the Task premise fails; avoid infinite no-information tweaking.
- Downloading, installation, CPU/GPU fitting, spending, external transfer, sealed confirmation, submissions and substantive scope changes require actual user authorization. Neither a stored reference, tool parameter nor upstream Skill grants permission.

**Success test:** valid evidence and reproducible progress per total real resource cost, not report length, number of Agent calls, figures or procedural checkmarks.

**v0.7 non-negotiable:** independent DEV metric recomputation and event-chain verification are required before claiming a model score or selecting Champion. Never attempt to use a normal development event as sealed confirmation; use a separately authorized evaluator when available. Statistics support uncertainty analysis but must not impose a universal p-value gate on exploratory research.
