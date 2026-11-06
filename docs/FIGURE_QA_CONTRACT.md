# Figure QA Contract — explicit user opt-in

**Highest-priority gate:** Images must be generated, modified, redrawn, previewed or assembled **ONLY when the actual user explicitly requests drawing or modifying the specified images**. No automatic diagnostic charts, evidence figures, manuscript figures, algorithm/flow diagrams, illustrations, contact sheets or image-generation calls. A credible Run, new evidence, stage transition, manuscript-writing authorization, installed Skill, saved old figure or proposed plot is NOT a request.

This is an on-demand reference, not an eighth Skill, new research stage, CLI state, self-awarded authorization or hard dependency on PD-RW. See [EXECUTION_POLICY](EXECUTION_POLICY.md).

## 1. Trigger and permission boundaries

- Allowed example: “draw Figure8a”, “redraw all ten listed figures”, “change this picture to a white background”. **Not allowed to draw:** “continue research”, “which graphs would be best?”, “assess the figures”, “make a plotting prompt”, “review results”, “write the manuscript”. Without an explicit drawing request, provide textual guidance, numeric evidence, tables, or an unexecuted plotting plan only. Do not run plot code, generate even a temporary preview or create images.
- Match the original user request to the named project, images and edits; a single request includes necessary within-scope iterations, exports and visual-QA previews, but does not authorize any unrelated figure or new project. Record the real message source. A JSON request marker, Agent proposal or older project STATE is never authorization by itself.
- Image authorization grants **no** new dataset access, CPU/GPU training, installation, SEALED/CONFIRMATION exposure, extra budget, release, upload, publication or manuscript-writing permission. Follow the existing evidence/permission contracts.
- A requested manuscript-quality figure is separate from manuscript prose authorization and does not unlock `WRITING_LOCKED`. If the user has not reviewed the research-results summary, the requested manuscript-looking image must be labeled **candidate**, not submission-ready. Conversely, science confirmation or writing permission does not trigger drawing.
- Existing image files may be inspected and critiqued within lawful access when requested, without rendering a new copy or modifying them unless the request explicitly asks for an image change.

## 2. Figure classes (all require explicit request before rendering)

- `DIAGNOSTIC`: minimal reproducible DEV error/distribution/learning diagnostic; not journal-polished by default.
- `EVIDENCE`: traceable claim-aligned visual, faithfully including negative effects, independent units and uncertainty.
- `PUBLICATION`: journal-style scientific plots or schematics, only from eligible verified evidence, project-defined fonts/colors/axes and actual post-export review.

## 3. Lightweight per-figure contract

Formal image QA accepts the legacy project-relative `figure-v1` contract for compatibility. The existing fields remain unchanged: `figure_id`, `figure_kind`, `user_request_ref`, actual source/plot-data SHA-256, `outputs:{svg,png}`, and `style:{background,font_family,semantic_colors,comparison_group,axis_limits,png_dpi,canvas_inches}`. Legacy v1 passes only report `LEGACY_V1_UNFROZEN`, **not** a style-system pass; see [legacy example](../templates/FIGURE_CONTRACT.example.json).

**New publication data plots should use `figure-v2`**, adding `style.theme_ref` (project-relative theme JSON), `theme_sha256`, `template_id`, `style_fingerprint`, `style_profile`, the locked `font_family` and, if the project explicitly pins a named palette, `palette_id`/`palette_registry_version`. Use the [v2 contract example](../templates/FIGURE_CONTRACT.v2.example.json) and [Figure Style System](FIGURE_STYLE_SYSTEM.md). Fingerprints include the theme, selected template and baseline mplstyle; no default-color-cycle or silent single-figure override is permitted.

Hashes bind bytes only. The figure checker does not independently certify a metric, sample provenance, research claim, legal access, actual color-to-data mapping or original human authorization. A Figure Contract cannot promote `REPORTED` to `METRIC_VERIFIED_DEV_ONLY`, or DEV evidence to confirmation. Unknown scientific status remains UNKNOWN; inappropriate sources remain BLOCKED.

### Optional read-only QA (only after the user requested actual figures and those figures already exist)

```bash
python -m tools.figure_qa --project PROJECT --contracts figures/Figure8a.json figures/Figure8b.json
```

It performs read-only source/plot-data SHA checks, project path confinement, SVG/PNG structure/dimensions and cross-figure color/scale checks. For v2 it **also checks pinned theme/template/style fingerprint and inspects the tagged series groups actually present in SVG** for their declared paint values (`series--model--SF` etc.). These checks also report a **white-background color contrast risk** for the declared series (advisory only), and inspect some editable SVG font declarations. They do not prove actual category-to-source-data binding, semantic accuracy, installed font matching, color-vision accessibility, pixel-level opacity, complete visual legibility or scientific confirmation. Actual Line2D/scatter coordinates may be checked during the authorized session with [figure_artist_audit](../tools/figure_artist_audit.py); its result is still not independent validation of raw Run/metric truth. It never executes plot code, trains, downloads or creates images. `STRUCTURAL_PASS_REVIEW_REQUIRED` is **not** figure correctness or scientific verification; rendering/visual checks and science checks stay separate.

## 4. Styles and real visual review
### Scientific metadata and real-artist integrity (strict on demand)

New formal data figures should set `"evidence_profile": "strict-scientific-v1"` and supply meaningful `metric`, `unit`, `denominator`, `independent_unit` plus `science_context.population_or_split / transform_notes / missing_policy / uncertainty_definition / selection_history`. A declared “no interval” needs an explicit rationale and may not imply certainty. The static `tools.figure_evidence` preflight rejects missing declarations in strict mode; existing v1/v2 contracts without the profile are **still supported** but report `INCOMPLETE_METADATA`. Completing text fields **does not verify their truth**, Run provenance, independent sampling or statistical validity.

For an image **already explicitly requested** and generated from lawful source tables, run the optional `tools.figure_artist_audit` on the actual Matplotlib artists. It now checks line/scatter arrays, zero-based rate-bar geometry/opaque paint, and heatmap arrays/scales against independently supplied verified plot rows. Its result is `MATCH_EXPECTED_ROWS_ONLY`, **not** scientific confirmation. Timeline segments, errors/intervals and third-party chart builders remain outside these narrow audit routines; do not claim full visual-data validation.

The requested SVG+PNG pair is rendered before either file is committed. The exporter exclusively creates target names and rolls back its own partial writes if a write fails. This prevents a common incomplete-pair failure; it is **not a true filesystem transaction against power loss**. Always check both output files and do not overwrite older verified images. Unit tests use text fixtures and in-memory checks, never rendered test charts or image previews.



Reference relevant parts of GitHub [scientific-visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md), [scientific-figures](https://github.com/databricks-industry-solutions/vital-skills/blob/main/skills/scientific-figures/SKILL.md), [publication-chart-skill](https://github.com/Galaxy-Dawn/publication-chart-skill/blob/main/SKILL.md) and [SciencePlots](https://github.com/garrettj403/SciencePlots). Do not require every Skill installed.

- Plot from trusted data and reproduce exported SVG/PNG from one script; preserve statistical unit, denominator, uncertainty, zero baselines, missingness, adverse results and honest scale.
- Default white opaque figure background, readable consistent fonts and dark labels. Map colors by **semantic identity** (model:SF etc.) across figures, never by bar position when categories differ; use markers/linestyles when helpful.
- Treat Arial, 15pt axis labels, all-black text, axis arrows, fixed color palette, 600dpi, one-/two-column widths and SVG text editing as **project-specific** directives. Apply the user's chosen settings precisely, without forcing meaningless axes onto a heatmap/timeline or identical dimensions onto unlike diagrams.
- Check actual rendered images at publication size for font substitution, overlap, arrow clipping, legends, margins, palette, meaningful units and accurate figure comparison. Automated checking cannot fully judge these.
- Frozen chart choice after a first scientifically valid design; fix only affected images and run local regression checks. Use a project-wide theme version and template ID rather than independent styling per figure; compare style fingerprints, consistent axes boxes and actual tagged SVG paints. Contact sheets are also images; only build them within the original explicit batch image request.

## 5. Outcome and handoff

Figure-only reporting vocabulary (not research CLI enums):
- `BLOCKED`: no verifiable drawing request or invalid permissions/source.
- `PARTIAL`: incomplete scientific evidence or provisional output.
- `QA_FAIL`: broken structural or visual checks.
- `STRUCTURAL_PASS_REVIEW_REQUIRED`: automated structure checks passed, *visual/scientific review still required*.
- `FINAL_PASS`: only after actual source-data reconciliation, eligible research evidence and rendered-image review.

Minimal report: `USER_REQUEST_REF | FIGURE_ID | SOURCE_RUN/UNIT/METRIC | OUTPUTS | AUTOMATED_QA | VISUAL_QA | LIMITS/BLOCKERS`. No forced formal figure making, no automatic manuscript drafting.
