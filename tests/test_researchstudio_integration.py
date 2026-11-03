"""Unit tests: vendored paper search + novelty precheck + plan are real but not science claims."""
import json
import tempfile
import unittest
from pathlib import Path

from adapters.researchstudio_search import VENDOR, search_papers
from adapters.novelty_check import fingerprint, prepare_review
from adapters.experiment_plan import prepare_experiment
from core.contracts import ContractError, validate
from core.state import initial_state, save_state, record_event, load_state

def _paper(title, doi, source, year=2025):
    return {"title": title, "doi": doi, "year": year, "authors": ["A. Example"],
            "abstract": "Sensors changing across batches", "source": source,
            "citation_count": 2, "venue": "Synthetic Fixture",
            "url": "https://doi.org/" + doi}

def _evidence():
    return search_papers(["sensor drift compensation"], sources=("crossref", "open_alex"),
        start_year=2023, end_year=2026, limit=3,
        worker=lambda s, q, a, b, n: {"source":s, "papers":[
            _paper("Concentration aware sensor drift", "10.1234/example", s)], "errors":[]})

def _active_task():
    return {"schema_version":"0.1", "task_id":"T1", "status":"ACTIVE",
        "question":"Can we learn drift adaptation from legal concentration-aware data?",
        "protocol_id":"P1", "metric":"macro_F1", "group_split":"batch-separated",
        "holdout_policy":"batches held out before task search", "baseline":"Ridge",
        "legal_inputs":["sensor readings", "observed concentration"],
        "data_refs":["official source"], "nearest_work":[]}

class VendorSearchTests(unittest.TestCase):
    def test_upstream_is_present(self):
        for name in ("source_worker.py", "search_papers.py", "postprocess.py",
                     "selftest_postprocess.py", "selftest_runtime.py"):
            self.assertTrue((VENDOR / name).is_file())

    def test_upstream_dedup_and_source_provenance(self):
        result = _evidence()
        self.assertEqual(result["retrieval_state"], "COMPLETE")
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(set(result["records"][0]["sources"]), {"open_alex", "crossref"})
        self.assertEqual(result["verification"], "METADATA_ONLY")
        self.assertTrue(result["records"][0]["record_id"])
        validate("evidence", result)

    def test_provider_failure_retained_not_hidden(self):
        def worker(s, q, a, b, n):
            if s=="crossref":
                raise RuntimeError("rate limit")
            return {"source": s, "papers": [_paper("A real metadata record","10.1234/foo",s)], "errors":[]}
        out=search_papers(["sensor drift"],sources=("crossref","open_alex"),
                          start_year=2022,end_year=2026,limit=3,worker=worker)
        self.assertEqual(out["retrieval_state"], "PARTIAL")
        self.assertEqual(out["sources_checked"], ["open_alex"])
        self.assertEqual(out["source_errors"][0]["provider"], "crossref")

    def test_all_providers_failure_not_success(self):
        def fail(s,q,a,b,n):
            raise RuntimeError("no network")
        with self.assertRaises(RuntimeError):
            search_papers(["sensor drift"],sources=("crossref","open_alex"),
                          limit=2,worker=fail)

    def test_empty_provider_results_do_not_pass_handoff(self):
        out=search_papers(["sensor drift"],sources=("crossref",),
                          limit=2,worker=lambda s,q,a,b,n:{"source":s,"papers":[],"errors":[]})
        self.assertEqual(out["records"],[])
        with self.assertRaises(ContractError):
            validate("evidence",out)

    def test_invalid_unbounded_search_rejected(self):
        with self.assertRaises(ValueError):
            search_papers(["sensor"],limit=120,worker=lambda *a:None)
        with self.assertRaises(ValueError):
            search_papers(["a"],worker=lambda *a:None)

class ScientificHandoffTests(unittest.TestCase):
    def test_novelty_is_not_auto_confirmed(self):
        t=_active_task()
        evidence=_evidence()
        review=prepare_review(t,evidence, mechanism="batch-conditional alignment",
                expected_difference="measurable real shift correction")
        validate("novelty",review)
        self.assertEqual(review["status"],"UNVERIFIED")
        self.assertEqual(review["closest_candidates"][0]["overlap_verdict"],"UNKNOWN")
        self.assertEqual(review["input_fingerprints"]["task"],fingerprint(t))
        self.assertFalse(any(item.get("fulltext_review")=="DONE" for item in review["closest_candidates"]))

    def test_review_stale_if_task_changes(self):
        t=_active_task()
        rev=prepare_review(t,_evidence(),mechanism="h",expected_difference="measurable delta")
        t["question"]="Different scientific question"
        with self.assertRaisesRegex(ValueError,"stale"):
            prepare_experiment(t,hypothesis="h",evaluator_ref="frozen evaluator",
                gpu_hours_max=0.25,positive="keep",negative="diagnose",novelty_review=rev)

    def test_experiment_valid_plan_never_authorizes_training(self):
        task=_active_task()
        rev=prepare_review(task,_evidence(),mechanism="h",expected_difference="d")
        plan=prepare_experiment(task,hypothesis="A vs B",evaluator_ref="eval-v1",
             gpu_hours_max=0.25,positive="check group effect",negative="fix or pivot",
             novelty_review=rev)
        validate("experiment",plan)
        self.assertEqual(plan["split"],"dev")
        self.assertEqual(plan["status"],"PLAN_ONLY")
        self.assertEqual(plan["authorization"],"NOT_GRANTED_BY_THIS_ARTIFACT")
        self.assertEqual(plan["novelty_precheck"],"UNVERIFIED")

    def test_draft_task_cannot_form_comparison_plan(self):
        t={"schema_version":"0.1","task_id":"T1","question":"Q?", "status":"DRAFT"}
        with self.assertRaises(ValueError):
            prepare_experiment(t,hypothesis="H",evaluator_ref="E",gpu_hours_max=1,
                               positive="keep",negative="stop")

    def test_handoff_events_with_versioned_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            save_state(root/"STATE.json",initial_state("demo","test scientific question"))
            task=_active_task()
            taskfile=root/"TASK.json"
            taskfile.write_text(json.dumps(task),encoding="utf-8")
            record_event(root,"TASK_DEFINED","Active task recorded",taskfile)
            self.assertEqual(load_state(root/"STATE.json")["active_task_id"],"T1")
            rev=prepare_review(task,_evidence(),mechanism="H",expected_difference="D")
            revfile=root/"NOVELTY.json"
            revfile.write_text(json.dumps(rev),encoding="utf-8")
            record_event(root,"NOVELTY_PRECHECK_READY","Unverified overlap; fulltext needed",revfile)
            plan=prepare_experiment(task,hypothesis="H",evaluator_ref="EV1",gpu_hours_max=0,
                                  positive="verify",negative="diagnose",novelty_review=rev)
            expfile=root/"EXPERIMENT.json"
            expfile.write_text(json.dumps(plan),encoding="utf-8")
            output=record_event(root,"EXPERIMENT_PLAN_READY","Plan only, no fitting",expfile)
            self.assertEqual(output["phase"],"ALGORITHM")
            self.assertEqual(load_state(root/"STATE.json")["phase"],"ALGORITHM")

    def test_review_cannot_claim_verified_originality(self):
        r=prepare_review(_active_task(),_evidence(),mechanism="h",expected_difference="d")
        r["status"]="CONFIRMED"
        with self.assertRaises(ContractError):
            validate("novelty",r)

if __name__ == "__main__":
    unittest.main()
