"""Static, read-only scientific figure style contracts; does not draw images.

General baseline can be copied into a project and configured before its first
explicitly requested figure. A fingerprint freezes the *effective* theme,
template and style source. No third-party runtime dependency.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_THEME = ROOT / "styles" / "figure_theme.json"
BASE_MPLSTYLE = ROOT / "styles" / "publication_base.mplstyle"
REGISTRY = ROOT / "templates" / "figure_registry.json"
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
SEMANTIC = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*:[a-zA-Z0-9_-]+$")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _color(value: Any, key: str) -> str:
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError(f"invalid {key}: required #RRGGBB")
    return value.upper()


def validate_theme(theme: dict) -> dict:
    if not isinstance(theme, dict) or theme.get("schema_version") != "figure-theme-v1":
        raise ValueError("figure-theme-v1 required")
    for name in ("theme_version", "style_profile", "font_family"):
        if not isinstance(theme.get(name), str) or not theme[name].strip():
            raise ValueError(f"invalid {name}")
    if _color(theme.get("background"), "background") != "#FFFFFF":
        raise ValueError("figure background must be opaque white")
    if _color(theme.get("text_color"), "text_color") != "#000000":
        raise ValueError("axis/label text must be black")
    sizes = theme.get("font_sizes_pt", {})
    for key in ("axis_title", "ticks", "legend", "annotation"):
        n = sizes.get(key) if isinstance(sizes, dict) else None
        if isinstance(n, bool) or not isinstance(n, (int, float)) or not 5 <= n <= 36:
            raise ValueError(f"invalid font_sizes_pt.{key}")
    canvas = theme.get("canvas", {})
    for key in ("single_width_mm", "double_width_mm", "default_height_mm"):
        n = canvas.get(key) if isinstance(canvas, dict) else None
        if isinstance(n, bool) or not isinstance(n, (int, float)) or not 25 <= n <= 500:
            raise ValueError(f"invalid canvas.{key}")
    if canvas["single_width_mm"] >= canvas["double_width_mm"]:
        raise ValueError("single column must be narrower than double column")
    axes = theme.get("axes", {})
    if not isinstance(axes, dict) or axes.get("arrow_policy") not in ("project_only", "cartesian", "none"):
        raise ValueError("unsupported axes.arrow_policy")
    for key in ("line_width_pt", "tick_width_pt", "tick_length_pt"):
        n = axes.get(key)
        if isinstance(n, bool) or not isinstance(n, (int, float)) or not 0.1 <= n <= 12:
            raise ValueError(f"invalid axes.{key}")
    marks = theme.get("marks", {})
    for key in ("line_width_pt", "marker_size_pt"):
        n = marks.get(key) if isinstance(marks, dict) else None
        if isinstance(n, bool) or not isinstance(n, (float, int)) or not 0.1 <= n <= 25:
            raise ValueError(f"invalid marks.{key}")
    legend = theme.get("legend", {})
    if not isinstance(legend, dict) or legend.get("placement") not in (
        "outside_top", "outside_right", "inside_best", "none"
    ) or not isinstance(legend.get("frame"), bool):
        raise ValueError("invalid legend settings")
    colors = theme.get("colors", {})
    if not isinstance(colors, dict) or not isinstance(colors.get("categorical"), list) or not colors["categorical"]:
        raise ValueError("nonempty categorical palette required")
    for item in colors["categorical"]:
        _color(item, "categorical palette")
    semantic = colors.get("semantic_colors")
    if not isinstance(semantic, dict):
        raise ValueError("colors.semantic_colors dictionary required")
    for name, value in semantic.items():
        if not SEMANTIC.fullmatch(name):
            raise ValueError(f"invalid semantic color key {name!r}")
        _color(value, name)
    return theme


def load_theme(path: Path | None = None) -> dict:
    theme = json.loads((path or BASE_THEME).read_text(encoding="utf-8"))
    return validate_theme(theme)


def load_registry(path: Path | None = None) -> dict:
    registry = json.loads((path or REGISTRY).read_text(encoding="utf-8"))
    if not isinstance(registry, dict) or registry.get("schema_version") != "figure-template-registry-v1":
        raise ValueError("invalid template registry")
    if not isinstance(registry.get("registry_version"), str) or not registry["registry_version"]:
        raise ValueError("registry_version required")
    templates = registry.get("templates")
    if not isinstance(templates, dict) or not templates:
        raise ValueError("templates required")
    for name, template in templates.items():
        if not isinstance(name, str) or not isinstance(template, dict):
            raise ValueError("invalid template entry")
        if template.get("kind") not in ("cartesian", "timeline", "matrix"):
            raise ValueError(f"invalid template kind: {name}")
        if template.get("canvas") not in ("single", "double"):
            raise ValueError(f"invalid canvas type: {name}")
        box = template.get("axes_box")
        if not isinstance(box, list) or len(box) != 4 or any(
            isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 1
            for v in box
        ):
            raise ValueError(f"invalid normalized axes_box: {name}")
        if min(box[2:]) <= 0 or box[0] + box[2] > 1 or box[1] + box[3] > 1:
            raise ValueError(f"axes_box exceeds figure: {name}")
        h = template.get("height_mm")
        if isinstance(h, bool) or not isinstance(h, (float, int)) or not 25 <= h <= 500:
            raise ValueError(f"invalid template height: {name}")
        if template.get("kind") != "cartesian" and template.get("axis_arrows", False):
            raise ValueError("non-cartesian template cannot force Cartesian arrows")
    return registry


def template_spec(template_id: str, registry: dict | None = None) -> dict:
    registry = registry or load_registry()
    if template_id not in registry["templates"]:
        raise ValueError(f"unsupported template_id: {template_id}")
    return registry["templates"][template_id]


def style_fingerprint(theme: dict, template_id: str,
                      registry: dict | None = None,
                      mplstyle_path: Path = BASE_MPLSTYLE) -> str:
    """Sha256 of effective style inputs, not a permission or research credential."""
    validate_theme(theme)
    registry = registry or load_registry()
    item = template_spec(template_id, registry)
    payload = {"theme": theme, "template_id": template_id, "template": item,
               "registry_version": registry["registry_version"],
               "mplstyle_sha256": hashlib.sha256(mplstyle_path.read_bytes()).hexdigest()}
    return hashlib.sha256(_canonical(payload)).hexdigest()


def semantic_gid(key: str) -> str:
    if not SEMANTIC.fullmatch(key):
        raise ValueError("series key must look like model:SF")
    return "series--" + key.replace(":", "--")


def semantic_color(theme: dict, key: str) -> str:
    colors = validate_theme(theme)["colors"]["semantic_colors"]
    if key not in colors:
        raise ValueError(f"semantic color missing for {key!r}; configure project theme first")
    return _color(colors[key], key)


def validate_style_lock(record: dict, project: Path) -> dict:
    """Figure-v2 style evidence check; no images, state mutations or permissions."""
    style = record.get("style")
    if not isinstance(style, dict):
        raise ValueError("v2 style object required")
    theme_ref = style.get("theme_ref")
    if not isinstance(theme_ref, str) or not theme_ref.strip():
        raise ValueError("v2 style.theme_ref required")
    from tools.figure_qa import _local  # import only on invocation; no side effects

    path = _local(project, theme_ref)
    expected_sha = style.get("theme_sha256")
    if not isinstance(expected_sha, str) or not re.fullmatch("[0-9a-fA-F]{64}", expected_sha):
        raise ValueError("valid style.theme_sha256 required")
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha.lower():
        raise ValueError("style theme bytes differ from pinned SHA-256")
    theme = load_theme(path)
    template_id = style.get("template_id")
    fingerprint = style_fingerprint(theme, template_id)
    if not isinstance(style.get("style_fingerprint"), str) or style["style_fingerprint"].lower() != fingerprint:
        raise ValueError("style_fingerprint mismatch: theme, template or .mplstyle changed")
    if style.get("style_profile") != theme["style_profile"]:
        raise ValueError("style_profile differs from theme")
    if style.get("font_family") != theme["font_family"]:
        raise ValueError("font differs from locked theme")
    if style.get("background", "#FFFFFF").upper() != theme["background"].upper():
        raise ValueError("background differs from theme")
    colors = style.get("semantic_colors", {})
    if not isinstance(colors, dict):
        raise ValueError("semantic_colors must be a dictionary")
    for key, color in colors.items():
        if semantic_color(theme, key) != _color(color, key):
            raise ValueError(f"semantic color differs from theme: {key}")
    return {"theme": theme, "template_id": template_id,
            "style_fingerprint": fingerprint, "semantic_colors": colors}
