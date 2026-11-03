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



class RawDevRecomputationTests(unittest.TestCase):
    """End-to-end synthetic group-held-out regression; no training or sealed data."""

    def setUp(self):
        import csv
        import hashlib
        from core.metric_verify import sample_hash, verify_metrics
        from core.receipts import fingerprint_file
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / "forge"
        self.pd_root = self.base / "pd"
        self.project.mkdir()
        self.pd_root.mkdir()
        rows = [(f"s{g}-{j}", f"G{g}", g+j)
                for g in range(4) for j in range(2)]
        with (self.project / "data.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["sid", "grp", "target"])
            w.writerows(rows)
        sha = fingerprint_file(self.project / "data.csv")
        manifest = {"schema_version": "0.1", "datasets": [{
            "dataset_id": "D", "role": "DEV", "source_url": "https://example.invalid/data",
            "group_unit": "person", "label_status": "VERIFIED",
            "local_path": "data.csv", "sha256": sha, "label_column": "target",
            "group_column": "grp", "sample_id_column": "sid",
        }]}
        (self.project / "manifest.json").write_text(json.dumps(manifest))
        split = {"train_groups": ["G0", "G1"], "dev_groups": ["G2", "G3"]}
        (self.project / "split.json").write_text(json.dumps(split))
        split_sha = fingerprint_file(self.project / "split.json")
        dev = [(i, r) for i, r in enumerate(rows) if r[1] in {"G2","G3"}]
        pred = [{"row_index":i, "prediction":float(r[2])+0.5} for i,r in dev]
        (self.project / "pred.json").write_text(json.dumps(pred))
        (self.pd_root / "pred.json").write_bytes((self.project / "pred.json").read_bytes())
        (self.project / "log.json").write_text('{"fixture":true}')
        forge = {
            "schema_version": "0.1", "run_id": "R1", "task_id": "T",
            "protocol_id": "P", "dataset_version": sha,
            "code_commit": "synthetic", "evaluator_version": "eval-v1",
            "status": "VALID", "split": "dev", "metrics": {"MAE": 0.0, "RMSE": 0.0},
            "group_split": "pinned-groups:" + split_sha,
            "sample_ids_hash": sample_hash([r[0] for i,r in dev]),
            "legal_inputs": ["sensor"], "level_id": "L1", "k_unit": "sample",
            "support_query_policy": "nonoverlap", "k_target_labels": 1,
            "inference_visible_info": "past_only",
            "artifact_refs": ["pred.json", "log.json"],
            "artifact_hashes": {
                p: fingerprint_file(self.project / p) for p in ("pred.json", "log.json")},
            "metric_spec": {
                "format": "forge-dev-regression-v1", "predictions_ref": "pred.json",
                "manifest_ref": "manifest.json",
                "manifest_sha256": fingerprint_file(self.project / "manifest.json"),
                "dataset_id": "D", "split_ref": "split.json",
                "split_sha256": split_sha, "aggregation": "group_mean",
            },
        }
        forge["metrics"] = verify_metrics(self.project, forge, check_reported=False)["computed"]
        self.forge_run = self.project / "RUN.json"
        self.forge_run.write_text(json.dumps(forge))
        pd = {k:v for k,v in forge.items()
              if k not in {"schema_version", "code_commit", "artifact_refs",
                           "artifact_hashes", "metric_spec"}}
        pd["artifact_refs"] = {"predictions": "pred.json",
                                "metrics": "metrics.json", "code": "model.py"}
        self.pd_run = self.pd_root / "RUN.json"
        self.pd_run.write_text(json.dumps(pd))

    def test_real_development_metric_recomputation(self):
        result = verify_pd_rw_handoff(
            self.project, Path("RUN.json"), self.pd_root, Path("RUN.json"), "MAE")
        self.assertEqual(result["status"], "METRIC_VERIFIED_DEV_ONLY")
        self.assertEqual(result["protocol_field_coverage"], "FULL")
        self.assertAlmostEqual(result["recomputed_value"], 0.5)

    def test_tampered_prediction_is_rejected(self):
        (self.pd_root / "pred.json").write_text('[{"row_index":9,"prediction":999}]')
        with self.assertRaisesRegex(ContractError, "PREDICTION_BYTES_MISMATCH"):
            verify_pd_rw_handoff(self.project, self.forge_run,
                                 self.pd_root, self.pd_run, "MAE")

    def test_tampered_claimed_metric_is_rejected(self):
        pd = json.loads(self.pd_run.read_text())
        pd["metrics"]["MAE"] = 0.0
        self.pd_run.write_text(json.dumps(pd))
        with self.assertRaisesRegex(ContractError, "RECOMPUTED_METRIC_MISMATCH"):
            verify_pd_rw_handoff(self.project, self.forge_run,
                                 self.pd_root, self.pd_run, "MAE")

if __name__ == "__main__":
    unittest.main()
