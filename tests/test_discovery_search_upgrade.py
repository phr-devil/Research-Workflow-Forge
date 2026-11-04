"""Keep early discovery comparative and authority boundaries source-aware."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DiscoverySearchUpgradeTests(unittest.TestCase):
    def test_search_has_competing_premise_and_falsification(self):
        for f in ("AGENTS.md", "skills/01_search/SKILL.md",
                  "docs/HIGH_VALUE_RESEARCH_ENGINEERING.md",
                  "docs/EXECUTION_POLICY.md"):
            with self.subTest(file=f):
                self.assertIn("COMPETING_CHOICE",
                              (ROOT / f).read_text(encoding="utf-8"))

    def test_pre_download_and_backtrack_are_separate(self):
        self.assertIn("PRE_DOWNLOAD_SCIENCE_FIT",
                      (ROOT / "skills/02_evidence_data/SKILL.md").read_text(encoding="utf-8"))
        self.assertIn("PREDOWNLOAD_ASSUMPTION_REFUTED",
                      (ROOT / "skills/03_problem_design/SKILL.md").read_text(encoding="utf-8"))
        contract = (ROOT / "docs/ARTIFACT_CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("NOT a metric/Run handoff", contract)
        self.assertIn("original user authorization", contract.lower())


if __name__ == "__main__":
    unittest.main()
