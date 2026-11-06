"""Scientific figure metadata preflight; text-only and NOT science verification.

Inspired by K-Dense scientific-visualization: record actual estimand,
uncertainty, replication, missingness and exclusions before polishing.
No plotting dependencies, data access, or image creation.
"""
from __future__ import annotations

REQUIRED_METRIC_FIELDS = (
    "metric", "unit", "denominator", "independent_unit"
)
REQUIRED_CONTEXT_FIELDS = (
    "population_or_split", "transform_notes", "missing_policy",
    "uncertainty_definition", "selection_history"
)


def _substantive(value) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not any(
        sentinel in value.upper() for sentinel in ("REPLACE_WITH", "TODO", "TBD")
    )


def inspect_evidence_metadata(record: dict) -> dict:
    """Check declarations exist; their accuracy must be established independently.

    Compatible figure-v1/v2 manifests remain usable, even if the scientific
    declarations are incomplete. Report incompleteness rather than guessing.
    """
    if not isinstance(record, dict):
        raise ValueError("figure record must be a dictionary")
    if record.get("figure_type", "data") != "data":
        return {"status": "NOT_APPLICABLE_SCHEMATIC",
                "missing_fields": [], "scientific_source_verified": False}
    ctx = record.get("science_context")
    ctx = ctx if isinstance(ctx, dict) else {}
    missing = [field for field in REQUIRED_METRIC_FIELDS if not _substantive(record.get(field))]
    missing += ["science_context." + field for field in REQUIRED_CONTEXT_FIELDS
                if not _substantive(ctx.get(field))]
    return {
        "status": "METADATA_COMPLETE_NOT_SCIENCE_VERIFIED" if not missing else "INCOMPLETE_METADATA",
        "missing_fields": missing,
        "scientific_source_verified": False,
        "note": "Declarations only: not independent Run, sample unit, uncertainty or metric verification",
    }
