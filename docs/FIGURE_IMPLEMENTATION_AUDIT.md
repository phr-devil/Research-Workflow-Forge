# Figure implementation audit — 2026-11-06

> Code review and static-contract remediation only. **No user authorization to generate images in this task**; no Matplotlib rendering, reference image or screenshot was produced. This document does not create a compulsory stage or grant permission.

| Reference | Reusable idea | Specific RWF gap | Action and boundary |
|---|---|---|---|
| [SciencePlots](https://github.com/garrettj403/SciencePlots) (high-star scientific styles) | Small composable style sheets and context-specific presentation | Existing theme + templates were reusable, but export could commit SVG before PNG generation failed | Render both into memory first; exclusively write both; delete own partial files on write failure |
| [Seaborn](https://github.com/mwaskom/seaborn) (mature statistical plotting) | Separate palette semantics, appearance and sizing context | Category and per-template controls existed; project styles still had a deprecated one-shot constructor with short-lived context | State `figure_session` as the only recommended multi-step rendering workflow; retain constructor for compatibility |
| [K-Dense scientific-visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md) | Source transformations, missingness, true independent units, uncertainty and scientific honesty | A style/structural QA PASS could coexist with undocumented exclusion/uncertainty | Add optional strict scientific metadata preflight; no auto-science confirmation or SEALED access |
| [Matplotlib](https://github.com/matplotlib/matplotlib) | File-like `savefig`, explicit figure canvas | Two file saves weren't one reliable output unit | Use in-memory SVG+PNG and test pair rollback with **plain text**, not generated images |
| [Colorcet](https://github.com/holoviz/colorcet) | Continuous/perceptual color design follows data semantics | Palette preset selection was implemented; true accessibility not fully testable from HEX alone | Preserve task-specific continuous/diverging/cyclic maps and contrast warnings; never claim color-vision proof |

## Resulting invariant

- Image creation remains strictly user-opt-in. CI tests only inspect code, text manifests, fake artists and existing byte fixtures; no image rendering.
- `FIGURE_DRAWING_LOCKED` is not lifted by Run acceptance, progress, authorship rights, manuscript-writing permission, a preset theme or a `user_request_ref` field in JSON.
- Output appearance, source-data truth, statistical completeness and permission are separate. `STRUCTURAL_PASS_REVIEW_REQUIRED` is not `FINAL_PASS`.
- Compatible v1 and existing v2 figure contracts remain readable; new research figures may choose `strict-scientific-v1`.

## Remaining limitations (do not advertise as solved)

- No real Matplotlib rendering or final-print-size font/overlap test was authorized, so final visual quality is still unverified.
- Bar/heatmap audits check limited artist geometry/arrays; uncertainty bars, box plots, external axes and temporal event geometry need type-specific review.
- Completeness of a string about uncertainty or missingness does not demonstrate correctness.
- SVG declared paints and fonts do not guarantee physical output color, CVD accessibility or publisher acceptance.
- Export rollback cannot make separate SVG and PNG files atomic across process crashes/power failure.
