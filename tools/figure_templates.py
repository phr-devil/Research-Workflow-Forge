"""Opt-in figure-template helpers; imports and static configuration NEVER render.

Only use create_template_figure/export_figure after checking the original
user instruction requesting the exact figures. The boolean/ref are *guards*,
NOT machine-verifiable authorization or permission to access data.
"""
from __future__ import annotations

from pathlib import Path

from tools.figure_style import (
    load_registry, load_theme, semantic_color, semantic_gid, template_spec,
)


def require_drawing_request(*, explicitly_requested: bool, user_request_ref: str) -> None:
    if explicitly_requested is not True or not isinstance(user_request_ref, str) or (
        not user_request_ref.strip() or "REPLACE_" in user_request_ref.upper()
    ):
        raise PermissionError("No image generation without an actual explicit user drawing request")


def create_template_figure(template_id: str, *, explicitly_requested: bool = False,
                           user_request_ref: str = "", theme: dict | None = None,
                           height_mm: float | None = None):
    """Create Matplotlib fig+axes with template geometry ONLY after opt-in.

    Agent is responsible for verifying original user message and scientific
    source. This function does not render/save and must not be called by CI.
    """
    require_drawing_request(explicitly_requested=explicitly_requested, user_request_ref=user_request_ref)
    from tools.figure_style import BASE_MPLSTYLE, validate_theme

    theme = validate_theme(theme or load_theme())
    cfg = template_spec(template_id, load_registry())
    import matplotlib as mpl  # lazy import: no dependency in ordinary research
    from matplotlib.figure import Figure

    width_mm = theme["canvas"]["single_width_mm" if cfg["canvas"] == "single" else "double_width_mm"]
    size_mm = height_mm if height_mm is not None else cfg["height_mm"]
    if isinstance(size_mm, bool) or not isinstance(size_mm, (int, float)) or not 25 <= size_mm <= 500:
        raise ValueError("invalid figure height")
    sz = theme["font_sizes_pt"]
    with mpl.style.context(str(BASE_MPLSTYLE)), mpl.rc_context(rc={
        "figure.facecolor": theme["background"], "axes.facecolor": theme["background"],
        "savefig.facecolor": theme["background"], "savefig.transparent": False,
        "text.color": theme["text_color"], "axes.labelcolor": theme["text_color"],
        "axes.edgecolor": theme["text_color"],
        "xtick.color": theme["text_color"], "ytick.color": theme["text_color"],
        "font.family": theme["font_family"], "font.size": sz["ticks"],
        "axes.labelsize": sz["axis_title"], "xtick.labelsize": sz["ticks"],
        "ytick.labelsize": sz["ticks"], "legend.fontsize": sz["legend"],
        "axes.linewidth": theme["axes"]["line_width_pt"],
        "lines.linewidth": theme["marks"]["line_width_pt"],
        "lines.markersize": theme["marks"]["marker_size_pt"],
        "svg.fonttype": "none", "axes.grid": False,
    }):
        fig = Figure(figsize=(width_mm / 25.4, size_mm / 25.4), facecolor=theme["background"])
        ax = fig.add_axes(cfg["axes_box"])
        ax.set_gid("template--" + template_id)
        ax.set_facecolor(theme["background"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(colors=theme["text_color"], width=theme["axes"]["tick_width_pt"],
                       length=theme["axes"]["tick_length_pt"])
        ax.xaxis.label.set_fontweight("bold")
        ax.yaxis.label.set_fontweight("bold")
        ax.xaxis.label.set_color(theme["text_color"])
        ax.yaxis.label.set_color(theme["text_color"])
        if theme["axes"]["arrow_policy"] == "cartesian" and cfg["kind"] == "cartesian":
            add_cartesian_arrows(ax)
    return fig, ax


def add_semantic_series(ax, x, y, *, theme: dict, semantic_key: str,
                        kind: str = "line", label: str | None = None):
    """Put a stable, inspectable SVG group ID and exact theme color on series."""
    color = semantic_color(theme, semantic_key)
    if kind == "line":
        artist, = ax.plot(x, y, color=color, label=label, linewidth=theme["marks"]["line_width_pt"])
    elif kind == "scatter":
        artist = ax.scatter(x, y, color=color, label=label,
                            s=theme["marks"]["marker_size_pt"] ** 2)
    else:
        raise ValueError("supported semantic series kinds: line, scatter")
    artist.set_gid(semantic_gid(semantic_key))
    return artist


def apply_template_legend(ax, template_id: str, theme: dict):
    """Place legends consistently within a template family, only on a drawn axis."""
    cfg = template_spec(template_id, load_registry())
    placement = cfg.get("legend_slot") or theme["legend"]["placement"]
    if placement == "none":
        return None
    kwargs = {"frameon": theme["legend"]["frame"],
              "fontsize": theme["font_sizes_pt"]["legend"]}
    if placement == "outside_top":
        return ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2, **kwargs)
    if placement == "outside_right":
        return ax.legend(loc="center left", bbox_to_anchor=(1.03, 0.5), **kwargs)
    return ax.legend(loc="best", **kwargs)


def add_cartesian_arrows(ax) -> None:
    """Optional project policy, only meaningful on genuine Cartesian axes."""
    for xy, xytext in (((1.025, 0), (0.965, 0)), ((0, 1.025), (0, 0.965))):
        ax.annotate("", xy=xy, xytext=xytext, xycoords="axes fraction",
                    arrowprops={"arrowstyle": "-|>", "color": "black", "lw": 1.2},
                    annotation_clip=False)


def export_figure(fig, svg: Path, png: Path, *, explicitly_requested: bool = False,
                  user_request_ref: str = "", dpi: int = 600) -> None:
    """Save only explicitly user-requested figures; never overwrite prior versions."""
    require_drawing_request(explicitly_requested=explicitly_requested, user_request_ref=user_request_ref)
    if isinstance(dpi, bool) or not isinstance(dpi, int) or not 72 <= dpi <= 1200:
        raise ValueError("invalid PNG dpi")
    svg, png = Path(svg), Path(png)
    if svg.suffix.lower() != ".svg" or png.suffix.lower() != ".png":
        raise ValueError("output extensions must be svg and png")
    if svg.exists() or png.exists():
        raise FileExistsError("version output paths instead of overwriting existing images")
    if not svg.parent.is_dir() or not png.parent.is_dir():
        raise ValueError("requested output directories must already exist")
    import matplotlib as mpl  # lazy import; drawing request checked above
    # Retain SVG text as text instead of silently converting labels to paths.
    from tools.figure_style import BASE_MPLSTYLE
    with mpl.style.context(str(BASE_MPLSTYLE)), \
         mpl.rc_context(rc={"svg.fonttype": "none", "savefig.transparent": False}):
        fig.savefig(svg, transparent=False, facecolor="#FFFFFF", dpi=dpi)
        fig.savefig(png, transparent=False, facecolor="#FFFFFF", dpi=dpi)
