"""Static regression: optional post-algorithm audits preserve authorization and evidence scope."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


class PostAlgorithmScienceAuditTests(unittest.TestCase):
    def test_route_visible_without_eighth_skill(self):
        for name in ("README.md", "AGENTS.md", "docs/EXECUTION_POLICY.md",
                     "docs/ARCHITECTURE.md", "SOURCES.md",
                     "skills/05_algorithm/SKILL.md", "skills/06_decision/SKILL.md",
                     "skills/07_confirmation/SKILL.md"):
            with self.subTest(file=name):
                self.assertIn("POST_ALGORITHM_SCIENCE_AUDIT.md", read(name))

    def test_audit_requires_falsification_and_honest_splits(self):
        policy = read("docs/POST_ALGORITHM_SCIENCE_AUDIT.md")
        for phrase in ("UPGRADE_PILOT", "EVIDENCE_ONLY", "KEEP_ORIGINAL",
                       "UNKNOWN", "COMPETING_EXPLANATION",
                       "DISTINCT_PREDICTION", "sealed", "WRITING_LOCKED"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, policy)

    def test_keeps_original_writing_and_auth_lock(self):
        self.assertIn("Manuscript writing lock", read("docs/EXECUTION_POLICY.md"))
        self.assertIn("one minimal fair DEV", read("docs/EXECUTION_POLICY.md"))
        self.assertIn("do not invent new machine states", read("docs/POST_ALGORITHM_SCIENCE_AUDIT.md"))
        self.assertIn("No automatic paper title", read("docs/POST_ALGORITHM_SCIENCE_AUDIT.md"))


if __name__ == "__main__":
    unittest.main()
