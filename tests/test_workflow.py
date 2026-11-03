"""Structural regression tests (not research performance tests)."""
import tempfile
import unittest
from pathlib import Path
from core.contracts import ContractError, validate
from core.router import ROUTES, route
from core.state import initial_state, load_state, record_event, save_state

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.state = initial_state("sensor-study", "Study scientific sensor generalization")

    def test_routes_reference_real_skills_and_never_execute(self):
        root = Path(__file__).resolve().parents[1]
        for event in ROUTES:
            decision = route(self.state, event)
            self.assertTrue((root / decision["skill"]).is_file())
            self.assertFalse(decision["executes_external_action"])

    def test_no_gain_is_not_project_stop(self):
        self.assertEqual(route(self.state, "NO_GAIN")["phase"], "DECISION")

    def test_state_does_not_authorize_confirmation(self):
        self.state["authorization_refs"] = ["STATE says approved"]
        result = route(self.state, "CONFIRM_REQUEST")
        self.assertFalse(result["executes_external_action"])
        self.assertTrue(any("original user" in w for w in result["warnings"]))

    def test_draft_unknown_allowed_active_requires_protocol(self):
        task = {"schema_version":"0.1","task_id":"T1","question":"Can we transfer?", "status":"DRAFT"}
        validate("task", task)
        task["status"] = "ACTIVE"
        with self.assertRaises(ContractError):
            validate("task", task)

    def test_exploratory_experiment_cannot_use_sealed_split(self):
        exp = {"schema_version":"0.1","experiment_id":"E1","task_id":"T1",
               "hypothesis":"H","evaluator_ref":"eval","split":"sealed",
               "budget":{"gpu_hours_max":1},"decision_if_positive":"keep",
               "decision_if_negative":"review"}
        with self.assertRaises(ContractError):
            validate("experiment", exp)

    def test_not_run_cannot_have_metrics(self):
        run = {"schema_version":"0.1","run_id":"R1","task_id":"T1",
               "protocol_id":"P1","dataset_version":"d1","code_commit":"c1",
               "evaluator_version":"e1","status":"NOT_RUN","split":"dev",
               "metrics":{"F1":0.9},"artifact_refs":[]}
        with self.assertRaises(ContractError):
            validate("run", run)

    def test_sealed_run_requires_refs(self):
        run = {"schema_version":"0.1","run_id":"R1","task_id":"T1",
               "protocol_id":"P1","dataset_version":"d1","code_commit":"c1",
               "evaluator_version":"e1","status":"VALID","split":"sealed",
               "metrics":{},"artifact_refs":[]}
        with self.assertRaises(ContractError):
            validate("run", run)

    def test_confirmed_claim_requires_refs(self):
        claim = {"schema_version":"0.1","claim_id":"C1","task_id":"T1",
                 "statement":"Novel mechanism","status":"CONFIRMED",
                 "evidence_run_ids":[],"nearest_work":[]}
        with self.assertRaises(ContractError):
            validate("claim", claim)

    def test_resume_and_append_only_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            save_state(p / "STATE.json", self.state)
            record_event(p, "SEARCH_READY", "Sources reported; no actual artifact")
            record_event(p, "DATA_READY", "Metadata reported; no actual artifact")
            self.assertEqual(load_state(p / "STATE.json")["phase"], "DISCOVERY")
            self.assertEqual(len((p / "EVENTS.jsonl").read_text().splitlines()), 2)

if __name__ == "__main__":
    unittest.main()
