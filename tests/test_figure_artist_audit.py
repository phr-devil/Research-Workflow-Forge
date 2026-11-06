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
