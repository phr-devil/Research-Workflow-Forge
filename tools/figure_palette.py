"""Read-only research palette registry and non-rendering color checks.

No plotting libraries are imported. Contrast thresholds are *advisory* for
thin/small non-text elements; do not mistake them for color-blindness testing.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTES = ROOT / "styles" / "palette_registry.json"
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
SEMANTIC = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*:[a-zA-Z0-9_-]+$")


def _hex(value: str) -> str:
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError("color must be a six-digit #RRGGBB hex")
    return value.upper()


def load_palettes(path: Path | None = None) -> dict:
    registry = json.loads((path or PALETTES).read_text(encoding="utf-8"))
    if not isinstance(registry, dict) or registry.get("schema_version") != "figure-palette-registry-v1":
        raise ValueError("invalid palette registry schema")
    if not isinstance(registry.get("registry_version"), str) or not registry["registry_version"]:
        raise ValueError("missing palette registry version")
    categorical = registry.get("categorical")
    if not isinstance(categorical, dict) or not categorical:
        raise ValueError("missing categorical palettes")
    for key, entry in categorical.items():
        colors = entry.get("colors") if isinstance(entry, dict) else None
        if not isinstance(colors, list) or not colors:
            raise ValueError(f"empty palette {key!r}")
        normalized = [_hex(c) for c in colors]
        if len(set(normalized)) != len(normalized):
            raise ValueError(f"duplicate colors in palette {key!r}")
    for key in ("existing_default", "recommended_new_project"):
        if registry.get(key) not in categorical:
            raise ValueError(f"unknown {key}")
    for entry in (registry.get("accents") or {}).get("colors", []):
        _hex(entry)
    continuous = registry.get("continuous")
    if not isinstance(continuous, dict):
        raise ValueError("missing continuous colormaps")
    for name, item in continuous.items():
        if item.get("kind") not in ("sequential", "diverging", "cyclic") or item.get("backend") not in ("matplotlib", "cmcrameri"):
            raise ValueError(f"invalid continuous colormap: {name}")
    return registry


def palette_colors(palette_id: str, registry: dict | None = None) -> list[str]:
    registry = registry or load_palettes()
    entry = registry["categorical"].get(palette_id)
    if entry is None:
        raise ValueError(f"unknown categorical palette: {palette_id}")
    return [_hex(c) for c in entry["colors"]]


def validate_theme_palette(colors: dict, registry: dict | None = None) -> None:
    """Legacy themes without palette_id remain valid, never silently migrated."""
    if not isinstance(colors, dict):
        raise ValueError("colors must be an object")
    palette_id = colors.get("palette_id")
    if palette_id is None:
        return  # backwards compatibility, no implicit reassignment
    registry = registry or load_palettes()
    if palette_id != "custom":
        if colors.get("palette_registry_version") != registry["registry_version"]:
            raise ValueError("palette registry version differs from project lock")
        expected = palette_colors(palette_id, registry)
        actual = [_hex(c) for c in colors.get("categorical", [])]
        if actual != expected:
            raise ValueError("categorical colors differ from selected palette")
    elif not colors.get("palette_registry_version"):
        raise ValueError("custom palette requires versioned project registry identifier")
    accents = colors.get("accents", [])
    if not isinstance(accents, list) or any(not HEX.fullmatch(str(c)) for c in accents):
        raise ValueError("invalid accents")
    # Semantic keys are project-specific and can intentionally use a highlight color.
    # Never silently recolor them just because a preset has been selected.


def white_contrast(color: str) -> float:
    """Relative contrast (#FFFFFF / #RRGGBB), sRGB linearized luminance."""
    color = _hex(color)
    rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb]
    luminance = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    return 1.05 / (luminance + 0.05)


def palette_diagnostics(colors: list[str], *, thin_mark_threshold: float = 3.0) -> dict:
    if not isinstance(colors, list):
        raise ValueError("expected colors array")
    rows = []
    for c in colors:
        ratio = white_contrast(c)
        rows.append({"color": _hex(c), "contrast_on_white": round(ratio, 2),
                     "risk": "LOW_CONTRAST_SMALL_MARK" if ratio < thin_mark_threshold else "NO_WHITE_CONTRAST_WARNING"})
    return {"colors": rows,
            "warnings": [f"{row['color']}: {row['contrast_on_white']}:1 on white; use thicker marks/outline or another color"
                         for row in rows if row["risk"] == "LOW_CONTRAST_SMALL_MARK"],
            "note": "Only background contrast assessed; not a color-vision, grayscale, or final visual QA certification"}


def assign_semantic_colors(keys: list[str], palette_id: str, *,
                           existing: dict[str, str] | None = None) -> dict[str, str]:
    """Explicit project-configuration helper: preserve previous keys and colors.

    Never infer keys from bar order, overwrite old mappings, or allow silent reuse
    after a palette's discrete colors have been exhausted. Creates NO images.
    """
    if not isinstance(keys, list) or len(keys) != len(set(keys)):
        raise ValueError("keys must be a unique list")
    if any(not isinstance(k, str) or not SEMANTIC.fullmatch(k) for k in keys):
        raise ValueError("semantic keys must be type:value, e.g. model:SF")
    palette = palette_colors(palette_id)
    mapped = dict(existing or {})
    if any(not isinstance(k, str) or not SEMANTIC.fullmatch(k) for k in mapped):
        raise ValueError("invalid existing semantic key")
    for value in mapped.values():
        _hex(value)
    occupied = {v.upper() for v in mapped.values()}
    remaining = [v for v in palette if v.upper() not in occupied]
    for key in keys:
        if key not in mapped:
            if not remaining:
                raise ValueError("palette exhausted: select a larger palette or explicitly define semantic colors")
            mapped[key] = remaining.pop(0)
    return mapped


def colormap_spec(name: str, purpose: str) -> dict:
    """Check semantic match, but do not import or render any color map."""
    registry = load_palettes()
    entry = registry["continuous"].get(name)
    if entry is None or entry["kind"] != purpose:
        raise ValueError("colormap must match sequential, diverging, or cyclic data semantics")
    return dict(entry)
