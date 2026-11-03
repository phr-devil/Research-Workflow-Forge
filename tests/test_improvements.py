"""v0.2: scientific routing, provenance and run-comparison regression cases."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from core.comparison import compare_runs
from core.contracts import ContractError, validate
from core.state import initial_state, load_state, record_event, save_state
from core.receipts import fingerprint_file
from core.state import history_status

def valid_run(name="A", value=0.8):
    return {"schema_version":"0.1","run_id":name,"task_id":"T1","protocol_id":"P1",
            "dataset_version":"D1","code_commit":"abc123", "evaluator_version":"EV1",
            "status":"VALID","split":"dev","metrics":{"macro_F1":value},
            "artifact_refs":[f"runs/{name}/log.json"],"group_split":"subject-independent",
            "sample_ids_hash":"ids-sha256", "legal_inputs":["IMU","past-window"]}

def valid_evidence():
    return {"schema_version":"0.1","query":"sensor generalization","retrieved_at":"2026-11-03T12:00:00+00:00",
            "verification":"METADATA_ONLY","sources_checked":["openalex"],
            "source_errors":[],"records":[{"record_id":"r123","title":"Example record (fixture)",
                                             "sources":["openalex"],"verification":"METADATA_ONLY"}]}

def valid_dataset():
    return {"schema_version":"0.1","datasets":[{"dataset_id":"D1","role":"DEV",
            "source_url":"https://example.org/dataset","group_unit":"subject",
            "label_status":"UNKNOWN"}]}

class EvidenceTests(unittest.TestCase):
    def test_empty_evidence_is_not_search_ready(self):
        obj=valid_evidence()
        obj["records"]=[]
        with self.assertRaises(ContractError):
            validate("evidence",obj)

    def test_evidence_source_required(self):
        obj=valid_evidence()
        obj["records"][0]["sources"]=[]
        with self.assertRaises(ContractError):
            validate("evidence",obj)

    def test_no_dataset_possible_for_theory_with_proof_path(self):
        obj={"schema_version":"0.1","datasets":[],"proof_path":"formal-proof-plan.md"}
        validate("dataset",obj)
        obj.pop("proof_path")
        with self.assertRaises(ContractError):
            validate("dataset",obj)

    def test_invalid_experiment_budget_nan(self):
        e={"schema_version":"0.1","experiment_id":"E1","task_id":"T1",
           "hypothesis":"H","evaluator_ref":"E", "split":"dev",
           "decision_if_positive":"GO", "decision_if_negative":"DIAGNOSE",
           "budget":{"gpu_hours_max":float("nan")}}
        with self.assertRaises(ContractError):
            validate("experiment",e)

class CompareTests(unittest.TestCase):
    def test_valid_same_protocol_and_group(self):
        a=valid_run("A",0.80)
        b=valid_run("B",0.83)
        output=compare_runs(a,b,"macro_F1")
        self.assertAlmostEqual(output["raw_delta"],0.03)
        self.assertEqual(output["comparison_status"],"DEVELOPMENT_ONLY")
        self.assertFalse(output["scientific_claim_confirmed"])

    def test_lower_is_better(self):
        a=valid_run("A",3.1);b=valid_run("B",2.9)
        self.assertGreater(compare_runs(a,b,"macro_F1",lower_is_better=True)["improvement_direction_delta"],0)

    def test_group_or_evaluator_differences_rejected(self):
        for field,value in (("sample_ids_hash","other"),("group_split","time-split"),
                            ("dataset_version","D2"),("evaluator_version","EV2"),
                            ("protocol_id","P2"),("task_id","T2"),("legal_inputs",["other"])):
            with self.subTest(field=field):
                a=valid_run(); b=valid_run("B")
                b[field]=value
                with self.assertRaisesRegex(ContractError,"NOT_COMPARABLE"):
                    compare_runs(a,b,"macro_F1")

    def test_sealed_comparison_rejected(self):
        a=valid_run(); b=valid_run("B")
        for run in (a,b):
            run["split"]="sealed"
            run["frozen_protocol_ref"]="freeze.json"
            run["authorization_ref"]="real-user-message"
        with self.assertRaisesRegex(ContractError,"sealed"):
            compare_runs(a,b,"macro_F1")

    def test_nan_metric_and_missing_raw_evidence_rejected(self):
        run=valid_run();run["metrics"]={"macro_F1":math.nan}
        with self.assertRaises(ContractError):
            validate("run",run)
        run=valid_run();run["artifact_refs"]=[]
        with self.assertRaises(ContractError):
            validate("run",run)

    def test_confirmed_claim_requires_nonempty_support(self):
        claim={"schema_version":"0.1","claim_id":"C1","task_id":"T1",
               "statement":"Novel result", "status":"CONFIRMED","evidence_run_ids":[],
               "nearest_work":[],"confirmation_ref":"sealed-run","frozen_protocol_ref":"protocol"}
        with self.assertRaises(ContractError):
            validate("claim",claim)

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.p=Path(self.t.name)/"study"
        save_state(self.p/"STATE.json",initial_state("study","Find a research task"))

    def tearDown(self):
        self.t.cleanup()

    def file(self,name,obj):
        if isinstance(obj,dict) and obj.get("run_id") and obj.get("status") in {"VALID","INCONCLUSIVE"}:
            obj=dict(obj)
            hashes={}
            for ref in obj["artifact_refs"]:
                logfile=self.p/ref
                logfile.parent.mkdir(parents=True,exist_ok=True)
                logfile.write_text("fixture raw log",encoding="utf-8")
                hashes[ref]=fingerprint_file(logfile)
            obj["artifact_hashes"]=hashes
        p=self.p/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(obj),encoding="utf-8")
        return p

    def test_note_only_never_advances_phase(self):
        result=record_event(self.p,"DATA_READY","I think data are ready")
        self.assertEqual(result["record_level"],"ROUTING_NOTE_ONLY")
        self.assertEqual(load_state(self.p/"STATE.json")["phase"],"DISCOVERY")
        self.assertTrue(history_status(self.p)["consistent"])

    def test_source_backed_handoffs_and_history(self):
        a=self.file("EVIDENCE.json",valid_evidence())
        result=record_event(self.p,"SEARCH_READY","Provider metadata returned",a)
        self.assertEqual(result["record_level"],"ARTIFACT_STRUCTURAL_ONLY")
        self.assertEqual(load_state(self.p/"STATE.json")["phase"],"EVIDENCE")
        d=self.file("DATA.json",valid_dataset())
        record_event(self.p,"DATA_READY","Dataset record saved, label still unknown",d)
        self.assertEqual(load_state(self.p/"STATE.json")["phase"],"PROBLEM")
        self.assertTrue(history_status(self.p)["consistent"])
        self.assertEqual(len(load_state(self.p/"STATE.json")["evidence_refs"]),2)
        self.assertEqual(len((self.p/"EVENTS.jsonl").read_text().splitlines()),2)

    def test_draft_cannot_be_marked_task_defined(self):
        task={"schema_version":"0.1","task_id":"T1","question":"Test?","status":"DRAFT"}
        with self.assertRaises(ContractError):
            record_event(self.p,"TASK_DEFINED","Task done",self.file("TASK.json",task))
        self.assertFalse((self.p/"EVENTS.jsonl").exists())

    def test_event_status_cannot_be_faked(self):
        with self.assertRaises(ContractError):
            record_event(self.p,"RUN_INVALID","Failed but recorded VALID",
                         self.file("RUN.json",valid_run()))

    def test_external_file_and_unsupported_artifact_rejected(self):
        outside=Path(self.t.name)/"outside.json"
        outside.write_text(json.dumps(valid_evidence()))
        with self.assertRaises(ValueError):
            record_event(self.p,"SEARCH_READY","Use external file",outside)
        with self.assertRaises(ValueError):
            record_event(self.p,"CODE_FAILURE","Unsupported evidence file",self.file("D.json",valid_dataset()))

    def test_cross_task_run_cannot_replace_active_task(self):
        state=load_state(self.p/"STATE.json")
        state["active_task_id"]="T1"
        save_state(self.p/"STATE.json",state)
        other=valid_run("R-other")
        other["task_id"]="T2"
        with self.assertRaisesRegex(ContractError,"task_id disagrees"):
            record_event(self.p,"RUN_RESULT","Wrong task",self.file("RUN.json",other))

    def test_run_handoff_needs_active_task(self):
        with self.assertRaisesRegex(ContractError,"active Task"):
            record_event(self.p,"BASELINE_VALID","No actual Task",
                         self.file("RUN.json",valid_run()))

    def test_valid_task_run_handoff(self):
        task={"schema_version":"0.1","task_id":"T1","question":"Generalize across subjects",
              "status":"ACTIVE","protocol_id":"P1","metric":"macro_F1",
              "group_split":"subject-independent","holdout_policy":"sealed-persons",
              "baseline":"Ridge","legal_inputs":["IMU"],"data_refs":["D1"],"nearest_work":[]}
        record_event(self.p,"TASK_DEFINED","Task protocol defined",self.file("TASK.json",task))
        self.assertEqual(load_state(self.p/"STATE.json")["active_task_id"],"T1")
        record_event(self.p,"BASELINE_VALID","Recorded real baseline provenance",
                     self.file("RUN.json",valid_run()))
        self.assertIsNone(load_state(self.p/"STATE.json")["best_valid_run_id"])  # selection is separate

    def test_event_log_state_mismatch_detectable(self):
        record_event(self.p,"NO_GAIN","Only a note, no empirical proof")
        state=load_state(self.p/"STATE.json")
        state["last_event_id"]="wrong"
        save_state(self.p/"STATE.json",state)
        self.assertFalse(history_status(self.p)["consistent"])

if __name__ == "__main__":
    unittest.main()
