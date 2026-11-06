"""No plotting libraries imported or images created by artist data audit tests."""
import unittest
from tools.figure_artist_audit import (
    artist_coordinates, audit_artist_coordinates, data_digest, normalize_xy,
)


class MockLine:
    def __init__(self, x, y, gid):
        self.x, self.y, self.gid = x, y, gid

    def get_xdata(self, orig=True):
        return self.x

    def get_ydata(self, orig=True):
        return self.y

    def get_gid(self):
        return self.gid


class MockScatter:
    def __init__(self, points, gid):
        self.points, self.gid = points, gid

    def get_offsets(self):
        return self.points

    def get_gid(self):
        return self.gid


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.expected = {
            "model:SF": {"x": [0, 1, 2], "y": [0.1, 0.2, 0.3],
                         "source_ref": "runs/DEV_RUN.json#SF"}
        }
        self.artist = MockLine([0, 1, 2], [0.1, 0.2, 0.3], "series--model--SF")

    def test_matching_artist_has_explicit_limited_status(self):
        report = audit_artist_coordinates({"model:SF": self.artist}, self.expected)
        self.assertEqual(report["status"], "ARTIST_COORDINATES_MATCH_EXPECTED_ROWS_ONLY")
        self.assertFalse(report["scientific_source_verified"])
        self.assertEqual(report["series"][0]["points"], 3)
        self.assertEqual(report["series"][0]["data_sha256"],
                         data_digest(self.expected["model:SF"]))

    def test_transposed_or_misassigned_data_fail(self):
        self.artist.y = [0.1, 0.3, 0.2]
        with self.assertRaisesRegex(ValueError, "coordinates differ"):
            audit_artist_coordinates({"model:SF": self.artist}, self.expected)
        self.artist.y = [0.1, 0.2, 0.3]
        self.artist.gid = "series--model--WRONG"
        with self.assertRaisesRegex(ValueError, "semantic ID"):
            audit_artist_coordinates({"model:SF": self.artist}, self.expected)

    def test_scatter_offsets_and_missing_source(self):
        scatter = MockScatter([[0, 2], [1, 3]], "series--model--SF")
        self.assertEqual(artist_coordinates(scatter), {"x": [0.0, 1.0], "y": [2.0, 3.0]})
        expected = {"model:SF": {"x": [0, 1], "y": [2, 3], "source_ref": "DEV-1"}}
        self.assertEqual(audit_artist_coordinates({"model:SF": scatter}, expected)["series"][0]["points"], 2)
        expected["model:SF"]["source_ref"] = ""
        with self.assertRaises(ValueError):
            audit_artist_coordinates({"model:SF": scatter}, expected)

    def test_missing_or_invalid_data_is_not_silently_accepted(self):
        with self.assertRaises(ValueError):
            normalize_xy([0, 1], [0.2])
        with self.assertRaises(ValueError):
            normalize_xy([0, 1], [float("nan"), 0.1])
        with self.assertRaises(ValueError):
            audit_artist_coordinates({}, self.expected)


if __name__ == "__main__":
    unittest.main()



class MockBar:
    def __init__(self, height=0.35, gid="series--model--SF", rgba=(68/255, 119/255, 170/255, 1)):
        self.height, self.gid, self.rgba = height, gid, rgba

    def get_height(self):
        return self.height

    def get_y(self):
        return 0

    def get_x(self):
        return -0.35

    def get_width(self):
        return 0.7

    def get_gid(self):
        return self.gid

    def get_facecolor(self):
        return self.rgba


class MockMatrix:
    def __init__(self, values=None, limits=(0.0, 1.0)):
        self.values = values if values is not None else [[0.25, 0.75], [0.0, 1.0]]
        self.limits = limits

    def get_array(self):
        return self.values

    def get_clim(self):
        return self.limits


class ExtraFigureAuditTests(unittest.TestCase):
    def test_bars_are_checked_for_exact_height_baseline_identity_and_paint(self):
        from tools.figure_artist_audit import audit_rate_bars

        expected = {"model:SF": {"value": 0.35, "index": 0, "color": "#4477AA",
                                  "source_ref": "verified-dev-01"}}
        result = audit_rate_bars({"model:SF": MockBar()}, expected)
        self.assertEqual(result["status"], "BAR_GEOMETRY_AND_PAINT_MATCH_EXPECTED_ROWS_ONLY")
        self.assertFalse(result["scientific_source_verified"])
        with self.assertRaisesRegex(ValueError, "geometry"):
            audit_rate_bars({"model:SF": MockBar(height=0.45)}, expected)
        with self.assertRaisesRegex(ValueError, "color"):
            audit_rate_bars({"model:SF": MockBar(rgba=(1, 0, 0, 1))}, expected)
        with self.assertRaisesRegex(ValueError, "identity"):
            audit_rate_bars({"model:SF": MockBar(gid="series--model--X")}, expected)

    def test_heatmap_array_and_color_limits(self):
        from tools.figure_artist_audit import audit_heatmap_array

        expected = {"source_ref": "verified-run-heatmap", "matrix": [[0.25, 0.75], [0.0, 1.0]],
                    "clim": [0.0, 1.0]}
        r = audit_heatmap_array(MockMatrix(), expected)
        self.assertEqual(r["shape"], [2, 2])
        self.assertFalse(r["scientific_source_verified"])
        with self.assertRaisesRegex(ValueError, "matrix differs"):
            audit_heatmap_array(MockMatrix(values=[[0.75, 0.25], [0.0, 1.0]]), expected)
        with self.assertRaisesRegex(ValueError, "color scale"):
            audit_heatmap_array(MockMatrix(limits=(0.1, 1.0)), expected)
