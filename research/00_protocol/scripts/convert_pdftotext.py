#!/usr/bin/env python3
"""Convert paper/Pxxx.pdf -> research/03_papers_markdown/Pxxx.md using poppler `pdftotext`.

Chosen over markitdown after a measured comparison (merged-word rate up to 0.32
with markitdown vs <=0.004 with pdftotext on the same PDFs; supervisor approved
fixing the Markdown on 2026-10-19). Previous markitdown files are preserved in
research/03_papers_markdown/_markitdown/.

Transformations (deliberately minimal — text itself is not edited):
  * `<!-- page N -->` marker before each PDF page (from pdftotext form feeds)
  * a short line that looks like a section heading ("1 Introduction",
    "3.2 Threats to Validity", "ABSTRACT", "REFERENCES") is prefixed with '## '
  * provenance comment at the top
  * small-caps headings split by pdftotext ("I NTRODUCTION", "R EFERENCES") are
    rejoined ONLY on short all-caps lines, and only when the joined token occurs in
    the corpus vocabulary while the split fragment does not (e.g. "A PPROACH" ->
    "APPROACH", but "A MOTIVATING" stays)
Known, unavoidable losses: table cell structure, equations, figure content.
"""
import csv, datetime as dt, hashlib, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PAPER = os.path.join(ROOT, "paper")
OUT = os.path.join(ROOT, "research", "03_papers_markdown")
REPORT = os.path.join(OUT, "conversion_report.csv")
HEAD_WORDS = r"(abstract|introduction|background|related work|motivation|approach|methodology|method|methods|evaluation|" \
             r"experiments?|results|discussion|threats to validity|limitations|conclusions?|future work|references|" \
             r"bibliography|acknowledg(e)?ments?|appendix|implementation|case study|research questions|study design|" \
             r"empirical study|overview|preliminaries|lessons learned)"
NUM_HEAD = re.compile(r"^(\d{1,2}(\.\d{1,2}){0,2}\.?|[IVX]{1,4}\.)\s+[A-Z][A-Za-z0-9 ,:;&()'’/\-–?]{2,80}$")
WORD_HEAD = re.compile(rf"^({HEAD_WORDS})\s*$", re.I)


VOCAB = set()


def build_vocab(pdfs):
    from collections import Counter
    c = Counter()
    for pdf in pdfs:
        raw = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True, text=True).stdout
        # only body-text spellings (some lowercase letter): all-caps tokens may themselves be split artefacts
        c.update(w.lower() for w in re.findall(r"[A-Za-z]{3,}", raw) if not w.isupper())
    VOCAB.update(w for w, n in c.items() if n >= 3)


def rejoin_smallcaps(s):
    letters = [ch for ch in s if ch.isalpha()]
    if not letters or len(s) > 90 or sum(ch.isupper() for ch in letters) / len(letters) < 0.8:
        return s
    def fix(m):
        joined, frag = (m.group(1) + m.group(2)).lower(), m.group(2).lower()
        return m.group(1) + m.group(2) if joined in VOCAB and frag not in VOCAB else m.group(0)
    return re.sub(r"\b([A-Z]) ([A-Z]{2,})\b", fix, s)


def is_heading(line, prev_blank):
    s = line.strip()
    if not s or len(s) > 90 or s.endswith((".", ",")) or not prev_blank:
        return False
    if WORD_HEAD.match(s):
        return True
    m = NUM_HEAD.match(s)
    return bool(m) and len(s.split()) <= 10 and not re.search(r"\d{3,}", s[len(m.group(1)):])


def quality(text, n_pages):
    toks = re.findall(r"[A-Za-z]+", text)
    rate = round(len([t for t in toks if len(t) >= 20]) / max(1, len(toks)), 4)
    low = text.lower()
    return {"chars": len(text), "chars_per_page": round(len(text) / max(1, n_pages)), "merged_token_rate": rate,
            "has_abstract": "abstract" in low[:20000],
            "has_references": bool(re.search(r"\n(## )?(\d+\.?\s+)?(references|bibliography)\s*\n", low)),
            "flag": "DAMAGED-SPACING" if rate > 0.01 else ("LOW-TEXT" if len(text) / max(1, n_pages) < 1500 else "ok")}


def convert(pdf):
    raw = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True, text=True).stdout
    pages = raw.split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    out, nhead = [], 0
    for i, pg in enumerate(pages, 1):
        out.append(f"\n<!-- page {i} -->\n")
        prev_blank = True
        for line in pg.split("\n"):
            line = rejoin_smallcaps(line)
            if is_heading(line, prev_blank):
                out.append("## " + line.strip()); nhead += 1
            else:
                out.append(line)
            prev_blank = not line.strip()
    return "\n".join(out), len(pages), nhead


def main():
    want = set(sys.argv[1:])
    ver = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr.split("\n")[0].strip()
    rows = []
    build_vocab([os.path.join(PAPER, f) for f in sorted(os.listdir(PAPER)) if f.endswith(".pdf")])
    for f in sorted(os.listdir(PAPER)):
        m = re.fullmatch(r"(P\d{3})\.pdf", f)
        if not m or (want and m.group(1) not in want):
            continue
        pid, pdf = m.group(1), os.path.join(PAPER, f)
        body, n, nhead = convert(pdf)
        sha = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
        header = (f"<!-- {pid} | source: paper/{f} | sha256: {sha} | pages: {n} | converter: {ver} (default reading order) | "
                  f"date: {dt.date.today()} | page markers '<!-- page N -->' = PDF page index | '## ' headings auto-detected | "
                  f"tables/equations/figures may be lost — verify against PDF -->\n")
        open(os.path.join(OUT, f"{pid}.md"), "w", encoding="utf-8").write(header + body)
        q = quality(body, n)
        rows.append({"final_id": pid, "converter": "pdftotext", "pages": n, "headings": nhead, **q})
        print(pid, q["flag"], q["merged_token_rate"], q["chars_per_page"], "abs" if q["has_abstract"] else "NO-ABS",
              "refs" if q["has_references"] else "NO-REFS", f"h={nhead}", flush=True)
    keys = ["final_id", "converter", "pages", "headings", "chars", "chars_per_page", "merged_token_rate", "has_abstract", "has_references", "flag"]
    with open(REPORT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
