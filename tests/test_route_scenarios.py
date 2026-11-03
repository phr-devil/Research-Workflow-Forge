"""Router behavior fixtures only; not a simulated research-success benchmark."""
import json
import unittest
from pathlib import Path
from core.router import route
from core.state import initial_state

class RouteScenarioTests(unittest.TestCase):
    def test_pinned_routes(self):
        file=Path(__file__).resolve().parents[1]/"evals"/"route_scenarios.json"
        data=json.loads(file.read_text(encoding="utf-8"))
        state=initial_state("fixture","research evaluation")
        for case in data["scenarios"]:
            with self.subTest(event=case["event"]):
                output=route(state,case["event"])
                self.assertEqual(output["skill"],case["expected_skill"])
                self.assertEqual(output["phase"],case["expected_phase"])
                self.assertFalse(output["executes_external_action"])

if __name__=="__main__":
    unittest.main()
