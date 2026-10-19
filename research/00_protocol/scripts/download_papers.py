#!/usr/bin/env python3
"""Download selected papers (P-IDs) into '<project>/paper/Pxxx.pdf' and log provenance.

Source order per paper: verified_pdf_url, then each alt_verified_pdf.
A download is accepted only if (1) the body starts with %PDF and (2) the
first-page text (pdftotext) contains the paper title with fuzzy similarity
>= 0.6 against the best-matching window — otherwise it is rejected and the
next source is tried. arxiv.org requests respect the 15 s robots crawl-delay.

Usage: download_papers.py [--from P010] [--to P038] [--only P018 ...]
Log  : paper/download_log.csv (appended/updated per ID)
"""
import argparse, csv, difflib, hashlib, os, re, subprocess, sys, time
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))  # project root
FINAL = os.path.join(ROOT, "research", "02_screening", "final_papers.csv")
OUT = os.path.join(ROOT, "paper")
LOG = os.path.join(OUT, "download_log.csv")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) api-research-review/1.0 (academic literature review)"}
# Sources found after PHASE B (first-page title checked with pdftotext on 2026-10-19)
EXTRA_SOURCES = {
    "P019": ["https://cseweb.ucsd.edu/~mcoblenz/assets/pdf/OOPSLA_2025_REST.pdf"],   # co-author page (UCSD)
    "P025": ["https://patricegodefroid.github.io/public_psfiles/issta2020.pdf"],     # co-author page, linked from MSR
}
FIELDS = ["final_id", "title", "status", "source_url", "version", "bytes", "pages", "sha256", "title_match", "note"]


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def title_match(pdf, title):
    txt = subprocess.run(["pdftotext", "-l", "2", pdf, "-"], capture_output=True, text=True).stdout
    t, x = norm(title), norm(txt)[:4000]
    if t and t in x:
        return 1.0
    words = x.split(); n = len(t.split())
    best = 0.0
    for i in range(0, max(1, len(words) - n + 1)):
        best = max(best, difflib.SequenceMatcher(None, t, " ".join(words[i:i + n])).ratio())
    return round(best, 3)


def pages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", out)
    return int(m.group(1)) if m else ""


def fetch(url, dest):
    r = requests.get(url, headers=UA, timeout=180, allow_redirects=True)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        return False, f"HTTP {r.status_code}, {r.headers.get('content-type')}, not PDF"
    open(dest, "wb").write(r.content)
    return True, r.url


def version_of(url, row):
    if "arxiv.org" in url:
        return "arXiv preprint (may differ from published version)"
    if "idus.us.es" in url:
        return "repository submitted version"
    if "proceedings.iclr.cc" in url:
        return "ICLR proceedings (published)"
    if "cseweb.ucsd.edu" in url or "github.io" in url:
        return "author-hosted copy"
    if "hal.science" in url:
        return "HAL repository copy"
    if any(h in url for h in ("link.springer.com", "ieeexplore.ieee.org", "ndss-symposium.org", "aclanthology.org")):
        return "publisher version"
    return "author/institution-hosted copy"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm", default="P001")
    ap.add_argument("--to", default="P038")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    log = {}
    if os.path.exists(LOG):
        log = {r["final_id"]: r for r in csv.DictReader(open(LOG, encoding="utf-8"))}
    rows = list(csv.DictReader(open(FINAL, encoding="utf-8")))
    for r in rows:
        pid = r["final_id"]
        if a.only and pid not in a.only:
            continue
        if not a.only and not (a.frm <= pid <= a.to):
            continue
        dest = os.path.join(OUT, f"{pid}.pdf")
        srcs = [u for u in [r["verified_pdf_url"]] + [s.strip() for s in r["alt_verified_pdf"].split(";")] if u.startswith("http")]
        srcs += EXTRA_SOURCES.get(pid, [])
        rec = {"final_id": pid, "title": r["title"], "status": "MISSING", "source_url": "", "version": "", "bytes": "",
               "pages": "", "sha256": "", "title_match": "", "note": "no verified open source; manual download required" if not srcs else ""}
        if os.path.exists(dest) and pid in log and log[pid]["status"] == "OK":
            print(pid, "already OK — skipped"); continue
        notes = []
        for u in srcs:
            try:
                ok, info = fetch(u, dest)
            except Exception as e:
                ok, info = False, str(e)[:120]
            if "arxiv.org" in u:
                time.sleep(15)
            if not ok:
                notes.append(f"{u}: {info}"); continue
            tm = title_match(dest, r["title"])
            if tm < 0.6:
                notes.append(f"{u}: title mismatch ({tm})"); os.remove(dest); continue
            data = open(dest, "rb").read()
            rec.update(status="OK", source_url=info, version=version_of(info, r), bytes=len(data), pages=pages(dest),
                       sha256=hashlib.sha256(data).hexdigest(), title_match=tm, note="; ".join(notes))
            break
        else:
            rec["note"] = rec["note"] or "; ".join(notes)
        log[pid] = rec
        print(pid, rec["status"], rec["version"], rec["pages"], rec["title_match"], rec["note"][:90], flush=True)
        with open(LOG, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL); w.writeheader()
            w.writerows(sorted(log.values(), key=lambda x: x["final_id"]))


if __name__ == "__main__":
    main()
