"""Pure validation/permission unit tests; never create chart, preview or image."""
import unittest

from tools.figure_charts import (
    _labels, _values, draw_dumbbell, draw_effect_ecdf, draw_heatmap,
    draw_model_dot, draw_paired_dot, draw_rate_ablation,
    draw_timeline_tracks, validate_matrix, validate_timeline_tracks,
)
from tools.figure_style import load_theme


class ChartGuards(unittest.TestCase):
    def test_every_template_refuses_before_any_matplotlib_operation(self):
        theme = load_theme()
        cases = [
            (draw_model_dot, (None, ["a"], [0.1], ["model:A"])),
            (draw_paired_dot, (None, ["a"], [0.1], [0.2], "model:A", "model:B")),
            (draw_dumbbell, (None, ["a"], [0.1], [0.2], "model:A", "model:B")),
            (draw_effect_ecdf, (None, [0.1],)),
            (draw_rate_ablation, (None, ["a"], [0.1], ["model:A"])),
            (draw_timeline_tracks, (None, {"Truth": []})),
            (draw_heatmap, (None, [[1.0]], ["c1"], ["r1"])),
        ]
        for fn, args in cases:
            with self.subTest(name=fn.__name__), self.assertRaises(PermissionError):
                extra = {"theme": theme} if fn not in (draw_heatmap,) else {}
                if fn == draw_effect_ecdf:
                    extra["semantic_key"] = "model:A"
                fn(*args, **extra)

    def test_schema_checks_before_any_user_drawing(self):
        theme = load_theme()
        theme["colors"]["semantic_colors"] = {"skill:Walk": "#4477AA"}
        valid = {"Ground Truth": [
            {"start": 1.0, "end": 2.0, "semantic_key": "skill:Walk"},
            {"start": 2.0, "end": 3.0, "semantic_key": "skill:Walk"},
        ]}
        self.assertIs(validate_timeline_tracks(valid, theme), valid)
        with self.assertRaises(ValueError):
            validate_timeline_tracks({"GT": [
                {"start": 1, "end": 3, "semantic_key": "skill:Walk"},
                {"start": 2, "end": 4, "semantic_key": "skill:Walk"}]}, theme)
        with self.assertRaises(ValueError):
            validate_matrix([[1], [2, 3]], ["a"], ["r1", "r2"])
        self.assertEqual(validate_matrix([[1.0, 2.0]], ["a", "b"], ["row"]), [[1.0, 2.0]])
        with self.assertRaises(ValueError):
            _values([0.1, float("inf")])
        with self.assertRaises(ValueError):
            _labels(["same", "same"], 2)


if __name__ == "__main__":
    unittest.main()
