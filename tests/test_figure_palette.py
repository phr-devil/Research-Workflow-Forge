"""Palette tests are text/numeric only, NEVER rendering or plotting."""
import copy
import unittest

from tools.figure_palette import (
    assign_semantic_colors, colormap_spec, load_palettes, palette_colors,
    palette_diagnostics, validate_theme_palette, white_contrast,
)
from tools.figure_style import load_theme, style_fingerprint


class PaletteTests(unittest.TestCase):
    def test_predefined_presets_and_research_colormaps(self):
        data = load_palettes()
        self.assertEqual(data["existing_default"], "tol-bright")
        self.assertEqual(data["recommended_new_project"], "tol-muted")
        for name in ("tol-bright", "tol-muted", "tol-vibrant", "okabe-ito", "tableau10"):
            with self.subTest(name=name):
                self.assertGreaterEqual(len(palette_colors(name)), 6)
        self.assertEqual(colormap_spec("viridis", "sequential")["backend"], "matplotlib")
        self.assertEqual(colormap_spec("vik", "diverging")["backend"], "cmcrameri")
        with self.assertRaises(ValueError):
            colormap_spec("viridis", "cyclic")

    def test_existing_theme_is_unchanged_tol_bright(self):
        theme = load_theme()
        self.assertEqual(theme["colors"]["palette_id"], "tol-bright")
        self.assertEqual(theme["colors"]["categorical"], palette_colors("tol-bright"))
        old = copy.deepcopy(theme)
        old["colors"].pop("palette_id")
        old["colors"].pop("palette_registry_version")
        validate_theme_palette(old["colors"])  # optional legacy metadata

    def test_immutable_semantic_identity_and_exhaustion(self):
        p = assign_semantic_colors(["model:A", "model:B"], "tol-muted")
        self.assertEqual(p, assign_semantic_colors(["model:B", "model:A"], "tol-muted", existing=p))
        self.assertEqual(p["model:A"], palette_colors("tol-muted")[0])
        with self.assertRaises(ValueError):
            assign_semantic_colors([f"model:{i}" for i in range(7)], "tol-muted")
        with self.assertRaises(ValueError):
            assign_semantic_colors(["model:A", "model:A"], "tol-muted")

    def test_white_contrast_reports_not_false_certification(self):
        self.assertAlmostEqual(white_contrast("#000000"), 21.0)
        self.assertAlmostEqual(white_contrast("#FFFFFF"), 1.0)
        r = palette_diagnostics(["#4477AA", "#66CCEE"])
        self.assertEqual(len(r["warnings"]), 1)
        self.assertIn("not a color-vision", r["note"])
        with self.assertRaises(ValueError):
            white_contrast("red")

    def test_registry_version_and_swatches_cannot_silently_drift(self):
        colors = copy.deepcopy(load_theme()["colors"])
        validate_theme_palette(colors)
        colors["categorical"][0] = "#111111"
        with self.assertRaises(ValueError):
            validate_theme_palette(colors)
        colors = copy.deepcopy(load_theme()["colors"])
        colors["palette_registry_version"] = "wrong-version"
        with self.assertRaises(ValueError):
            validate_theme_palette(colors)


if __name__ == "__main__":
    unittest.main()
