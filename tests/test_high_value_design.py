"""Policy integration checks, NOT automated proof of scientific novelty."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class HighValueDesignTests(unittest.TestCase):
    def test_existing_skills_link_quality_guide(self):
        names = ("AGENTS.md", "README.md", "docs/EXECUTION_POLICY.md",
                 "docs/DISCOVERY_PLAYBOOK.md", "docs/POST_ALGORITHM_SCIENCE_AUDIT.md",
                 "skills/01_search/SKILL.md", "skills/02_evidence_data/SKILL.md",
                 "skills/03_problem_design/SKILL.md", "skills/04_feasibility/SKILL.md",
                 "skills/05_algorithm/SKILL.md", "skills/06_decision/SKILL.md")
        for name in names:
            with self.subTest(path=name):
                self.assertIn("HIGH_VALUE_RESEARCH_ENGINEERING",
                              (ROOT / name).read_text(encoding="utf-8"))

    def test_value_discriminability_and_authority(self):
        doc = (ROOT / "docs/HIGH_VALUE_RESEARCH_ENGINEERING.md").read_text(encoding="utf-8")
        for needle in ("COMPETING", "DISTINCT_PREDICTION", "CONFOUNDED",
                       "Q2", "WRITING_LOCKED", "NEXT_ACTION_POLICY",
                       "Optuna", "RD-Agent"):
            with self.subTest(needle=needle):
                self.assertIn(needle, doc)
        self.assertIn("research_success_rate", (ROOT / "adapters/opportunity_review.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
