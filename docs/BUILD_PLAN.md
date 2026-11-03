# Build plan and measurable scientific evaluation

## Implemented

**P0** (v0.1): seven modular Skills, short AI entry, sourced design ledger, deterministic route suggestions, five base artifact types and basic CI.

**P1a** (v0.2): opt-in public OpenAlex/Crossref metadata adapter with two-provider normalization, DOI de-duplication and partial failure disclosure; extended evidence/dataset schemas; source-hashed handoff, no note-only phase promotion; DEV Run fair-comparison tool and regression tests. HTTP mocked in CI; actual public API connectivity has **not** been tested in CI. No full-text retrieval or novelty model has been implemented.

## Next, in priority order

1. **P1b:** attach authoritative official dataset catalog and Source → Observation → Claim graph; add direct nearest-paper full-text inspection and difference table; distinguish actual observations from hypothetical mechanisms. Do not treat metadata titles/DOIs as verified novelty.
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
