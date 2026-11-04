"""Static policy regression: research evidence readiness is not writing authorization."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def doc(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ManuscriptWritingGateTests(unittest.TestCase):
    def test_authority_and_entrypoints(self):
        policy = doc("docs/EXECUTION_POLICY.md")
        self.assertIn("Manuscript writing lock (highest-priority", policy)
        self.assertIn("WRITING_LOCKED", policy)
        self.assertIn("explicitly review/accept", policy)
        self.assertIn("separately and explicitly authorize writing", policy)
        self.assertIn("MANUSCRIPT_WRITE_AUTH", policy)
        self.assertIn("an additional gate on authorized research", policy)
        self.assertIn("manuscript writing lock", doc("AGENTS.md"))
        self.assertIn("Mandatory manuscript writing lock", doc("README.md"))

    def test_scientific_routes_do_not_unlock_drafts(self):
        decision = doc("skills/06_decision/SKILL.md")
        confirmation = doc("skills/07_confirmation/SKILL.md")
        self.assertIn("never authorizes a paper outline or draft", decision)
        self.assertIn("do **not** generate a paper outline", confirmation)
        self.assertNotIn("An early outline may contain", confirmation)
        self.assertIn("evidence completion", doc("docs/EXECUTION_POLICY.md").lower())

    def test_no_machine_status_as_user_permission(self):
        self.assertIn("never writing approval", doc("docs/CONTRACTS.md"))
        self.assertIn("never trigger manuscript text", doc("docs/ARCHITECTURE.md"))


if __name__ == "__main__":
    unittest.main()
