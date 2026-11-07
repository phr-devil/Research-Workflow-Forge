"""PD-RW opt-in publication chart invariants; no image generation in CI."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import Mock

from tools.figure_style import load_theme, validate_theme
from tools.figure_templates import (
    aligned_panel_session, allow_observation_points, audit_publication_format,
)

ROOT = Path(__file__).resolve().parents[1]
PD_RW_THEME = ROOT / "styles" / "figure_theme_pdrw.json"


class FakeAnnotation:
    def __init__(self, gid):
        self.gid = gid

    def get_gid(self):
        return self.gid


PathCollection = type("PathCollection", (), {})


class FakeBar:
    def __init__(self):
        self.patches = [object()]


class FakeLine:
    def __init__(self, marker="o"):
        self.marker = marker

    def get_marker(self):
        return self.marker


class FakeAx:
    def __init__(self, panel_id="main", box=(0.25, 0.2, 0.65, 0.65)):
        self.texts = [FakeAnnotation("axis-arrow-x--" + panel_id),
                      FakeAnnotation("axis-arrow-y--" + panel_id)]
        self.containers = [FakeBar()]
        self.lines = []
        self.collections = []
        self.box = box

    def get_position(self):
        return Mock(bounds=self.box)


class FakeFig:
    def __init__(self, theme, ax=None, template="rate_ablation"):
        self._rwf_theme = theme
        self._rwf_template_id = template
        self.axes = [ax or FakeAx()]


class FigurePublicationGuards(unittest.TestCase):
    def setUp(self):
        self.theme = load_theme(PD_RW_THEME)

    def test_profile_is_explicit_and_legacy_is_not_changed(self):
        legacy = load_theme()
        self.assertEqual(legacy["axes"]["arrow_policy"], "project_only")
        self.assertEqual(self.theme["style_profile"], "PD_RW_PUBLICATION")
        self.assertEqual(self.theme["axes"]["arrow_policy"], "cartesian")
        self.assertEqual(self.theme["marks"]["bar_overlay_policy"], "no_redundant_points")
        incorrect = copy.deepcopy(self.theme)
        incorrect["axes"]["arrow_policy"] = "none"
        with self.assertRaises(ValueError):
            validate_theme(incorrect)

    def test_arrows_required_on_cartesian_and_not_required_on_heatmap(self):
        fig = FakeFig(self.theme)
        self.assertEqual(audit_publication_format(fig)["axis_arrow_objects"], 2)
        fig.axes[0].texts.pop()
        with self.assertRaisesRegex(ValueError, "arrows missing"):
            audit_publication_format(fig)
        heatmap = FakeFig(self.theme, ax=FakeAx(), template="heatmap")
        heatmap.axes[0].texts = []
        self.assertEqual(audit_publication_format(heatmap)["axis_arrow_objects"], 0)

    def test_colored_bars_reject_redundant_points(self):
        ax = FakeAx()
        ax.collections.append(PathCollection())
        with self.assertRaisesRegex(ValueError, "redundant"):
            audit_publication_format(FakeFig(self.theme, ax=ax))
        with self.assertRaises(ValueError):
            allow_observation_points(ax, source_ref="", scientific_reason="very important")
        allow_observation_points(ax, source_ref="run:valid-dev", scientific_reason="independent subject observations")
        self.assertEqual(audit_publication_format(FakeFig(self.theme, ax=ax))["axes"], 1)
        ax.collections = []
        ax.lines.append(FakeLine("s"))
        del ax._rwf_bar_point_exception
        with self.assertRaisesRegex(ValueError, "redundant"):
            audit_publication_format(FakeFig(self.theme, ax=ax))

    def test_panel_alignment_and_misalignment(self):
        axes = [[FakeAx("r0c0", (0.1, 0.5, 0.3, 0.3)),
                 FakeAx("r0c1", (0.5, 0.5, 0.3, 0.3))],
                [FakeAx("r1c0", (0.1, 0.1, 0.3, 0.3)),
                 FakeAx("r1c1", (0.5, 0.1, 0.3, 0.3))]]
        fig = FakeFig(self.theme)
        fig._rwf_panel_axes = axes
        self.assertEqual(audit_publication_format(fig)["panel_grid"], [2, 2])
        axes[0][1].box = (0.5, 0.53, 0.3, 0.3)
        with self.assertRaisesRegex(ValueError, "not aligned"):
            audit_publication_format(fig)

    def test_permission_stays_locked_before_matplotlib(self):
        with self.assertRaises(PermissionError):
            with aligned_panel_session("rate_ablation", rows=2, cols=2):
                self.fail("should never enter without authorization")

    def test_arrow_gids_are_on_actual_arrow_patch(self):
        src = (ROOT / "tools/figure_templates.py").read_text(encoding="utf-8")
        self.assertIn("annotation.arrow_patch.set_gid(gid)", src)

    def test_documentation_and_no_image_fixture(self):
        doc = (ROOT / "docs/FIGURE_STYLE_SYSTEM.md").read_text(encoding="utf-8")
        for item in ("aligned_panel_session", "allow_observation_points",
                     "PD_RW_PUBLICATION", "arrowheads", "visual inspection"):
            self.assertIn(item, doc)


if __name__ == "__main__":
    unittest.main()
