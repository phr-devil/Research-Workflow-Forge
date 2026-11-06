# Figure Style System — same project, consistent scientific visual language

**MANDATORY OPT-IN:** This file only defines reusable configuration and code. **Do not generate, redraw, preview, export or create even CI test images unless the actual user has explicitly requested those specific images.** An accepted Run, scientific finding, writing authorization, style template, sample command or an Agent preference does not authorize rendering. See [FIGURE_QA_CONTRACT](FIGURE_QA_CONTRACT.md).

## Architecture: Theme → Template → Figure instance

1. **Global theme**: [publication_base.mplstyle](../styles/publication_base.mplstyle) and [figure_theme.json](../styles/figure_theme.json) fix white background, dark typography, line/tick widths, semantic palette strategy, legend rules and canvas width presets. The default is **general journal**, not an exact publisher guarantee. Arial / 15-13-12pt / all-arrow axes / 600dpi may be specified in a project theme; do not make project-specific requirements mandatory for other research.
2. **Template registry**: [figure_registry.json](../templates/figure_registry.json) specifies a shared normalized axes rectangle, canvas profile, legend slot and semantics for each of 7 figure types: model dot, paired dot, dumbbell, effect distribution, rate/ablation, temporal tracks and heatmap. Templates express a layout family; they do not choose the science, sample units or chart type for the researcher.
3. **Figure instance**: a user-requested figure binds validated source data, protocol, metric, unit, independent groups, a named template and a project theme. Reuse code and style, **not** hidden assumptions from an unrelated project.

### Project theme and style freeze

Copy the baseline JSON into the project only after a user has asked to configure the plotting workflow, or when their explicit drawing request makes it necessary (copying/editing text is not image creation). Set a **single project theme** before first official render. Provide semantic keys like \`model:SF\` or \`skill:Walk\` under \`colors.semantic_colors\`; the same key must have the same color throughout the project. Unknown semantic keys must fail, not fall back to Matplotlib's color cycle.

- For every new **figure-v2** contract, pin \`style.theme_ref\` (project-relative), \`style.theme_sha256\`, \`style.template_id\`, \`style.style_profile\`, \`style.font_family\` and \`style.style_fingerprint\`. The fingerprint covers normalized effective theme + template definition + base MPL style bytes. See [v2 example](../templates/FIGURE_CONTRACT.v2.example.json).
- Never silently alter a project theme after it is frozen. If the journal's official requirements or a user's explicit request require a new theme, increment \`theme_version\`, record reason, and redraw **only explicitly requested/affected figures**.
- Same-template comparable figures should share axes geometry, labels/legend conventions, coherent marker and line sizes. Same metric/comparison group should also use the same template ID, physical canvas and scale. Different amounts of content may justify different **height** and position; explicit exceptions should be documented, not treated as general style drift.
- Project-specific Arial and font sizes are intentional choices, **not proof that the submission journal accepts them**. Verify official requirements at the actual journal/submission stage. Effective font size must be reviewed at final publication size.

### Actual figure code (optional Matplotlib; never run in CI)

[figure_templates.py](../tools/figure_templates.py) provides a request-gated \`create_template_figure\`, \`add_semantic_series\`, optional Cartesian arrowheads and \`export_figure\`. The implementation lazily imports Matplotlib **only after** a verified user request is asserted by the calling Agent. The guard's Boolean/message reference does **not** itself prove permission: check the original user message. It never accesses raw training/SEALED data or runs model fitting.

Use \`artist.set_gid("series--model--SF")\` (the helper sets this automatically) on each significant semantic series so the exported SVG can be checked for its **actual** declared paint color. This tagged-group convention is only a limited check and does not prove correspondence to source values, font fallback, visual contrast or correctness of plot labels. For a matrix with continuous colormap, use a properly chosen scale and colorbar; do not force categorical colors or meaningless axis arrows onto it.

Do **not** create figures from \`__main__\`, Python imports, initialization, tests or CI. Automated tests should exercise theme parsing, template metadata, permission guards and XML **in memory**; no generated figure files, snapshots or contact sheets. An authorized plotting task can use its specific data and produce one or more SVG/PNG exports from the same Matplotlib figure object; use explicit figure size instead of silently changing physical canvas with \`bbox_inches="tight"\`.

### QA and exceptions

- **Static:** verify theme/registry schema, source hashes, template ID, fingerprint, comparable axis limits, file structure, and actual tagged SVG colors when provided. Do not claim to verify image aesthetics or scientific claims from config hashes alone.
- **Authorized visual review:** inspect the actual exported SVG/PNG at final paper width for font substitution, black labels, axes arrows, legend overlap, plot alignment, clipping, color contrast, symbol legibility, and whether identical templates really appear consistent. Keep source-data reconciliation separate from file QA.
- **Regression:** compare normalized layout/template and metadata for paired plots; avoid global pixel equality requirements because data and antialiasing can differ. Re-run only affected checks and redraw only affected **authorized** images.
- **Exceptions:** scientific readability > mechanical uniformity. Increasing height for 17 categories, choosing timeline instead of Cartesian Y axis, or moving a crowded legend with a documented reason is legitimate. Never distort sample units, denominators, baselines or effect sizes to satisfy the style template.

Related GitHub projects (selectively referenced, not automatically installed): [SciencePlots](https://github.com/garrettj403/SciencePlots), [Seaborn](https://github.com/mwaskom/seaborn), [Scientific Visualization](https://github.com/rougier/scientific-visualization-book), [LovelyPlots](https://github.com/killiansheriff/LovelyPlots), [K-Dense scientific-visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md).
