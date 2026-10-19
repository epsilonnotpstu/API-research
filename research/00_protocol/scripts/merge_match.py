#!/usr/bin/env python3
"""PHASE B1: match Claude and Codex candidate records.

Match order: exact DOI (case-insensitive) -> arXiv ID -> normalised title
(similarity >= 0.90). Pairs with 0.70 <= similarity < 0.90 are listed for
manual review (never auto-merged). Claude's six screened-out-but-verified
records are included so that provenance 'Both' is not missed.

Output: research/02_screening/_match_groups.json (consumed by merge_build.py)
"""
import csv, difflib, json, os, re, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "01_discovery")
OUT = os.path.join(ROOT, "02_screening")


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def ax_of(doi, ax):
    m = re.search(r"(\d{4}\.\d{4,5})", (ax or "") + " " + (doi or ""))
    return m.group(1) if m and ("arxiv" in (doi or "").lower() or ax) else ""


claude = []
for r in csv.DictReader(open(os.path.join(D, "claude_candidates.csv"), encoding="utf-8")):
    claude.append({"id": r["temp_id"], "title": r["title"], "doi": "" if r["doi"] == "Not applicable" else r["doi"].lower(),
                   "ax": "" if r["arxiv_id"] == "Not found" else r["arxiv_id"], "status": "included"})
# Claude screened-out records (verified in PHASE A)
build = json.load(open(os.path.join(D, "raw", "verify", "_catalog_build.json"), encoding="utf-8"))
seeds = {s["cid"]: s for s in csv.DictReader(open(os.path.join(D, "seed_candidates.csv"), encoding="utf-8"))}
for cid, title, why in build["excluded"]:
    claude.append({"id": cid, "title": title, "doi": seeds[cid]["doi"].lower(), "ax": seeds[cid]["arxiv"], "status": "screened-out"})

codex = []
for r in csv.DictReader(open(os.path.join(D, "codex_candidates.csv"), encoding="utf-8")):
    doi = r["doi"].strip().lower()
    codex.append({"id": "X" + r["candidate_id"][1:], "orig": r["candidate_id"], "title": r["title"],
                  "doi": "" if doi.startswith("10.48550") else doi, "ax": ax_of(doi, r["arxiv_id"]), "status": "included"})

pairs, used_c, used_x, review = [], set(), set(), []
for x in codex:
    hit = None
    for c in claude:
        if c["id"] in used_c:
            continue
        if x["doi"] and x["doi"] == c["doi"]:
            hit = (c, "exact DOI")
        elif x["ax"] and x["ax"] == c["ax"]:
            hit = (c, "arXiv ID")
        elif sim(x["title"], c["title"]) >= 0.90:
            hit = (c, f"normalised title (sim={sim(x['title'], c['title']):.2f})")
        if hit:
            break
    if hit:
        pairs.append({"claude": hit[0]["id"], "claude_status": hit[0]["status"], "codex": x["orig"], "rule": hit[1],
                      "claude_doi": hit[0]["doi"], "codex_doi": x["doi"], "title_sim": round(sim(x["title"], hit[0]["title"]), 3),
                      "claude_title": hit[0]["title"], "codex_title": x["title"]})
        used_c.add(hit[0]["id"]); used_x.add(x["id"])
for x in codex:
    if x["id"] in used_x:
        continue
    for c in claude:
        s = sim(x["title"], c["title"])
        if 0.70 <= s < 0.90 or (x["doi"] and c["doi"] and x["doi"].split(".")[-1] == c["doi"].split(".")[-1] and x["doi"] != c["doi"]):
            review.append({"codex": x["orig"], "claude": c["id"], "sim": round(s, 3), "codex_title": x["title"], "claude_title": c["title"]})
res = {"pairs": pairs, "manual_review": review,
       "claude_only": [c["id"] for c in claude if c["id"] not in used_c],
       "codex_only": [x["orig"] for x in codex if x["id"] not in used_x]}
os.makedirs(OUT, exist_ok=True)
json.dump(res, open(os.path.join(OUT, "_match_groups.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"pairs={len(pairs)} claude_only={len(res['claude_only'])} codex_only={len(res['codex_only'])} review={len(review)}")
for p in pairs:
    flag = "" if p["claude_doi"] == p["codex_doi"] else f"  DOI-DIFF {p['claude_doi']} vs {p['codex_doi']}"
    print(f"  {p['claude']}({p['claude_status'][0]}) = {p['codex']} [{p['rule']}] sim={p['title_sim']}{flag}")
print("REVIEW:", json.dumps(review, ensure_ascii=False, indent=0))
print("codex_only:", res["codex_only"])
