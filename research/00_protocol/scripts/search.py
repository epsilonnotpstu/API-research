#!/usr/bin/env python3
"""Reproducible scholarly search harness for the API research review.

Every call appends one row to research/00_protocol/search_log.csv and stores
the raw API response under research/01_discovery/raw/<source>/<query_id>.json
so that each search can be audited and re-run.

Usage:
  search.py openalex "<query>" [--from 2022-01-01] [--to 2026-12-31] [--sort cited|relevance|date] [--n 25] [--pass 1] [--note ...]
  search.py crossref "<query>" [--from 2022] [--n 20] ...
  search.py arxiv "<arxiv search_query>" [--n 25] ...
  search.py s2 "<query>" [--from 2022] [--n 25] ...
"""
import argparse, csv, datetime as dt, json, os, re, sys, time, urllib.parse
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG = os.path.join(ROOT, "00_protocol", "search_log.csv")
RAW = os.path.join(ROOT, "01_discovery", "raw")
UA = {"User-Agent": "api-research-review/1.0 (academic literature review)"}
FIELDS = ["query_id", "pass", "retrieval_utc", "source", "query", "filters",
          "sort", "total_results", "retrieved", "request_url", "note"]


def next_qid(source):
    os.makedirs(os.path.join(RAW, source), exist_ok=True)
    n = len([f for f in os.listdir(os.path.join(RAW, source)) if f.endswith(".json")])
    return f"{source[:2].upper()}{n + 1:03d}"


def log(row):
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        if new:
            w.writeheader()
        w.writerow(row)


def get(url, params=None, tries=5):
    for i in range(tries):
        r = requests.get(url, params=params, headers=UA, timeout=60)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(5 * (i + 1))
            continue
        r.raise_for_status()
        return r
    r.raise_for_status()


def abstract_from_inverted(inv):
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def openalex(a):
    flt = []
    if a.frm:
        flt.append(f"from_publication_date:{a.frm}")
    if a.to:
        flt.append(f"to_publication_date:{a.to}")
    if a.filter:
        flt.append(a.filter)
    sort = {"cited": "cited_by_count:desc", "date": "publication_date:desc"}.get(a.sort)
    if a.ta:
        flt.append("title_and_abstract.search:" + a.query)
        params = {"per-page": a.n}
    else:
        params = {"search": a.query, "per-page": a.n}
    if a.cs:
        flt.append("primary_topic.field.id:17")
    if flt:
        params["filter"] = ",".join(flt)
    if sort:
        params["sort"] = sort
    r = get("https://api.openalex.org/works", params)
    d = r.json()
    rows = []
    for w in d.get("results", []):
        loc = (w.get("primary_location") or {}).get("source") or {}
        rows.append({
            "id": w["id"].rsplit("/", 1)[-1], "title": w.get("display_name"),
            "year": w.get("publication_year"), "venue": loc.get("display_name"),
            "type": w.get("type"), "cites": w.get("cited_by_count"),
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "authors": "; ".join(x["author"]["display_name"] for x in w.get("authorships", [])[:4]),
            "oa_url": (w.get("best_oa_location") or {}).get("pdf_url"),
            "abstract": abstract_from_inverted(w.get("abstract_inverted_index"))[:600],
        })
    return d.get("meta", {}).get("count"), rows, r.url, d, "; ".join(flt), sort or "relevance"


def crossref(a):
    params = {"query.bibliographic": a.query, "rows": a.n,
              "select": "DOI,title,author,issued,container-title,type,is-referenced-by-count"}
    flt = []
    if a.frm:
        flt.append(f"from-pub-date:{a.frm}")
    if flt:
        params["filter"] = ",".join(flt)
    r = get("https://api.crossref.org/works", params)
    d = r.json()["message"]
    rows = []
    for it in d.get("items", []):
        rows.append({
            "id": it.get("DOI"), "title": (it.get("title") or [""])[0],
            "year": ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0],
            "venue": (it.get("container-title") or [""])[0], "type": it.get("type"),
            "cites": it.get("is-referenced-by-count"), "doi": it.get("DOI"),
            "authors": "; ".join(f"{x.get('given','')} {x.get('family','')}".strip() for x in it.get("author", [])[:4]),
        })
    return d.get("total-results"), rows, r.url, d, "; ".join(flt), "relevance"


def arxiv(a):
    params = {"search_query": a.query, "max_results": a.n,
              "sortBy": "submittedDate" if a.sort == "date" else "relevance"}
    r = get("https://export.arxiv.org/api/query", params)
    txt = r.text
    total = re.search(r"<opensearch:totalResults>(\d+)", txt)
    rows = []
    for e in re.findall(r"<entry>(.*?)</entry>", txt, re.S):
        g = lambda t: (re.search(rf"<{t}>(.*?)</{t}>", e, re.S) or [None, ""])[1]
        rows.append({
            "id": g("id").rsplit("/abs/", 1)[-1], "title": " ".join(g("title").split()),
            "year": g("published")[:4], "venue": "arXiv",
            "authors": "; ".join(re.findall(r"<name>(.*?)</name>", e)[:4]),
            "doi": (re.search(r"<arxiv:doi[^>]*>(.*?)</arxiv:doi>", e) or [None, ""])[1],
            "journal_ref": (re.search(r"<arxiv:journal_ref[^>]*>(.*?)</arxiv:journal_ref>", e, re.S) or [None, ""])[1],
            "abstract": " ".join(g("summary").split())[:600],
        })
    return (int(total.group(1)) if total else None), rows, r.url, {"atom": txt}, "", params["sortBy"]


def s2(a):
    params = {"query": a.query, "limit": a.n,
              "fields": "title,year,venue,citationCount,externalIds,authors,publicationTypes,openAccessPdf"}
    if a.frm:
        params["year"] = f"{a.frm[:4]}-"
    r = get("https://api.semanticscholar.org/graph/v1/paper/search", params, tries=8)
    d = r.json()
    rows = []
    for p in d.get("data", []):
        ext = p.get("externalIds") or {}
        rows.append({
            "id": p.get("paperId"), "title": p.get("title"), "year": p.get("year"),
            "venue": p.get("venue"), "cites": p.get("citationCount"),
            "doi": ext.get("DOI"), "arxiv": ext.get("ArXiv"),
            "authors": "; ".join(x["name"] for x in (p.get("authors") or [])[:4]),
        })
    return d.get("total"), rows, r.url, d, params.get("year", ""), "relevance"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", choices=["openalex", "crossref", "arxiv", "s2"])
    ap.add_argument("query")
    ap.add_argument("--from", dest="frm")
    ap.add_argument("--to")
    ap.add_argument("--filter", help="extra raw OpenAlex filter, e.g. type:review")
    ap.add_argument("--sort", default="relevance")
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--pass", dest="pas", default="1")
    ap.add_argument("--note", default="")
    ap.add_argument("--abstracts", action="store_true")
    ap.add_argument("--ta", action="store_true", help="OpenAlex: restrict match to title+abstract")
    ap.add_argument("--cs", action="store_true", help="OpenAlex: restrict to Computer Science field (17)")
    a = ap.parse_args()
    total, rows, url, raw, filters, sort = globals()[a.source](a)
    qid = next_qid(a.source)
    with open(os.path.join(RAW, a.source, f"{qid}.json"), "w", encoding="utf-8") as fh:
        json.dump({"query": a.query, "url": url, "rows": rows, "raw": raw}, fh, ensure_ascii=False)
    log({"query_id": qid, "pass": a.pas, "retrieval_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
         "source": a.source, "query": a.query, "filters": filters, "sort": sort,
         "total_results": total, "retrieved": len(rows), "request_url": url, "note": a.note})
    print(f"## {qid} [{a.source}] total={total} :: {a.query}")
    for i, x in enumerate(rows, 1):
        extra = f" | {x.get('journal_ref')}" if x.get("journal_ref") else ""
        print(f"{i:2d}. {x['title']} ({x.get('year')}) | {x.get('venue')} | c={x.get('cites')} | {x.get('type','')} | doi={x.get('doi')} | id={x['id']}{extra}")
        if a.abstracts and x.get("abstract"):
            print(f"     ABS: {x['abstract'][:400]}")


if __name__ == "__main__":
    main()
