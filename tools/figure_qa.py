"""Read-only structural QA for explicitly user-requested, already-created figures.

No image generation, plotting code execution, or authorization/science attestation.
Python >=3.10, standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
DIM = re.compile(r"^([0-9.]+)(pt|px|in|mm|cm)$")
SVG_PAINT = re.compile(r"#[0-9a-fA-F]{6}\b")


def _local(root: Path, rel: str) -> Path:
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        raise ValueError("missing or absolute artifact path")
    path = (root / rel).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"artifact not found within project: {rel}")
    return path


def _verify_hash(root: Path, record: dict) -> None:
    if not isinstance(record, dict) or not SHA256.fullmatch(str(record.get("sha256", ""))):
        raise ValueError("missing/invalid source SHA-256")
    path = _local(root, record.get("path"))
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != record["sha256"].lower():
        raise ValueError(f"source SHA-256 mismatch: {record['path']}")


def _inch(value: str) -> float:
    match = DIM.fullmatch(str(value))
    if not match:
        raise ValueError(f"unsupported SVG dimension: {value}")
    num, unit = float(match[1]), match[2]
    return num * {"pt": 1 / 72, "px": 1 / 96, "in": 1, "mm": 1 / 25.4, "cm": 1 / 2.54}[unit]


def _safe_svg_xml(raw: bytes) -> bytes:
    """Allow only Matplotlib's fixed SVG 1.1 PUBLIC DTD; never resolve entities."""
    if b"<!ENTITY" in raw.upper():
        raise ValueError("SVG entity declarations prohibited")
    # Matplotlib's SVG backend includes this harmless standard prolog.
    fixed = re.compile(
        rb'<!DOCTYPE\s+svg\s+PUBLIC\s+"-//W3C//DTD SVG 1\.1//EN"\s+'
        rb'"http://www\.w3\.org/Graphics/SVG/1\.1/DTD/svg11\.dtd"\s*>',
        flags=re.IGNORECASE,
    )
    cleaned = fixed.sub(b"", raw)
    if b"<!DOCTYPE" in cleaned.upper():
        raise ValueError("unrecognized SVG DOCTYPE prohibited")
    return cleaned


def _svg_size(path: Path) -> tuple[float, float]:
    root = ET.fromstring(_safe_svg_xml(path.read_bytes()))
    if root.tag.split("}")[-1] != "svg":
        raise ValueError("SVG root element missing")
    w, h = _inch(root.get("width", "")), _inch(root.get("height", ""))
    if min(w, h) <= 0:
        raise ValueError("SVG has nonpositive size")
    return w, h


def _png_info(path: Path) -> tuple[int, int, tuple[float, float] | None]:
    width = height = None
    dpi = None
    done = False
    with path.open("rb") as f:
        if f.read(8) != PNG_MAGIC:
            raise ValueError("invalid PNG signature")
        while True:
            hdr = f.read(8)
            if len(hdr) != 8:
                break
            count, kind = struct.unpack(">I4s", hdr)
            if count > 200_000_000:
                raise ValueError("oversized PNG chunk")
            crc = zlib.crc32(kind)
            buf = bytearray()
            remaining = count
            while remaining:
                part = f.read(min(remaining, 1024 * 1024))
                if not part:
                    raise ValueError("truncated PNG data")
                crc = zlib.crc32(part, crc)
                if kind in (b"IHDR", b"pHYs"):
                    buf.extend(part)
                remaining -= len(part)
            stored = f.read(4)
            if len(stored) != 4 or struct.unpack(">I", stored)[0] != crc & 0xFFFFFFFF:
                raise ValueError("PNG CRC mismatch/truncation")
            if kind == b"IHDR":
                if count != 13:
                    raise ValueError("invalid IHDR length")
                width, height = struct.unpack(">II", buf[:8])
            elif kind == b"pHYs" and count == 9:
                x, y, unit = struct.unpack(">IIB", buf)
                if unit == 1:
                    dpi = (x * 0.0254, y * 0.0254)
            elif kind == b"IEND":
                done = True
                break
    if not done or not width or not height:
        raise ValueError("incomplete PNG")
    return width, height, dpi


def inspect_svg_semantic_paints(svg_xml: bytes, expected: dict[str, str]) -> dict[str, list[str]]:
    """Inspect *actual SVG-tagged artists*, not just expected palette metadata.

    Each artist from tools.figure_templates.add_semantic_series has gid
    series--model--SF etc. Only six-digit literal paints can be proven by
    this structural test; inherited/CSS paints and data correctness require
    separate inspection. No SVG/image creation.
    """
    from tools.figure_style import semantic_gid
    root = ET.fromstring(_safe_svg_xml(svg_xml))
    result = {}
    for semantic_key, specified in expected.items():
        tag = semantic_gid(semantic_key)
        matching = [node for node in root.iter() if node.attrib.get("id") == tag]
        if len(matching) != 1:
            raise ValueError(f"semantic SVG artist group missing/duplicated: {tag}")
        group = matching[0]
        observed = set()
        for node in group.iter():
            for attr in ("style", "fill", "stroke"):
                value = node.attrib.get(attr, "")
                observed.update(color.upper() for color in SVG_PAINT.findall(value))
        target = specified.upper()
        if target not in observed:
            raise ValueError(f"actual SVG paint mismatch: {semantic_key}, expected {target}, observed {sorted(observed)}")
        result[semantic_key] = sorted(observed)
    return result


def inspect_svg_typography(svg_xml: bytes, expected_family: str) -> dict:
    """Inspect explicit SVG text font/fill declarations; not OS font substitution."""
    root = ET.fromstring(_safe_svg_xml(svg_xml))
    text_nodes = [el for el in root.iter() if el.tag.split("}")[-1] == "text"]
    checked = 0
    for el in text_nodes:
        style = el.attrib.get("style", "")
        family = el.attrib.get("font-family", "") or el.attrib.get("font", "")
        if family and expected_family.lower() not in family.lower():
            raise ValueError(f"actual SVG text font mismatch: {family!r}")
        if ("font:" in style or "font-family:" in style):
            if expected_family.lower() not in style.lower():
                raise ValueError(f"actual SVG font style differs from locked family: {style!r}")
            checked += 1
        colors = []
        if "fill" in el.attrib:
            colors += SVG_PAINT.findall(el.attrib["fill"])
        fill_rule = re.search(r"(?:^|;)\s*fill\s*:\s*(#[0-9A-Fa-f]{6})\b", style)
        if fill_rule:
            colors.append(fill_rule.group(1))
        if any(color.upper() != "#000000" for color in colors):
            raise ValueError("non-black SVG text fill under locked theme")
    return {"text_elements": len(text_nodes), "explicit_font_checks": checked,
            "note": "Font metadata only; actual font rendering/substitution requires visual inspection"}


def inspect_svg_publication_arrows(svg_xml: bytes, *, template_kind: str,
                                   panel_grid: dict | None = None) -> dict:
    """Verify exported SVG axis-arrow *paths*, not just requested theme JSON.

    In matplotlib, an empty Annotation's Text.draw emits no SVG group; arrow
    patch needs its own gid. Counts and panel tags are structural only and do
    not prove visible placement or lack of clipping.
    """
    root = ET.fromstring(_safe_svg_xml(svg_xml))
    ids = {node.attrib.get("id") for node in root.iter() if node.attrib.get("id")}
    if panel_grid is None:
        panel_ids = ["main"]
    else:
        if not isinstance(panel_grid, dict):
            raise ValueError("style.panel_grid must be an object")
        rows, cols = panel_grid.get("rows"), panel_grid.get("cols")
        if any(isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 8
               for n in (rows, cols)):
            raise ValueError("style.panel_grid rows/cols must be 1..8 integers")
        panel_ids = [f"r{r}c{c}" for r in range(rows) for c in range(cols)]
        for panel_id in panel_ids[1:]:
            if "panel--" + panel_id not in ids:
                raise ValueError("SVG missing panel group: " + panel_id)
        if len(panel_ids) > 1:
            labels = [x for x in ids if x.startswith("panel-label--")]
            if len(labels) != len(panel_ids):
                raise ValueError("SVG missing/duplicated panel labels")
    if template_kind == "cartesian":
        missing = [f"axis-arrow-{axis}--{panel_id}" for panel_id in panel_ids
                   for axis in ("x", "y")
                   if f"axis-arrow-{axis}--{panel_id}" not in ids]
        if missing:
            raise ValueError("SVG missing Cartesian arrow path groups: " + ", ".join(missing))
    return {"panel_count": len(panel_ids),
            "cartesian_arrow_paths": 2 * len(panel_ids) if template_kind == "cartesian" else 0,
            "not_visual_geometry_verified": True}


def _check_one(root: Path, record: dict) -> tuple[dict, dict]:
    version = record.get("schema_version")
    if version not in ("figure-v1", "figure-v2"):
        raise ValueError("figure-v1 or figure-v2 schema required")
    figure_id = record.get("figure_id")
    if not isinstance(figure_id, str) or not figure_id.strip():
        raise ValueError("figure_id required")
    if record.get("figure_kind") not in ("DIAGNOSTIC", "EVIDENCE", "PUBLICATION"):
        raise ValueError("invalid figure_kind")
    ref = record.get("user_request_ref")
    if not isinstance(ref, str) or not ref.strip() or "REPLACE_" in ref.upper():
        raise ValueError("original user figure-request reference missing (not proof of authorization)")
    sources = record.get("source_artifacts")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source_artifacts required")
    for item in sources:
        if not isinstance(item, dict) or not isinstance(item.get("role", ""), str):
            raise ValueError("invalid source artifact record")
        if item.get("role", "").upper() in ("SEALED", "CONFIRMATION"):
            raise ValueError("direct sealed/confirmation sources not accepted by generic QA")
        _verify_hash(root, item)
    if record.get("figure_type", "data") == "data":
        _verify_hash(root, record.get("plot_data"))
    outputs = record.get("outputs", {})
    svg = _local(root, outputs.get("svg"))
    png = _local(root, outputs.get("png"))
    if svg.suffix.lower() != ".svg" or png.suffix.lower() != ".png":
        raise ValueError("SVG and PNG output paths required")
    sw, sh = _svg_size(svg)
    pw, ph, dpi = _png_info(png)
    style = record.get("style") or {}
    canvas = style.get("canvas_inches")
    if canvas is not None:
        if not isinstance(canvas, list) or len(canvas) != 2 or any(not isinstance(v, (float, int)) or v <= 0 for v in canvas):
            raise ValueError("invalid canvas_inches")
        if max(abs(sw - canvas[0]), abs(sh - canvas[1])) > 0.01:
            raise ValueError("SVG canvas_inches mismatch")
    target_dpi = style.get("png_dpi")
    if target_dpi is not None:
        if not isinstance(target_dpi, (int, float)) or target_dpi <= 0:
            raise ValueError("invalid png_dpi")
        if dpi is None or max(abs(x - target_dpi) for x in dpi) > 0.25:
            raise ValueError("PNG dpi metadata absent/inconsistent")
        if max(abs(pw - sw * target_dpi), abs(ph - sh * target_dpi)) > 2.0:
            raise ValueError("SVG/PNG canvas dimensions differ")
    elif dpi is not None:
        if max(abs(pw - sw * dpi[0]), abs(ph - sh * dpi[1])) > 2.0:
            raise ValueError("SVG/PNG dimensions differ")
    colors = style.get("semantic_colors", {})
    if not isinstance(colors, dict) or any(not isinstance(k, str) or not HEX.fullmatch(v or "") for k, v in colors.items()):
        raise ValueError("invalid semantic_colors")
    group = style.get("comparison_group")
    axes = style.get("axis_limits")
    if group and (not isinstance(axes, dict) or not axes or canvas is None):
        raise ValueError("comparison_group requires axis_limits and canvas_inches")
    background = style.get("background", "#FFFFFF")
    if not isinstance(background, str) or not HEX.fullmatch(background):
        raise ValueError("invalid declared background color")
    lock = None
    observed_paints = {}
    typography = None
    palette_report = None
    publication_format = None
    if version == "figure-v2":
        from tools.figure_style import validate_style_lock

        lock = validate_style_lock(record, root)
        from tools.figure_palette import palette_diagnostics

        palette_report = {
            "palette_id": lock["theme"]["colors"].get("palette_id", "LEGACY_UNPINNED"),
            "palette_registry_version": lock["theme"]["colors"].get("palette_registry_version"),
            # Checks colors actually declared for this figure, not every unused swatch.
            **palette_diagnostics(list(colors.values())),
        }
        svg_content = svg.read_bytes()
        xml = ET.fromstring(_safe_svg_xml(svg_content))
        expected_template_gid = "template--" + lock["template_id"]
        if not any(node.attrib.get("id") == expected_template_gid for node in xml.iter()):
            raise ValueError("SVG lacks tagged template group: " + expected_template_gid)
        # Tagged series paint checks inspect the *exported* SVG rather than style declarations alone.
        if colors:
            observed_paints = inspect_svg_semantic_paints(svg_content, colors)
        typography = inspect_svg_typography(svg_content, lock["theme"]["font_family"])
        if (lock["theme"]["style_profile"] == "PD_RW_PUBLICATION" and
                record.get("figure_kind") == "PUBLICATION" and
                record.get("figure_type", "data") == "data"):
            from tools.figure_style import template_spec
            kind = template_spec(lock["template_id"])["kind"]
            publication_format = inspect_svg_publication_arrows(
                svg_content, template_kind=kind,
                panel_grid=style.get("panel_grid"))
        if record.get("figure_kind") == "PUBLICATION" and record.get("figure_type", "data") == "data":
            if not typography["text_elements"]:
                raise ValueError("v2 publication data SVG has no editable text labels")
        if style.get("comparison_group") and not style.get("axis_limits"):
            raise ValueError("v2 comparison group requires explicit comparable axis limits")
    from tools.figure_evidence import enforce_evidence_profile

    evidence_metadata = enforce_evidence_profile(record)
    detail = {"figure_id": figure_id, "status": "STRUCTURAL_PASS_REVIEW_REQUIRED",
              "svg_inches": [round(sw, 4), round(sh, 4)], "png_pixels": [pw, ph],
              "style_lock": "VERIFIED" if lock else "LEGACY_V1_UNFROZEN",
              "tagged_semantic_paints": observed_paints,
              "svg_typography": typography,
              "palette_report": palette_report,
              "publication_format": publication_format,
              "evidence_metadata": evidence_metadata,
              "note": "User permission, actual data-to-mark linkage, white-pixel opacity, font substitution, rendered layout and science NOT verified"}
    cross = {"colors": {k: v.upper() for k, v in colors.items()},
             "group": group, "axes": axes, "canvas": canvas,
             "template": style.get("template_id") if lock else None,
             "fingerprint": lock["style_fingerprint"] if lock else None}
    return detail, cross


def check_contracts(project: Path, contract_paths: list[Path]) -> dict:
    """Read existing files only. All passes remain pending scientific/visual review."""
    root = project.resolve()
    records, errors, color_registry, group_registry = [], [], {}, {}
    for manifest in contract_paths:
        fig = str(manifest)
        try:
            spec = json.loads(_local(root, str(manifest)).read_text(encoding="utf-8"))
            if not isinstance(spec, dict):
                raise ValueError("figure contract must be a JSON object")
            detail, cross = _check_one(root, spec)
            ident = detail["figure_id"]
            for key, value in cross["colors"].items():
                if key in color_registry and color_registry[key] != value:
                    raise ValueError(f"semantic color conflict {key}")
            if cross["group"]:
                group = cross["group"]
                signature = (json.dumps(cross["axes"], sort_keys=True), tuple(cross["canvas"]),
                             cross["template"], cross["fingerprint"])
                if group in group_registry and group_registry[group] != signature:
                    raise ValueError(f"comparison group scale/canvas mismatch: {group}")
                group_registry[group] = signature
            color_registry.update(cross["colors"])
            records.append(detail)
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
            errors.append({"contract": fig, "error": str(exc)})
    return {"status": "QA_FAIL" if errors else "STRUCTURAL_PASS_REVIEW_REQUIRED",
            "results": records, "errors": errors, "permission_verified": False,
            "science_verified": False, "rendered_visual_review_verified": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--contracts", type=Path, nargs="+", required=True)
    args = parser.parse_args(argv)
    report = check_contracts(args.project, args.contracts)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "QA_FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
