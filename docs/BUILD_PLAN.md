# Build plan and measurable scientific evaluation

## Implemented

**P0** (v0.1): seven modular Skills, short AI entry, sourced design ledger, deterministic route suggestions, five base artifact types and basic CI.

**P1a** (v0.2): opt-in public OpenAlex/Crossref metadata adapter with two-provider normalization, DOI de-duplication and partial failure disclosure; extended evidence/dataset schemas; source-hashed handoff, no note-only phase promotion; DEV Run fair-comparison tool and regression tests. HTTP mocked in CI; actual public API connectivity has **not** been tested in CI. No full-text retrieval or novelty model has been implemented.

**P1b (v0.3):** pinned licensed ResearchStudio Paper Search source workers, selftests and postprocess with a Forge adapter; selected IdeaSpark references and upstream Scoop Check Skill for careful prior-art review; pinned ARIS experiment-plan Skill for evidence-backed planning. Original adapters produce UNVERIFIED novelty matrices and PLAN_ONLY bounded experiment contracts. Includes input-fingerprint mismatch detection. Integration tests are deterministic mocks; full-text novelty claims and live search coverage remain unverified.

## Next, in priority order

1. **P1c:** attach official dataset/license/label/group catalogs and a source→observation→claim graph; integrate optional full-text paper reading and verified nearest-work comparisons. The current novelty adapter is a precheck, not an autonomous original idea judge.
2. **P2:** authorized execution integration with one coding Agent. Protected evaluator and sealed split, train-only preprocessing audits, smallest credible baseline, one real Challenger, group-level predictions, immutable raw logs/versions/compute cost and recovery. Avoid parallel expensive Agent trees until proven useful.
3. **P3:** confirm that Run and Claim refs point to original real results; independent held-out eligibility by task *after* task search, frozen protocol, named nearest prior method, group-level effect/uncertainty. Add blinded before/after research decision evaluation using tasks comparable to chapter 08 and 10 at equal resource budgets.

## Optimization principles from high-star projects

- **ResearchStudio:** source-backed ideas and version-bound audit receipts.
- **Anthropic Skills:** metadata→SKILL→optional supporting resources, not preload everything.
- **obra/superpowers:** trace the first real root cause and verify before claiming completion; no compulsory multi-agent for routine bugs.
- **AutoResearch:** protect evaluation from algorithm search (concept only; upstream repo license undeclared).
- **AIDE/R&D-Agent:** retain candidate lineage and let reliable experimental feedback suggest a **new** mechanism, not merely rename the same failure.

### Evidence for claims about the workflow itself

Measure earliest valid-result cost, correct task/agent routing, token/GPU/time cost, protocol violations, false project STOP, no-information continuation and truly independent claim support. CI passing is engineering evidence only; no success-rate improvement has yet been measured.

## v0.4 implemented (this iteration)

- **P0:** cross-platform file lock on event writes; active Task raw SHA and normalized content fingerprint; revalidation at plan/Run/novelty handoff; explicit TASK_PIVOT and PROTOCOL_REVISED with versioned Decision + new ACTIVE Task and history-preserving Champion reset; selection/journal commands.
- **P1:** 1900-to-present search default (explicit narrowed windows still allowed), source conflict report, conservative DOI-safe dedup, novelty shortlist coverage + selected record IDs; vendored Superpowers optional debugging/verification Skills.
- **P2 preflight only:** bounded read-only DEV CSV and manifest structure audit, no sealed data reading or fitting.
- **P4 software-only:** deterministic routing fixtures and negative/positive regression tests, Windows+Ubuntu CI.
- **P3:** read-only candidate Journal implemented, but an authorized executable AIDE/R&D-Agent backend is NOT yet integrated.

Remaining high-value tasks are a genuine official dataset catalog + full-text nearest-work verification; a narrowly scoped, user-authorized coding/experiment runner with raw logs and split isolation; and blinded prospective scientific workflow evaluations at equal budgets. Do NOT pretend P2/P3/P4 are proven research-success improvements because CI passes.
