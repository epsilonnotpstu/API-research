#!/usr/bin/env python3
"""PHASE C1 automated document-integrity scan of research/03_papers_markdown/Pxxx.md.

For every paper it locates (first line number) the sections required by the
protocol, counts table/figure captions and numbered references, and records the
PDF version used (from paper/download_log.csv). Output:
  research/04_paper_analysis/integrity_scan.csv
The human-readable report (document_integrity_report.md) combines this scan with
manual observations recorded while reading each paper.
Heuristic: absence of a keyword is a flag to check, not proof the section is missing.
"""
import csv, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MD = os.path.join(ROOT, "research", "03_papers_markdown")
OUT = os.path.join(ROOT, "research", "04_paper_analysis")
LOG = os.path.join(ROOT, "paper", "download_log.csv")
SECTIONS = {
    "abstract": r"^(## )?\s*(abstract|a b s t r a c t)\b",
    "introduction": r"^(## )?\s*((\d|I)\.?\s+)?introduction\b",
    "related_work": r"^(## )?\s*((\d+|[IVX]+)\.?\s+)?(related work|background|state of the art|related literature)",
    "objectives_rqs": r"\b(RQ\s?\d|research questions?)\b",
    "method": r"^(## )?\s*((\d+|[IVX]+)\.?\s+)?(approach|methodology|method|design|our approach|technique|study design|overview)",
    "experimental_setup": r"\b(experimental setup|experiment(al)? design|evaluation setup|subjects|study setup|setup)\b",
    "datasets": r"\b(dataset|benchmark|corpus|subject (apis|systems|services))\b",
    "baselines": r"\b(baselines?|compared (with|against)|state-of-the-art tools?)\b",
    "metrics": r"\b(metrics?|precision|recall|coverage|f1)\b",
    "results": r"^(## )?\s*((\d+|[IVX]+)\.?\s+)?(results|findings|evaluation)\b",
    "limitations": r"\b(limitations?)\b",
    "threats": r"\bthreats to (the )?validity\b",
    "conclusion": r"^(## )?\s*((\d+|[IVX]+)\.?\s+)?(conclusions?|concluding remarks|summary)\b",
    "references": r"^(## )?\s*((\d+|[IVX]+)\.?\s+)?(references|bibliography)\s*$",
}


def scan(pid):
    lines = open(os.path.join(MD, f"{pid}.md"), encoding="utf-8").read().split("\n")
    low = [l.lower() for l in lines]
    res = {"final_id": pid, "lines": len(lines),
           "pages": sum(1 for l in lines if l.startswith("<!-- page "))}
    for k, pat in SECTIONS.items():
        rx = re.compile(pat, re.I | re.M)
        hit = next((i + 1 for i, l in enumerate(lines) if rx.search(l)), "")
        res[k] = hit
    res["table_captions"] = len({m.group(1) for l in lines for m in [re.match(r"^\s*(?:TABLE|Table)\s+([0-9IVX]+)[.:]?", l)] if m})
    res["figure_captions"] = len({m.group(1) for l in lines for m in [re.match(r"^\s*(?:Fig\.|Figure|FIGURE)\s*([0-9]+)[.:]?", l)] if m})
    res["numbered_refs"] = sum(1 for l in lines if re.match(r"^\s*\[\d{1,3}\]\s+\S", l))
    res["equation_like_lines"] = sum(1 for l in lines if re.search(r"[=≤≥∑∀∃∈]\s", l) and len(l) < 80)
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    log = {r["final_id"]: r for r in csv.DictReader(open(LOG, encoding="utf-8"))}
    rows = []
    for f in sorted(os.listdir(MD)):
        m = re.fullmatch(r"(P\d{3})\.md", f)
        if m:
            r = scan(m.group(1)); r["version"] = log.get(r["final_id"], {}).get("version", ""); rows.append(r)
    keys = list(rows[0].keys())
    with open(os.path.join(OUT, "integrity_scan.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(rows)
    for r in rows:
        miss = [k for k in SECTIONS if not r[k]]
        print(r["final_id"], f"pg={r['pages']} tab={r['table_captions']} fig={r['figure_captions']} refs={r['numbered_refs']}", "MISSING:", ",".join(miss) or "-")


if __name__ == "__main__":
    main()
