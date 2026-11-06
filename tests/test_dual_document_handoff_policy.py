"""Static policy test: RWF provides evidence but does not unlock manuscript prose."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DualDocumentHandoffTests(unittest.TestCase):
    def test_two_file_scope_and_user_permissions(self):
        text = (ROOT / "docs/PD_RW_DUAL_DOCUMENT_HANDOFF.md").read_text(encoding="utf-8")
        for value in ("RESEARCH_RECORD.md", "PAPER_BLUEPRINT.md", "H1/H2",
                      "EXP/Run/Claim", "WRITING_LOCKED", "user reviews",
                      "separately authorizes", "explicit drawing request",
                      "SEALED/CONFIRMATION", "NOT_RUN", "negative"):
            self.assertIn(value, text)

    def test_entrypoints_link_handoff(self):
        for name in ("AGENTS.md", "README.md", "docs/EXECUTION_POLICY.md"):
            with self.subTest(path=name):
                self.assertIn("PD_RW_DUAL_DOCUMENT_HANDOFF.md",
                              (ROOT / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
