"""v0.4 regression: task pivots, receipts, conservative literature and DEV audit."""
import csv
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from adapters.paper_merge import merge_papers
from adapters.researchstudio_search import run_upstream_worker, search_papers
from adapters.novelty_check import prepare_review
from core.receipts import fingerprint, fingerprint_file
from core.champion import promote_champion
from core.selection import selection_history
from core.journal import candidate_journal
from core.state import initial_state, load_state, save_state, record_event, history_status
from core.contracts import ContractError, validate
from tools.data_audit import audit_manifest, audit_development_csv

def task(tid="T1", protocol="P1"):
    return {"schema_version":"0.1","task_id":tid,"protocol_id":protocol,
            "question":"Can we generalize across sensor devices?",
            "status":"ACTIVE","metric":"macro_F1","metric_direction":"maximize", "group_split":"device-independent",
            "baseline":"Ridge", "holdout_policy":"sealed devices",
            "legal_inputs":["measured signals"], "data_refs":["D1"],"nearest_work":[]}

def run(tid="T1", protocol="P1", name="R1"):
    return {"schema_version":"0.1","task_id":tid,"protocol_id":protocol,
            "run_id":name, "dataset_version":"v1","code_commit":"c1",
            "evaluator_version":"e1","status":"VALID","split":"dev",
            "metrics":{"macro_F1":0.8},"artifact_refs":[f"runs/{name}.log"],
            "group_split":"device-independent","sample_ids_hash":"samples",
            "legal_inputs":["measured signals"]}

class TaskLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.p=Path(self.tmp.name)
        save_state(self.p/"STATE.json",initial_state("demo","sensor research"))

    def tearDown(self):
        self.tmp.cleanup()

    def file(self,rel,obj):
        if isinstance(obj,dict) and obj.get("run_id") and obj.get("status") in {"VALID","INCONCLUSIVE"}:
            obj=dict(obj)
            hashes={}
            for ref in obj["artifact_refs"]:
                logfile=self.p/ref
                logfile.parent.mkdir(parents=True,exist_ok=True)
                logfile.write_text("fixture raw log",encoding="utf-8")
                hashes[ref]=fingerprint_file(logfile)
            obj["artifact_hashes"]=hashes
        path=self.p/rel
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(obj),encoding="utf-8")
        return path

    def record_task(self,obj=None):
        path=self.file("tasks/T1.json",obj or task())
        record_event(self.p,"TASK_DEFINED","Define initial scientific protocol",path)
        return path

    def transition(self,event,new,decision_id="D1"):
        target=self.file(f"tasks/{new['task_id']}-{new['protocol_id']}.json",new)
        old=load_state(self.p/"STATE.json")
        dec={"schema_version":"0.1","decision_id":decision_id,"decision_type":event,
             "from_task_id":old["active_task_id"],"from_protocol_id":old["active_protocol_id"],
             "to_task_id":new["task_id"],"to_protocol_id":new["protocol_id"],
             "new_task_path":target.relative_to(self.p).as_posix(),
             "new_task_sha256":fingerprint_file(target),
             "reason":"Evidence justifies independent task/condition",
             "user_approval_ref":"actual-user-instruction-reference",
             "evidence_refs":["prior-run-or-paper"]}
        p=self.file(f"decisions/{decision_id}.json",dec)
        return record_event(self.p,event,"Decision recorded, approval must be checked externally",p)

    def test_task_receipt_stale_blocks_experiment(self):
        path=self.record_task()
        plan={"schema_version":"0.1","experiment_id":"E1","task_id":"T1",
              "protocol_id":"P1","hypothesis":"H","evaluator_ref":"eval-v1","split":"dev",
              "budget":{"gpu_hours_max":0},"decision_if_positive":"keep",
              "decision_if_negative":"diagnose","status":"PLAN_ONLY",
              "task_fingerprint":fingerprint(task())}
        exp=self.file("EXPERIMENT.json",plan)
        record_event(self.p,"EXPERIMENT_PLAN_READY","Plan recorded",exp)
        changed=task()
        changed["metric"]="accuracy"  # same ID and protocol but scientifically different
        path.write_text(json.dumps(changed),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"changed"):
            record_event(self.p,"EXPERIMENT_PLAN_READY","Stale plan",exp)

    def test_pivot_retains_history_and_retires_champion(self):
        self.record_task()
        run_path=self.file("runs/R1.json",run())
        record_event(self.p,"BASELINE_VALID","Verified raw Run receipt",run_path)
        self.assertIsNone(load_state(self.p/"STATE.json")["best_valid_run_id"])
        promote_champion(self.p,run_path)
        self.assertEqual(load_state(self.p/"STATE.json")["best_valid_run_id"],"R1")
        self.transition("TASK_PIVOT",task("T2","P2"))
        s=load_state(self.p/"STATE.json")
        self.assertEqual(s["active_task_id"],"T2")
        self.assertEqual(s["best_valid_run_id"],None)
        self.assertEqual(s["active_protocol_id"],"P2")
        history=selection_history(self.p)
        self.assertEqual(history["task_or_protocol_selection_count"],2)
        j=candidate_journal(self.p)
        self.assertEqual(len(j["runs"]),1)
        self.assertFalse(j["runs"][0]["current_protocol"])
        self.assertTrue(history_status(self.p)["consistent"])

    def test_revise_same_task_new_protocol(self):
        self.record_task()
        self.transition("PROTOCOL_REVISED",task("T1","P2"))
        s=load_state(self.p/"STATE.json")
        self.assertEqual(s["active_task_id"],"T1")
        self.assertEqual(s["active_protocol_id"],"P2")
        with self.assertRaisesRegex(ContractError,"protocol_id mismatches"):
            record_event(self.p,"BASELINE_VALID","Old Run",self.file("RUN.json",run()))

    def test_transition_requires_distinct_id_or_version(self):
        self.record_task()
        with self.assertRaises(ContractError):
            self.transition("TASK_PIVOT",task("T1","P2"))
        with self.assertRaises(ContractError):
            self.transition("PROTOCOL_REVISED",task("T1","P1"))

    def test_decision_must_know_old_protocol(self):
        self.record_task()
        new=task("T2","P2")
        target=self.file("tasks/T2.json",new)
        dec={"schema_version":"0.1","decision_id":"D1","decision_type":"TASK_PIVOT",
             "from_task_id":"T1","from_protocol_id":"WRONG","to_task_id":"T2",
             "to_protocol_id":"P2","new_task_path":"tasks/T2.json",
             "new_task_sha256":fingerprint_file(target),"reason":"New failure premise",
             "evidence_refs":["R1"],"user_approval_ref":"actual-user-message"}
        with self.assertRaises(ContractError):
            record_event(self.p,"TASK_PIVOT","Stale decision",self.file("D1.json",dec))

    def test_task_update_requires_explicit_revision(self):
        self.record_task()
        with self.assertRaises(ContractError):
            record_event(self.p,"TASK_DEFINED","Changing protocol silently",
                              self.file("tasks/new.json",task("T1","P2")))

    def test_legacy_state_migration_retains_history_not_old_champion(self):
        s=load_state(self.p/"STATE.json")
        s["active_task_id"]="T1"
        s["best_valid_run_id"]="legacy-run"
        save_state(self.p/"STATE.json",s)
        self.record_task()
        new=load_state(self.p/"STATE.json")
        self.assertEqual(new["active_protocol_id"],"P1")
        self.assertIsNone(new["best_valid_run_id"])

    def test_parallel_note_events_preserve_log(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda i:record_event(self.p,"CODE_FAILURE",f"note {i}"),range(8)))
        self.assertTrue(history_status(self.p)["consistent"])
        self.assertEqual(len((self.p/"EVENTS.jsonl").read_text().splitlines()),8)

class SearchCorrectness(unittest.TestCase):
    @staticmethod
    def paper(doi,source,title="Same title"):
        return {"title":title,"doi":doi,"source":source,"year":2021,
                "authors":["A"],"abstract":"sensor classification method",
                "citation_count":3,"url":"https://doi.org/"+doi}

    def test_distinct_dois_with_same_title_not_collapsed(self):
        a=self.paper("10.1234/a","open_alex")
        b=self.paper("10.1234/b","crossref")
        papers, warnings=merge_papers({"open_alex":[a],"crossref":[b]},["sensor method"])
        self.assertEqual(len(papers),2)
        self.assertTrue(any(w["kind"]=="TITLE_DOI_CONFLICT" for w in warnings))

    def test_equivalent_doi_cross_source_is_combined(self):
        a=self.paper("10.1234/a","open_alex")
        b=self.paper("https://doi.org/10.1234/a","crossref")
        papers,_=merge_papers({"open_alex":[a],"crossref":[b]},["sensor method"])
        self.assertEqual(len(papers),1)
        self.assertEqual(len(papers[0]["found_in"]),2)

    def test_default_search_includes_old_papers(self):
        checked=[]
        def worker(source,queries,start,end,limit):
            checked.append((start,end))
            return {"source":source,"papers":[self.paper("10.1234/old",source)],"errors":[]}
        b=search_papers(["sensor method"],sources=("crossref",),worker=worker)
        self.assertEqual(checked[0][0],1900)
        self.assertEqual(b["search_window"]["start_year"],1900)

    def test_precheck_marks_metadata_shortlist_not_verified_nearest(self):
        def worker(source,queries,start,end,limit):
            return {"source":source,"papers":[self.paper(f"10.1234/{i}",source,f"Method {i}") for i in range(5)],"errors":[]}
        e=search_papers(["sensor method"],sources=("crossref",),worker=worker)
        rev=prepare_review(task(),e,mechanism="sensor bias correction",expected_difference="d")
        self.assertEqual(rev["coverage"]["total_metadata_records"],5)
        self.assertEqual(len(rev["coverage"]["unreviewed_record_ids"]),2)
        self.assertEqual(rev["coverage"]["selected_as"],"SCREENING_SET_NOT_NEAREST_WORK")
        self.assertTrue(rev["coverage"]["relevant_missing_papers_possible"])
        with self.assertRaises(ValueError):
            prepare_review(task(),e,mechanism="a",expected_difference="b",candidate_ids=["absent"])

    def test_worker_windows_safe_lock_without_real_network(self):
        with tempfile.TemporaryDirectory() as temp:
            def fake_run(cmd, **kwargs):
                output=Path(cmd[cmd.index("--out")+1])
                output.write_text(json.dumps({"source":"arxiv","papers":[],"errors":[]}))
                return type("Completed",(),{"returncode":0})()
            with patch("adapters.researchstudio_search.subprocess.run", side_effect=fake_run):
                result=run_upstream_worker("arxiv",["sensor drift"],2020,2026,2,timeout=2)
                self.assertEqual(result["source"],"arxiv")

class DataAuditTests(unittest.TestCase):
    def test_manifest_missing_labels_are_not_certified(self):
        manifest={"schema_version":"0.1","datasets":[
            {"dataset_id":"D1","source_url":"https://example.org/data","group_unit":"subject",
             "role":"DEV","label_status":"UNKNOWN"}]}
        report=audit_manifest(manifest)
        self.assertEqual(report["status"],"NEEDS_EVIDENCE")

    def test_sealed_selection_access_flags_block(self):
        manifest={"schema_version":"0.1","datasets":[
            {"dataset_id":"T","source_url":"https://example.org","group_unit":"device",
             "role":"SEALED_CONFIRM","label_status":"VERIFIED","accessed_during_selection":True}]}
        self.assertEqual(audit_manifest(manifest)["status"],"BLOCKED")

    def test_actual_dev_csv_audit_without_fitting(self):
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/"dev.csv"
            with file.open("w",newline="",encoding="utf-8") as f:
                writer=csv.writer(f);writer.writerow(["id","device","label","x"])
                writer.writerows([["1","A","run",1],["2","B","walk",2],["3","A","run",3]])
            r=audit_development_csv(file,group_col="device",label_col="label",id_col="id")
            self.assertEqual((r["rows"],r["groups"],r["classes"]),(3,2,2))
            self.assertFalse(r["model_fitting_performed"])
            self.assertFalse(r["sealed_data_read"])
            self.assertEqual(r["status"],"STRUCTURAL_PASS")

if __name__=="__main__":
    unittest.main()
