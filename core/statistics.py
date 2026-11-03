"""Optional paired group bootstrap for exploratory DEV uncertainty.

Do not use its 95% interval as a mandatory stop/novelty rule: adaptive
selection, small group counts and protocol-specific dependence still matter.
"""
from __future__ import annotations
import json
import random
from collections import defaultdict
from pathlib import Path
from core.contracts import ContractError
from core.metric_verify import _scores
from core.receipts import resolve_project_file

def _prediction_rows(project:Path, run:dict)->dict:
    spec=run["metric_spec"]
    rows=json.loads(resolve_project_file(project,spec["predictions_ref"]).read_text(encoding="utf-8"))
    return {row["row_index"]:row for row in rows}

def group_bootstrap(project:Path,a:dict,b:dict,metric:str, *,
                    lower_is_better:bool=False,iterations:int=300,seed:int=17)->dict:
    if metric not in {"macro_F1","balanced_accuracy"}:
        return {"status":"NOT_SUPPORTED","metric":metric}
    if type(iterations) is not int or not 100<=iterations<=5000:
        raise ValueError("bootstrap iterations must be 100..5000")
    x,y=_prediction_rows(project,a),_prediction_rows(project,b)
    if set(x)!=set(y):
        raise ContractError("Different prediction row IDs; paired group bootstrap not applicable")
    pairs=defaultdict(list)
    for i in sorted(x):
        r,s=x[i],y[i]
        if r["group"]!=s["group"] or r["truth"]!=s["truth"]:
            raise ContractError("Mismatched paired groups/truth between runs")
        pairs[r["group"]].append((r["truth"],r["prediction"],s["prediction"]))
    groups=sorted(pairs)
    if len(groups)<4:
        return {"status":"INSUFFICIENT_INDEPENDENT_GROUPS","n_groups":len(groups),
                "decision":"EXPLORATORY_ONLY"}
    rng=random.Random(seed)
    deltas=[]
    for _ in range(iterations):
        sample=[rng.choice(groups) for _ in groups]
        observations=[item for g in sample for item in pairs[g]]
        truth=[u[0] for u in observations]
        labels=sorted(set(truth)|{v for u in observations for v in u[1:]})
        old=_scores(truth,[u[1] for u in observations],labels)[metric]
        new=_scores(truth,[u[2] for u in observations],labels)[metric]
        deltas.append((old-new) if lower_is_better else (new-old))
    deltas.sort()
    lo=deltas[int((iterations-1)*0.025)]
    hi=deltas[int((iterations-1)*0.975)]
    return {"status":"EXPLORATORY_INTERVAL","method":"PAIRED_GROUP_BOOTSTRAP",
            "n_groups":len(groups),"iterations":iterations,"seed":seed,
            "directional_delta_ci95":[lo,hi],
            "suggestive_positive":lo>0,
            "decision":"NOT_A_FORMAL_CONFIRMATION",
            "selection_bias_warning":"Adaptively selecting many Challengers invalidates naive interval coverage"}
