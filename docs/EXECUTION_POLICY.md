# AI Research Execution Policy · v0.14

This file is the **single shared source** for execution efficiency. Read it once per research session; each Skill adds only its specific task. Requirements are defaults unless scientific correctness, actual permissions or the user's instruction require otherwise.

## Scope and context
- Start from the current **blocker**, not stage 01. Read `AGENTS.md`, the actual project `STATE.json`, relevant source/Run receipts, and **one** Skill. Load other files only to resolve a named dependency.
- Prefer `python -m core.cli brief --dir PROJECT` for a compact project snapshot. It reports pointers, **not** scientific verification. Reuse prior valid experiments, data audits, downloads, code and paper evidence; invalidate stale versions rather than recomputing everything.
- State uncertainties as UNKNOWN, not automatic STOP. An exploration Pilot may be negative without falsifying the Task. Distinguish code error, invalid evaluation, weak mechanism, infeasible Task and unsupported Claim.

## Evidence-first experiment priority (not an extra gate)
- Starting from the current Task/Run, prefer this **skippable** order: legal truth/group/time/inputs → validated simple reference (existing if possible) → observed signal and recoverable error → smallest discriminator or correction → more complex architecture only when it addresses a named unresolved limit, distinct falsifiable mechanism or real deployment need. Some physical/temporal tasks can require complex models from the outset; justify this with a cheap probe where possible.
- Keep three outcomes separate: `LEGAL_SIGNAL`, `MINIMUM_RELIABLE_RESULT`, `MINIMUM_INDEPENDENT_CLAIM`. Simple improvement is not novelty, Oracle headroom is not identifiable deployable gain, negative challenger does not invalidate a preserved reference or Task.
- For experimental cost choose A (read-only existing predictions/statistics), B (authorized lightweight fit), C (authorized complex training). Use the least costly experiment that can change the current decision; these are cost descriptions, not universal GPU/time thresholds or new authorization.
- Preserve the simplest credible matched-information reference, its raw predictions and receipts when testing challengers. Mark incompatible Task/K/evaluator comparisons NOT_COMPARABLE; never silently overwrite old results. On matched simple-baseline domination without a distinct lever, stop *that mechanism* and return the scientific question/novelty gap to PD-RW if used.

## Claim-proportional publication evidence (not a new gate)
- A single real incremental contribution can justify a paper candidate: task-relevant improvement, efficiency/calibration cost for an acceptable accuracy tradeoff, reliable failure/robustness law, or meaningful combination/protocol improvement. Global SOTA, all metrics positive, novel backbone and mandatory multi-dataset superiority are **not** prerequisites.
- Compare with the **strongest relevant matched** simple alternative and named nearest predecessors, not every model ever published. Report adverse metrics and compute/label costs, independent groups, selection history, uncertainty, and a confirmation scope matching the Claim. A single dataset may suffice for a properly limited Claim with genuinely independent confirmation groups; cross-dataset claims require corresponding evidence.
- Separate `ENGINEERING_ASSET_ONLY`, `PAPER_PATH_CANDIDATE`, and `CONFIRMED_CLAIM` as **scientific interpretations already used by PD-RW**, not new Forge CLI enum values. Small DEV gains are exploratory until verified; negative results require a reproducible, not-yet-known insight rather than merely losing a leaderboard.

## Small-discovery rescue and venue handoff (optional)
- At a **real negative or narrow positive** DEV result, distinguish failed algorithm mechanism from viable scientific contribution. Before project-level abandonment, check *once at the affected decision boundary* for a testable new calibration-cost curve, resource–accuracy tradeoff, controlled failure/heterogeneity law, or claim-limited improvement not already resolved by named neighbors. A weak finding is `UNKNOWN/CLAIM_WITH_GAPS` until evidenced, not instantly `NO_INDEPENDENT_CLAIM` or `CONFIRMED`. Do not endlessly retell the same negative score as a novel discovery.
- Pass `CLAIM_SENTENCE | EVIDENCE_RUN | NEAREST_NEIGHBOR_GAP | ONE_DECISIVE_MISSING_TEST | LIMITS` to the research controller when publication assessment is relevant; do not spawn venue search automatically on every Run. The optional S/A/B/C manuscript-potential and STRETCH/TARGET/FALLBACK venue suggestions are **separate, nonbinding advisory axes**, owned by PD-RW if used, not new Forge enum/state gates; C is **not** an automatic failure and S/A is not a validation badge.
- Real venue recommendations require current evidence on scope, article type, recent precedents, indexing/JCR category-year, fees and publisher; do not infer acceptance chances, equate journal quartiles to manuscript potential, or require multi-dataset supremacy. See [PD-RW venue strategy](https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/VENUE_STRATEGY.md) only when requested.

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
