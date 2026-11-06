# Figure Style System — same project, consistent scientific visual language

**MANDATORY OPT-IN:** This file only defines reusable configuration and code. **Do not generate, redraw, preview, export or create even CI test images unless the actual user has explicitly requested those specific images.** An accepted Run, scientific finding, writing authorization, style template, sample command or an Agent preference does not authorize rendering. See [FIGURE_QA_CONTRACT](FIGURE_QA_CONTRACT.md).

## Architecture: Theme → Template → Figure instance

1. **Global theme**: [publication_base.mplstyle](../styles/publication_base.mplstyle) and [figure_theme.json](../styles/figure_theme.json) fix white background, dark typography, line/tick widths, semantic palette strategy, legend rules and canvas width presets. The default is **general journal**, not an exact publisher guarantee. Arial / 15-13-12pt / all-arrow axes / 600dpi may be specified in a project theme; do not make project-specific requirements mandatory for other research.
2. **Template registry**: [figure_registry.json](../templates/figure_registry.json) specifies a shared normalized axes rectangle, canvas profile, legend slot and semantics for each of 7 figure types: model dot, paired dot, dumbbell, effect distribution, rate/ablation, temporal tracks and heatmap. Templates express a layout family; they do not choose the science, sample units or chart type for the researcher.
3. **Figure instance**: a user-requested figure binds validated source data, protocol, metric, unit, independent groups, a named template and a project theme. Reuse code and style, **not** hidden assumptions from an unrelated project.

### Palette selection — categoricals, effects and continuous data

[Palette registry](../styles/palette_registry.json) contains versioned categorical presets:
`tol-bright` (the existing default, **unchanged**), `tol-muted` (recommended candidate for new projects), `tol-vibrant`, `okabe-ito` and `tableau10`. `accents` is a separate three-color annotation palette; accents are not silently assigned as extra model categories. Continuous `viridis`/`cividis` and optional `batlow` are for sequential values, `vik` for signed/diverging data and `twilight` for periodic data. Optional `cmcrameri` may be installed **only when needed for an authorized drawing task**.

Presets are **choices, not a mandate to recolor old projects**. The baseline theme keeps Tol Bright as its default. Set `colors.palette_id`, `colors.palette_registry_version` and `colors.semantic_colors` in a **project theme**; stable `model:SF`, `skill:Walk`, etc. always map to the same specified HEX. An old theme without `palette_id` remains a legacy unpinned theme. Use `custom` for an explicitly selected project palette; do not silently change an existing semantic mapping or assign new colors by bar position.

The pure-text `tools.figure_palette` helpers can propose stable keys and calculate white-background contrast; marks with a white contrast ratio below 3:1 trigger **advisory warnings**, not an automatic rule that every filled shape is invalid. These calculations **cannot certify color-vision accessibility or grayscale legibility**. Confirm thin lines, tiny symbols and color-blind distinguishability during authorized final visual review. When categories exceed available colors, choose a larger palette or use distinguishable markers/line types rather than reusing a color without explanation.

### Project theme and style freeze

Copy the baseline JSON into the project only after a user has asked to configure the plotting workflow, or when their explicit drawing request makes it necessary (copying/editing text is not image creation). Set a **single project theme** before first official render. Provide semantic keys like `model:SF` or `skill:Walk` under `colors.semantic_colors`; the same key must have the same color throughout the project. Unknown semantic keys must fail, not fall back to Matplotlib's color cycle.

- For every new **figure-v2** contract, pin `style.theme_ref` (project-relative), `style.theme_sha256`, `style.template_id`, `style.style_profile`, `style.font_family` and `style.style_fingerprint`. The fingerprint covers normalized effective theme + template definition + base MPL style bytes. See [v2 example](../templates/FIGURE_CONTRACT.v2.example.json).

A **read-only** command calculates the v2 style lock fields from an existing project theme, without importing Matplotlib or generating images:

```bash
python -m tools.figure_style --theme PROJECT/figures/theme.json --template rate_ablation
```

Copy the result into the per-figure contract, supply a project-relative `theme_ref`, and separately cite the real original user figure request. The hash is not a permission token or a scientific verification.

- Never silently alter a project theme after it is frozen. If the journal's official requirements or a user's explicit request require a new theme, increment `theme_version`, record reason, and redraw **only explicitly requested/affected figures**.
- Same-template comparable figures should share axes geometry, labels/legend conventions, coherent marker and line sizes. Same metric/comparison group should also use the same template ID, physical canvas and scale. Different amounts of content may justify different **height** and position; explicit exceptions should be documented, not treated as general style drift.
- Project-specific Arial and font sizes are intentional choices, **not proof that the submission journal accepts them**. Verify official requirements at the actual journal/submission stage. Effective font size must be reviewed at final publication size.

### Actual figure code (optional Matplotlib; never run in CI)

[figure_templates.py](../tools/figure_templates.py) provides request-gated `figure_session`, legacy `create_template_figure`, `add_semantic_series`, consistent legend placement, optional Cartesian arrows, `font_preflight` and `export_figure`. **New code must use the full `figure_session` context from figure creation through artists, legend and export**; the old constructor closes rc_context at return and is compatibility-only. The renderer resolves the actual installed font and fails on substitution instead of silently replacing Arial (or any chosen family). Matplotlib remains an optional lazy import, only for authorized drawing. The guard's Boolean/message reference does **not** itself prove permission: the calling Agent must check the original user message.

[figure_charts.py](../tools/figure_charts.py) contains explicitly request-gated draw functions for seven families: model dots, paired dots, dumbbells, signed-effect ECDF, rates/ablations, unsmoothed timeline tracks and continuous heatmaps. These are **drawing helpers, not automatic chart recommendations or implicit permission**. A continuous map must match its scientific role; signed diverging effects are centered on zero rather than arbitrary data midpoint. The data source and metric denominator remain external scientific duties. No plotting module is imported in ordinary tasks or tests, and no example command generates images.

For reproducible authorized exports, call `rendering_environment_receipt(fig, explicitly_requested=True, user_request_ref=...)` inside the same verified figure task to record the resolved font family, Matplotlib/Python versions, frozen template/style fingerprint and code hashes. The receipt is **not** a provenance certificate for experiment execution and is not permission to render another figure. Do not save or distribute font files.

[figure_artist_audit.py](../tools/figure_artist_audit.py) optionally reads actual finished Line2D/scatter coordinates and compares them to independently supplied expected plot rows, requiring a real source reference; this catches series swaps and point value changes. It **does not** independently validate that source Run, the metric arithmetic, denominators, labels or causal scientific claim. Bars, heatmaps and timeline segments need their own appropriate data/geometry checks and must not be claimed fully audited. Any saved provenance report is a **text artifact**, created only as part of an authorized figure task.

Use `artist.set_gid("series--model--SF")` (the helper sets this automatically) on each significant semantic series so the exported SVG can be checked for its **actual** declared paint color. This tagged-group convention is only a limited check and does not prove correspondence to source values, font fallback, visual contrast or correctness of plot labels. For a matrix with continuous colormap, use a properly chosen scale and colorbar; do not force categorical colors or meaningless axis arrows onto it.

Do **not** create images automatically from imports, initialization, ordinary tests or CI. A dedicated script may render only after a real, explicit user request for those specific figures. Automated tests should exercise theme parsing, template metadata, permission guards and XML **in memory**; no generated figure files, snapshots or contact sheets. An authorized plotting task can use its specific data and produce one or more SVG/PNG exports from the same Matplotlib figure object; use explicit figure size instead of silently changing physical canvas with `bbox_inches="tight"`.

### QA and exceptions
### Review lessons from established GitHub projects

[SciencePlots](https://github.com/garrettj403/SciencePlots) demonstrates composable journal style presets; [Seaborn](https://github.com/mwaskom/seaborn) separates semantic palette, style and size contexts; [K-Dense scientific-visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md) explicitly requires truthful sample/interval/missing-data definitions and inspection of deliverables. These are **design references, not mandatory package dependencies or a claim of endorsement**. See the compact [implementation audit](FIGURE_IMPLEMENTATION_AUDIT.md).

Use `figure_session` throughout the expressly requested drawing task; the old `create_template_figure` convenience function closes its styling context at return and must not be used for a new multi-step figure. `export_figure` first produces SVG/PNG in memory and then writes a non-overwriting pair with rollback. Verify both files before use. For scientific results, an output pair and a valid style hash are insufficient without source-data reconciliation.



- **Static:** verify theme/palette registry versions, semantic colors, source hashes, template ID, fingerprint, comparable axis limits, file structure, actual tagged SVG colors when supported, and a contrast-risk report for declared series. The checks are read-only and never generate new figures. Do not claim to verify image aesthetics or scientific claims from config hashes alone.
- **Authorized visual review:** inspect the actual exported SVG/PNG at final paper width for font substitution, black labels, axes arrows, legend overlap, plot alignment, clipping, color contrast, symbol legibility, and whether identical templates really appear consistent. Keep source-data reconciliation separate from file QA.
- **Regression:** compare normalized layout/template and metadata for paired plots; avoid global pixel equality requirements because data and antialiasing can differ. Re-run only affected checks and redraw only affected **authorized** images.
- **Exceptions:** scientific readability > mechanical uniformity. Increasing height for 17 categories, choosing timeline instead of Cartesian Y axis, or moving a crowded legend with a documented reason is legitimate. Never distort sample units, denominators, baselines or effect sizes to satisfy the style template.

Related GitHub projects (selectively referenced, not automatically installed): [SciencePlots](https://github.com/garrettj403/SciencePlots), [Seaborn](https://github.com/mwaskom/seaborn), [Scientific Visualization](https://github.com/rougier/scientific-visualization-book), [LovelyPlots](https://github.com/killiansheriff/LovelyPlots), [K-Dense scientific-visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md).
