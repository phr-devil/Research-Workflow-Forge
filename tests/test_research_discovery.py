"""Synthetic adversarial tests: discovery evidence contracts, not scientific validation."""
from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from adapters.hypothesis_bank import (
    _write_new, create_bank, make_observation_seeds, record_run_feedback,
)
from adapters.opportunity_review import review_opportunities
from core.contracts import ContractError
from core.metric_verify import sample_hash, verify_metrics
from core.receipts import fingerprint_file


def write(path: Path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


class ResearchDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        rows = []
        for i in range(8):
            for j in range(2):
                rows.append((f"S{i}-{j}", f"G{i}", float(i+j)))
        self.rows = rows
        with (self.project/"data.csv").open("w", newline="", encoding="utf-8") as out:
            w = csv.writer(out)
            w.writerow(["sid","group","y"])
            w.writerows(rows)
        self.manifest = write(self.project/"manifest.json", {
            "schema_version":"0.1","datasets":[{
                "dataset_id":"D","role":"DEV","source_url":"https://example.invalid/synthetic",
                "group_unit":"person","label_status":"VERIFIED",
                "local_path":"data.csv","sha256":fingerprint_file(self.project/"data.csv"),
                "label_column":"y","group_column":"group","sample_id_column":"sid",
            }]
        })
        self.split = write(self.project/"split.json",{
            "train_groups":[f"G{i}" for i in range(4)],
            "dev_groups":[f"G{i}" for i in range(4,8)],
        })
        self.dev = [(index, row) for index,row in enumerate(rows) if row[1] in {f"G{i}" for i in range(4,8)}]
        self.lit = write(self.project/"papers.json", {
            "schema_version":"0.1","query":"synthetic cross person",
            "retrieved_at":"2026-11-03T00:00:00Z",
            "verification":"METADATA_ONLY",
            "sources_checked":["open_alex"],
            "source_errors":[],
            "records":[{"record_id":"paper-A","title":"Synthetic controlled prior",
                        "sources":["open_alex"],"verification":"METADATA_ONLY"}],
        })
        self.cards = write(self.project/"cards.json",{"candidates":[self.idea()]})

    def idea(self):
        return {
            "hypothesis_id":"H01",
            "research_question":"Is the group error repeatable?",
            "mechanism":"Group-dependent residual structure may persist after matching input budgets",
            "strongest_alternative":"Different label distribution across held-out groups",
            "distinct_prediction":"Within matched label strata the group effect should persist",
            "minimum_test":"Compare grouped errors after train-only label-stratum matching",
            "if_positive":"Retain as a mechanism hypothesis requiring independent replication",
            "if_negative":"Abandon this lever and preserve negative group evidence",
            "legal_information":"Sensor values available before each prediction, no query labels",
            "legal_information_status":"UNKNOWN",
            "baseline_status":"UNKNOWN","test_cost":"LOW",
            "source_seed_ids":["S_GROUP_ERRORS"],
            "paper_record_ids":["paper-A"],
        }

    def make_run(self, name, offset):
        preds = [{"row_index":i,"prediction":row[2]+offset} for i,row in self.dev]
        pred = write(self.project/(name+"-pred.json"), preds)
        log = write(self.project/(name+"-log.json"), {"synthetic": True})
        split_sha = fingerprint_file(self.split)
        run = {
            "schema_version":"0.1","run_id":name,
            "task_id":"T","protocol_id":"P","dataset_version":fingerprint_file(self.project/"data.csv"),
            "code_commit":"synthetic-only","evaluator_version":"v0.8","status":"VALID","split":"dev",
            "metrics":{"MAE":0.0,"RMSE":0.0},
            "group_split":"pinned-groups:"+split_sha,
            "legal_inputs":["sensor"],"sample_ids_hash":sample_hash([row[0] for _,row in self.dev]),
            "artifact_refs":[pred.name,log.name],
            "artifact_hashes":{p.name:fingerprint_file(p) for p in (pred,log)},
            "metric_spec":{
                "format":"forge-dev-regression-v1",
                "predictions_ref":pred.name,
                "manifest_ref":self.manifest.name,
                "manifest_sha256":fingerprint_file(self.manifest),
                "dataset_id":"D",
                "split_ref":self.split.name,
                "split_sha256":split_sha,
                "aggregation":"group_mean",
            },
        }
        run["metrics"] = verify_metrics(self.project,run,check_reported=False)["computed"]
        return write(self.project/(name+"-RUN.json"),run)

    def seed_file(self, reference=False):
        a=self.make_run("Candidate",1)
        b=self.make_run("Reference",2) if reference else None
        seed=make_observation_seeds(self.project,a,b,metric="MAE" if reference else None)
        return _write_new(self.project/"seeds.json",seed), a

    def test_real_verified_dev_receipts_seed_observations_not_mechanism(self):
        path, _ = self.seed_file(reference=True)
        seeds = json.loads(path.read_text())
        self.assertEqual(seeds["status"], "DEV_OBSERVATION_NOT_SCIENTIFIC_CONFIRMATION")
        self.assertIn("S_GROUP_ERRORS", [x["seed_id"] for x in seeds["seeds"]])
        self.assertIn("S_MATCHED_COMPARISON", [x["seed_id"] for x in seeds["seeds"]])
        self.assertEqual(seeds["diagnostic"]["signal_evidence"],
                         "DEV_IMPROVEMENT_OVER_REFERENCE_OBSERVED")
        self.assertEqual(seeds["diagnostic"]["remaining_error"]["theoretical_attainable_gain"],"UNKNOWN")

    def test_seed_and_literature_combine_into_unverified_hypothesis(self):
        s, _ = self.seed_file()
        bank=create_bank(self.project,self.cards,seed_path=s,literature_path=self.lit)
        self.assertEqual(bank["status"],"HYPOTHESIS_BANK_UNVERIFIED")
        self.assertEqual(bank["source_truth"]["literature"],"METADATA_ONLY")
        self.assertEqual(bank["source_truth"]["data_run"],"METRICS_RECOMPUTED_DEV_ONLY")
        self.assertEqual(bank["hypotheses"][0]["novelty_status"],"UNVERIFIED")
        review=review_opportunities(self.project,bank)
        self.assertEqual(review["candidates"][0]["next_action"],"LEGAL_INFORMATION_PROBE")
        self.assertEqual(review["research_success_rate"],"NOT_MEASURED")

    def test_literature_only_needs_actual_data_and_does_not_imply_novelty(self):
        card=self.idea()
        card["source_seed_ids"]=[]
        self.cards=write(self.cards,{"candidates":[card]})
        bank=create_bank(self.project,self.cards,literature_path=self.lit)
        self.assertEqual(review_opportunities(self.project,bank)["candidates"][0]["next_action"],
                         "VERIFY_DATA_SIGNAL")
        self.assertEqual(bank["source_truth"]["data_run"],"NOT_AVAILABLE")

    def test_data_note_is_weak_observation_not_verified_run(self):
        note=self.project/"observations.txt"
        note.write_text("A dataset owner claims one feature is drifting",encoding="utf-8")
        card=self.idea()
        card["source_seed_ids"]=[]
        card["paper_record_ids"]=[]
        card["uses_data_note"]=True
        self.cards=write(self.cards,{"candidates":[card]})
        bank=create_bank(self.project,self.cards,data_note_path=note)
        self.assertEqual(bank["source_truth"]["data_note"],"AGENT_NOTE_NOT_RECOMPUTED")
        self.assertEqual(review_opportunities(self.project,bank)["candidates"][0]["next_action"],
                         "CHECK_ORIGINAL_DATA_SIGNAL")

    def test_invalid_paper_identifier_and_duplicate_hypothesis(self):
        s,_=self.seed_file()
        card=self.idea()
        card["paper_record_ids"]=["invented-paper"]
        write(self.cards,{"candidates":[card]})
        with self.assertRaisesRegex(ContractError,"unknown paper"):
            create_bank(self.project,self.cards,seed_path=s,literature_path=self.lit)
        write(self.cards,{"candidates":[self.idea(),self.idea()]})
        with self.assertRaisesRegex(ContractError,"duplicate"):
            create_bank(self.project,self.cards,seed_path=s,literature_path=self.lit)

    def test_modified_seed_and_run_are_rejected(self):
        s, run_path=self.seed_file()
        fake=json.loads(s.read_text())
        fake["diagnostic"]["remaining_error"]["group_macro_mean"]=-10
        write(s,fake)
        with self.assertRaisesRegex(ContractError,"seed summary"):
            create_bank(self.project,self.cards,seed_path=s,literature_path=self.lit)
        # Recompute correctly, then mutate original Run after its receipt is recorded.
        write(s,make_observation_seeds(self.project,run_path))
        run=json.loads(run_path.read_text())
        run["metrics"]["MAE"]=0.0
        write(run_path,run)
        with self.assertRaises((ValueError,ContractError)):
            create_bank(self.project,self.cards,seed_path=s,literature_path=self.lit)

    def test_feedback_retains_dev_scope_and_version_history(self):
        s, candidate = self.seed_file()
        bank = create_bank(self.project,self.cards,seed_path=s,literature_path=self.lit)
        old = _write_new(self.project/"bank-v1.json",bank)
        next_bank=record_run_feedback(self.project,old,"H01",candidate,"INCONCLUSIVE")
        self.assertEqual(next_bank["revision"],1)
        self.assertEqual(next_bank["hypotheses"][0]["status"],"EXPLORATORY_RUN_RECORDED")
        self.assertEqual(next_bank["hypotheses"][0]["task_id"],"T")
        self.assertAlmostEqual(next_bank["hypotheses"][0]["run_feedback"][0]["verified_dev_metrics"]["MAE"],1)
        self.assertEqual(bank["hypotheses"][0]["run_feedback"],[])
        new_path=_write_new(self.project/"bank-v2.json",next_bank)
        with self.assertRaisesRegex(ContractError,"duplicate Run"):
            record_run_feedback(self.project,new_path,"H01",candidate,"INCONCLUSIVE")
        with self.assertRaises(FileExistsError):
            _write_new(new_path,next_bank)

    def test_failed_information_premise_never_becomes_stop(self):
        s,_=self.seed_file()
        card=self.idea()
        card["legal_information_status"]="BLOCKED"
        write(self.cards,{"candidates":[card]})
        bank=create_bank(self.project,self.cards,seed_path=s,literature_path=self.lit)
        review=review_opportunities(self.project,bank)
        self.assertEqual(review["candidates"][0]["next_action"],
                         "REVISE_ILLEGAL_INFORMATION_PREMISE")
        self.assertEqual(review["authorization"],"NOT_GRANTED")
        self.assertNotEqual(review["candidates"][0]["next_action"],"STOP")

    def test_bad_task_binding_and_source_escape_fail_closed(self):
        s,_=self.seed_file()
        card=self.idea()
        card["task_id"]="wrong-task"
        write(self.cards,{"candidates":[card]})
        with self.assertRaisesRegex(ContractError,"mismatch"):
            create_bank(self.project,self.cards,seed_path=s,literature_path=self.lit)
        with self.assertRaisesRegex(ContractError,"project-contained"):
            create_bank(self.project,self.cards,seed_path=Path("/tmp/outside-run.json"))


    def test_review_fails_on_stale_original_run_and_forged_source_id(self):
        s, run = self.seed_file()
        bank = create_bank(self.project, self.cards, seed_path=s, literature_path=self.lit)
        bank["hypotheses"][0]["source_seed_ids"]=["INVENTED"]
        with self.assertRaisesRegex(ContractError,"source_seed_ids"):
            review_opportunities(self.project,bank)
        bank = create_bank(self.project,self.cards,seed_path=s,literature_path=self.lit)
        original = json.loads(run.read_text())
        original["metrics"]["MAE"]=999
        write(run, original)
        with self.assertRaises((ContractError,ValueError)):
            review_opportunities(self.project,bank)


if __name__=="__main__":
    unittest.main()
