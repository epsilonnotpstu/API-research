#!/usr/bin/env python3
"""Build claude_candidates.csv / .md from verification evidence + manual annotations.

Inputs (all under research/01_discovery/):
  seed_candidates.csv, claude_annotations.json,
  raw/verify/<cid>.json, <cid>.enrich.json, <cid>.abstract.json, _extra_pdf_probes.json
Year rule: earliest Crossref date among published-online / published-print / issued,
unless that lies after the current year (article in press) -> OpenAlex year, noted.
Discrepancies with OpenAlex are written to the year_note column.
"""
import csv, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "01_discovery")
V = os.path.join(D, "raw", "verify")
CURRENT_YEAR = 2026

# Venue facts verified outside Crossref (official proceedings pages, 2026-10-19)
MANUAL_VENUE = {
    "C56": ("International Conference on Learning Representations (ICLR 2024)",
            "https://proceedings.iclr.cc/paper_files/paper/2024/hash/28e50ee5b72e90b50e7196fde8ea260e-Abstract-Conference.html"),
    "C70": ("International Conference on Learning Representations (ICLR 2025)",
            "https://proceedings.iclr.cc/paper_files/paper/2025/hash/d8d1d325f822e07d16866780cc23deb2-Abstract-Conference.html"),
}
# arXiv version counts read directly from arxiv.org/abs pages on 2026-10-19
ARXIV_VERSIONS = {"C18": 1, "C19": 1, "C56": 2, "C59": 2, "C64": 4, "C70": 4}
TRACK_NOTE = {"C09": "ICSE NIER (new ideas) track", "C34": "ACL Industry Track", "C48": "ICSE SEIP (in practice) track",
              "C60": "ICSE SEIP (in practice) track", "C67": "Workshop (CCGridW)", "C14": "ICST (tool/benchmark paper; track Not verified)"}
ABSTRACT_SRC_OVERRIDE = {"C08": "Consensus search CO001 (full abstract; OpenAlex copy truncated)",
                         "C34": "ACL Anthology landing page", "C65": "Partial abstract via WebSearch snippet of institutional repository (flore.unifi.it)"}

TAXONOMY = [  # (area-string prefix, code) — codes defined in 00_protocol/api_research_landscape.md
    ("REST API testing", "T1"), ("GraphQL", "T2"), ("RPC/gRPC", "T2"), ("API architecture styles", "T2"),
    ("API security", "T3"), ("OpenAPI specification", "T4"), ("API evolution", "T5"),
    ("API documentation", "T6"), ("REST API design", "T6"), ("Web API design", "T6"), ("API governance", "T6"),
    ("API misuse", "T7"), ("LLM", "T8"), ("Model Context Protocol", "T8"), ("Microservice", "T9"),
    ("API recommendation", "T10"), ("API monitoring", "T11")]
SECONDARY = {"C07": "T4", "C09": "T4", "C10": "T4", "C15": "T1", "C13": "T1", "C27": "T1", "C28": "T1", "C30": "T1",
             "C32": "T1", "C33": "T1", "C34": "T8", "C35": "T8", "C38": "T9", "C39": "T1", "C52": "T8", "C53": "T8",
             "C59": "T4", "C60": "T6", "C62": "T3", "C63": "T3", "C64": "T4", "C66": "T1", "C67": "T3", "C68": "T8",
             "C69": "T8", "C70": "T8", "C25": "T9", "C14": "T2", "C19": "T3", "C58": "T5", "C55": "T6"}


def taxonomy(cid, area):
    prim = next(code for pre, code in TAXONOMY if area.startswith(pre))
    return prim + (f" (+{SECONDARY[cid]})" if cid in SECONDARY else "")


FIELDS = ["temp_id", "title", "authors", "year", "year_note", "venue", "publication_type", "review_status",
          "paper_kind", "era", "doi", "arxiv_id", "canonical_url", "doi_url", "direct_pdf_url_verified",
          "alt_oa_url", "access_status", "research_area", "taxonomy", "main_problem", "claimed_contribution", "methods",
          "key_findings", "inclusion_reason", "metadata_verification", "evidence_access_level", "abstract_source",
          "source_databases", "potential_research_relevance", "selection_confidence", "uncertainty"]


def load(p, default=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def main():
    seeds = {r["cid"]: r for r in csv.DictReader(open(os.path.join(D, "seed_candidates.csv"), encoding="utf-8"))}
    ann = load(os.path.join(D, "claude_annotations.json"))
    extra = load(os.path.join(V, "_extra_pdf_probes.json"), {})
    rows, excluded = [], []
    for cid, s in seeds.items():
        v = load(os.path.join(V, f"{cid}.json"))
        e = load(os.path.join(V, f"{cid}.enrich.json"), {})
        ab = load(os.path.join(V, f"{cid}.abstract.json"))
        cr, dc, oa = v.get("crossref") or {}, v.get("datacite") or {}, v.get("openalex") or {}
        title = cr.get("title") or dc.get("title")
        if cid in ann["excluded"]:
            excluded.append((cid, title, ann["excluded"][cid]))
            continue
        a = ann["included"][cid]
        doi = s["doi"].strip().lower()
        arx = s["arxiv"].strip() or ((v.get("arxiv_ids") or [None])[0]) or ((e.get("arxiv_found") or [{}])[0].get("arxiv"))
        # ---- year
        note = []
        if doi:
            ys = [y for y in (e.get("year_online"), e.get("year_print"), e.get("year_issued")) if y]
            year = min(ys) if ys else cr.get("year")
            if year and year > CURRENT_YEAR:
                note.append(f"Crossref issue year {year} (article in press); OpenAlex year used")
                year = oa.get("year")
            if oa.get("year") and year and oa["year"] != year:
                note.append(f"OpenAlex lists {oa['year']} (likely early-access/online-first)")
            if e.get("year_issued") and e["year_issued"] != year:
                note.append(f"journal issue/volume year {e['year_issued']}")
        else:
            year = dc.get("year")
            if cid in ARXIV_VERSIONS:
                note.append(f"arXiv v1 {year}; {ARXIV_VERSIONS[cid]} version(s) on arXiv")
        # ---- venue / type / review
        if cid in MANUAL_VENUE:
            venue, canon = MANUAL_VENUE[cid]
            ptype, review = "Conference paper", "Peer-reviewed (ICLR proceedings page verified)"
            year = int(re.search(r"(20\d\d)\)", venue).group(1))
        elif doi:
            venue = cr.get("venue") or "Not verified"
            canon = f"https://doi.org/{doi}"
            t = cr.get("type")
            ptype = {"proceedings-article": "Conference paper", "journal-article": "Journal article"}.get(t, t)
            review = "Peer-reviewed"
        else:
            venue, canon = "arXiv (preprint)", f"https://arxiv.org/abs/{arx}"
            ptype, review = "Preprint", "Not peer-reviewed (no peer-reviewed version found as of 2026-10-19)"
        if cid in TRACK_NOTE:
            review += f"; {TRACK_NOTE[cid]}"
        # ---- PDF links
        pdfs = [p for p in v.get("pdf_probes", []) if p.get("is_pdf")]
        for k, p in extra.items():
            if k.rstrip("b") == cid and p.get("is_pdf"):
                pdfs.append(p)
        publisher_pdf = [p["final_url"] for p in pdfs if "arxiv.org" not in p["final_url"]]
        arxiv_pdf = [p["final_url"] for p in pdfs if "arxiv.org" in p["final_url"]]
        direct = (publisher_pdf or arxiv_pdf or ["Not verified"])[0]
        alt = ""
        if publisher_pdf and arxiv_pdf:
            alt = arxiv_pdf[0]
        elif arx and direct != f"https://arxiv.org/pdf/{arx}" and arxiv_pdf:
            alt = arxiv_pdf[0]
        if not doi:
            access = "Open (arXiv)" if cid not in MANUAL_VENUE else "Open (ICLR proceedings + arXiv)"
        elif publisher_pdf:
            access = "Open access (publisher/repository PDF verified)"
        elif arxiv_pdf:
            access = "Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)"
        else:
            access = "Paywalled or not verified; landing page only — unrestricted full text NOT verified"
        # ---- verification status
        ver = []
        if doi and cr.get("title"):
            ver.append("Crossref DOI record OK")
        if dc.get("title"):
            ver.append("DataCite record OK")
        if cid in MANUAL_VENUE:
            ver.append("venue verified on official proceedings page")
        sim = v.get("title_sim_openalex")
        if sim is not None and sim < 0.9:
            ver.append(f"OpenAlex record MISMATCH (title similarity {sim}) — OpenAlex data not used")
        elif sim is not None:
            ver.append("OpenAlex consistent")
        if oa.get("retracted"):
            ver.append("RETRACTED per OpenAlex")
        if cr.get("updated_by"):
            ver.append(f"Crossref updated-by: {cr['updated_by']}")
        checked = bool(cr.get("title")) or (bool(oa.get("title")) and (sim or 0) >= 0.9)
        if not checked:
            ver.append("retraction status Not assessed (no Crossref/usable OpenAlex record)")
        elif not cr.get("updated_by") and not oa.get("retracted"):
            ver.append("no retraction/correction notice found")
        # ---- abstract source / evidence level
        if cid in ABSTRACT_SRC_OVERRIDE:
            asrc = ABSTRACT_SRC_OVERRIDE[cid]
        elif ab:
            asrc = f"DataCite (arXiv {ab['arxiv']})"
        elif cid == "C56":
            asrc = "DataCite (arXiv 2307.16789)"
        else:
            asrc = next((k for k in ("crossref", "datacite", "openalex") if len((v.get(k) or {}).get("abstract") or "") > 150), "None")
        level = "Metadata only" if asrc == "None" else ("Partial abstract" if cid in ("C65", "C51") else "Abstract")
        authors = cr.get("authors") or [  # DataCite gives "Family, Given"; normalise to "Given Family"
            " ".join(reversed([x.strip() for x in n.split(",", 1)])) if "," in n else n for n in (dc.get("authors") or [])]
        rows.append({
            "temp_id": cid, "title": title, "authors": "; ".join(authors), "year": year, "year_note": "; ".join(note),
            "venue": venue, "publication_type": ptype, "review_status": review, "paper_kind": a["kind"], "era": a["era"],
            "doi": doi or "Not applicable", "arxiv_id": arx or "Not found",
            "canonical_url": canon, "doi_url": f"https://doi.org/{doi}" if doi else (f"https://doi.org/10.48550/arXiv.{arx}" if arx else ""),
            "direct_pdf_url_verified": direct, "alt_oa_url": alt or "", "access_status": access,
            "research_area": s["area"], "taxonomy": taxonomy(cid, s["area"]), "main_problem": a["problem"], "claimed_contribution": a["contribution"],
            "methods": a["methods"], "key_findings": a["findings"], "inclusion_reason": a["inclusion"],
            "metadata_verification": "; ".join(ver), "evidence_access_level": level, "abstract_source": asrc,
            "source_databases": f"Discovered: {s['found_in']} | Verified: " + ", ".join(
                x for x, ok in (("Crossref", bool(cr.get("title"))), ("DataCite", bool(dc.get("title"))),
                                ("OpenAlex", bool(oa.get("title")) and (sim or 0) >= 0.9)) if ok),
            "potential_research_relevance": a["relevance"], "selection_confidence": a["confidence"],
            "uncertainty": a["uncertainty"],
        })
    with open(os.path.join(D, "claude_candidates.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    json.dump({"rows": rows, "excluded": excluded}, open(os.path.join(V, "_catalog_build.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(rows), "included;", len(excluded), "excluded")


if __name__ == "__main__":
    main()
