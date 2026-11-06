"""Text-only scientific metadata checks; no images or plotting."""
import unittest
from tools.figure_evidence import inspect_evidence_metadata


class FigureEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.example = {
            "figure_type": "data",
            "metric": "misclassification_rate", "unit": "percent",
            "independent_unit": "subject", "denominator": "all true Lift samples",
            "science_context": {
                "population_or_split": "DEV only, 24 subjects",
                "transform_notes": "No smoothing or exclusions",
                "missing_policy": "No missing observations",
                "uncertainty_definition": "None displayed: descriptive rates only",
                "selection_history": "Fixed before this display; not confirmatory",
            }
        }

    def test_complete_means_declarations_only(self):
        report = inspect_evidence_metadata(self.example)
        self.assertEqual(report["status"], "METADATA_COMPLETE_NOT_SCIENCE_VERIFIED")
        self.assertFalse(report["scientific_source_verified"])

    def test_missing_context_does_not_get_fabricated(self):
        incomplete = {**self.example, "science_context": {"missing_policy": "TODO"}}
        report = inspect_evidence_metadata(incomplete)
        self.assertEqual(report["status"], "INCOMPLETE_METADATA")
        self.assertIn("science_context.missing_policy", report["missing_fields"])
        self.assertIn("science_context.uncertainty_definition", report["missing_fields"])

    def test_schematic_does_not_demand_fictitious_denominator(self):
        rec = {"figure_type": "schematic"}
        self.assertEqual(inspect_evidence_metadata(rec)["status"], "NOT_APPLICABLE_SCHEMATIC")


if __name__ == "__main__":
    unittest.main()
