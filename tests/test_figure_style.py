"""Pure static theme/template contract checks (never render a test image)."""
import copy
import json
import unittest
from pathlib import Path

from tools.figure_style import (
    BASE_THEME, REGISTRY, frozen_style_fields, load_registry, load_theme, semantic_color,
    semantic_gid, style_fingerprint, template_spec, validate_theme,
)
from tools.figure_templates import require_drawing_request, create_template_figure, export_figure, rendering_environment_receipt, _write_pair_exclusive


class FigureStyleTests(unittest.TestCase):
    def test_repository_theme_and_all_templates_are_valid(self):
        theme = load_theme()
        registry = load_registry()
        self.assertEqual(len(registry["templates"]), 7)
        self.assertEqual(theme["background"], "#FFFFFF")
        self.assertEqual(theme["text_color"], "#000000")
        for name in registry["templates"]:
            with self.subTest(name=name):
                cfg = template_spec(name, registry)
                self.assertTrue(cfg["axes_box"])
                self.assertEqual(len(style_fingerprint(theme, name)), 64)

    def test_fingerprint_changes_with_theme_or_template(self):
        theme = load_theme(BASE_THEME)
        original = style_fingerprint(theme, "model_dot")
        self.assertEqual(original, style_fingerprint(load_theme(), "model_dot"))
        self.assertNotEqual(original, style_fingerprint(theme, "heatmap"))
        modified = copy.deepcopy(theme)
        modified["font_sizes_pt"]["axis_title"] += 1
        self.assertNotEqual(original, style_fingerprint(modified, "model_dot"))

    def test_static_style_metadata_matches_fingerprint(self):
        fields = frozen_style_fields(BASE_THEME, "paired_dot")
        self.assertEqual(fields["style_fingerprint"], style_fingerprint(load_theme(), "paired_dot"))
        self.assertEqual(fields["template_id"], "paired_dot")
        self.assertEqual(fields["background"], "#FFFFFF")
        self.assertEqual(len(fields["theme_sha256"]), 64)
        self.assertNotIn("user_request_ref", fields)  # cannot self-grant authorization

    def test_named_palette_version_is_pinned_and_legacy_themes_still_valid(self):
        from tools.figure_palette import load_palettes, palette_colors, assign_semantic_colors, colormap_spec
        registry = load_palettes()
        theme = load_theme()
        self.assertEqual(theme["colors"]["palette_id"], registry["existing_default"])
        self.assertEqual(theme["colors"]["categorical"], palette_colors("tol-bright"))
        self.assertEqual(registry["recommended_new_project"], "tol-muted")
        self.assertEqual(colormap_spec("vik", "diverging")["backend"], "cmcrameri")
        with self.assertRaises(ValueError):
            colormap_spec("viridis", "diverging")
        mapped = assign_semantic_colors(["model:A", "model:B"], "tol-muted")
        stable = assign_semantic_colors(["model:B", "model:A"], "tol-muted", existing=mapped)
        self.assertEqual(stable, mapped)
        old_theme = copy.deepcopy(theme)
        old_theme["colors"].pop("palette_id")
        old_theme["colors"].pop("palette_registry_version")
        old_theme["colors"].pop("accents")
        self.assertIs(validate_theme(old_theme), old_theme)
        bad = copy.deepcopy(theme)
        bad["colors"]["palette_registry_version"] = "stale-version"
        with self.assertRaises(ValueError):
            validate_theme(bad)

    def test_palette_contrast_warning_not_overstated_as_accessibility(self):
        from tools.figure_palette import white_contrast, palette_diagnostics
        self.assertAlmostEqual(white_contrast("#000000"), 21.0, places=5)
        self.assertAlmostEqual(white_contrast("#FFFFFF"), 1.0, places=5)
        summary = palette_diagnostics(["#4477AA", "#66CCEE"])
        self.assertEqual(len(summary["warnings"]), 1)
        self.assertIn("not a color-vision", summary["note"])

    def test_invalid_or_missing_semantic_color_cannot_use_default_cycle(self):
        theme = load_theme()
        with self.assertRaises(ValueError):
            semantic_color(theme, "model:SF")
        theme["colors"]["semantic_colors"] = {"model:SF": "#769EB2"}
        self.assertEqual(semantic_color(theme, "model:SF"), "#769EB2")
        self.assertEqual(semantic_gid("model:SF"), "series--model--SF")
        theme["background"] = "#EEEEEE"
        with self.assertRaises(ValueError):
            validate_theme(theme)

    def test_exclusive_export_pair_rolls_back_on_collision(self):
        # Plain text files, never generated SVG/PNG or preview images.
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "output-a.txt"
            second = Path(directory) / "output-b.txt"
            second.write_bytes(b"important-existing-original")
            with self.assertRaises(FileExistsError):
                _write_pair_exclusive([(first, b"first"), (second, b"second")])
            self.assertFalse(first.exists())
            self.assertEqual(second.read_bytes(), b"important-existing-original")
            _write_pair_exclusive([(first, b"first")])
            self.assertEqual(first.read_bytes(), b"first")

    def test_exclusive_export_pair_rejects_empty_second_payload(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "output-a.txt"
            second = Path(directory) / "output-b.txt"
            with self.assertRaises(ValueError):
                _write_pair_exclusive([(first, b"data"), (second, b"")])
            self.assertFalse(first.exists())
            self.assertFalse(second.exists())

    def test_request_guard_blocks_before_plotting_import(self):
        with self.assertRaises(PermissionError):
            require_drawing_request(explicitly_requested=False, user_request_ref="user-message")
        with self.assertRaises(PermissionError):
            create_template_figure("paired_dot", explicitly_requested=False,
                                   user_request_ref="user-message")
        with self.assertRaises(PermissionError):
            export_figure(None, Path("none.svg"), Path("none.png"),
                          explicitly_requested=False, user_request_ref="user-message")
        with self.assertRaises(PermissionError):
            require_drawing_request(explicitly_requested=True, user_request_ref="REPLACE_WITH_ID")
        with self.assertRaises(PermissionError):
            rendering_environment_receipt(None, explicitly_requested=False,
                                          user_request_ref="ungranted")
        # No call above is permitted to import Matplotlib or produce a figure.


if __name__ == "__main__":
    unittest.main()
