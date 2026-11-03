"""Import Codex/WorkBuddy/AIDE predictions without executing untrusted agent code.

An external Agent can run in its own separately secured workspace and give
Forge predictions + source code. Forge binds DEV labels and independently
recomputes metrics. This is NOT a sandbox or an automated Agent executor.
"""
from __future__ import annotations
import argparse
import json
import math
import re
import shutil
from pathlib import Path
from core.contracts import ContractError, validate
from core.data_access import bind_dev_dataset
from core.metric_verify import FORMAT, sample_hash, verify_metrics
from core.receipts import fingerprint, fingerprint_file, check_state_task, resolve_project_file
from core.run_integrity import validate_run_evidence
from core.state import load_state

def import_agent_predictions(project:Path,manifest_path:Path,dataset_id:str,
                             run_id:str,predictions_path:Path,source_path:Path, *,
                             parent_run_id:str|None=None,
                             measured_wall_seconds:float|None=None)->dict:
    project=project.resolve()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}",run_id):
        raise ValueError("unsafe run_id")
    if measured_wall_seconds is not None and (
        type(measured_wall_seconds) not in (float,int) or not math.isfinite(measured_wall_seconds) or
        measured_wall_seconds<0):
        raise ValueError("invalid measured wall time")
    task=check_state_task(project,load_state(project/"STATE.json"))
    if task is None:
        raise ContractError("An ACTIVE Task is required")
    data_path,ds=bind_dev_dataset(project,manifest_path,dataset_id,purpose="EVALUATE_DEV")
    if dataset_id not in task["data_refs"]:
        raise ContractError("dataset not declared in active Task")
    manifest=manifest_path.resolve()
    try:
        manifest_ref=manifest.relative_to(project).as_posix()
    except ValueError as exc:
        raise ContractError("Manifest must be project-contained and SHA-pinned") from exc
    # Agent-produced sources must be inspectable, project-contained and versioned.
    src=source_path.resolve()
    pred=predictions_path.resolve()
    for path in (src,pred):
        if not path.is_relative_to(project) or not path.is_file():
            raise ValueError("Agent outputs must exist inside project")
    if src.stat().st_size>2_000_000 or pred.stat().st_size>5_000_000:
        raise ValueError("Agent artifact exceeds bounded import size")
    raw=json.loads(pred.read_text(encoding="utf-8"))
    if not isinstance(raw,list) or not raw:
        raise ContractError("Predictions must be a nonempty list of row_index/group/truth/prediction")
    if parent_run_id:
        from core.journal import candidate_journal
        parents=[r for r in candidate_journal(project)["runs"] if r["run_id"]==parent_run_id and r["current_protocol"]]
        if len(parents)!=1:
            raise ContractError("Unknown or ambiguous parent run")
    folder=project/"runs"/run_id
    if folder.exists():
        raise FileExistsError("run_id already exists")
    folder.mkdir(parents=True,exist_ok=False)
    target=folder/"predictions.json"
    shutil.copyfile(pred,target)
    source_ref=src.relative_to(project).as_posix()
    ref=f"runs/{run_id}/predictions.json"
    ids=[p["row_index"] for p in raw]
    sample_col=ds.get("sample_id_column")
    if sample_col:
        import csv
        with data_path.open(encoding="utf-8-sig",newline="") as f:
            keys=[row.get(sample_col,"").strip() for row in csv.DictReader(f)]
        if any(type(i)!=int or i<0 or i>=len(keys) for i in ids):
            raise ContractError("invalid external prediction row")
        ids=[keys[i] for i in ids]
    run={"schema_version":"0.1","run_id":run_id,"task_id":task["task_id"],
         "protocol_id":task["protocol_id"],"status":"VALID","split":"dev",
         "dataset_version":ds["sha256"],"code_commit":"sha256:"+fingerprint_file(src),
         "evaluator_version":"forge-metric-verify-v1:"+fingerprint_file(Path(__file__).resolve().parents[1]/"core"/"metric_verify.py")[:12],
         "metrics":{"macro_F1":0.0,"balanced_accuracy":0.0},
         "group_split":task["group_split"],"sample_ids_hash":sample_hash(ids),
         "legal_inputs":list(task["legal_inputs"]), "parent_run_id":parent_run_id,
         "branch_kind":"IMPROVE" if parent_run_id else "DRAFT",
         "artifact_refs":[ref,source_ref],
         "artifact_hashes":{ref:fingerprint_file(target),source_ref:fingerprint_file(src)},
         "metric_spec":{"format":FORMAT,"predictions_ref":ref,"manifest_ref":manifest_ref,
                        "manifest_sha256":fingerprint_file(manifest),"dataset_id":dataset_id},
         "measured_cost":{"wall_seconds":measured_wall_seconds} if measured_wall_seconds is not None else {},
         "execution_scope":"EXTERNAL_AGENT_EXECUTION_NOT_ATTESTED"}
    try:
        calculated=verify_metrics(project,run,check_reported=False)["computed"]
        run["metrics"]=calculated
        validate("run",run)
        validate_run_evidence(project,run)
        path=folder/"RUN.json"
        path.write_text(json.dumps(run,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    except Exception:
        # Do not leave a misleading VALID Run on failed import.
        if target.exists():
            target.unlink()
        if folder.exists() and not list(folder.iterdir()):
            folder.rmdir()
        raise
    return {"run_path":str(path),"metrics":calculated,
            "source":"EXTERNAL_CODE_UNVERIFIED_EXECUTION",
            "evidence":"DEV_METRICS_RECOMPUTED",
            "science_confirmation":False}

def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description="Read and re-evaluate external Agent outputs; NO code execution")
    parser.add_argument("--project",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--dataset-id",required=True)
    parser.add_argument("--run-id",required=True)
    parser.add_argument("--predictions",type=Path,required=True)
    parser.add_argument("--source-code",type=Path,required=True)
    parser.add_argument("--parent-run-id")
    parser.add_argument("--measured-wall-seconds",type=float)
    args=parser.parse_args(argv)
    try:
        result=import_agent_predictions(args.project,args.manifest,args.dataset_id,args.run_id,
                                        args.predictions,args.source_code,parent_run_id=args.parent_run_id,
                                        measured_wall_seconds=args.measured_wall_seconds)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (ValueError,OSError,TypeError,KeyError) as exc:
        parser.exit(2,f"agent import failed: {exc}\n")

if __name__=="__main__":
    raise SystemExit(main())
