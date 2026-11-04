"""Real file checks, including tampering and path/holdout rejection."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from core.contracts import ContractError
from tools.external_artifact_preflight import verify_external_artifacts


class ExternalArtifactTests(unittest.TestCase):
    def test_streamed_digest_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = b"external GPU checkpoint output" * 100
            (root / "predictions.json").write_bytes(payload)
            record = {"split": "dev", "artifacts": [
                {"path": "predictions.json", "kind": "predictions",
                 "sha256": hashlib.sha256(payload).hexdigest()}]}
            result = verify_external_artifacts(root, record)
            self.assertEqual(result["status"], "ARTIFACT_HASHES_VERIFIED_ONLY")
            self.assertFalse(result["metric_verification"])
            self.assertFalse(result["scientific_confirmation"])
            (root / "predictions.json").write_bytes(payload + b"tampered")
            with self.assertRaises(ContractError):
                verify_external_artifacts(root, record)

    def test_scope_or_path_violation_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "safe.log").write_text("test", encoding="utf-8")
            sha = hashlib.sha256(b"test").hexdigest()
            row = {"path": "safe.log", "kind": "log", "sha256": sha}
            for bad in (
                {"split": "sealed", "artifacts": [row]},
                {"split": "dev", "artifacts": [{**row, "path": "../safe.log"}]},
                {"split": "dev", "artifacts": [row, row]},
                {"split": "dev", "artifacts": [{**row, "kind": "data"}]},
            ):
                with self.subTest(bad=bad):
                    with self.assertRaises(ContractError):
                        verify_external_artifacts(root, bad)


if __name__ == "__main__":
    unittest.main()
