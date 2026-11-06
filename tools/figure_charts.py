"""Explicitly requested scientific chart builders for seven layout families.

No side effects on import. All actual plot operations require the original
user's explicit permission to draw the specified image. These helpers do not
load experiments, train, select claims or access any sealed confirmation.
"""
from __future__ import annotations

import math
from numbers import Real

from tools.figure_palette import colormap_spec
from tools.figure_style import semantic_color, semantic_gid
from tools.figure_templates import add_semantic_series, require_drawing_request


def _gate(explicitly_requested: bool, user_request_ref: str):
    require_drawing_request(explicitly_requested=explicitly_requested,
                            user_request_ref=user_request_ref)


def _labels(labels, n: int):
    if not isinstance(labels, (list, tuple)) or len(labels) != n or n == 0:
        raise ValueError("exactly one category label is needed for each value")
    if any(not isinstance(v, str) or not v.strip() for v in labels):
        raise ValueError("category names must be nonempty strings")
    if len(set(labels)) != len(labels):
        raise ValueError("duplicate categories require explicit prior aggregation")


def _values(values, *, name="values"):
    if not isinstance(values, (tuple, list)) or not values:
        raise ValueError(f"{name} must be a nonempty list")
    for v in values:
        if isinstance(v, bool) or not isinstance(v, Real) or not math.isfinite(float(v)):
            raise ValueError(f"{name} contains nonfinite/non-numeric values")
    return [float(v) for v in values]


def _semantic_keys(keys, count: int):
    if not isinstance(keys, (list, tuple)) or len(keys) != count:
        raise ValueError("must provide explicit semantic_key per category")
    if len(set(keys)) != len(keys):
        raise ValueError("semantic keys must not be duplicated within a category figure")


def draw_model_dot(ax, labels, values, semantic_keys, *, theme,
                   explicitly_requested: bool = False, user_request_ref: str = ""):
    """One colored horizontal dot per model, preserving caller's explicit order."""
    _gate(explicitly_requested, user_request_ref)
    vals = _values(values)
    _labels(labels, len(vals))
    _semantic_keys(semantic_keys, len(vals))
    artists = {}
    for i, (label, value, key) in enumerate(zip(labels, vals, semantic_keys)):
        artists[key] = add_semantic_series(ax, [value], [i], theme=theme,
                                           semantic_key=key, kind="scatter", label=label)
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    return artists


def draw_paired_dot(ax, categories, first_values, second_values,
                    first_key, second_key, *, theme, xlabel: str = "",
                    explicitly_requested: bool = False, user_request_ref: str = ""):
    """Matched pairs only: category identity/order must come from verified input."""
    _gate(explicitly_requested, user_request_ref)
    a, b = _values(first_values, name="first_values"), _values(second_values, name="second_values")
    if len(a) != len(b):
        raise ValueError("paired series lengths must match")
    _labels(categories, len(a))
    if first_key == second_key:
        raise ValueError("paired series must use different semantic model keys")
    rows = list(range(len(categories)))
    for i, (left, right) in enumerate(zip(a, b)):
        ax.plot([left, right], [i, i], color="#AAAAAA", linewidth=0.8, zorder=1)
    first = add_semantic_series(ax, a, rows, theme=theme, semantic_key=first_key,
                               kind="scatter", label=first_key.split(":", 1)[-1])
    second = add_semantic_series(ax, b, rows, theme=theme, semantic_key=second_key,
                                kind="scatter", label=second_key.split(":", 1)[-1])
    ax.set_yticks(rows, categories)
    ax.set_xlabel(xlabel)
    ax.invert_yaxis()
    return {first_key: first, second_key: second}


def draw_dumbbell(ax, categories, first_values, second_values, first_key, second_key,
                  *, theme, xlabel: str = "", explicitly_requested: bool = False,
                  user_request_ref: str = ""):
    """Dumbbell uses the same fixed paired layout contract, not a new aesthetic."""
    return draw_paired_dot(ax, categories, first_values, second_values, first_key,
                           second_key, theme=theme, xlabel=xlabel,
                           explicitly_requested=explicitly_requested,
                           user_request_ref=user_request_ref)


def draw_effect_ecdf(ax, effects, *, theme, semantic_key: str,
                     explicitly_requested: bool = False, user_request_ref: str = ""):
    """Empirical CDF of REAL supplied signed effects; no smoothing or interpolation."""
    _gate(explicitly_requested, user_request_ref)
    vals = sorted(_values(effects, name="signed effects"))
    y = [(i + 1) / len(vals) for i in range(len(vals))]
    color = semantic_color(theme, semantic_key)
    line = ax.step(vals, y, where="post", color=color,
                   linewidth=theme["marks"]["line_width_pt"], label=semantic_key.split(":", 1)[-1])[0]
    line.set_gid(semantic_gid(semantic_key))
    ax.axvline(0, color="#666666", linestyle="--", linewidth=0.8)
    ax.set_ylim(0, 1)
    return {semantic_key: line}


def draw_rate_ablation(ax, labels, rates, semantic_keys, *, theme,
                       limits: tuple[float, float] | None = None,
                       explicitly_requested: bool = False, user_request_ref: str = ""):
    """Bar chart from supplied rates; caller is responsible for true denominator.

    Do not infer percentage vs proportion: display unit and limits must be
    explicit in the figure contract. Bars start at zero by design.
    """
    _gate(explicitly_requested, user_request_ref)
    vals = _values(rates, name="rates")
    _labels(labels, len(vals))
    _semantic_keys(semantic_keys, len(vals))
    if any(v < 0 for v in vals):
        raise ValueError("rates cannot be negative; use effect template for signed deltas")
    if limits is not None and (
        len(limits) != 2 or limits[0] != 0 or limits[1] < max(vals)
    ):
        raise ValueError("rate axis must start at zero and include all observed rates")
    artists = {}
    for i, (label, v, key) in enumerate(zip(labels, vals, semantic_keys)):
        rect = ax.bar([i], [v], width=0.7, color=semantic_color(theme, key),
                      edgecolor="#000000", linewidth=0.3)[0]
        rect.set_gid(semantic_gid(key))
        artists[key] = rect
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylim(bottom=0)
    if limits is not None:
        ax.set_ylim(*limits)
    return artists


def validate_timeline_tracks(tracks: dict, theme: dict) -> dict:
    """Non-rendering schema validation: no invented, dropped or reversed events."""
    if not isinstance(tracks, dict) or not tracks:
        raise ValueError("track map is required")
    names = list(tracks)
    if len(names) != len(set(names)):
        raise ValueError("duplicate tracks")
    for name, intervals in tracks.items():
        if not isinstance(name, str) or not isinstance(intervals, list):
            raise ValueError("invalid track format")
        previous_end = -float("inf")
        for item in intervals:
            if not isinstance(item, dict):
                raise ValueError("invalid segment")
            start, end, key = item.get("start"), item.get("end"), item.get("semantic_key")
            if (not isinstance(start, Real) or not isinstance(end, Real)
                    or isinstance(start, bool) or isinstance(end, bool)
                    or not math.isfinite(float(start)) or not math.isfinite(float(end))
                    or end <= start or start < previous_end):
                raise ValueError("invalid/nonmonotonic/non-disjoint segment boundaries")
            semantic_color(theme, key)
            previous_end = end
    return tracks


def draw_timeline_tracks(ax, tracks: dict, *, theme,
                         explicitly_requested: bool = False, user_request_ref: str = ""):
    """Truth/prediction temporal tracks; never smooth, pad or silently merge segments."""
    _gate(explicitly_requested, user_request_ref)
    tracks = validate_timeline_tracks(tracks, theme)
    for j, (name, rows) in enumerate(tracks.items()):
        for item in rows:
            start, end, key = item["start"], item["end"], item["semantic_key"]
            bars = ax.broken_barh([(start, end - start)], (j + 0.12, 0.70),
                                  facecolors=semantic_color(theme, key), edgecolors="none")
            # Multiple occurrences share the *semantic color*, but intentionally
            # do not reuse unique SVG series tags (which denote one plotted group).
            bars.set_gid("track--" + str(j) + "--" + str(start))
    ax.set_yticks([j + 0.47 for j in range(len(tracks))], list(tracks))
    ax.set_ylim(0, len(tracks) + 0.1)
    return ax


def validate_matrix(matrix: list[list[float]], xlabels, ylabels):
    if not isinstance(matrix, list) or not matrix or not all(isinstance(row, list) for row in matrix):
        raise ValueError("matrix must be a nonempty rectangular nested list")
    _labels(ylabels, len(matrix))
    _labels(xlabels, len(matrix[0]))
    if any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("nonrectangular matrix")
    for row in matrix:
        _values(row, name="matrix row")
    return matrix


def draw_heatmap(ax, matrix, xlabels, ylabels, *, palette_name: str = "viridis",
                 palette_kind: str = "sequential", colorbar: bool = True,
                 explicitly_requested: bool = False, user_request_ref: str = ""):
    """Continuous heatmap: scientific semantic colormap, not categorical model colors."""
    _gate(explicitly_requested, user_request_ref)
    validate_matrix(matrix, xlabels, ylabels)
    colormap = colormap_spec(palette_name, palette_kind)
    if colormap["backend"] == "cmcrameri":
        try:
            from cmcrameri import cm
        except ImportError as exc:
            raise RuntimeError("cmcrameri is an optional colormap dependency") from exc
        cmap = getattr(cm, colormap["name"])
    else:
        import matplotlib
        cmap = matplotlib.colormaps[colormap["name"]]
    from matplotlib.colors import Normalize, TwoSlopeNorm
    values = [float(v) for row in matrix for v in row]
    minimum, maximum = min(values), max(values)
    if palette_kind == "diverging":
        # A signed effect must be centered at the scientific neutral point.
        bound = max(abs(minimum), abs(maximum))
        if bound == 0:
            raise ValueError("all-zero effects need an explicit nonzero reference scale")
        norm = TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound)
    elif palette_kind == "cyclic":
        raise ValueError("cyclic phase plots require an explicit domain-specific normalizer")
    else:
        # A uniform matrix has no visual gradient to show; do not fabricate one.
        norm = Normalize(vmin=minimum, vmax=maximum) if minimum != maximum else None
    im = ax.imshow(matrix, interpolation="nearest", cmap=cmap, norm=norm, aspect="auto")
    ax.set_xticks(range(len(xlabels)), xlabels)
    ax.set_yticks(range(len(ylabels)), ylabels)
    if colorbar:
        ax.figure.colorbar(im, ax=ax)
    return im
