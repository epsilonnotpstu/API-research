#!/usr/bin/env python3
"""Second-stage enrichment of verified candidates.

1. Crossref date detail: published-online / published-print / issued years
   (Crossref 'issued' can be the journal issue year, not first publication).
2. Find arXiv versions OpenAlex did not link: title search restricted to the
   OpenAlex arXiv source (S4306400194), then confirm the arXiv DOI title at
   DataCite (OpenAlex arXiv titles were observed to be wrong for some records).
3. Arxiv-only seeds: read arxiv.org/abs page (version count, comments,
   journal-ref) respecting the 15 s crawl-delay from arxiv.org/robots.txt.

Writes research/01_discovery/raw/verify/<cid>.enrich.json
"""
import csv, difflib, json, os, re, sys, time, unicodedata
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SEEDS = os.environ.get("SEEDS") or os.path.join(ROOT, "01_discovery", "seed_candidates.csv")
OUT = os.environ.get("VOUT") or os.path.join(ROOT, "01_discovery", "raw", "verify")
UA = {"User-Agent": "api-research-review/1.0 (academic literature review; metadata verification)"}
ARXIV_DELAY = 15


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def sim(a, b):
    return round(difflib.SequenceMatcher(None, norm(a), norm(b)).ratio(), 3)


def j(url, params=None):
    for i in range(4):
        r = requests.get(url, params=params, headers=UA, timeout=45)
        if r.status_code in (429, 500, 502, 503):
            time.sleep(5 * (i + 1))
            continue
        return r.json() if r.ok else None
    return None


def yr(part):
    return ((part or {}).get("date-parts") or [[None]])[0][0]


def arxiv_abs(ax):
    r = requests.get(f"https://arxiv.org/abs/{ax}", headers=UA, timeout=45)
    h = r.text
    title = re.search(r'<meta name="citation_title" content="([^"]*)"', h)
    comments = re.search(r'<td class="tablecell comments[^>]*>(.*?)</td>', h, re.S)
    jref = re.search(r'<td class="tablecell jref">(.*?)</td>', h, re.S)
    dates = re.findall(r'\[v(\d+)\]</a?>?</strong>\s*([^<(]+)', h) or re.findall(r'\[v(\d+)\]</strong>\s*([^<(]+)', h)
    absm = re.search(r'<meta name="citation_abstract" content="([^"]*)"', h, re.S)
    clean = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip() if s else None
    return {"http": r.status_code, "title": title.group(1) if title else None,
            "comments": clean(comments.group(1)) if comments else None,
            "journal_ref": clean(jref.group(1)) if jref else None,
            "versions": [(v, d.strip()) for v, d in dates],
            "abstract": clean(absm.group(1)) if absm else None}


def main():
    seeds = list(csv.DictReader(open(SEEDS, encoding="utf-8")))
    want = set(sys.argv[1:])
    for s in seeds:
        cid = s["cid"]
        if want and cid not in want:
            continue
        base = json.load(open(os.path.join(OUT, f"{cid}.json"), encoding="utf-8"))
        e = {"cid": cid}
        doi = s["doi"].strip().lower()
        if doi:
            m = (j(f"https://api.crossref.org/works/{doi}") or {}).get("message", {})
            e["year_online"] = yr(m.get("published-online"))
            e["year_print"] = yr(m.get("published-print"))
            e["year_issued"] = yr(m.get("issued"))
            e["volume"], e["issue"], e["page"] = m.get("volume"), m.get("issue"), m.get("page")
        title = (base.get("crossref") or {}).get("title") or (base.get("datacite") or {}).get("title")
        axs = list(base.get("arxiv_ids") or [])
        if doi and not axs and title:
            # OpenAlex daily quota was exhausted on 2026-10-19, so arXiv versions
            # are searched in DataCite (registrar of arXiv DOIs, prefix 10.48550).
            q = re.sub(r"[^A-Za-z0-9 ]", " ", title)
            res = j("https://api.datacite.org/dois", {"query": q, "prefix": "10.48550", "page[size]": 10})
            for w in (res or {}).get("data", []):
                dct = (w["attributes"].get("titles") or [{}])[0].get("title")
                if dct and sim(dct, title) >= 0.85:
                    e.setdefault("arxiv_found", []).append({"arxiv": w["id"].split("arxiv.")[-1], "datacite_title": dct, "sim": sim(dct, title)})
            time.sleep(0.5)
        if s["arxiv"].strip():
            e["arxiv_abs"] = arxiv_abs(s["arxiv"].strip())
            time.sleep(ARXIV_DELAY)
        json.dump(e, open(os.path.join(OUT, f"{cid}.enrich.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(cid, {k: v for k, v in e.items() if k in ("year_online", "year_print", "year_issued", "arxiv_found")},
              (e.get("arxiv_abs") or {}).get("journal_ref"), (e.get("arxiv_abs") or {}).get("comments"), flush=True)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
