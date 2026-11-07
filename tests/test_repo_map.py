"""RWF index-only repo map: local link correctness and unchanged authority."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


class RepositoryMapTests(unittest.TestCase):
    def test_index_is_opt_in_and_small(self):
        index = ROOT / "docs/REPO_MAP.md"
        data = index.read_text(encoding="utf-8")
        self.assertIn("INDEX_ONLY", data)
        self.assertLess(len(data), 3200)
        self.assertIn("REPO_MAP.md", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn("EXECUTION_POLICY.md", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))

    def test_links_resolve_without_migration(self):
        index = ROOT / "docs/REPO_MAP.md"
        for href in LINK.findall(index.read_text(encoding="utf-8")):
            if href.startswith(("https:", "http:", "#", "mailto:")):
                continue
            target = (index.parent / href.split("#")[0]).resolve()
            self.assertTrue(target.is_relative_to(ROOT.resolve()))
            self.assertTrue(target.exists(), href)

    def test_figure_permissions_and_legacy_paths_preserved(self):
        for path in ("docs/FIGURE_QA_CONTRACT.md", "docs/FIGURE_STYLE_SYSTEM.md",
                     "styles/figure_theme.json", "styles/figure_theme_pdrw.json",
                     "tools/figure_templates.py", "tools/figure_qa.py",
                     "docs/EXECUTION_POLICY.md"):
            self.assertTrue((ROOT / path).is_file(), path)
        text = (ROOT / "docs/FIGURE_QA_CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("explicit", text.lower())
        self.assertIn("no automatic", text.lower())


if __name__ == "__main__":
    unittest.main()
