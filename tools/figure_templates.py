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
        add_cartesian_arrows(ax, line_width=theme["axes"]["line_width_pt"])
    return fig, ax


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


def add_cartesian_arrows(ax, *, line_width: float = 1.2) -> None:
    """Only on genuine Cartesian axes; not on timelines or heatmaps."""
    for xy, xytext in (((1.02, 0), (0.97, 0)), ((0, 1.02), (0, 0.97))):
        ax.annotate("", xy=xy, xytext=xytext, xycoords="axes fraction",
                    arrowprops={"arrowstyle": "-|>", "color": "black", "lw": line_width},
                    annotation_clip=False)


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
