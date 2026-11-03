"""v0.6: minimal context loading and delta-only state handoff.

No model, API, browser, file download or user research dataset is accessed.
"""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from core.brief import project_brief
from core.cli import main
from core.state import initial_state, record_event, save_state

ROOT = Path(__file__).resolve().parents[1]


class EfficiencyPolicyTests(unittest.TestCase):
    def test_single_shared_policy_and_on_demand_skills(self):
        policy_path = ROOT / "docs" / "EXECUTION_POLICY.md"
        policy = policy_path.read_text(encoding="utf-8")
        for essential in (
            "No automatic plots",
            "delta-only",
            "focused tests",
            "First negative Pilot",
            "authorization",
            "total real resource cost",
        ):
            self.assertIn(essential.lower(), policy.lower())
        entry = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/EXECUTION_POLICY.md", entry)
        self.assertIn("one", entry.lower())
        paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(paths), 7)
        for path in paths:
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                self.assertTrue(content.startswith("---\nname:"))
                self.assertIn("../../docs/EXECUTION_POLICY.md", content)
                self.assertIn("Handoff", content)
                self.assertNotIn("v0.3", content)
                self.assertNotIn("v0.4", content)
                self.assertNotIn("v0.5", content)

    def test_policy_avoids_hard_report_and_agent_gate(self):
        policy = (ROOT / "docs/EXECUTION_POLICY.md").read_text(encoding="utf-8")
        self.assertIn("not mandate multi-Agent voting", policy)
        self.assertIn("Do not generate a Markdown report after every command", policy)
        self.assertIn("Never invent Token or compute costs", policy)
        self.assertIn("independent confirmation", policy)

class CompactStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        save_state(self.path / "STATE.json", initial_state("demo", "Synthetic test only"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_snapshot_is_small_honest_and_read_only(self):
        info = project_brief(self.path)
        self.assertEqual(info["project_id"], "demo")
        self.assertEqual(info["phase"], "DISCOVERY")
        self.assertTrue(info["event_history_consistent"])
        self.assertEqual(info["token_gpu_cost"], "NOT_MEASURED")
        self.assertEqual(info["recent_events"], [])
        self.assertFalse((self.path / "EVENTS.jsonl").exists())

    def test_last_n_events_only_and_no_unbounded_logs(self):
        for i in range(6):
            record_event(self.path, "CODE_FAILURE", "x" * 350 + str(i))
        info = project_brief(self.path, recent=2)
        self.assertEqual(len(info["recent_events"]), 2)
        self.assertTrue(all(len(e["note"]) <= 160 for e in info["recent_events"]))
        self.assertTrue(info["event_history_consistent"])
        self.assertEqual(info["phase"], "DISCOVERY")  # note only
        self.assertEqual(len((self.path / "EVENTS.jsonl").read_text().splitlines()), 6)
        self.assertNotIn("x" * 200, json.dumps(info))

    def test_zero_events_and_invalid_window(self):
        record_event(self.path, "CODE_FAILURE", "Fix script parsing")
        self.assertEqual(project_brief(self.path, recent=0)["recent_events"], [])
        for invalid in (-1, 6, 1.5, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                project_brief(self.path, recent=invalid)

    def test_detect_broken_event_state_consistency(self):
        record_event(self.path, "CODE_FAILURE", "Found real regression")
        state = json.loads((self.path / "STATE.json").read_text())
        state["last_event_id"] = "stale"
        save_state(self.path / "STATE.json", state)
        info = project_brief(self.path)
        self.assertFalse(info["event_history_consistent"])
        self.assertEqual(len(info["recent_events"]), 1)

    def test_cli_brief(self):
        capture = io.StringIO()
        with redirect_stdout(capture):
            exit_code = main(["brief", "--dir", str(self.path), "--recent", "0"])
        self.assertEqual(exit_code, 0)
        result = json.loads(capture.getvalue())
        self.assertEqual(result["recent_events"], [])
        self.assertEqual(result["evidence_level"], "STATE_AND_EVENT_POINTERS_ONLY")
        self.assertEqual(result["token_gpu_cost"], "NOT_MEASURED")


if __name__ == "__main__":
    unittest.main()
