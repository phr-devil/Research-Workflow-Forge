"""Static structural-QA tests. IMPORTANT: no SVG/PNG or preview is generated.

All image metadata is mocked; only text manifests, CSVs and in-memory XML
snippets are exercised, preserving the explicit-user-only drawing gate in CI.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.figure_qa import check_contracts, inspect_svg_semantic_paints, _local
from tools.figure_style import BASE_THEME, load_theme, style_fingerprint


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FigureQATests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "results.csv").write_text("x,y\n1,2\n", encoding="utf-8")
        (self.root / "plot.csv").write_text("x,y\n1,2\n", encoding="utf-8")
        self.base = {
            "schema_version": "figure-v1", "figure_id": "F1",
            "figure_kind": "PUBLICATION", "user_request_ref": "actual-user-message-1",
            "source_artifacts": [{"path": "results.csv", "role": "DEV",
                                  "sha256": _sha(self.root / "results.csv")}],
            "plot_data": {"path": "plot.csv", "sha256": _sha(self.root / "plot.csv")},
            "outputs": {"svg": "f.svg", "png": "f.png"},
            "style": {"background": "#FFFFFF", "font_family": "Arial",
                      "png_dpi": 72, "canvas_inches": [1, 1],
                      "semantic_colors": {"model:SF": "#769EB2"},
                      "comparison_group": "pair", "axis_limits": {"y": [0, 100]}}
        }

    def _check_records(self, records, *, dpi=(72, 72), svg_bytes=None):
        manifests = []
        for i, record in enumerate(records):
            file = self.root / f"spec{i}.json"
            file.write_text(json.dumps(record), encoding="utf-8")
            manifests.append(Path(file.name))
        orig_read = Path.read_bytes

        def safe_local(root, rel):
            if rel in ("f.svg", "f.png"):
                return (root / rel).resolve()
            return _local(root, rel)

        def safe_read(path):
            if path.suffix.lower() == ".svg":
                return svg_bytes if svg_bytes is not None else b"<svg/>"
            return orig_read(path)

        with patch("tools.figure_qa._local", side_effect=safe_local), \
             patch("tools.figure_qa._svg_size", return_value=(1.0, 1.0)), \
             patch("tools.figure_qa._png_info", return_value=(72, 72, dpi)), \
             patch.object(Path, "read_bytes", autospec=True, side_effect=safe_read):
            result = check_contracts(self.root, manifests)
        # CI must not create even temporary image files.
        self.assertFalse(list(self.root.rglob("*.svg")))
        self.assertFalse(list(self.root.rglob("*.png")))
        return result

    def _check(self, **updates):
        return self._check_records([{**self.base, **updates}])

    def _v2(self):
        theme = load_theme(BASE_THEME)
        theme["colors"]["semantic_colors"] = {"model:SF": "#769EB2"}
        dest = self.root / "theme.json"
        dest.write_text(json.dumps(theme, sort_keys=True), encoding="utf-8")
        v2 = json.loads(json.dumps(self.base))
        v2["schema_version"] = "figure-v2"
        v2["style"].update({
            "theme_ref": "theme.json", "theme_sha256": _sha(dest),
            "template_id": "rate_ablation", "style_profile": theme["style_profile"],
            "font_family": theme["font_family"],
            "style_fingerprint": style_fingerprint(theme, "rate_ablation"),
        })
        return v2

    def test_legacy_structural_pass_not_permission_or_science_pass(self):
        result = self._check()
        self.assertEqual(result["status"], "STRUCTURAL_PASS_REVIEW_REQUIRED")
        self.assertEqual(result["results"][0]["style_lock"], "LEGACY_V1_UNFROZEN")
        for k in ("permission_verified", "science_verified", "rendered_visual_review_verified"):
            self.assertFalse(result[k])

    def test_invalid_contract_or_source_is_rejected(self):
        bad = [{**self.base, "schema_version": "unknown"},
               {**self.base, "user_request_ref": ""},
               {**self.base, "source_artifacts": [{**self.base["source_artifacts"][0], "role": "SEALED"}]},
               {**self.base, "outputs": {"svg": "../other.svg", "png": "f.png"}}]
        for spec in bad:
            with self.subTest(spec=spec):
                self.assertEqual(self._check_records([spec])["status"], "QA_FAIL")
        (self.root / "results.csv").write_text("tampered", encoding="utf-8")
        self.assertEqual(self._check()["status"], "QA_FAIL")

    def test_png_metadata_required(self):
        self.assertEqual(self._check_records([self.base], dpi=None)["status"], "QA_FAIL")

    def test_group_limits_and_palette(self):
        a = self.base
        b = json.loads(json.dumps(a))
        b["figure_id"] = "F2"
        b["style"]["axis_limits"] = {"y": [0, 1]}
        self.assertEqual(self._check_records([a, b])["status"], "QA_FAIL")
        b["style"]["axis_limits"] = {"y": [0, 100]}
        b["style"]["semantic_colors"] = {"model:SF": "#FF0000"}
        self.assertEqual(self._check_records([a, b])["status"], "QA_FAIL")

    def test_v2_style_lock_and_actual_svg_semantic_tag(self):
        v2 = self._v2()
        svg = b'<svg><g id="template--rate_ablation"/><g id="series--model--SF"><path style="fill: #769eb2; stroke: #000000"/></g></svg>'
        result = self._check_records([v2], svg_bytes=svg)
        self.assertEqual(result["status"], "STRUCTURAL_PASS_REVIEW_REQUIRED")
        self.assertEqual(result["results"][0]["style_lock"], "VERIFIED")
        self.assertIn("model:SF", result["results"][0]["tagged_semantic_paints"])

    def test_v2_theme_drift_and_silent_color_override_fail(self):
        v2 = self._v2()
        svg = b'<svg><g id="template--rate_ablation"/><g id="series--model--SF"><path style="fill: #769eb2"/></g></svg>'
        v2["style"]["semantic_colors"]["model:SF"] = "#FF0000"
        self.assertEqual(self._check_records([v2], svg_bytes=svg)["status"], "QA_FAIL")
        v2["style"]["semantic_colors"]["model:SF"] = "#769EB2"
        v2["style"]["style_fingerprint"] = "0" * 64
        self.assertEqual(self._check_records([v2], svg_bytes=svg)["status"], "QA_FAIL")

    def test_matplotlib_prolog_and_explicit_font_checks(self):
        from tools.figure_qa import _safe_svg_xml, inspect_svg_typography
        prefix = (b'<?xml version="1.0"?>'
                  b'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
                  b'"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
        xml = (prefix + b'<svg><text style="font: 11px &apos;DejaVu Sans&apos;; fill: #000000">'
               b'F1</text></svg>')
        self.assertIn(b"<svg>", _safe_svg_xml(xml))
        self.assertEqual(inspect_svg_typography(xml, "DejaVu Sans")["explicit_font_checks"], 1)
        with self.assertRaises(ValueError):
            inspect_svg_typography(xml, "Arial")
        with self.assertRaises(ValueError):
            _safe_svg_xml(b'<!DOCTYPE svg SYSTEM "http://other.com/x.dtd"><svg/>')

    def test_actual_tagged_svg_paint(self):
        okay = b'<svg><g id="series--model--SF"><path style="stroke: #769eb2; fill: none"/></g></svg>'
        observed = inspect_svg_semantic_paints(okay, {"model:SF": "#769EB2"})
        self.assertIn("#769EB2", observed["model:SF"])
        for bad in (
            b'<svg><g id="series--model--SF"><path style="stroke: #ee6677"/></g></svg>',
            b'<svg><path style="stroke: #769eb2"/></svg>',
            b'<!DOCTYPE svg><svg/>',
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                inspect_svg_semantic_paints(bad, {"model:SF": "#769EB2"})


if __name__ == "__main__":
    unittest.main()
