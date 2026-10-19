#!/usr/bin/env python3
"""Verify candidate bibliographic records against independent registries.

For each seed (DOI or arXiv ID) it collects:
  * Crossref  (DOI registrar record: title, authors, year, venue, type, retractions/updates)
  * DataCite  (registrar for arXiv DOIs 10.48550/arXiv.*)
  * OpenAlex  (aggregator: OA status, alternate locations incl. arXiv, abstract, retraction flag)
and probes every candidate PDF URL with a small ranged GET, accepting it as a
verified direct PDF only if the response body starts with %PDF.

Raw responses: research/01_discovery/raw/verify/<cid>.json
Summary:       research/01_discovery/raw/verify/_summary.json

Usage: verify.py [cid ...]   (default: all seeds)
"""
import csv, difflib, json, os, re, sys, time, unicodedata
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SEEDS = os.environ.get("SEEDS") or os.path.join(ROOT, "01_discovery", "seed_candidates.csv")
OUT = os.environ.get("VOUT") or os.path.join(ROOT, "01_discovery", "raw", "verify")
UA = {"User-Agent": "api-research-review/1.0 (academic literature review; metadata verification)"}


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").lower()
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def sim(a, b):
    return round(difflib.SequenceMatcher(None, norm(a), norm(b)).ratio(), 3) if a and b else None


def get_json(url, tries=4):
    for i in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=45)
        except requests.RequestException as e:
            err = str(e)
            time.sleep(3 * (i + 1))
            continue
        if r.status_code == 404:
            return None, 404
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(5 * (i + 1))
            continue
        try:
            return r.json(), r.status_code
        except ValueError:
            return None, r.status_code
    return None, "error"


def crossref(doi):
    d, st = get_json(f"https://api.crossref.org/works/{doi}")
    if not d:
        return {"status": st}
    m = d["message"]
    return {
        "status": st,
        "title": (m.get("title") or [""])[0],
        "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() or a.get("name", "") for a in m.get("author", [])],
        "year": ((m.get("issued") or {}).get("date-parts") or [[None]])[0][0],
        "venue": (m.get("container-title") or [""])[0],
        "event": (m.get("event") or {}).get("name") if isinstance(m.get("event"), dict) else None,
        "type": m.get("type"), "publisher": m.get("publisher"),
        "updated_by": m.get("updated-by") or [], "update_to": m.get("update-to") or [],
        "relation": m.get("relation") or {},
        "links": [l.get("URL") for l in m.get("link", [])],
        "license": [l.get("URL") for l in m.get("license", [])],
        "resource": (m.get("resource") or {}).get("primary", {}).get("URL"),
        "abstract": re.sub(r"<[^>]+>", " ", m.get("abstract") or "").strip(),
    }


def datacite(doi):
    d, st = get_json(f"https://api.datacite.org/dois/{doi}")
    if not d:
        return {"status": st}
    a = d["data"]["attributes"]
    return {
        "status": st, "title": (a.get("titles") or [{}])[0].get("title"),
        "authors": [c.get("name") for c in a.get("creators", [])],
        "year": a.get("publicationYear"),
        "abstract": " ".join(x.get("description", "") for x in a.get("descriptions", []) if x.get("descriptionType") == "Abstract"),
        "related": [(r.get("relationType"), r.get("relatedIdentifier")) for r in a.get("relatedIdentifiers", [])],
        "url": a.get("url"),
    }


def inv(i):
    if not i:
        return ""
    pos = {p: w for w, ps in i.items() for p in ps}
    return " ".join(pos[k] for k in sorted(pos))


def openalex(doi):
    if os.environ.get("NO_OPENALEX"):
        return {"status": "skipped: OpenAlex daily quota exhausted 2026-10-19"}
    d, st = get_json(f"https://api.openalex.org/works/doi:{doi}")
    if not d:
        return {"status": st}
    locs = []
    for l in d.get("locations", []):
        src = (l.get("source") or {}).get("display_name")
        locs.append({"source": src, "landing": l.get("landing_page_url"), "pdf": l.get("pdf_url"),
                     "oa": l.get("is_oa"), "version": l.get("version")})
    return {
        "status": st, "id": d["id"], "title": d.get("display_name"), "year": d.get("publication_year"),
        "authors": [a["author"]["display_name"] for a in d.get("authorships", [])],
        "venue": ((d.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "type": d.get("type"), "cited_by": d.get("cited_by_count"), "retracted": d.get("is_retracted"),
        "oa_status": (d.get("open_access") or {}).get("oa_status"),
        "oa_url": (d.get("open_access") or {}).get("oa_url"),
        "best_pdf": (d.get("best_oa_location") or {}).get("pdf_url"),
        "locations": locs, "abstract": inv(d.get("abstract_inverted_index")),
    }


def probe_pdf(url):
    """Ranged GET; verified only if body starts with %PDF."""
    try:
        r = requests.get(url, headers={**UA, "Range": "bytes=0-1023"}, timeout=40, allow_redirects=True, stream=True)
        head = next(r.iter_content(1024), b"")
        r.close()
        return {"url": url, "http": r.status_code, "final_url": r.url,
                "ctype": r.headers.get("content-type"), "is_pdf": head[:4] == b"%PDF"}
    except Exception as e:
        return {"url": url, "http": "error", "error": str(e)[:200], "is_pdf": False}


def arxiv_pdf_from_locations(oa):
    out = []
    for l in oa.get("locations", []) if oa else []:
        for u in (l.get("pdf"), l.get("landing")):
            if u and "arxiv.org" in u:
                m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})", u)
                if m:
                    out.append(m.group(1))
    return sorted(set(out))


def verify(seed):
    rec = {"cid": seed["cid"], "seed": seed}
    doi = seed["doi"].strip().lower()
    ax = seed["arxiv"].strip()
    if ax and not doi:
        rec["datacite"] = datacite(f"10.48550/arxiv.{ax}")
        rec["openalex"] = openalex(f"10.48550/arxiv.{ax}")
        ref_title = (rec["datacite"] or {}).get("title")
        rec["arxiv_ids"] = [ax]
    else:
        rec["crossref"] = crossref(doi)
        rec["openalex"] = openalex(doi)
        ref_title = rec["crossref"].get("title")
        if not ref_title:  # some proceedings DOIs (e.g. NDSS, Curran) may sit at DataCite
            rec["datacite"] = datacite(doi)
            ref_title = rec["datacite"].get("title")
        rec["arxiv_ids"] = arxiv_pdf_from_locations(rec["openalex"])
    rec["title_sim_openalex"] = sim(ref_title, (rec.get("openalex") or {}).get("title"))
    # candidate PDFs: OpenAlex locations + arXiv
    cands = []
    for l in (rec.get("openalex") or {}).get("locations", []):
        if l.get("pdf"):
            cands.append(l["pdf"])
    for a in rec["arxiv_ids"]:
        cands.append(f"https://arxiv.org/pdf/{a}")
    seen, probes = set(), []
    for u in cands:
        if u in seen:
            continue
        seen.add(u)
        probes.append(probe_pdf(u))
        time.sleep(1.5)
    rec["pdf_probes"] = probes
    return rec


def main():
    with open(SEEDS, encoding="utf-8") as fh:
        seeds = list(csv.DictReader(fh))
    want = set(sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)
    for s in seeds:
        if want and s["cid"] not in want:
            continue
        rec = verify(s)
        with open(os.path.join(OUT, f"{s['cid']}.json"), "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=1)
        cr = rec.get("crossref") or rec.get("datacite") or {}
        ok_pdf = [p["url"] for p in rec["pdf_probes"] if p["is_pdf"]]
        print(f"{s['cid']} | {cr.get('title')} | {cr.get('year')} | {cr.get('venue', '')} | sim={rec['title_sim_openalex']} "
              f"| retracted={(rec.get('openalex') or {}).get('retracted')} | upd={bool(cr.get('updated_by'))} "
              f"| arxiv={rec['arxiv_ids']} | pdf_ok={ok_pdf[:2]}", flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main()
