"""Read-only, training-free dataset preflight.

Inspect only an explicitly designated DEVELOPMENT CSV; never opens SEALED
files, normalizes features or fits a model. A manifest is not proof of license.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from core.contracts import validate

MAX_BYTES = 150_000_000
MAX_ROWS = 1_000_000

def audit_manifest(manifest: dict) -> dict:
    validate("dataset", manifest)
    issues, warnings, roles = [], [], {}
    for entry in manifest["datasets"]:
        roles.setdefault(entry["role"], []).append(entry["dataset_id"])
        if entry["label_status"] == "UNKNOWN":
            warnings.append(f"{entry['dataset_id']}: labels are not verified")
        if entry["role"] == "SEALED_CONFIRM" and entry.get("accessed_during_selection"):
            issues.append(f"{entry['dataset_id']}: sealed resource reported accessed during task selection")
        if not entry.get("license_ref"):
            warnings.append(f"{entry['dataset_id']}: official license not verified")
    names = [d["dataset_id"] for d in manifest["datasets"]]
    if len(set(names)) != len(names):
        issues.append("Duplicate dataset_id in manifest")
    return {"status": "BLOCKED" if issues else ("NEEDS_EVIDENCE" if warnings else "STRUCTURAL_PASS"),
            "datasets_by_role": roles, "issues": issues, "warnings": warnings,
            "scientific_evaluation_completed": False}

def audit_development_csv(path: Path, *, group_col: str, label_col: str,
                          id_col: str | None = None) -> dict:
    """Limited local DEV CSV preflight, no sealed reference or train operation."""
    size = path.stat().st_size
    if not (0 < size <= MAX_BYTES):
        raise ValueError("development CSV exceeds bounded audit size or is empty")
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    rows, groups, labels, seen_ids = 0, Counter(), Counter(), set()
    missing_group, missing_label, duplicate_ids = 0, 0, 0
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = [group_col, label_col] + ([id_col] if id_col else [])
        if not reader.fieldnames or any(c not in reader.fieldnames for c in required):
            raise ValueError("DEV CSV missing requested group/label/ID column")
        for row in reader:
            rows += 1
            if rows > MAX_ROWS:
                raise ValueError("DEV CSV exceeds maximum audit row count")
            group, label = (row.get(group_col) or "").strip(), (row.get(label_col) or "").strip()
            if group:
                groups[group] += 1
            else:
                missing_group += 1
            if label:
                labels[label] += 1
            else:
                missing_label += 1
            if id_col:
                rid = (row.get(id_col) or "").strip()
                if rid and rid in seen_ids:
                    duplicate_ids += 1
                seen_ids.add(rid)
    issues = []
    if missing_group or missing_label:
        issues.append("Missing group/label values in development samples")
    if duplicate_ids:
        issues.append("Duplicate development sample IDs")
    if not rows:
        issues.append("No development rows")
    return {"status": "BLOCKED" if issues else "STRUCTURAL_PASS",
            "kind": "DEV_CSV_ONLY", "bytes": size, "sha256": digest.hexdigest(),
            "rows": rows, "groups": len(groups), "classes": len(labels),
            "class_counts": dict(labels), "group_sizes": dict(groups),
            "missing_groups": missing_group, "missing_labels": missing_label,
            "duplicate_ids": duplicate_ids, "issues": issues,
            "model_fitting_performed": False, "sealed_data_read": False,
            "notes": "No train/test split or semantic correctness is inferred from this report"}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only manifest/DEV CSV preflight; no fitting")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--dev-csv", type=Path)
    parser.add_argument("--group-col")
    parser.add_argument("--label-col")
    parser.add_argument("--id-col")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if not args.manifest and not args.dev_csv:
        parser.error("Specify --manifest and/or --dev-csv")
    if args.dev_csv and (not args.group_col or not args.label_col):
        parser.error("--dev-csv requires --group-col and --label-col")
    try:
        result = {"analysis_type": "READ_ONLY_PREFLIGHT"}
        if args.manifest:
            result["manifest"] = audit_manifest(json.loads(args.manifest.read_text(encoding="utf-8")))
        if args.dev_csv:
            result["development"] = audit_development_csv(args.dev_csv, group_col=args.group_col,
                                      label_col=args.label_col, id_col=args.id_col)
        if args.out:
            if args.out.exists():
                parser.error("refusing to overwrite an existing audit")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if any(section.get("status") == "BLOCKED" for section in result.values()
                        if isinstance(section, dict)) else 0
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        parser.exit(2, f"preflight failed: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
