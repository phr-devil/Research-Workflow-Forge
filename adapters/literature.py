"""Source-backed public paper-metadata discovery (OpenAlex + Crossref).

Only an explicit CLI call performs network requests. This is NOT full-text
verification or novelty assessment; raw metadata remains untrusted input.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SCHEMA_VERSION = "0.1"
MAX_RESPONSE_BYTES = 3_000_000
PROVIDERS = ("openalex", "crossref")

def _get_json(req: Request) -> dict:
    try:
        with urlopen(req, timeout=15) as response:
            payload = response.read(MAX_RESPONSE_BYTES + 1)
        if len(payload) > MAX_RESPONSE_BYTES:
            raise ValueError("Provider response exceeds safe metadata limit")
        result = json.loads(payload.decode("utf-8"))
        if not isinstance(result, dict):
            raise ValueError("Expected JSON object from provider")
        return result
    except (HTTPError, URLError, TimeoutError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Provider unavailable: {type(exc).__name__}: {exc}") from exc

def fetch_provider(provider: str, query: str, limit: int, api_key: str | None = None) -> dict:
    headers = {"Accept": "application/json", "User-Agent": "ResearchWorkflowForge/0.2 (academic metadata search)"}
    if provider == "openalex":
        params = {"search": query, "per_page": str(limit),
                  "select": "id,display_name,doi,publication_year,primary_location"}
        if api_key:
            # Header avoids leaking keys via URLs, error messages and event logs.
            headers["Authorization"] = f"Bearer {api_key}"
        url = "https://api.openalex.org/works?" + urlencode(params)
    elif provider == "crossref":
        url = "https://api.crossref.org/works?" + urlencode({"query.bibliographic": query, "rows": limit})
    else:
        raise ValueError(f"unsupported provider: {provider}")
    return _get_json(Request(url, headers=headers))

def _doi(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = re.sub(r"(?i)^https?://(?:dx\.)?doi\.org/", "", value.strip())
    return raw.lower() or None

def _year(raw: object) -> int | None:
    return raw if isinstance(raw, int) and not isinstance(raw, bool) and 1500 <= raw <= 2200 else None

def _canonical_record(title: object, doi: object, year: object, url: object, provider: str) -> dict | None:
    if not isinstance(title, str) or not title.strip():
        return None
    normalized_title = " ".join(title.split()).strip()
    norm_doi = _doi(doi)
    norm_year = _year(year)
    key = f"doi:{norm_doi}" if norm_doi else f"title:{''.join(ch for ch in normalized_title.lower() if ch.isalnum())}:{norm_year}"
    link = f"https://doi.org/{norm_doi}" if norm_doi else (url if isinstance(url, str) and url.startswith("https://") else None)
    return {"record_id": hashlib.sha256(key.encode("utf-8")).hexdigest()[:16],
            "title": normalized_title, "doi": norm_doi, "year": norm_year, "url": link,
            "sources": [provider], "verification": "METADATA_ONLY"}

def normalize(provider: str, payload: dict) -> list[dict]:
    if provider == "openalex":
        rows = payload.get("results")
        if not isinstance(rows, list):
            raise ValueError("OpenAlex returned no results list")
        out = []
        for row in rows:
            if isinstance(row, dict):
                obj = _canonical_record(row.get("display_name"), row.get("doi"), row.get("publication_year"), row.get("id"), provider)
                if obj: out.append(obj)
        return out
    if provider == "crossref":
        rows = payload.get("message", {}).get("items") if isinstance(payload.get("message"), dict) else None
        if not isinstance(rows, list):
            raise ValueError("Crossref returned no message.items list")
        out = []
        for row in rows:
            if not isinstance(row, dict): continue
            titles = row.get("title")
            title = titles[0] if isinstance(titles, list) and titles else None
            dates = row.get("published", {}).get("date-parts") if isinstance(row.get("published"), dict) else None
            year = dates[0][0] if isinstance(dates, list) and dates and isinstance(dates[0], list) and dates[0] else None
            obj = _canonical_record(title, row.get("DOI"), year, row.get("URL"), provider)
            if obj: out.append(obj)
        return out
    raise ValueError(f"unsupported provider: {provider}")

def search(query: str, limit: int = 6, providers: tuple[str, ...] = PROVIDERS,
           api_key: str | None = None, fetcher=fetch_provider) -> dict:
    query = " ".join(query.split())
    if not (3 <= len(query) <= 300):
        raise ValueError("query must have 3-300 characters")
    if isinstance(limit, bool) or not isinstance(limit, int) or not (1 <= limit <= 25):
        raise ValueError("limit must be 1..25 per provider")
    if not providers or any(p not in PROVIDERS for p in providers):
        raise ValueError("invalid provider")
    unique: dict[str, dict] = {}
    checked, errors = [], []
    for provider in dict.fromkeys(providers):
        try:
            docs = normalize(provider, fetcher(provider, query, limit, api_key=api_key))
            checked.append(provider)
            for doc in docs:
                key = doc["record_id"]
                if key not in unique:
                    unique[key] = doc
                elif provider not in unique[key]["sources"]:
                    unique[key]["sources"].append(provider)
        except (RuntimeError, ValueError, KeyError, TypeError) as exc:
            errors.append({"provider": provider, "error": str(exc)[:400]})
    if not checked:
        raise RuntimeError(f"No usable provider results: {errors}")
    return {"schema_version": SCHEMA_VERSION, "query": query,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "verification": "METADATA_ONLY", "sources_checked": checked,
            "source_errors": errors, "records": list(unique.values())}

def write_bundle(path: Path, bundle: dict, overwrite: bool = False) -> None:
    from core.contracts import validate
    # An empty result remains informative but cannot satisfy SEARCH_READY.
    if bundle["records"]:
        validate("evidence", bundle)
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists; pass --overwrite intentionally")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".literature-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Explicit public metadata search, not full-paper novelty check")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--provider", choices=("all", *PROVIDERS), default="all")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    providers = PROVIDERS if args.provider == "all" else (args.provider,)
    try:
        bundle = search(args.query, args.limit, providers, os.getenv("OPENALEX_API_KEY"))
        if args.out:
            write_bundle(args.out, bundle, args.overwrite)
        print(json.dumps({"status": "METADATA_ONLY", "papers": len(bundle["records"]),
                          "sources_checked": bundle["sources_checked"],
                          "source_errors": bundle["source_errors"],
                          "output": str(args.out) if args.out else None,
                          "preview": [{"title": d["title"], "doi": d["doi"]}
                                      for d in bundle["records"][:5]]}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(2, f"search failed: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
