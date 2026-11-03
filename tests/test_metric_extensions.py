"""v0.8 engineering regression tests; synthetic groups and events only."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from core.metric_verify import sample_hash, verify_metrics
from core.comparison import compare_runs
from core.contracts import ContractError
from core.receipts import fingerprint_file
from core.run_integrity import validate_run_evidence
from core.statistics import group_bootstrap


def write_json(path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


class TypedMetricTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.rows=[]
        for group in range(8):
            for j in range(3):
                self.rows.append((f"S{group}-{j}",f"G{group}",str(group+j),str(j+1.0)))
        with (self.root/"data.csv").open("w",newline="",encoding="utf-8") as out:
            w=csv.writer(out);w.writerow(["id","group","target","event"]);w.writerows(self.rows)
        self.manifest=write_json(self.root/"manifest.json",{
            "schema_version":"0.1","datasets":[{
                "dataset_id":"D","role":"DEV","source_url":"https://example.invalid/synth",
                "group_unit":"group","label_status":"VERIFIED","local_path":"data.csv",
                "sha256":fingerprint_file(self.root/"data.csv"),
                "label_column":"target","group_column":"group","sample_id_column":"id"}]})
        self.split=write_json(self.root/"split.json",{
            "train_groups":[f"G{i}" for i in range(4)],
            "dev_groups":[f"G{i}" for i in range(4,8)]})
        self.msha=fingerprint_file(self.manifest)
        self.ssha=fingerprint_file(self.split)
        self.dev=[i for i,x in enumerate(self.rows) if x[1] in {f"G{g}" for g in range(4,8)}]

    def make_run(self,kind="regression",run_id="R1",shift=0.0):
        event=kind=="event"
        if event:
            manifest=json.loads(self.manifest.read_text(encoding="utf-8"))
            manifest["datasets"][0]["label_column"]="event"
            write_json(self.manifest,manifest)
            self.msha=fingerprint_file(self.manifest)
        preds=[]
        for i in self.dev:
            row=self.rows[i]
            if event:
                preds.append({"row_index":i,"trigger_time_s":(float(row[3])+shift) if row[3] != "NONE" else 0.5})
            else:
                preds.append({"row_index":i,"prediction":float(row[2])+shift})
        predfile=write_json(self.root/f"{run_id}.json",preds)
        logfile=write_json(self.root/f"{run_id}-log.json",{"fixture":True})
        fmt="forge-dev-event-v1" if event else "forge-dev-regression-v1"
        spec={"format":fmt,"predictions_ref":predfile.name,"manifest_ref":"manifest.json",
              "manifest_sha256":self.msha,"dataset_id":"D",
              "split_ref":"split.json","split_sha256":self.ssha}
        if event:
            spec.update({"tolerance_s":0.5,"prediction_mode":"SINGLE_EMISSION_PER_EPISODE"})
        else:
            spec["aggregation"]="group_mean"
        run={"schema_version":"0.1","run_id":run_id,"task_id":"T","protocol_id":"P",
             "dataset_version":fingerprint_file(self.root/"data.csv"),
             "code_commit":"synthetic","evaluator_version":"v08","status":"VALID",
             "split":"dev","metrics":{"event_recall":0.0} if event else {"MAE":0.0,"RMSE":0.0},
             "group_split":"pinned-groups:"+self.ssha,"legal_inputs":["sensor"],
             "sample_ids_hash":sample_hash([self.rows[i][0] for i in self.dev]),
             "artifact_refs":[predfile.name,logfile.name],
             "artifact_hashes":{p.name:fingerprint_file(p) for p in (predfile,logfile)},
             "metric_spec":spec}
        computed=verify_metrics(self.root,run,check_reported=False)["computed"]
        run["metrics"]=computed
        return run

    def test_regression_rescores_group_mae_rmse(self):
        run=self.make_run(shift=1.25)
        rec=validate_run_evidence(self.root,run)
        self.assertEqual(rec["metric_receipt"]["n_groups"],4)
        self.assertAlmostEqual(run["metrics"]["MAE"],1.25)
        self.assertAlmostEqual(run["metrics"]["RMSE"],1.25)
        run["metrics"]["MAE"]=0.01
        with self.assertRaisesRegex(ContractError,"RECOMPUTED_METRIC_MISMATCH"):
            validate_run_evidence(self.root,run)

    def test_regression_paired_difference_and_uncertainty(self):
        a=self.make_run(run_id="A",shift=2)
        b=self.make_run(run_id="B",shift=1)
        result=compare_runs(a,b,"MAE",lower_is_better=True)
        self.assertAlmostEqual(result["improvement_direction_delta"],1)
        interval=group_bootstrap(self.root,a,b,"MAE",lower_is_better=True,iterations=100)
        self.assertEqual(interval["status"],"EXPLORATORY_INTERVAL")
        self.assertAlmostEqual(interval["directional_delta_ci95"][0],1)

    def test_group_versus_pooled_not_comparable(self):
        a=self.make_run(run_id="A",shift=0)
        b=self.make_run(run_id="B",shift=1)
        b["metric_spec"]["aggregation"]="pooled"
        with self.assertRaisesRegex(ContractError,"NOT_COMPARABLE"):
            compare_runs(a,b,"MAE")

    def test_event_arithmetic_and_no_truth_window(self):
        run=self.make_run(kind="event",shift=0.2)
        self.assertAlmostEqual(run["metrics"]["event_recall"],1.0)
        validate_run_evidence(self.root,run)
        p=self.root/run["metric_spec"]["predictions_ref"]
        raw=json.loads(p.read_text())
        raw[0]["candidate_scores"]=[0.7,0.9]
        write_json(p,raw)
        run["artifact_hashes"][p.name]=fingerprint_file(p)
        with self.assertRaisesRegex(ContractError,"one row_index"):
            validate_run_evidence(self.root,run)

    def test_frozen_group_overlap_and_missing_predictions(self):
        run=self.make_run(run_id="C",shift=0.0)
        write_json(self.split,{"train_groups":["G1","G4"],"dev_groups":["G4","G5","G6","G7"]})
        run["metric_spec"]["split_sha256"]=fingerprint_file(self.split)
        run["group_split"]="pinned-groups:"+run["metric_spec"]["split_sha256"]
        with self.assertRaisesRegex(ContractError,"overlap"):
            verify_metrics(self.root,run)
        write_json(self.split,{"train_groups":[f"G{i}" for i in range(4)],
                               "dev_groups":[f"G{i}" for i in range(4,8)]})
        run=self.make_run(run_id="D",shift=0.0)
        path=self.root/run["metric_spec"]["predictions_ref"]
        raw=json.loads(path.read_text())[:-1]
        write_json(path,raw)
        run["artifact_hashes"][path.name]=fingerprint_file(path)
        with self.assertRaisesRegex(ContractError,"complete frozen DEV query"):
            verify_metrics(self.root,run)

    def test_external_typed_import_recomputes_only_dev(self):
        from adapters.typed_agent_bridge import import_typed_predictions
        from core.state import initial_state, save_state, record_event
        save_state(self.root/"STATE.json",initial_state("test","synthetic only"))
        task={"schema_version":"0.1","task_id":"T","protocol_id":"P",
              "status":"ACTIVE","question":"evaluate regression","metric":"MAE",
              "metric_direction":"minimize",
              "group_split":"pinned-groups:"+self.ssha,
              "baseline":"dummy","holdout_policy":"external untouched",
              "legal_inputs":["sensor"],"data_refs":["D"],"nearest_work":[]}
        taskfile=write_json(self.root/"TASK.json",task)
        record_event(self.root,"TASK_DEFINED","Synthetic grouped Task",taskfile)
        predicted=write_json(self.root/"external.json",
                   [{"row_index":i,"prediction":float(self.rows[i][2])+1} for i in self.dev])
        source=self.root/"model.py"
        source.write_text("# provided by external Agent; never executed\n",encoding="utf-8")
        result=import_typed_predictions(self.root,self.manifest,self.split,"D","typed1",predicted,source)
        self.assertAlmostEqual(result["metrics"]["MAE"],1)
        self.assertFalse(result["causal_execution_attested"])
        run=json.loads(Path(result["run_path"]).read_text(encoding="utf-8"))
        validate_run_evidence(self.root,run)
        with self.assertRaises(FileExistsError):
            import_typed_predictions(self.root,self.manifest,self.split,"D","typed1",predicted,source)

    def test_no_event_rows_are_false_alarms(self):
        # Create one no-event row in DEV and record no trigger; source manifest digest changes.
        self.rows[12]=(self.rows[12][0],self.rows[12][1],self.rows[12][2],"NONE")
        with (self.root/"data.csv").open("w",newline="",encoding="utf-8") as out:
            w=csv.writer(out);w.writerow(["id","group","target","event"]);w.writerows(self.rows)
        manifest=json.loads(self.manifest.read_text())
        manifest["datasets"][0]["sha256"]=fingerprint_file(self.root/"data.csv")
        write_json(self.manifest,manifest)
        self.msha=fingerprint_file(self.manifest)
        run=self.make_run(kind="event",run_id="E")
        self.assertGreater(run["metrics"]["false_alarm_rate"],0)
        self.assertLess(run["metrics"]["event_recall"],1.01)


if __name__=="__main__":
    unittest.main()
