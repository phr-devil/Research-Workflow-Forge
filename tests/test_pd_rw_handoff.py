"""Synthetic interface tests; verification of raw DEV arithmetic is covered separately."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adapters.pd_rw_bridge import verify_pd_rw_handoff
from core.comparison import compare_runs
from core.contracts import ContractError


def run_template(run_id):
    return {
        "schema_version": "0.1", "run_id": run_id, "task_id": "T",
        "protocol_id": "P", "dataset_version": "d",
        "evaluator_version": "e", "code_commit": "test",
        "status": "VALID", "split": "dev",
        "group_split": "group", "sample_ids_hash": "hash",
        "legal_inputs": ["sensor"], "metrics": {"macro_F1": 0.7},
        "artifact_refs": ["pred.json"], "level_id": "L1",
        "k_unit": "per-person", "support_query_policy": "separate",
        "k_target_labels": 1, "inference_visible_info": "predecision",
    }


class ProtocolAndHandoffTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        self.forge_root = self.root / "forge"
        self.pd_root = self.root / "pd"
        self.forge_root.mkdir()
        self.pd_root.mkdir()
        (self.forge_root / "pred.json").write_text('[{"row_index":0,"prediction":"A"}]')
        (self.pd_root / "pred.json").write_bytes((self.forge_root / "pred.json").read_bytes())
        self.forge = run_template("B")
        self.forge["metric_spec"] = {"predictions_ref": "pred.json"}
        self.pd = dict(run_template("A"))
        self.pd["artifact_refs"] = {"predictions": "pred.json", "metrics": "m.json", "code": "c.py"}
        self.pd_path = self.pd_root / "run.json"
        self.forge_path = self.forge_root / "run.json"

    def verify(self):
        self.pd_path.write_text(json.dumps(self.pd))
        self.forge_path.write_text(json.dumps(self.forge))
        with patch("adapters.pd_rw_bridge.load_verified_run",
                   return_value=(self.forge, "forge-run-sha")):
            return verify_pd_rw_handoff(self.forge_root, self.forge_path,
                                        self.pd_root, self.pd_path, "macro_F1")

    def test_handoff_same_samples_is_metric_only(self):
        result = self.verify()
        self.assertEqual(result["status"], "METRIC_VERIFIED_DEV_ONLY")
        self.assertEqual(result["protocol_field_coverage"], "FULL")

    def test_forged_metric_rejected(self):
        self.pd["metrics"] = {"macro_F1": 0.99}
        with self.assertRaisesRegex(ContractError, "RECOMPUTED_METRIC_MISMATCH"):
            self.verify()

    def test_different_predictions_rejected(self):
        (self.pd_root / "pred.json").write_text("different")
        with self.assertRaisesRegex(ContractError, "PREDICTION_BYTES_MISMATCH"):
            self.verify()

    def test_different_task_level_rejected(self):
        self.pd["level_id"] = "L2"
        with self.assertRaisesRegex(ContractError, "NOT_COMPARABLE"):
            self.verify()

    def test_missing_pd_information_is_not_assumed(self):
        self.pd.pop("k_target_labels")
        with self.assertRaisesRegex(ContractError, "NOT_COMPARABLE"):
            self.verify()

    def test_sealed_is_not_dev(self):
        self.pd["split"] = "sealed"
        with self.assertRaisesRegex(ContractError, "VALID development"):
            self.verify()

    def test_comparison_tracks_missing_optional_contracts(self):
        a, b = run_template("A"), run_template("B")
        self.assertEqual(compare_runs(a, b, "macro_F1")["protocol_field_coverage"], "FULL")
        b["level_id"] = "L2"
        with self.assertRaisesRegex(ContractError, "NOT_COMPARABLE"):
            compare_runs(a, b, "macro_F1")
        a.pop("level_id")
        b.pop("level_id")
        self.assertEqual(compare_runs(a, b, "macro_F1")["protocol_field_coverage"],
                         "PARTIAL_LEGACY")


if __name__ == "__main__":
    unittest.main()
