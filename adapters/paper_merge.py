"""Conservative cross-source metadata dedup, reusing ResearchStudio scoring.

Unlike upstream title-only merging, never merge conflicting known DOIs.
Ambiguous DOI-less titles are kept separate for manual disambiguation.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

VENDOR_POSTPROCESS = Path(__file__).resolve().parents[1] / "vendor" / "researchstudio" / "paper_search" / "scripts" / "postprocess.py"

def postprocess():
    spec = importlib.util.spec_from_file_location("_forge_rs_postprocess", VENDOR_POSTPROCESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("Missing pinned ResearchStudio postprocess source")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def merge_papers(by_source: dict, queries: list[str]) -> tuple[list[dict], list[dict]]:
    rs = postprocess()
    ordered = [(src, dict(p)) for src in sorted(by_source, key=rs._source_priority)
               for p in by_source[src] if isinstance(p, dict)]
    title_dois: dict[str, set[str]] = {}
    arxiv_dois: dict[str, set[str]] = {}
    for src, p in ordered:
        doi = rs.norm_doi(p.get("doi"))
        if not doi:
            continue
        title = rs.title_norm(p.get("title"))
        arxiv = rs.norm_arxiv(p.get("arxiv_id"))
        if title:
            title_dois.setdefault(title, set()).add(doi)
        if arxiv:
            arxiv_dois.setdefault(arxiv, set()).add(doi)
    title_conflicts = {k: v for k, v in title_dois.items() if len(v) > 1}
    arxiv_conflicts = {k: v for k, v in arxiv_dois.items() if len(v) > 1}

    groups: list[dict] = []
    for src, p in ordered:
        doi = rs.norm_doi(p.get("doi"))
        arxiv = rs.norm_arxiv(p.get("arxiv_id"))
        title = rs.title_norm(p.get("title"))
        choice = None
        for i, g in enumerate(groups):
            gd = rs.norm_doi(g.get("doi"))
            ga = rs.norm_arxiv(g.get("arxiv_id"))
            gt = rs.title_norm(g.get("title"))
            # Distinct known identifiers cannot be collapsed by a title collision.
            if doi and gd and doi != gd:
                continue
            if arxiv and ga and arxiv != ga and not (doi and gd and doi == gd):
                continue
            same_doi = bool(doi and gd and doi == gd)
            same_arxiv = bool(arxiv and ga and arxiv == ga and arxiv not in arxiv_conflicts)
            same_title = bool(title and gt == title and title not in title_conflicts
                              and (not arxiv or arxiv not in arxiv_conflicts))
            if same_doi or same_arxiv or same_title:
                choice = i
                break
        if choice is None:
            p["found_in"] = [src]
            groups.append(p)
        else:
            g = groups[choice]
            if src not in g["found_in"]:
                g["found_in"].append(src)
            g["citation_count"] = max(g.get("citation_count") or 0, p.get("citation_count") or 0)
            for field in rs._FILL_FIELDS:
                if not g.get(field) and p.get(field):
                    g[field] = p[field]
    for p in groups:
        p["found_in"].sort(key=rs._source_priority)
    ranked, _ = rs.rank(groups, queries, min_score=None)
    warnings = [{"kind": "TITLE_DOI_CONFLICT", "title_normalized": title,
                 "dois": sorted(dois)} for title, dois in sorted(title_conflicts.items())]
    warnings += [{"kind": "ARXIV_DOI_CONFLICT", "arxiv": arxiv,
                  "dois": sorted(dois)} for arxiv, dois in sorted(arxiv_conflicts.items())]
    return ranked, warnings
