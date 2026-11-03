"""Local chain-of-digests for audit-history corruption detection.

SHA chaining detects accidental edits/deletions/reordering with a trusted
STATE anchor. It is not a signature: someone able to rewrite BOTH the ledger
and its anchor can forge a new consistent chain. Use remote immutable backups
for adversarial tamper resistance.
"""
from __future__ import annotations
import hashlib
import json
import os
import tempfile
from pathlib import Path
from core.contracts import ContractError

GENESIS = "0"*64

def digest(entry:dict)->str:
    canonical={k:v for k,v in entry.items() if k!="event_digest"}
    raw=json.dumps(canonical,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def scan(project:Path)->dict:
    path=project/"EVENTS.jsonl"
    if not path.exists():
        return {"chain_length":0,"head_digest":GENESIS,"last_event_id":None,"entries":[],"errors":[]}
    entries,errors=[],[]
    prev=GENESIS
    with path.open(encoding="utf-8") as f:
        for line_no,line in enumerate(f,1):
            if not line.strip():
                errors.append(f"blank event line {line_no}")
                continue
            try:
                row=json.loads(line)
                if not isinstance(row,dict):
                    raise ValueError("not an object")
                if row.get("seq")!=line_no:
                    errors.append(f"incorrect event seq on line {line_no}")
                if row.get("prev_digest")!=prev:
                    errors.append(f"previous digest mismatch on line {line_no}")
                calculated=digest(row)
                if row.get("event_digest")!=calculated:
                    errors.append(f"event digest mismatch on line {line_no}")
                prev=calculated
                entries.append(row)
            except (ValueError,TypeError) as exc:
                errors.append(f"invalid event on line {line_no}: {exc}")
    if len({row.get("event_id") for row in entries})!=len(entries):
        errors.append("duplicate event IDs")
    return {"chain_length":len(entries),"head_digest":prev,
            "last_event_id":entries[-1].get("event_id") if entries else None,
            "entries":entries,"errors":errors}

def match_state(state:dict,ledger:dict, *,allow_one_pending:bool=False)->dict:
    length=state.get("ledger_length")
    head=state.get("ledger_head_digest")
    if type(length) is not int or not isinstance(head,str):
        return {"consistent":False,"reason":"LEGACY_UNANCHORED_REQUIRES_MIGRATION"}
    if ledger["errors"]:
        return {"consistent":False,"reason":"CHAIN_CORRUPTED","errors":ledger["errors"]}
    actual_len=ledger["chain_length"]
    if length==actual_len and head==ledger["head_digest"] and state.get("last_event_id")==ledger["last_event_id"]:
        return {"consistent":True,"reason":"CHAIN_AND_STATE_MATCH"}
    if allow_one_pending and actual_len==length+1:
        prior=ledger["entries"][-1]
        if (prior["prev_digest"]==head and
                (ledger["entries"][-2]["event_id"] if length else None)==state.get("last_event_id")):
            return {"consistent":False,"reason":"ONE_PENDING_EVENT"}
    return {"consistent":False,"reason":"CHAIN_ANCHOR_MISMATCH"}

def append(project:Path,state:dict,row:dict)->dict:
    if "seq" in row or "prev_digest" in row or "event_digest" in row:
        raise ContractError("Event chain fields are controller-generated")
    length=state.get("ledger_length")
    head=state.get("ledger_head_digest")
    if type(length) is not int or not isinstance(head,str):
        raise ContractError("Legacy log must be explicitly migrated before new writes")
    enriched={**row,"seq":length+1,"prev_digest":head}
    enriched["event_digest"]=digest(enriched)
    # Caller already holds .forge-state.lock and checked history_status.
    with (project/"EVENTS.jsonl").open("a",encoding="utf-8") as f:
        f.write(json.dumps(enriched,ensure_ascii=False,allow_nan=False)+"\n")
        f.flush()
        os.fsync(f.fileno())
    state["ledger_length"]=length+1
    state["ledger_head_digest"]=enriched["event_digest"]
    state["last_event_id"]=enriched["event_id"]
    return enriched

def migrate_legacy(project:Path, *,apply:bool=False)->dict:
    """One-time explicit anchoring; cannot prove historical content predates migration."""
    import shutil
    from datetime import datetime,timezone
    from core.locking import file_lock
    from core.state import load_state,save_state
    with file_lock(project/".forge-state.lock"):
        state=load_state(project/"STATE.json")
        raw=(project/"EVENTS.jsonl").read_text(encoding="utf-8").splitlines() if (project/"EVENTS.jsonl").exists() else []
        rows=[json.loads(l) for l in raw if l.strip()]
        if len(rows)!=len(raw) or any(not isinstance(x,dict) for x in rows):
            raise ValueError("Malformed legacy log; manual recovery required")
        if rows and state.get("last_event_id")!=rows[-1].get("event_id"):
            raise ValueError("Legacy head disagrees with State; refuse to anchor")
        if not rows and state.get("last_event_id") is not None:
            raise ValueError("State references missing legacy events")
        if any("event_digest" in row or "prev_digest" in row or "seq" in row for row in rows):
            raise ValueError("Partly migrated log; manual recovery required")
        if state.get("ledger_length") is not None or state.get("ledger_head_digest") is not None:
            raise ValueError("Ledger already anchored; migration inappropriate")
        prev=GENESIS
        encoded=[]
        for index,row in enumerate(rows,1):
            item={**row,"seq":index,"prev_digest":prev}
            item["event_digest"]=digest(item)
            encoded.append(json.dumps(item,ensure_ascii=False,allow_nan=False))
            prev=item["event_digest"]
        summary={"status":"LEGACY_UNVERIFIED_PREMIGRATION","events":len(encoded),
                 "warning":"Hash chains cannot retroactively establish prior history authenticity",
                 "applied":False}
        if not apply:
            return summary
        stamp=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        backup=project/("EVENTS.before-chain-"+stamp+".jsonl")
        state_backup=project/("STATE.before-chain-"+stamp+".json")
        shutil.copy2(project/"STATE.json", state_backup)
        if (project/"EVENTS.jsonl").exists():
            shutil.copy2(project/"EVENTS.jsonl",backup)
        fd,tmp=tempfile.mkstemp(dir=project,prefix=".migrate-ledger-")
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as f:
                f.write("\n".join(encoded)+("\n" if encoded else ""))
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp,project/"EVENTS.jsonl")
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        state["ledger_length"]=len(encoded)
        state["ledger_head_digest"]=prev
        save_state(project/"STATE.json",state)
        return {**summary,"applied":True,"backup":str(backup),"state_backup":str(state_backup)}
