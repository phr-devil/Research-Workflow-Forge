"""Synthetic PD-RW scientific handoff: file integrity is not science or permission."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from adapters.science_handoff import review_science_handoff
from core.contracts import ContractError


class ScienceHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / "dev-summary.json"
        self.data.write_text('{"DEV":"observation"}', encoding="utf-8")
        self.packet = {
            "format": "pd-rw-science-handoff-v1",
            "task_id": "T1", "research_question": "Why is transfer weak?",
            "importance_rationale": "Meaningful transfer cost",
            "named_nearest_original": "DOI:source requires reading",
            "claimed_knowledge_delta": "Predictive boundary not covered",
            "strongest_alternative": "Subject distribution shift",
            "distinct_prediction": "Matched groups would differ",
            "data_discriminability_limitations": "Device nested in subject",
            "independent_group_unit": "subject",
            "legal_information_contract": "DEV only; K=0 predecision",
            "next_discriminating_test": "Read DEV metadata crossing",
            "pd_rw_scientific_choice": "T1 chosen by PD-RW",
            "authorization_reference": "Original user message must be checked",
            "source_receipts": [{
                "path": "dev-summary.json", "role": "DEV",
                "sha256": hashlib.sha256(self.data.read_bytes()).hexdigest(),
            }],
        }

    def test_valid_receipt_has_no_science_certification(self):
        r = review_science_handoff(self.root, self.packet)
        self.assertEqual(r["status"], "SCIENCE_HANDOFF_FILE_HASHES_VERIFIED_ONLY")
        for key in ("research_problem_selected_by_forge", "scientific_value_ranked_by_forge",
                    "q2_potential_verified", "original_user_authorization_verified"):
            self.assertFalse(r[key])

    def test_tampered_receipt_rejected(self):
        self.data.write_text("tampered", encoding="utf-8")
        with self.assertRaises(ContractError):
            review_science_handoff(self.root, self.packet)

    def test_missing_scientific_rationale_rejected(self):
        self.packet["distinct_prediction"] = ""
        with self.assertRaisesRegex(ContractError, "distinct_prediction"):
            review_science_handoff(self.root, self.packet)

    def test_sealed_and_path_escape_rejected(self):
        self.packet["source_receipts"][0]["role"] = "SEALED_CONFIRM"
        with self.assertRaises(ContractError):
            review_science_handoff(self.root, self.packet)
        self.packet["source_receipts"][0]["role"] = "DEV"
        self.packet["source_receipts"][0]["path"] = "../outside.json"
        with self.assertRaises(ContractError):
            review_science_handoff(self.root, self.packet)


if __name__ == "__main__":
    unittest.main()
