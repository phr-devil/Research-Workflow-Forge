"""Optional journal-style Matplotlib helpers. Importing this module NEVER renders.

Use figure_session as a context manager only after reading the user's explicit
request to draw these images. Booleans/project files cannot grant permission.
Matplotlib is an optional dependency loaded only on an authorized path.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

from tools.figure_style import (
    BASE_MPLSTYLE, load_registry, load_theme, semantic_color, semantic_gid,
    template_spec, validate_theme,
)


def require_drawing_request(*, explicitly_requested: bool, user_request_ref: str) -> None:
    if explicitly_requested is not True or not isinstance(user_request_ref, str) or (
        not user_request_ref.strip() or "REPLACE_" in user_request_ref.upper()
    ):
        raise PermissionError("No image generation without an actual explicit user drawing request")


def _render_rc(theme: dict) -> dict:
    sz = theme["font_sizes_pt"]
    return {
        "figure.facecolor": theme["background"], "axes.facecolor": theme["background"],
        "savefig.facecolor": theme["background"], "savefig.transparent": False,
        "text.color": theme["text_color"], "axes.labelcolor": theme["text_color"],
        "axes.edgecolor": theme["text_color"], "xtick.color": theme["text_color"],
        "ytick.color": theme["text_color"], "font.family": theme["font_family"],
        "font.size": sz["ticks"], "axes.labelsize": sz["axis_title"],
        "xtick.labelsize": sz["ticks"], "ytick.labelsize": sz["ticks"],
        "legend.fontsize": sz["legend"],
        "axes.linewidth": theme["axes"]["line_width_pt"],
        "lines.linewidth": theme["marks"]["line_width_pt"],
        "lines.markersize": theme["marks"]["marker_size_pt"],
        "xtick.major.width": theme["axes"]["tick_width_pt"],
        "ytick.major.width": theme["axes"]["tick_width_pt"],
        "xtick.major.size": theme["axes"]["tick_length_pt"],
        "ytick.major.size": theme["axes"]["tick_length_pt"],
        "svg.fonttype": "none", "axes.grid": False,
        "axes.labelweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.autolayout": False,
    }


def font_preflight(font_family: str) -> dict:
    """Resolve installed font; missing or substituted fonts cause explicit errors.

    Calls Matplotlib font lookup but NEVER creates any figure.
    """
    from matplotlib import font_manager

    try:
        path = font_manager.findfont(
            font_manager.FontProperties(family=[font_family]), fallback_to_default=False
        )
    except (ValueError, OSError) as exc:
        raise RuntimeError(f"Required project font {font_family!r} unavailable") from exc
    actual = font_manager.FontProperties(fname=path).get_name()
    if actual.casefold() != font_family.casefold():
        raise RuntimeError(f"Font substitution: requested {font_family!r}, got {actual!r}")
    return {"requested": font_family, "resolved": actual, "font_path": path}


def _build_figure(template_id: str, theme: dict, height_mm: float | None = None):
    from matplotlib.figure import Figure

    cfg = template_spec(template_id, load_registry())
    width_mm = theme["canvas"]["single_width_mm" if cfg["canvas"] == "single" else "double_width_mm"]
    size_mm = height_mm if height_mm is not None else cfg["height_mm"]
    if isinstance(size_mm, bool) or not isinstance(size_mm, (int, float)) or not 25 <= size_mm <= 500:
        raise ValueError("invalid figure height")
    fig = Figure(figsize=(width_mm / 25.4, size_mm / 25.4), facecolor=theme["background"])
    fig._rwf_theme = deepcopy(theme)  # Not a permission / scientific receipt.
    fig._rwf_template_id = template_id
    ax = fig.add_axes(cfg["axes_box"])
    _prepare_axis(ax, theme, cfg, panel_id="main")
    return fig, ax


def _prepare_axis(ax, theme: dict, template: dict, *, panel_id: str) -> None:
    """Centralized axis styling for single charts and aligned multi-panel charts."""
    ax.set_facecolor(theme["background"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=theme["text_color"], width=theme["axes"]["tick_width_pt"],
                   length=theme["axes"]["tick_length_pt"])
    for label in (ax.xaxis.label, ax.yaxis.label):
        label.set_fontweight("bold")
        label.set_color(theme["text_color"])
    if theme["axes"]["arrow_policy"] == "cartesian" and template["kind"] == "cartesian":
        add_cartesian_arrows(ax, line_width=theme["axes"]["line_width_pt"], panel_id=panel_id)


@contextmanager
def figure_session(template_id: str, *, explicitly_requested: bool = False,
                   user_request_ref: str = "", theme: dict | None = None,
                   height_mm: float | None = None):
    """Hold theme across ALL artist creation, legends and export.

    This corrects the old behavior where rc_context ended at canvas creation.
    The caller is responsible for verifying the actual original user message.
    """
    require_drawing_request(explicitly_requested=explicitly_requested, user_request_ref=user_request_ref)
    import matplotlib as mpl  # lazy; never triggered by ordinary research or CI
    import matplotlib.style as mplstyle

    theme = validate_theme(deepcopy(theme) if theme is not None else load_theme())
    with mplstyle.context(str(BASE_MPLSTYLE)), mpl.rc_context(rc=_render_rc(theme)):
        font_preflight(theme["font_family"])
        yield _build_figure(template_id, theme, height_mm)


def create_template_figure(template_id: str, *, explicitly_requested: bool = False,
                           user_request_ref: str = "", theme: dict | None = None,
                           height_mm: float | None = None):
    """Legacy constructor; new code should use figure_session for full style scope.

    Previously-created artists preserve their configured style, but late-added
    text/legend may inherit caller globals once this temporary context ends.
    """
    with figure_session(template_id, explicitly_requested=explicitly_requested,
                        user_request_ref=user_request_ref, theme=theme,
                        height_mm=height_mm) as pair:
        return pair


def add_semantic_series(ax, x, y, *, theme: dict, semantic_key: str,
                        kind: str = "line", label: str | None = None,
                        marker: str | None = None):
    """Use a stable SVG semantic ID and the exact project-defined series color."""
    color = semantic_color(theme, semantic_key)
    if kind == "line":
        artist, = ax.plot(x, y, color=color, label=label,
                          linewidth=theme["marks"]["line_width_pt"], marker=marker)
    elif kind == "scatter":
        artist = ax.scatter(x, y, color=color, label=label,
                            s=theme["marks"]["marker_size_pt"] ** 2, marker=marker or "o")
    else:
        raise ValueError("supported semantic series kinds: line, scatter")
    artist.set_gid(semantic_gid(semantic_key))
    return artist


def apply_template_legend(ax, template_id: str, theme: dict):
    """Stable legend slot; no automatic reordering or guessed positions."""
    cfg = template_spec(template_id, load_registry())
    placement = cfg.get("legend_slot") or theme["legend"]["placement"]
    handles, labels = ax.get_legend_handles_labels()
    if not labels or placement == "none":
        return None
    opts = {"frameon": theme["legend"]["frame"],
            "fontsize": theme["font_sizes_pt"]["legend"]}
    if placement == "outside_top":
        return ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2, **opts)
    if placement == "outside_right":
        return ax.legend(loc="center left", bbox_to_anchor=(1.03, 0.5), **opts)
    return ax.legend(loc="best", **opts)


def add_cartesian_arrows(ax, *, line_width: float = 1.2,
                         panel_id: str = "main") -> None:
    """Arrowheads continue the bottom/left spines (not a second full-length axis)."""
    for axis, xy, xytext in (
        ("x", (1.025, 0), (0.972, 0)),
        ("y", (0, 1.025), (0, 0.972)),
    ):
        annotation = ax.annotate(
            "", xy=xy, xytext=xytext, xycoords="axes fraction",
            arrowprops={"arrowstyle": "-|>", "color": "black", "lw": line_width,
                        "mutation_scale": 9, "shrinkA": 0, "shrinkB": 0},
            annotation_clip=False,
        )
        annotation.set_gid(f"axis-arrow-{axis}--{panel_id}")


@contextmanager
def aligned_panel_session(template_id: str, *, rows: int, cols: int,
                          explicitly_requested: bool = False, user_request_ref: str = "",
                          theme: dict | None = None, height_mm: float | None = None,
                          wspace: float = 0.30, hspace: float = 0.35):
    """Create exactly aligned data-area grids; returns (Figure, rows x columns Axes).

    For heterogeneous chart types use separate suitable axes/templates instead.
    This is request-gated, like figure_session, and does not create a preview.
    """
    require_drawing_request(explicitly_requested=explicitly_requested, user_request_ref=user_request_ref)
    for name, value in (("rows", rows), ("cols", cols)):
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 8:
            raise ValueError(f"{name} must be an integer in 1..8")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or
           not 0 <= value <= 2 for value in (wspace, hspace)):
        raise ValueError("invalid grid spacing")
    with figure_session(template_id, explicitly_requested=explicitly_requested,
                        user_request_ref=user_request_ref, theme=theme,
                        height_mm=height_mm) as (fig, initial_ax):
        initial_ax.remove()
        template = template_spec(template_id, load_registry())
        x, y, width, height = template["axes_box"]
        grid = fig.add_gridspec(rows, cols, left=x, right=x + width,
                                bottom=y, top=y + height, wspace=wspace, hspace=hspace)
        axes = []
        for r in range(rows):
            current = []
            for c in range(cols):
                ax = fig.add_subplot(grid[r, c])
                panel_id = f"r{r}c{c}"
                ax.set_gid("panel--" + panel_id)
                _prepare_axis(ax, theme if theme is not None else fig._rwf_theme,
                              template, panel_id=panel_id)
                current.append(ax)
            axes.append(current)
        fig._rwf_panel_axes = axes
        fig.align_labels([ax for row in axes for ax in row])
        yield fig, axes


def add_panel_label(ax, letter: str) -> None:
    """Consistent panel-label anchor; keeps labels out of the plotting data area."""
    if not isinstance(letter, str) or not letter or len(letter) > 3:
        raise ValueError("panel label must be a short letter/id")
    artist = ax.text(-0.11, 1.03, f"({letter})", transform=ax.transAxes,
                     fontsize=10, fontweight="bold", ha="left", va="bottom")
    artist.set_gid("panel-label--" + letter)


def allow_observation_points(ax, *, source_ref: str, scientific_reason: str) -> None:
    """An explicit, auditable exception for actual independent observations.

    Never authorize a purely decorative second encoding of colored bars.
    """
    if (not isinstance(source_ref, str) or not source_ref.strip() or
        not isinstance(scientific_reason, str) or len(scientific_reason.strip()) < 12):
        raise ValueError("independent-observation source and scientific reason required")
    ax._rwf_bar_point_exception = {
        "source_ref": source_ref.strip(), "scientific_reason": scientific_reason.strip()}


def audit_publication_format(fig) -> dict:
    """Read existing artist/axes structure before export, no rendering or source verification.

    Only the explicitly selected PD-RW publication profile is strict. Legacy
    and independently frozen project themes remain unchanged.
    """
    theme = getattr(fig, "_rwf_theme", None) or {}
    if theme.get("style_profile") != "PD_RW_PUBLICATION":
        return {"status": "NOT_APPLICABLE_LEGACY_PROFILE"}
    template_id = getattr(fig, "_rwf_template_id", None)
    if template_id is None:
        raise ValueError("missing figure template ID")
    cfg = template_spec(template_id, load_registry())
    panels = getattr(fig, "_rwf_panel_axes", None)
    axes = [ax for row in panels for ax in row] if panels else list(fig.axes)
    if not axes:
        raise ValueError("no plot axes")
    arrow_count = 0
    for i, ax in enumerate(axes):
        panel_id = next((f"r{r}c{c}" for r, row in enumerate(panels or [])
                         for c, item in enumerate(row) if item is ax), "main")
        if cfg["kind"] == "cartesian":
            expected = {f"axis-arrow-{name}--{panel_id}" for name in ("x", "y")}
            actual = {a.get_gid() for a in ax.texts if hasattr(a, "get_gid")}
            if not expected.issubset(actual):
                raise ValueError(f"Cartesian axis arrows missing in {panel_id}")
            arrow_count += 2
        has_bars = any(getattr(container, "patches", None) for container in ax.containers)
        if not has_bars:
            continue
        # Marker artists from real error bars are not decorative overlay points.
        caplines = {id(cap) for container in ax.containers
                    if container.__class__.__name__ == "ErrorbarContainer"
                    for cap in (container.lines[1] if getattr(container, "lines", None) else ())}
        scatter = any(item.__class__.__name__ == "PathCollection" for item in ax.collections)
        lines = any(id(line) not in caplines and
                    str(line.get_marker()).lower() not in ("none", "", " ", "null")
                    for line in ax.lines)
        if (scatter or lines) and not getattr(ax, "_rwf_bar_point_exception", None):
            raise ValueError(f"redundant point markers over colored bars in {panel_id}")
    if panels:
        tolerance = 1e-6
        for row in panels:
            positions = [ax.get_position().bounds for ax in row]
            if any(abs(p[1] - positions[0][1]) > tolerance or
                   abs(p[3] - positions[0][3]) > tolerance for p in positions[1:]):
                raise ValueError("panel row axes are not aligned")
        for c in range(len(panels[0])):
            positions = [row[c].get_position().bounds for row in panels]
            if any(abs(p[0] - positions[0][0]) > tolerance or
                   abs(p[2] - positions[0][2]) > tolerance for p in positions[1:]):
                raise ValueError("panel column axes are not aligned")
    return {"status": "ARTIST_GEOMETRY_CHECKED_NOT_VISUAL_QA",
            "axes": len(axes), "axis_arrow_objects": arrow_count,
            "panel_grid": [len(panels), len(panels[0])] if panels else None,
            "source_data_verified": False}



def export_figure(fig, svg: Path, png: Path, *, explicitly_requested: bool = False,
                  user_request_ref: str = "", dpi: int = 600) -> None:
    """Requested-only export; never overwrite, never silently crop physical canvas."""
    require_drawing_request(explicitly_requested=explicitly_requested, user_request_ref=user_request_ref)
    if isinstance(dpi, bool) or not isinstance(dpi, int) or not 72 <= dpi <= 1200:
        raise ValueError("invalid PNG dpi")
    svg, png = Path(svg), Path(png)
    if svg.suffix.lower() != ".svg" or png.suffix.lower() != ".png":
        raise ValueError("output extensions must be svg and png")
    if svg.exists() or png.exists():
        raise FileExistsError("Version output paths rather than overwriting old images")
    if not svg.parent.is_dir() or not png.parent.is_dir():
        raise ValueError("Requested output directories must already exist")
    import matplotlib as mpl
    import matplotlib.style as mplstyle

    theme = validate_theme(getattr(fig, "_rwf_theme", None) or load_theme())
    audit_publication_format(fig)  # fail before writing either output; not visual/science QA
    # Prepare both exports before touching either destination. The two final
    # filenames are reserved with 'xb': no silent clobber and no stale lone SVG
    # if PNG rendering or writing fails. This occurs ONLY on authorized drawing.
    from io import BytesIO

    with mplstyle.context(str(BASE_MPLSTYLE)), mpl.rc_context(rc=_render_rc(theme)):
        font_preflight(theme["font_family"])
        svg_bytes, png_bytes = BytesIO(), BytesIO()
        fig.savefig(svg_bytes, format="svg", transparent=False, facecolor="#FFFFFF", dpi=dpi)
        fig.savefig(png_bytes, format="png", transparent=False, facecolor="#FFFFFF", dpi=dpi)
    _write_pair_exclusive([(svg, svg_bytes.getvalue()), (png, png_bytes.getvalue())])


def _write_pair_exclusive(outputs: list[tuple[Path, bytes]]) -> None:
    """Best-effort all-or-clean rollback for output files; no plotting or imports.

    File creation is exclusive even under concurrent runs. A power loss is not
    transactional, so users must still verify the complete output pair.
    """
    created: list[Path] = []
    try:
        for path, payload in outputs:
            path = Path(path)
            if not isinstance(payload, bytes) or not payload:
                raise ValueError("empty or invalid rendered output payload")
            with path.open("xb") as stream:
                created.append(path)
                stream.write(payload)
    except BaseException:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise


def rendering_environment_receipt(fig, *, explicitly_requested: bool = False,
                                  user_request_ref: str = "") -> dict:
    """Non-image metadata for a figure that the user explicitly requested.

    Records environment/version and font facts; no source science or user
    authorization is proven by this receipt. Only invoke within the already
    authorized plotting task, never as a CI image-generation prerequisite.
    """
    require_drawing_request(explicitly_requested=explicitly_requested, user_request_ref=user_request_ref)
    import hashlib
    import platform
    import matplotlib
    from tools.figure_style import REGISTRY, style_fingerprint

    theme = validate_theme(getattr(fig, "_rwf_theme", None) or load_theme())
    template_id = getattr(fig, "_rwf_template_id", None)
    if template_id is None:
        raise ValueError("figure template ID not stored; use figure_session")
    font = font_preflight(theme["font_family"])
    files = [Path(__file__), Path(__file__).with_name("figure_style.py"),
             Path(__file__).with_name("figure_charts.py")]
    return {
        "theme_version": theme["theme_version"],
        "palette_id": theme["colors"].get("palette_id", "LEGACY_UNPINNED"),
        "template_id": template_id,
        "template_registry_sha256": hashlib.sha256(REGISTRY.read_bytes()).hexdigest(),
        "style_fingerprint": style_fingerprint(theme, template_id),
        "matplotlib_version": matplotlib.__version__,
        "python_version": platform.python_version(),
        "font_family_requested": font["requested"],
        "font_family_resolved": font["resolved"],
        "plot_helper_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "status": "RENDER_ENV_METADATA_ONLY",
        "science_verified": False,
    }
