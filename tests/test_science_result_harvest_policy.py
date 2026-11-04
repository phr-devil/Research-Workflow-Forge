"""Test that research-value harvesting stays within established Skills and writing lock."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class ScienceResultHarvestPolicyTests(unittest.TestCase):
    def test_stage_integration(self):
        files = ("AGENTS.md", "README.md", "docs/EXECUTION_POLICY.md",
                 "docs/POST_ALGORITHM_SCIENCE_AUDIT.md",
                 "docs/HIGH_VALUE_RESEARCH_ENGINEERING.md",
                 "skills/05_algorithm/SKILL.md", "skills/06_decision/SKILL.md",
                 "skills/07_confirmation/SKILL.md", "docs/ARTIFACT_CONTRACT.md")
        for path in files:
            with self.subTest(path=path):
                self.assertIn("SCIENCE_RESULT_HARVEST.md",
                              (ROOT / path).read_text(encoding="utf-8"))

    def test_separate_articulation_and_scientific_proof(self):
        policy = (ROOT / "docs/SCIENCE_RESULT_HARVEST.md").read_text(encoding="utf-8")
        for keyword in ("ARTICULATION_GAP", "EVIDENCE_GAP", "BOTH", "NONE",
                        "EXPLORATORY", "WRITING_LOCKED", "Q2",
                        "source", "PD-RW"):
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, policy)
        self.assertIn("WRITING_LOCKED", (ROOT / "docs/EXECUTION_POLICY.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
