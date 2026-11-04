"""Static regression: research success requires credible Q2+ potential, not acceptance."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class Q2PublicationGoalTests(unittest.TestCase):
    def test_policy_distinguishes_success_and_acceptance(self):
        policy = read("docs/EXECUTION_POLICY.md")
        for phrase in ("Minimum publication target: JCR Q2+ potential",
                       "Q2_POTENTIAL_SUPPORTED", "Q2_UPGRADE_POSSIBLE",
                       "Q2_UNCERTAIN", "BELOW_Q2_TARGET", "Q1",
                       "not required and cannot be promised",
                       "WRITING_LOCKED", "not new CLI states"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, policy)

    def test_stages_keep_scientific_venue_goal(self):
        for path in ("AGENTS.md", "README.md", "docs/ARCHITECTURE.md",
                     "docs/POST_ALGORITHM_SCIENCE_AUDIT.md",
                     "skills/03_problem_design/SKILL.md",
                     "skills/05_algorithm/SKILL.md",
                     "skills/06_decision/SKILL.md",
                     "skills/07_confirmation/SKILL.md"):
            with self.subTest(path=path):
                self.assertIn("Q2", read(path))

    def test_manuscript_remains_locked(self):
        self.assertIn("Manuscript writing lock",
                      read("docs/EXECUTION_POLICY.md"))
        self.assertIn("MANUSCRIPT_WRITE_AUTH",
                      read("docs/EXECUTION_POLICY.md"))
        self.assertIn("WRITING_LOCKED", read("AGENTS.md"))


if __name__ == "__main__":
    unittest.main()
