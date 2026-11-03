"""Adversarial v0.7 evidence tests: no user data, no network or external code."""
from __future__ import annotations
import csv
import json
import tempfile
import unittest
from pathlib import Path

from adapters.agent_bridge import import_agent_predictions
from core.champion import preview_champion, promote_champion
from core.cli import main as cli
from core.contracts import ContractError
from core.event_chain import migrate_legacy
from core.receipts import fingerprint_file
from core.run_integrity import load_verified_run, validate_run_evidence
from core.state import initial_state, load_state, record_event, save_state, history_status
from tools.experiment_runner import fit_development

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return path

class AdversarialScienceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.p=Path(self.tmp.name)
        save_state(self.p/"STATE.json",initial_state("fixture","Synthetic trust-boundary tests"))
        self.csv=self.p/"dev.csv"
        with self.csv.open("w",encoding="utf-8",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["id","group","label","x"])
            for group in range(8):
                for i in range(8):
                    y="A" if i%2==0 else "B"
                    writer.writerow([f"S{group}-{i}",f"G{group}",y,-3.0 if y=="A" else 3.0])
        self.manifest=write_json(self.p/"DATA_MANIFEST.json",{
            "schema_version":"0.1","datasets":[{
                "dataset_id":"D","source_url":"https://example.invalid/synthetic",
                "group_unit":"group","role":"DEV","label_status":"VERIFIED",
                "local_path":"dev.csv","sha256":fingerprint_file(self.csv),
                "group_column":"group","label_column":"label",
                "sample_id_column":"id","feature_columns":["x"]}]})
        self.task=write_json(self.p/"TASK.json",{
            "schema_version":"0.1","task_id":"T","protocol_id":"P",
            "question":"grouped classification","status":"ACTIVE",
            "metric":"macro_F1","metric_direction":"maximize",
            "group_split":"group-shuffle:group:seed=42:test=0.25",
            "holdout_policy":"external data untouched","baseline":"dummy",
            "legal_inputs":["x"],"data_refs":["D"],"nearest_work":[]})
        record_event(self.p,"TASK_DEFINED","Grouped synthetic fixture",self.task)

    def tearDown(self):
        self.tmp.cleanup()

    def fitted(self,run_id="R1",model="dummy"):
        result=fit_development(self.p,self.manifest,"D",run_id,model,explicit_cpu_fit=True)
        return Path(result["run_path"])

    def test_forged_f1_even_with_valid_hashes_is_rejected(self):
        path=self.fitted()
        run=json.loads(path.read_text(encoding="utf-8"))
        run["metrics"]["macro_F1"]=0.97
        write_json(path,run)  # source artifacts SHA still match; metric is a lie
        with self.assertRaisesRegex(ContractError,"RECOMPUTED_METRIC_MISMATCH"):
            validate_run_evidence(self.p,run)
        with self.assertRaises(ContractError):
            record_event(self.p,"BASELINE_VALID","Forged baseline",path)
        with self.assertRaises(ContractError):
            preview_champion(self.p,path)
        with self.assertRaises(SystemExit) as call:
            cli(["compare","--dir",str(self.p),"--champion",str(path),
                 "--challenger",str(path),"--metric","macro_F1"])
        self.assertEqual(call.exception.code,2)

    def test_cherry_picked_indices_cannot_verify(self):
        path=self.fitted()
        run=json.loads(path.read_text(encoding="utf-8"))
        rel=run["metric_spec"]["predictions_ref"]
        rawfile=self.p/rel
        preds=json.loads(rawfile.read_text())
        preds.pop()
        write_json(rawfile,preds)
        run["artifact_hashes"][rel]=fingerprint_file(rawfile)
        write_json(path,run)
        with self.assertRaisesRegex(ContractError,"PREDICTIONS_NOT_ON_FROZEN_DEV_SPLIT"):
            load_verified_run(self.p,path)

    def test_labels_must_match_independent_dataset(self):
        path=self.fitted()
        run=json.loads(path.read_text(encoding="utf-8"))
        rel=run["metric_spec"]["predictions_ref"]
        rawfile=self.p/rel
        preds=json.loads(rawfile.read_text())
        preds[0]["truth"]="FAKE_LABEL"
        write_json(rawfile,preds)
        run["artifact_hashes"][rel]=fingerprint_file(rawfile)
        write_json(path,run)
        with self.assertRaisesRegex(ContractError,"truth/group disagrees"):
            load_verified_run(self.p,path)

    def test_normal_runner_metrics_are_recomputed(self):
        path=self.fitted()
        run,_=load_verified_run(self.p,path)
        self.assertIn("metric_spec",run)
        self.assertIn("macro_F1",run["metrics"])
        record_event(self.p,"BASELINE_VALID","Real fixture with recalculated metrics",path)
        result=promote_champion(self.p,path)
        self.assertEqual(result["decision"],"FIRST_VERIFIED_CHAMPION")
        self.assertTrue(history_status(self.p)["consistent"])

    def test_external_agent_predictions_verified_but_not_executed(self):
        original=self.fitted()
        run=json.loads(original.read_text())
        code=self.p/"candidate.py"
        code.write_text("print('This script is stored, not executed by Forge')\n",encoding="utf-8")
        imported=import_agent_predictions(self.p,self.manifest,"D","AGENT1",
            self.p/run["metric_spec"]["predictions_ref"],code,measured_wall_seconds=0.5)
        output=Path(imported["run_path"])
        external,_=load_verified_run(self.p,output)
        self.assertAlmostEqual(external["metrics"]["macro_F1"],run["metrics"]["macro_F1"])
        self.assertEqual(external["execution_scope"],"EXTERNAL_AGENT_EXECUTION_NOT_ATTESTED")
        self.assertTrue((self.p/"candidate.py").exists())

    def test_sealed_result_cannot_enter_development_journal(self):
        path=self.fitted()
        run=json.loads(path.read_text(encoding="utf-8"))
        run.update(split="sealed",frozen_protocol_ref="fake-freeze",authorization_ref="fake-approval")
        write_json(path,run)
        with self.assertRaisesRegex(ContractError,"SEALED_RUN_REQUIRES_INDEPENDENT_CONFIRMATION"):
            record_event(self.p,"RUN_RESULT","Sealed should be blocked",path)

    def test_edit_middle_event_or_remove_first_blocks_next_record(self):
        record_event(self.p,"CODE_FAILURE","one")
        record_event(self.p,"CODE_FAILURE","two")
        log=self.p/"EVENTS.jsonl"
        initial=log.read_text(encoding="utf-8").splitlines()
        edited=list(initial)
        mid=json.loads(edited[1])
        mid["note"]="hidden failure"
        edited[1]=json.dumps(mid)
        log.write_text("\n".join(edited)+"\n",encoding="utf-8")
        self.assertFalse(history_status(self.p)["consistent"])
        with self.assertRaises(RuntimeError):
            record_event(self.p,"CODE_FAILURE","must be blocked")
        log.write_text("\n".join(initial[1:])+"\n",encoding="utf-8")
        self.assertFalse(history_status(self.p)["consistent"])

    def test_unanchored_legacy_requires_explicit_migration(self):
        record_event(self.p,"CODE_FAILURE","one")
        record_event(self.p,"CODE_FAILURE","two")
        log=self.p/"EVENTS.jsonl"
        old=[{k:v for k,v in json.loads(line).items() if k not in {"seq","prev_digest","event_digest"}}
             for line in log.read_text().splitlines()]
        log.write_text("\n".join(map(json.dumps,old))+"\n",encoding="utf-8")
        state=load_state(self.p/"STATE.json")
        state.pop("ledger_length");state.pop("ledger_head_digest")
        save_state(self.p/"STATE.json",state)
        self.assertFalse(history_status(self.p)["consistent"])
        preview=migrate_legacy(self.p,apply=False)
        self.assertEqual(preview["events"],3)
        done=migrate_legacy(self.p,apply=True)
        self.assertTrue(done["applied"])
        self.assertTrue(history_status(self.p)["consistent"])
        self.assertTrue(Path(done["backup"]).exists())

    def test_bootstrap_does_not_create_false_scientific_certainty(self):
        one=self.fitted()
        record_event(self.p,"BASELINE_VALID","Baseline",one)
        promote_champion(self.p,one)
        two=self.fitted("R2","logistic")
        report=preview_champion(self.p,two)
        self.assertIn(report["uncertainty"]["status"],
                      {"INSUFFICIENT_INDEPENDENT_GROUPS","EXPLORATORY_INTERVAL"})
        self.assertEqual(report["promotion_scope"],"PROVISIONAL_DEVELOPMENT_ONLY")
        self.assertFalse(report["scientific_claim_confirmed"])

if __name__=="__main__":
    unittest.main()
