"""Regression tests for read-only figure QA; no matplotlib required."""
import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from tools.figure_qa import check_contracts


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)


def _png(path):
    # Valid, opaque RGB, 72 x 72 pixels at 72dpi.
    w = h = 72
    raw = (b"\x00" + b"\xff\xff\xff" * w) * h
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + _chunk(b"pHYs", struct.pack(">IIB", 2835, 2835, 1))
        + _chunk(b"IDAT", zlib.compress(raw))
        + _chunk(b"IEND", b"")
    )


class FigureQATests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "results.csv").write_text("x,y\n1,2\n", encoding="utf-8")
        (self.root / "plot.csv").write_text("x,y\n1,2\n", encoding="utf-8")
        (self.root / "f.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="72pt" height="72pt"><rect x="0" y="0" width="72" height="72" fill="#ffffff"/></svg>', encoding="utf-8")
        _png(self.root / "f.png")
        self.base = {
            "schema_version": "figure-v1", "figure_id": "F1",
            "figure_kind": "PUBLICATION", "user_request_ref": "user-message-1",
            "source_artifacts": [{"path": "results.csv", "role": "DEV", "sha256": _sha(self.root / "results.csv")}],
            "plot_data": {"path": "plot.csv", "sha256": _sha(self.root / "plot.csv")},
            "outputs": {"svg": "f.svg", "png": "f.png"},
            "style": {"background": "#FFFFFF", "font_family": "Arial",
                      "png_dpi": 72, "canvas_inches": [1, 1],
                      "semantic_colors": {"model:SF": "#769EB2"},
                      "comparison_group": "pair", "axis_limits": {"y": [0, 100]}}
        }

    def _check(self, **updates):
        record = {**self.base, **updates}
        (self.root / "spec.json").write_text(json.dumps(record), encoding="utf-8")
        return check_contracts(self.root, [Path("spec.json")])

    def test_structural_pass_is_not_visual_or_permission_pass(self):
        result = self._check()
        self.assertEqual(result["status"], "STRUCTURAL_PASS_REVIEW_REQUIRED")
        self.assertFalse(result["permission_verified"])
        self.assertFalse(result["science_verified"])
        self.assertFalse(result["rendered_visual_review_verified"])

    def test_hash_tamper(self):
        (self.root / "results.csv").write_text("tampered", encoding="utf-8")
        self.assertEqual(self._check()["status"], "QA_FAIL")

    def test_missing_request_marker(self):
        self.assertEqual(self._check(user_request_ref="")["status"], "QA_FAIL")

    def test_outside_project_rejected(self):
        bad = dict(self.base["outputs"], svg="../outside.svg")
        self.assertEqual(self._check(outputs=bad)["status"], "QA_FAIL")

    def test_bad_png_crc(self):
        with (self.root / "f.png").open("r+b") as out:
            out.seek(0, 2)
            size = out.tell()
            out.seek(size - 1)
            out.write(b"x")
        self.assertEqual(self._check()["status"], "QA_FAIL")

    def test_sealed_role_rejected(self):
        bad_source = [{**self.base["source_artifacts"][0], "role": "SEALED"}]
        self.assertEqual(self._check(source_artifacts=bad_source)["status"], "QA_FAIL")

    def test_comparison_group_and_color_conflict(self):
        a = self.base
        b = json.loads(json.dumps(a))
        b["figure_id"] = "F2"
        b["style"]["axis_limits"] = {"y": [0, 1]}
        (self.root / "a.json").write_text(json.dumps(a), encoding="utf-8")
        (self.root / "b.json").write_text(json.dumps(b), encoding="utf-8")
        self.assertEqual(check_contracts(self.root, [Path("a.json"), Path("b.json")])["status"], "QA_FAIL")
        b["style"]["axis_limits"] = {"y": [0, 100]}
        b["style"]["semantic_colors"]["model:SF"] = "#FF0000"
        (self.root / "b.json").write_text(json.dumps(b), encoding="utf-8")
        self.assertEqual(check_contracts(self.root, [Path("a.json"), Path("b.json")])["status"], "QA_FAIL")


if __name__ == "__main__":
    unittest.main()
