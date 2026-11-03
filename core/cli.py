"""CLI: no search, download, fitting or external execution."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from core.contracts import VALIDATORS, ContractError, validate
from core.router import ROUTES, route
from core.state import initial_state, load_state, record_event, save_state

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
    check = sub.add_parser("validate")
    check.add_argument("--kind", required=True, choices=sorted(VALIDATORS))
    check.add_argument("--file", required=True, type=Path)
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
            result = record_event(args.dir, args.event, args.note)
        else:
            with args.file.open(encoding="utf-8") as f:
                validate(args.kind, json.load(f))
            result = {"file": str(args.file), "kind": args.kind, "status": "STRUCTURE_VALID_ONLY"}
    except (ValueError, ContractError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
