"""Pure static theme/template contract checks (never render a test image)."""
import copy
import json
import unittest
from pathlib import Path

from tools.figure_style import (
    BASE_THEME, REGISTRY, load_registry, load_theme, semantic_color,
    semantic_gid, style_fingerprint, template_spec, validate_theme,
)
from tools.figure_templates import require_drawing_request, create_template_figure, export_figure


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
        # No call above is permitted to import Matplotlib or produce a figure.


if __name__ == "__main__":
    unittest.main()
