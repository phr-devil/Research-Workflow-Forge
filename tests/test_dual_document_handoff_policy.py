"""RWF's compact entry / two-file handoff; structure checks only, no images or experiments."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DualDocumentHandoffTests(unittest.TestCase):
    def test_two_file_scope_and_user_permissions(self):
        text = (ROOT / "docs/PD_RW_DUAL_DOCUMENT_HANDOFF.md").read_text(encoding="utf-8")
        for value in ("RESEARCH_RECORD.md", "PAPER_BLUEPRINT.md", "H1/H2",
                      "EXP/Run/Claim", "WRITING_LOCKED", "user reviews",
                      "separately authorizes", "explicit drawing request",
                      "SEALED/CONFIRMATION", "NOT_RUN", "negative",
                      "SEC_ID", "SOURCE_CONFLICT", "no new phase"):
            with self.subTest(value=value):
                self.assertIn(value.lower(), text.lower())

    def test_entrypoints_and_read_order(self):
        for name in ("AGENTS.md", "README.md", "docs/EXECUTION_POLICY.md"):
            with self.subTest(path=name):
                self.assertIn("PD_RW_DUAL_DOCUMENT_HANDOFF.md",
                              (ROOT / name).read_text(encoding="utf-8"))
        agent = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for phrase in ("最短读取顺序", "RESEARCH_RECORD.md", "PAPER_BLUEPRINT.md",
                       "SEC_ID", "STATE.json", "NEXT_ACTION_POLICY.md",
                       "SCIENCE_RESULT_HARVEST.md", "POST_ALGORITHM_SCIENCE_AUDIT.md"):
            self.assertIn(phrase, agent)

    def test_compact_entry_and_lazy_policy(self):
        agent = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        policy = (ROOT / "docs/EXECUTION_POLICY.md").read_text(encoding="utf-8")
        self.assertLess(len(agent), 3500, "RWF AGENTS should only route to one Skill")
        for marker in ("RULE_REPO", "RULE_COMMIT", "LOADED_FILES",
                       "RULE_VERSION_UNVERIFIED", "七个 Skills"):
            self.assertIn(marker, agent)
        self.assertIn("only the sections applicable to the current blocker", policy)
        self.assertNotIn("Read it once per research session", policy)

    def test_original_seven_skills_and_authority_retained(self):
        entry = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for sid in ("01_search", "02_evidence_data", "03_problem_design",
                    "04_feasibility", "05_algorithm", "06_decision",
                    "07_confirmation"):
            self.assertIn(sid, entry)
        for boundary in ("Q2", "SEALED", "WRITING_LOCKED", "用户明确要求",
                         "HIGH_VALUE_RESEARCH_ENGINEERING"):
            self.assertIn(boundary, entry)


if __name__ == "__main__":
    unittest.main()


class DiagnosticFigurePermissionRegression(unittest.TestCase):
    def test_no_implicit_diagnostic_chart(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("make a small diagnostic chart only when needed to decide", readme)
        self.assertIn("do not generate any image", readme)
        agent = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("用户明确要求绘制/修改具体图片", agent)

    def test_rwf_handoff_does_not_erase_concurrent_project_work(self):
        guide = (ROOT / "docs/PD_RW_DUAL_DOCUMENT_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("concurrent Agent edits", guide)
        self.assertIn("legacy projects", guide)
        self.assertIn("actual original user permission", guide)
