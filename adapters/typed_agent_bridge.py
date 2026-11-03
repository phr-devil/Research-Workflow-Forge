"""Import typed regression/event predictions from a separately controlled Agent.

Does not run external code, attest causal execution, or grant authorization.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import re
import shutil
from pathlib import Path

from core.contracts import ContractError, validate
from core.data_access import bind_dev_dataset
from core.metric_extensions import REGRESSION_FORMAT, EVENT_FORMAT
from core.metric_verify import sample_hash, verify_metrics
from core.receipts import fingerprint_file, check_state_task
from core.run_integrity import validate_run_evidence
from core.state import load_state


def import_typed_predictions(project: Path, manifest_path: Path, split_path: Path,
                             dataset_id: str, run_id: str, predictions_path: Path,
                             source_path: Path, *, kind: str = "regression",
                             aggregation: str = "group_mean",
                             tolerance_s: float | None = None) -> dict:
    project = project.resolve()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", run_id):
        raise ValueError("unsafe run_id")
    if kind not in {"regression", "event"}:
        raise ValueError("kind must be regression/event")
    task=check_state_task(project,load_state(project/"STATE.json"))
    if task is None:
        raise ContractError("ACTIVE task required for typed import")
    if dataset_id not in task["data_refs"]:
        raise ContractError("dataset must belong to the active Task")
    manifest=manifest_path.resolve()
    split=split_path.resolve()
    src=source_path.resolve()
    preds=predictions_path.resolve()
    for f in (manifest,split,src,preds):
        if not f.is_relative_to(project) or not f.is_file():
            raise ValueError("input must be an existing file inside the project")
    if src.stat().st_size > 2_000_000 or preds.stat().st_size > 5_000_000:
        raise ValueError("external Agent output exceeds bounded import size")
    split_sha=fingerprint_file(split)
    protocol="pinned-groups:"+split_sha
    if task["group_split"] != protocol:
        raise ContractError("pinned-group split differs from active Task")
    fmt=REGRESSION_FORMAT if kind=="regression" else EVENT_FORMAT
    metric=task["metric"]
    permitted={"MAE","RMSE"} if kind=="regression" else {"event_recall","false_alarm_rate"}
    if metric not in permitted:
        raise ContractError("active Task metric does not match typed evaluator")
    if kind=="regression" and aggregation not in {"group_mean","pooled"}:
        raise ContractError("invalid regression aggregation")
    if kind=="event" and (type(tolerance_s) not in (int,float) or
                          not math.isfinite(tolerance_s) or not 0<tolerance_s<=30):
        raise ContractError("event tolerance must be >0 and <=30 seconds")
    data_path,ds=bind_dev_dataset(project,manifest,dataset_id,purpose="EVALUATE_DEV")
    groups=json.loads(split.read_text(encoding="utf-8")).get("dev_groups")
    if not isinstance(groups,list) or not groups:
        raise ContractError("missing frozen development groups")
    sample_col,group_col=ds.get("sample_id_column"),ds.get("group_column")
    if not all(isinstance(x,str) and x for x in (sample_col,group_col)):
        raise ContractError("typed input requires trusted sample IDs and independent groups")
    selected=[]
    with data_path.open(encoding="utf-8-sig",newline="") as stream:
        for row in csv.DictReader(stream):
            if row[group_col] in groups:
                selected.append(row[sample_col])
    if not selected or any(not x for x in selected):
        raise ContractError("no valid trusted DEV sample identities")
    folder=project/"runs"/run_id
    if folder.exists():
        raise FileExistsError("run ID already exists; never overwrite")
    folder.mkdir(parents=True,exist_ok=False)
    copied=folder/"predictions.json"
    try:
        shutil.copyfile(preds,copied)
        source_ref=src.relative_to(project).as_posix()
        pred_ref=copied.relative_to(project).as_posix()
        spec={"format":fmt,"predictions_ref":pred_ref,
              "manifest_ref":manifest.relative_to(project).as_posix(),
              "manifest_sha256":fingerprint_file(manifest),
              "dataset_id":dataset_id,
              "split_ref":split.relative_to(project).as_posix(),
              "split_sha256":split_sha}
        if kind=="regression":
            spec["aggregation"]=aggregation
            placeholder={"MAE":0.0,"RMSE":0.0}
        else:
            spec["tolerance_s"]=float(tolerance_s)
            spec["prediction_mode"]="SINGLE_EMISSION_PER_EPISODE"
            placeholder={"event_recall":0.0,"false_alarm_rate":0.0}
        run={"schema_version":"0.1","run_id":run_id,"task_id":task["task_id"],
             "protocol_id":task["protocol_id"],
             "dataset_version":ds["sha256"],"code_commit":"sha256:"+fingerprint_file(src),
             "evaluator_version":"forge-typed-v0.8",
             "status":"VALID","split":"dev","metrics":placeholder,
             "group_split":protocol,"sample_ids_hash":sample_hash(selected),
             "legal_inputs":list(task["legal_inputs"]),
             "artifact_refs":[pred_ref,source_ref],
             "artifact_hashes":{pred_ref:fingerprint_file(copied),source_ref:fingerprint_file(src)},
             "metric_spec":spec,
             "execution_scope":"EXTERNAL_AGENT_EXECUTION_NOT_ATTESTED"}
        run["metrics"]=verify_metrics(project,run,check_reported=False)["computed"]
        validate("run",run)
        validate_run_evidence(project,run)
        result_path=folder/"RUN.json"
        with result_path.open("x",encoding="utf-8") as out:
            json.dump(run,out,ensure_ascii=False,indent=2)
            out.write("\n")
    except Exception:
        for f in folder.iterdir():
            if f.is_file():
                f.unlink()
        folder.rmdir()
        raise
    return {"run_path":str(result_path),"metrics":run["metrics"],
            "verification":"DEV_METRIC_ARITHMETIC_RECOMPUTED",
            "causal_execution_attested":False,"science_confirmation":False}


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description="Import typed Agent predictions; no external code execution")
    parser.add_argument("--project",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--split",type=Path,required=True)
    parser.add_argument("--dataset-id",required=True)
    parser.add_argument("--run-id",required=True)
    parser.add_argument("--predictions",type=Path,required=True)
    parser.add_argument("--source-code",type=Path,required=True)
    parser.add_argument("--kind",choices=("regression","event"),required=True)
    parser.add_argument("--aggregation",choices=("group_mean","pooled"),default="group_mean")
    parser.add_argument("--tolerance-s",type=float)
    args=parser.parse_args(argv)
    try:
        result=import_typed_predictions(args.project,args.manifest,args.split,args.dataset_id,
                 args.run_id,args.predictions,args.source_code,
                 kind=args.kind,aggregation=args.aggregation,tolerance_s=args.tolerance_s)
    except (ValueError,OSError,TypeError,KeyError) as exc:
        parser.exit(2,"typed import failed: "+str(exc)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
