"""Only verifies RWF points to PD-RW's single historical-case index."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = "https://github.com/phr-devil/Problem-Data-Research-Workflow/blob/main/LESSONS/CASE_REGISTRY.md"


class CaseRouteTest(unittest.TestCase):
    def test_link_is_on_demand_and_not_a_second_science_policy(self):
        map_text = (ROOT / "docs/REPO_MAP.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agent = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(REF, map_text)
        self.assertIn(REF, readme)
        self.assertIn("RWF 不复制", map_text)
        self.assertNotIn("CASE_REGISTRY.md", agent)


if __name__ == "__main__":
    unittest.main()
