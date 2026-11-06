"""Read-only comparison of already-created plot artists with expected series data.

This module creates NO images, executes NO plotting code, and has NO
matplotlib dependency. Agent must independently validate actual source Run,
metric, denominator and sample units; array comparison alone is not science.
"""
from __future__ import annotations

import hashlib
import json
import math
from numbers import Real

from tools.figure_style import semantic_gid


def _native(value):
    if hasattr(value, "tolist"):
        value = value.tolist()
    if hasattr(value, "item") and not isinstance(value, (list, tuple)):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass
    if isinstance(value, (list, tuple)):
        return [_native(x) for x in value]
    if isinstance(value, bool):
        raise ValueError("Boolean coordinates do not establish a numeric metric")
    if isinstance(value, Real):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("Non-finite artist coordinates require separate missing-data handling")
        return number
    if isinstance(value, str):
        return value
    raise ValueError(f"Unsupported artist coordinate type: {type(value).__name__}")


def normalize_xy(x, y) -> dict:
    x, y = _native(x), _native(y)
    if not isinstance(x, list) or not isinstance(y, list) or len(x) != len(y):
        raise ValueError("x/y must be nonempty equal-length arrays")
    if not x:
        raise ValueError("empty plotted series")
    if any(isinstance(v, list) for v in x + y):
        raise ValueError("nested array not accepted for a single line/scatter series")
    return {"x": x, "y": y}


def data_digest(data: dict) -> str:
    normalized = normalize_xy(data["x"], data["y"])
    return hashlib.sha256(json.dumps(normalized, sort_keys=True,
                                     separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def artist_coordinates(artist):
    """Extract actual Line2D/PathCollection coords, not contracts' declarations."""
    if hasattr(artist, "get_xdata") and hasattr(artist, "get_ydata"):
        return normalize_xy(artist.get_xdata(orig=True), artist.get_ydata(orig=True))
    if hasattr(artist, "get_offsets"):
        offsets = _native(artist.get_offsets())
        if not isinstance(offsets, list) or not offsets or any(
            not isinstance(row, list) or len(row) != 2 for row in offsets
        ):
            raise ValueError("unsupported scatter offsets")
        return normalize_xy([row[0] for row in offsets], [row[1] for row in offsets])
    raise ValueError("artist has no supported xy coordinates: bar, heatmap, timeline need dedicated audit")


def audit_artist_coordinates(artists: dict, expected: dict) -> dict:
    """Fail if a labelled artist differs from independently supplied plotting rows.

    expected = {'model:SF': {'x':[...], 'y':[...], 'source_ref':'...', ...}}
    Actual model-to-source alignment still depends on trustworthy expected rows.
    No isolated QA pass can replace raw data/metric verification.
    """
    if not isinstance(artists, dict) or not isinstance(expected, dict) or not expected:
        raise ValueError("nonempty artist and expected mappings required")
    if set(artists) != set(expected):
        raise ValueError("missing or extra semantic plotted series")
    details = []
    for key in sorted(expected):
        artist = artists[key]
        if not hasattr(artist, "get_gid") or artist.get_gid() != semantic_gid(key):
            raise ValueError(f"wrong artist semantic ID for {key}")
        rows = expected[key]
        if not isinstance(rows, dict) or not isinstance(rows.get("source_ref"), str) or not rows["source_ref"]:
            raise ValueError("expected rows must carry real source_ref pointer")
        wanted = normalize_xy(rows["x"], rows["y"])
        observed = artist_coordinates(artist)
        if wanted != observed:
            raise ValueError(f"actual plotted coordinates differ from expected series: {key}")
        details.append({"series": key, "source_ref": rows["source_ref"],
                        "points": len(wanted["x"]), "data_sha256": data_digest(wanted)})
    return {"status": "ARTIST_COORDINATES_MATCH_EXPECTED_ROWS_ONLY",
            "series": details, "scientific_source_verified": False,
            "note": "Not an independent metric, dataset/label, denominator or scientific-confirmation audit"}
