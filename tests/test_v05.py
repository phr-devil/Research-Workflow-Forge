"""v0.5 scientific guardrails + bounded real CPU DEV execution tests.

Tiny local synthetic fixtures are ENGINEERING TESTS, not research results.
No external network, no sealed data and no user's research datasets are used.
"""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from core.champion import preview_champion, promote_champion
from core.comparison import compare_runs
from core.candidate_tree import candidate_tree
from core.contracts import ContractError
from core.data_access import bind_dev_dataset
from core.receipts import fingerprint_file
from core.recovery import recover
from core.run_integrity import load_verified_run, validate_run_evidence
from core.state import initial_state, load_state, record_event, save_state, history_status
from tools.experiment_runner import fit_development
from tools.data_audit import main as audit_main

def fixture_task():
    return {"schema_version":"0.1","task_id":"T1","status":"ACTIVE","protocol_id":"P1",
            "question":"Can numeric signals generalize across withheld groups?",
            "metric":"macro_F1","metric_direction":"maximize",
            "group_split":"group-shuffle:group:seed=42:test=0.25",
            "baseline":"dummy", "holdout_policy":"separate external confirmation not tested",
            "legal_inputs":["x","z"], "data_refs":["D"], "nearest_work":[]}

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

class GuardrailTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.project=Path(self.temp.name)
        save_state(self.project/"STATE.json", initial_state("demo","Engineering tests only"))
        rows=[]
        for group in range(8):
            for idx in range(8):
                label = "B" if idx % 2 else "A"
                x = 2.5 if label == "B" else -2.5
                rows.append((f"G{group}", label, x + idx*0.01, group*0.1))
        self.data=self.project/"dev.csv"
        with self.data.open("w",encoding="utf-8",newline="") as f:
            w=csv.writer(f);w.writerow(["group","label","x","z"])
            w.writerows(rows)
        self.data_sha=fingerprint_file(self.data)
        self.manifest={"schema_version":"0.1", "datasets":[{
            "dataset_id":"D","role":"DEV","source_url":"https://example.invalid/synthetic",
            "group_unit":"group", "label_status":"VERIFIED",
            "local_path":"dev.csv", "sha256":self.data_sha,
            "group_column":"group","label_column":"label",
            "feature_columns":["x","z"], "license_ref":"SYNTHETIC_FIXTURE"
        }]}
        self.manifest_path=write_json(self.project/"DATA_MANIFEST.json",self.manifest)
        self.task_path=write_json(self.project/"TASK.json", fixture_task())
        record_event(self.project,"TASK_DEFINED","Synthetic task metadata for engineering test",self.task_path)

    def tearDown(self):
        self.temp.cleanup()

    def test_dev_binding_checks_hash_and_records_access(self):
        path,entry=bind_dev_dataset(self.project,self.manifest_path,"D",purpose="AUDIT_DEV")
        self.assertEqual(path.resolve(),self.data.resolve())
        self.assertEqual(entry["role"],"DEV")
        entries=(self.project/"DATA_ACCESS.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(entries),1)
        self.assertEqual(json.loads(entries[0])["purpose"],"AUDIT_DEV")

    def test_sealed_cannot_be_requested_or_alias_dev(self):
        m=json.loads(json.dumps(self.manifest))
        m["datasets"][0]["role"]="SEALED_CONFIRM"
        file=write_json(self.project/"sealed_manifest.json",m)
        with self.assertRaises(PermissionError):
            bind_dev_dataset(self.project,file,"D",purpose="FIT_DEV")
        m=json.loads(json.dumps(self.manifest))
        m["datasets"].append({**m["datasets"][0],"dataset_id":"H","role":"SEALED_CONFIRM"})
        file=write_json(self.project/"alias_manifest.json",m)
        with self.assertRaises(PermissionError):
            bind_dev_dataset(self.project,file,"D",purpose="FIT_DEV")
        self.assertFalse((self.project/"DATA_ACCESS.jsonl").exists())

    def test_stale_hash_cannot_fit(self):
        m=json.loads(json.dumps(self.manifest))
        m["datasets"][0]["sha256"]="a"*64
        file=write_json(self.project/"modified_manifest.json",m)
        with self.assertRaises(ValueError):
            bind_dev_dataset(self.project,file,"D",purpose="FIT_DEV")

    def test_audit_cli_rejects_unbound_csv(self):
        with self.assertRaises(SystemExit) as ctx:
            audit_main(["--dev-csv",str(self.data),"--group-col","group","--label-col","label"])
        self.assertEqual(ctx.exception.code,2)

    def test_explicit_opt_in_needed_before_fit(self):
        with self.assertRaises(PermissionError):
            fit_development(self.project,self.manifest_path,"D","R1","dummy")
        self.assertFalse((self.project/"runs").exists())

    def test_real_bounded_baseline_challenger_with_verified_artifacts(self):
        first=fit_development(self.project,self.manifest_path,"D","R1","dummy",
                              explicit_cpu_fit=True)
        first_path=Path(first["run_path"])
        original,_=load_verified_run(self.project,first_path)
        self.assertTrue(first["group_disjoint"])
        self.assertFalse(first["research_claim_confirmed"])
        record_event(self.project,"BASELINE_VALID","Fixture baseline Run receipt",first_path)
        self.assertIsNone(load_state(self.project/"STATE.json")["best_valid_run_id"])
        promoted=promote_champion(self.project,first_path)
        self.assertEqual(promoted["decision"],"FIRST_VERIFIED_CHAMPION")
        self.assertEqual(load_state(self.project/"STATE.json")["best_valid_run_id"],"R1")
        second=fit_development(self.project,self.manifest_path,"D","R2","logistic",
                               explicit_cpu_fit=True,parent_run_id="R1")
        candidate_path=Path(second["run_path"])
        challenger,_=load_verified_run(self.project,candidate_path)
        record_event(self.project,"RUN_RESULT","Fixture challenger Run receipt",candidate_path)
        scores=compare_runs(original,challenger,"macro_F1")
        self.assertGreater(scores["improvement_direction_delta"],0)
        selection=preview_champion(self.project,candidate_path)
        self.assertEqual(selection["decision"],"PROMOTE")
        result=promote_champion(self.project,candidate_path)
        self.assertEqual(result["decision"],"PROMOTE")
        state=load_state(self.project/"STATE.json")
        self.assertEqual(state["best_valid_run_id"],"R2")
        tree=candidate_tree(self.project)
        self.assertEqual(tree["status"],"STRUCTURAL_PASS")
        self.assertEqual(len(tree["candidates"]),2)
        self.assertTrue(history_status(self.project)["consistent"])
        self.assertTrue((self.project/"DATA_ACCESS.jsonl").exists())

    def test_tampering_blocks_raw_evidence(self):
        result=fit_development(self.project,self.manifest_path,"D","R1","dummy",
                               explicit_cpu_fit=True)
        path=Path(result["run_path"])
        record=json.loads(path.read_text(encoding="utf-8"))
        log=self.project/record["artifact_refs"][0]
        log.write_text("tampered",encoding="utf-8")
        with self.assertRaises(ContractError):
            validate_run_evidence(self.project,record)
        with self.assertRaises(ContractError):
            record_event(self.project,"BASELINE_VALID","Tampered evidence",path)

    def test_unverified_old_style_run_cannot_be_promoted(self):
        fake={"schema_version":"0.1","run_id":"F","task_id":"T1",
              "protocol_id":"P1","dataset_version":"v1","code_commit":"c1",
              "evaluator_version":"E1","status":"VALID","split":"dev",
              "metrics":{"macro_F1":0.8},"group_split":"group-shuffle:group:seed=42:test=0.25",
              "sample_ids_hash":"x","legal_inputs":["x","z"],"artifact_refs":["not-present.log"]}
        path=write_json(self.project/"R_fake.json",fake)
        with self.assertRaises(ContractError):
            record_event(self.project,"BASELINE_VALID","Unverified fixture",path)
        with self.assertRaises(ContractError):
            preview_champion(self.project,path)

    def test_run_output_id_cannot_overwrite(self):
        fit_development(self.project,self.manifest_path,"D","R1","dummy",
                        explicit_cpu_fit=True)
        with self.assertRaises(FileExistsError):
            fit_development(self.project,self.manifest_path,"D","R1","dummy",
                            explicit_cpu_fit=True)

    def test_champion_requires_explicit_metric_direction(self):
        prior=json.loads(self.task_path.read_text(encoding="utf-8"))
        state=load_state(self.project/"STATE.json")
        # Re-registering same Task cannot silently change it; create a fresh project instead.
        with self.assertRaises(ContractError):
            changed={**prior,"metric_direction":None}
            change=write_json(self.project/"other_task.json",changed)
            record_event(self.project,"TASK_DEFINED","Invalid silent metric change",change)

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.p=Path(self.t.name)
        save_state(self.p/"STATE.json",initial_state("demo","Recovery only"))

    def tearDown(self):
        self.t.cleanup()

    def test_recover_interrupted_note_preserves_event(self):
        before=load_state(self.p/"STATE.json")
        record_event(self.p,"CODE_FAILURE","A note only")
        save_state(self.p/"STATE.json",before)
        self.assertFalse(history_status(self.p)["consistent"])
        dry=recover(self.p,apply=False)
        self.assertEqual(dry["status"],"REPLAYABLE_ONE_EVENT")
        self.assertFalse(dry["applied"])
        applied=recover(self.p,apply=True)
        self.assertTrue(applied["applied"])
        self.assertTrue(history_status(self.p)["consistent"])

    def test_recover_rejects_modified_artifact(self):
        before=load_state(self.p/"STATE.json")
        ev={"schema_version":"0.1","query":"sensor literature",
            "retrieved_at":"2026-11-03T00:00:00+00:00",
            "verification":"METADATA_ONLY",
            "sources_checked":["crossref"],"source_errors":[],
            "records":[{"record_id":"1","title":"Paper","sources":["crossref"],
                        "verification":"METADATA_ONLY"}]}
        file=write_json(self.p/"EVIDENCE.json",ev)
        record_event(self.p,"SEARCH_READY","Evidence recorded",file)
        save_state(self.p/"STATE.json",before)
        file.write_text("{}",encoding="utf-8")
        with self.assertRaises(ValueError):
            recover(self.p,apply=False)

if __name__=="__main__":
    unittest.main()
