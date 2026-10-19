#!/usr/bin/env python3
"""Convert paper/Pxxx.pdf -> research/03_papers_markdown/Pxxx.md with markitdown
(the supervisor's chosen converter) and record conversion-quality signals.

A provenance comment (source PDF, sha256, converter version, date) is prepended;
the markitdown body itself is left unmodified.

Quality signals written to research/03_papers_markdown/conversion_report.csv:
  merged_token_rate : share of alphabetic tokens >= 20 chars (missing spaces)
  has_abstract / has_references : section keywords found
  chars_per_page    : body characters per PDF page (very low => text lost)
Thresholds are heuristics for triage, not proof of correctness.
"""
import csv, datetime as dt, hashlib, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PAPER = os.path.join(ROOT, "paper")
OUT = os.path.join(ROOT, "research", "03_papers_markdown")
REPORT = os.path.join(OUT, "conversion_report.csv")


def mk_version():
    r = subprocess.run(["markitdown", "--version"], capture_output=True, text=True)
    return (r.stdout or r.stderr).strip()


def pages(pdf):
    m = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout)
    return int(m.group(1)) if m else 0


def quality(text, n_pages):
    toks = re.findall(r"[A-Za-z]+", text)
    longt = [t for t in toks if len(t) >= 20]
    rate = round(len(longt) / max(1, len(toks)), 4)
    low = text.lower()
    return {"chars": len(text), "chars_per_page": round(len(text) / max(1, n_pages)),
            "merged_token_rate": rate, "has_abstract": "abstract" in low[:20000],
            "has_references": bool(re.search(r"\n\s*#*\s*(references|bibliography)\b", low)),
            "flag": "DAMAGED-SPACING" if rate > 0.01 else ("LOW-TEXT" if len(text) / max(1, n_pages) < 1500 else "ok")}


def main():
    want = set(sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)
    ver = mk_version()
    rep = {}
    if os.path.exists(REPORT):
        rep = {r["final_id"]: r for r in csv.DictReader(open(REPORT, encoding="utf-8"))}
    for f in sorted(os.listdir(PAPER)):
        m = re.fullmatch(r"(P\d{3})\.pdf", f)
        if not m or (want and m.group(1) not in want):
            continue
        pid, pdf = m.group(1), os.path.join(PAPER, f)
        r = subprocess.run(["markitdown", pdf], capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            rep[pid] = {"final_id": pid, "flag": "CONVERSION-FAILED", "note": r.stderr[:200]}
            print(pid, "FAILED", r.stderr[:120]); continue
        sha = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
        n = pages(pdf)
        header = (f"<!-- Converted by Claude for the API research project | source: paper/{f} | sha256: {sha} | "
                  f"pages: {n} | converter: {ver} | date: {dt.date.today()} | body below is unmodified markitdown output -->\n\n")
        open(os.path.join(OUT, f"{pid}.md"), "w", encoding="utf-8").write(header + r.stdout)
        q = quality(r.stdout, n)
        rep[pid] = {"final_id": pid, "pages": n, **q, "note": ""}
        print(pid, q["flag"], q["merged_token_rate"], q["chars_per_page"], q["has_abstract"], q["has_references"], flush=True)
    keys = ["final_id", "pages", "chars", "chars_per_page", "merged_token_rate", "has_abstract", "has_references", "flag", "note"]
    with open(REPORT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, quoting=csv.QUOTE_ALL, extrasaction="ignore"); w.writeheader()
        w.writerows(sorted(rep.values(), key=lambda x: x["final_id"]))


if __name__ == "__main__":
    main()
