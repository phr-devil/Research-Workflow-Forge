"""Deterministic CLI: route, record evidence pointers, compare or validate."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from core.comparison import compare_runs
from core.contracts import VALIDATORS, ContractError, validate
from core.router import ROUTES, route
from core.state import history_status, initial_state, load_state, record_event, save_state
from core.selection import selection_history
from core.journal import candidate_journal
from core.receipts import check_state_task

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-forge")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--dir", required=True, type=Path)
    init.add_argument("--project-id", required=True)
    init.add_argument("--goal", required=True)
    rt = sub.add_parser("route")
    rt.add_argument("--dir", required=True, type=Path)
    rt.add_argument("--event", required=True, choices=sorted(ROUTES))
    rec = sub.add_parser("record")
    rec.add_argument("--dir", required=True, type=Path)
    rec.add_argument("--event", required=True, choices=sorted(ROUTES))
    rec.add_argument("--note", required=True)
    rec.add_argument("--artifact", type=Path, help="shape-checked handoff file under --dir; without it only a note is logged")
    check = sub.add_parser("validate")
    check.add_argument("--kind", required=True, choices=sorted(VALIDATORS))
    check.add_argument("--file", required=True, type=Path)
    cmp = sub.add_parser("compare")
    cmp.add_argument("--champion", required=True, type=Path)
    cmp.add_argument("--challenger", required=True, type=Path)
    cmp.add_argument("--metric", required=True)
    cmp.add_argument("--lower-is-better", action="store_true")
    hist = sub.add_parser("history")
    hist.add_argument("--dir", required=True, type=Path)
    selection = sub.add_parser("selection", help="Read append-only task/protocol selection history")
    selection.add_argument("--dir", required=True, type=Path)
    receipt = sub.add_parser("check-task", help="Verify current active Task matches persisted receipt")
    receipt.add_argument("--dir", required=True, type=Path)
    journal = sub.add_parser("journal", help="Reconstruct candidate history from versioned Run receipts")
    journal.add_argument("--dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            path = args.dir / "STATE.json"
            if path.exists():
                parser.error(f"refusing to overwrite {path}")
            save_state(path, initial_state(args.project_id, args.goal))
            result = {"created": str(path), "status": "SCAFFOLD_ONLY"}
        elif args.command == "route":
            result = route(load_state(args.dir / "STATE.json"), args.event)
        elif args.command == "record":
            result = record_event(args.dir, args.event, args.note, args.artifact)
        elif args.command == "validate":
            with args.file.open(encoding="utf-8") as f:
                validate(args.kind, json.load(f))
            result = {"file": str(args.file), "kind": args.kind, "status": "STRUCTURE_VALID_ONLY"}
        elif args.command == "compare":
            with args.champion.open(encoding="utf-8") as f:
                champion = json.load(f)
            with args.challenger.open(encoding="utf-8") as f:
                challenger = json.load(f)
            result = compare_runs(champion, challenger, args.metric,
                                  lower_is_better=args.lower_is_better)
        elif args.command == "selection":
            result = selection_history(args.dir)
        elif args.command == "journal":
            result = candidate_journal(args.dir)
        elif args.command == "check-task":
            task = check_state_task(args.dir, load_state(args.dir / "STATE.json"))
            result = {"receipt_valid": True, "task_id": task["task_id"] if task else None}
        else:
            result = history_status(args.dir)
    except (ValueError, RuntimeError, ContractError, OSError, json.JSONDecodeError, UnicodeError, KeyError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("consistent", True) else 2

if __name__ == "__main__":
    raise SystemExit(main())
