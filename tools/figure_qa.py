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


def _svg_size(path: Path) -> tuple[float, float]:
    raw = path.read_bytes()
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("SVG DOCTYPE/ENTITY prohibited")
    root = ET.fromstring(raw)
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
    upper = svg_xml.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError("SVG DOCTYPE/ENTITY prohibited")
    root = ET.fromstring(svg_xml)
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
    if version == "figure-v2":
        from tools.figure_style import validate_style_lock

        lock = validate_style_lock(record, root)
        # For v2, check tagged artist groups in the *exported SVG*.
        if colors:
            observed_paints = inspect_svg_semantic_paints(svg.read_bytes(), colors)
        if style.get("comparison_group") and not style.get("axis_limits"):
            raise ValueError("v2 comparison group requires explicit comparable axis limits")
    detail = {"figure_id": figure_id, "status": "STRUCTURAL_PASS_REVIEW_REQUIRED",
              "svg_inches": [round(sw, 4), round(sh, 4)], "png_pixels": [pw, ph],
              "style_lock": "VERIFIED" if lock else "LEGACY_V1_UNFROZEN",
              "tagged_semantic_paints": observed_paints,
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
