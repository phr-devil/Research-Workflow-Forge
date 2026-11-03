"""Forge adapter for the vendored ResearchStudio multi-source paper search.

Directly executes upstream *source_worker.py* and reuses upstream *postprocess.py*.
The copied upstream package remains unmodified under vendor/, with its MIT LICENSE.
Only public paper metadata is collected: no paper/full-text download, novelty
judgment, dataset download, training or user authorization inference.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from adapters.literature import write_bundle
from core.contracts import validate

VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "researchstudio" / "paper_search" / "scripts"
UPSTREAM_REVISION = "063f10088af49909e1a4a7ea8d29efe19633f34e"
SOURCES = ("open_alex", "crossref", "arxiv", "semantic_scholar", "dblp", "openreview")
DEFAULT_SOURCES = ("open_alex", "crossref", "arxiv")

def _postprocess():
    """Load vendored pure-Python dedup/ranking without importing provider dependencies."""
    path = VENDOR / "postprocess.py"
    spec = importlib.util.spec_from_file_location("_forge_rs_postprocess", path)
    if not spec or not spec.loader:
        raise RuntimeError("ResearchStudio postprocess.py missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_upstream_worker(source: str, queries: list[str], start_year: int,
                        end_year: int, limit: int, timeout: int = 100) -> dict:
    """Explicit network operation with hard process timeout and no shell execution."""
    worker = VENDOR / "source_worker.py"
    if not worker.is_file():
        raise FileNotFoundError(f"Vendored upstream worker missing: {worker}")
    with tempfile.TemporaryDirectory(prefix="forge-rs-") as tmp:
        output = Path(tmp) / "papers.json"
        command = [sys.executable, str(worker), "--source", source,
                   "--queries-json", json.dumps(queries, ensure_ascii=False),
                   "--start-year", str(start_year), "--end-year", str(end_year),
                   "--max-results", str(limit), "--out", str(output)]
        try:
            result = subprocess.run(command, text=True, capture_output=True,
                                    encoding="utf-8", timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"{source}: worker timed out after {timeout}s") from exc
        if result.returncode != 0:
            # Do not echo stderr into persisted evidence; it may contain local configuration.
            raise RuntimeError(f"{source}: worker exited with code {result.returncode}")
        if not output.is_file() or output.stat().st_size > 3_000_000:
            raise RuntimeError(f"{source}: missing or oversized worker output")
        payload = json.loads(output.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("source") != source:
            raise RuntimeError(f"{source}: worker output source mismatch")
        return payload

def _record(paper: dict) -> dict | None:
    title = paper.get("title")
    if not isinstance(title, str) or not title.strip():
        return None
    title = " ".join(title.split())
    doi = paper.get("doi")
    if isinstance(doi, str):
        doi = doi.strip().lower()
        for prefix in ("https://doi.org/", "http://doi.org/", "doi.org/", "doi:"):
            if doi.startswith(prefix):
                doi = doi[len(prefix):]
        doi = doi or None
    else:
        doi = None
    arxiv = paper.get("arxiv_id")
    arxiv = str(arxiv).strip() if arxiv else None
    year = paper.get("year")
    if isinstance(year, bool) or not isinstance(year, int):
        year = None
    ident = f"doi:{doi}" if doi else (f"arxiv:{arxiv}" if arxiv else f"title:{title.lower()}:{year}")
    sources = [s for s in paper.get("found_in", []) if s in SOURCES]
    if not sources and paper.get("source") in SOURCES:
        sources = [paper["source"]]
    if not sources:
        return None
    url = paper.get("url")
    return {"record_id": hashlib.sha256(ident.encode("utf-8")).hexdigest()[:16],
            "title": title, "doi": doi, "arxiv_id": arxiv, "year": year,
            "url": url if isinstance(url, str) and url.startswith(("https://", "http://")) else None,
            "abstract": paper.get("abstract") if isinstance(paper.get("abstract"), str) else None,
            "authors": [a for a in (paper.get("authors") or []) if isinstance(a, str)][:30],
            "citation_count": paper.get("citation_count"),
            "relevance_score": paper.get("relevance_score"),
            "is_survey": bool(paper.get("is_survey")),
            "sources": sources, "verification": "METADATA_ONLY"}

def search_papers(queries: list[str], *, sources: tuple[str, ...] = DEFAULT_SOURCES,
                  start_year: int | None = None, end_year: int | None = None,
                  limit: int = 6, worker: Callable = run_upstream_worker) -> dict:
    queries = [" ".join(q.split()) for q in queries]
    if not queries or len(queries) > 4 or any(not 3 <= len(q) <= 250 for q in queries):
        raise ValueError("Supply 1-4 concrete queries of length 3..250")
    sources = tuple(dict.fromkeys(sources))
    if not sources or any(s not in SOURCES for s in sources):
        raise ValueError("Choose supported paper sources")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("limit must be 1..20 per query/source")
    current = datetime.now(timezone.utc).year
    end = current if end_year is None else end_year
    start = max(1900, end - 3) if start_year is None else start_year
    if type(start) is not int or type(end) is not int or not (1900 <= start <= end <= current + 1):
        raise ValueError("invalid search year window")

    by_source, errors, completed = {}, [], []
    for source in sources:
        try:
            result = worker(source, queries, start, end, limit)
            if not isinstance(result, dict) or result.get("source") != source:
                raise ValueError("wrong or missing source in worker result")
            papers = result.get("papers")
            if not isinstance(papers, list):
                raise ValueError("worker returned no papers list")
            by_source[source] = [p for p in papers if isinstance(p, dict)]
            failures = result.get("errors") or []
            for failure in failures:
                errors.append({"provider": source, "error": str(failure)[:280]})
            if not failures:
                completed.append(source)
        except (ValueError, RuntimeError, OSError, TypeError, json.JSONDecodeError) as exc:
            errors.append({"provider": source, "error": f"{type(exc).__name__}: {str(exc)[:220]}"})
    if not completed and not any(by_source.values()):
        raise RuntimeError("No source completed successfully; see source failures and retry explicitly")

    process = _postprocess()
    merged = process.dedup(by_source)
    ranked, _ = process.rank(merged, queries, min_score=None)  # preserve full recall
    records = [r for paper in ranked if (r := _record(paper))]
    bundle = {"schema_version": "0.1", "query": " | ".join(queries),
              "queries": queries, "retrieved_at": datetime.now(timezone.utc).isoformat(),
              "verification": "METADATA_ONLY", "retrieval_state": "PARTIAL" if errors else "COMPLETE",
              "upstream": "microsoft/ResearchStudio:paper_search",
              "upstream_commit": UPSTREAM_REVISION,
              "sources_attempted": list(sources), "sources_checked": completed,
              "source_errors": errors, "records": records}
    if records:
        validate("evidence", bundle)  # structural source data, not scientific certification
    return bundle

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Source-backed multi-source paper metadata discovery")
    parser.add_argument("--query", action="append", required=True, help="Repeat for complementary research queries")
    parser.add_argument("--sources", nargs="+", choices=SOURCES, default=list(DEFAULT_SOURCES))
    parser.add_argument("--start-year", type=int)
    parser.add_argument("--end-year", type=int)
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        bundle = search_papers(args.query, sources=tuple(args.sources),
                               start_year=args.start_year, end_year=args.end_year,
                               limit=args.limit)
        write_bundle(args.out, bundle, overwrite=args.overwrite)
        print(json.dumps({"state": bundle["retrieval_state"],
                          "records": len(bundle["records"]), "out": str(args.out),
                          "sources_checked": bundle["sources_checked"],
                          "errors": bundle["source_errors"],
                          "verification": "METADATA_ONLY"}, ensure_ascii=False, indent=2))
        return 0 if bundle["sources_checked"] else 2
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(2, f"search failed: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
