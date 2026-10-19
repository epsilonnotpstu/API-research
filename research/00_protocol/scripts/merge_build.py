#!/usr/bin/env python3
"""PHASE B1/B2: build research/02_screening/merged_candidates.csv.

Canonical metadata come from registrar verification records, never copied
from either agent's CSV:
  Claude records -> research/01_discovery/raw/verify/<C..>.json (+ .enrich.json)
  Codex-only     -> research/02_screening/raw/verify_codex/<X..>.json (+ .enrich.json)
Links are labelled by evidence:
  verified_pdf   : body began with %PDF in our own probe
  candidate_url  : URL reported by an agent/search but NOT verified by us
Manual decisions (false matches, corrections) are listed in OVERRIDES and
documented in duplicate_resolution.md / metadata_verification_log.md.
"""
import csv, html, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D1 = os.path.join(ROOT, "01_discovery")
V1 = os.path.join(D1, "raw", "verify")
D2 = os.path.join(ROOT, "02_screening")
V2 = os.path.join(D2, "raw", "verify_codex")
CURRENT_YEAR = 2026

FALSE_MATCHES = {("C20", "C003")}  # RESTTESTGEN (ICST 2020) != RESTest (ISSTA 2021)
TITLE_FIX = {"X004": "Morest: Model-based RESTful API Testing with Execution Feedback"}  # Crossref title+subtitle
ICLR = {"C56": (2024, "International Conference on Learning Representations (ICLR 2024)",
                "https://proceedings.iclr.cc/paper_files/paper/2024/hash/28e50ee5b72e90b50e7196fde8ea260e-Abstract-Conference.html"),
        "C70": (2025, "International Conference on Learning Representations (ICLR 2025)",
                "https://proceedings.iclr.cc/paper_files/paper/2025/hash/d8d1d325f822e07d16866780cc23deb2-Abstract-Conference.html")}
# Extra verified PDFs found in PHASE B (first-page title checked with pdftotext, 2026-10-19)
EXTRA_VERIFIED_PDF = {
    "C01": "https://www.microsoft.com/en-us/research/uploads/prod/2021/03/RESTler.pdf",
    "C37": "https://ece.uwaterloo.ca/~wshang/pubs/mlamothe_csur_2021.pdf",
    "X015": "https://idus.us.es/bitstreams/0592cee5-2a9b-407f-bde5-8a2941fa41d8/download",
    "C21": "https://idus.us.es/bitstreams/85cae9eb-bcbe-45f8-845d-cce7736e862b/download",
}
PDF_VERSION_NOTE = {
    "C01": "Microsoft Research-hosted copy; first page title = ICSE 2019 paper",
    "C37": "author-hosted copy (U. Waterloo); first page title verified; version-of-record equivalence not verified",
    "X015": "idUS repository; OpenAlex labels 'submittedVersion' — may differ from published version",
    "C21": "idUS repository; OpenAlex labels 'submittedVersion' — may differ from published version",
}
EXTRA_ARXIV = {"C01": ("1806.09739", "earlier preprint with different title 'REST-ler: Automatic Intelligent REST API Fuzzing' — content may differ"),
               "X054": ("2504.12067", "arXiv version found via DataCite")}
UNVERIFIED_CANDIDATES = {
    "C32": "https://par.nsf.gov/servlets/purl/10537946 (NSF PAR; found by WebSearch; request timed out — NOT verified); https://dl.acm.org/doi/pdf/10.1145/3597503.3639137 (OpenAlex: publisher OA 'hybrid'; HTTP 403 to scripts — try in browser)",
    "C13": "https://dl.acm.org/doi/pdf/10.1145/3597926.3598114 (OpenAlex: publisher OA 'bronze'; HTTP 403 to scripts — try in browser)",
    "X026": "https://dl.acm.org/doi/pdf/10.1145/3763055 (OpenAlex: publisher OA 'diamond'; HTTP 403 to scripts — try in browser)",
    "C30": "https://arxiv.org/abs/2604.00702 (preprint of the EXTENDED JSS 2026 version 'Enhancing REST API Fuzzing with Access Policy Violation Checks and Injection Attacks' — a DIFFERENT, longer paper; use only if ISSRE version unavailable and record this)",
    "C65": "https://hdl.handle.net/2158/1438341 and https://hdl.handle.net/11568/1331513 (Florence / Pisa repository records of the submitted version; OpenAlex marks them not OA — access NOT verified)",
    "C39": "https://www.microsoft.com/en-us/research/publication/differential-regression-testing-for-rest-apis/ (MSR page; earlier technical report MSR-TR-2019-23 — PDF not verified, may differ from ISSTA version)",
}
CLUSTER = {  # merged taxonomy (see selection_methodology.md)
    "T1": "REST/Web API testing & fuzzing", "T2": "GraphQL, RPC/gRPC & architecture styles",
    "T3": "API security & authorization", "T4": "API specification inference & enrichment",
    "T5": "API evolution, breaking changes & deprecation", "T6": "API documentation, design quality & governance",
    "T7": "API misuse detection", "T8": "LLM tool use, API calling & MCP", "T9": "Microservice APIs, reliability & observability",
    "T10": "API recommendation & composition"}
CODEX_AREA_TO_T = {"API testing": "T1", "API security": "T3", "API specification": "T4", "API documentation": "T6",
                   "API evolution": "T5", "GraphQL": "T2", "API discovery": "T10", "Microservice": "T9", "LLM": "T8"}
CODEX_T_OVERRIDE = {"X022": "T7", "X058": "T5", "X059": "T4", "X060": "T4", "X026": "T4", "X025": "T4", "X027": "T4",
                    "X028": "T4", "X054": "T9", "X053": "T9", "X055": "T9", "X052": "T9"}


def load(p, d=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def year_of(cr_e, oa, dc):
    ys = [y for y in (cr_e.get("year_online"), cr_e.get("year_print"), cr_e.get("year_issued")) if y]
    y = min(ys) if ys else None
    note = []
    if y and y > CURRENT_YEAR:
        note.append(f"Crossref issue year {y} (in press)")
        y = (oa or {}).get("year")
    if not y:
        y = (dc or {}).get("year") or (oa or {}).get("year")
    if oa and oa.get("year") and y and oa["year"] != y:
        note.append(f"OpenAlex/online-first year {oa['year']}")
    if cr_e.get("year_issued") and cr_e["year_issued"] != y:
        note.append(f"issue year {cr_e['year_issued']}")
    return y, "; ".join(note)


def pdfs_of(v, extra_probe_ids=()):
    good = [p["final_url"] for p in (v or {}).get("pdf_probes", []) if p.get("is_pdf")]
    return good


def main():
    claude = {r["temp_id"]: r for r in csv.DictReader(open(os.path.join(D1, "claude_candidates.csv"), encoding="utf-8"))}
    build = load(os.path.join(V1, "_catalog_build.json"))
    claude_excl = {cid: why for cid, _, why in build["excluded"]}
    codex = {r["candidate_id"]: r for r in csv.DictReader(open(os.path.join(D1, "codex_candidates.csv"), encoding="utf-8"))}
    groups = load(os.path.join(D2, "_match_groups.json"))
    extra_probes = load(os.path.join(V1, "_extra_pdf_probes.json"), {})
    codex_reprobe = load(os.path.join(V2, "_codex_pdf_reprobe.json"), {})
    seeds = {s["cid"]: s for s in csv.DictReader(open(os.path.join(D1, "seed_candidates.csv"), encoding="utf-8"))}

    pairs = [(p["claude"], p["codex"]) for p in groups["pairs"] if (p["claude"], p["codex"]) not in FALSE_MATCHES]
    paired_c = {a for a, _ in pairs}
    paired_x = {b for _, b in pairs}
    units = [("Both", a, b) for a, b in pairs]
    units += [("Claude only", c, None) for c in list(claude) + list(claude_excl) if c not in paired_c]
    units += [("Codex only", None, x) for x in codex if x not in paired_x]

    out = []
    for i, (prov, cid, xid) in enumerate(units, 1):
        if cid:
            v = load(os.path.join(V1, f"{cid}.json")); e = load(os.path.join(V1, f"{cid}.enrich.json"), {})
            vid = cid
        else:
            vid = "X" + xid[1:]
            v = load(os.path.join(V2, f"{vid}.json")); e = load(os.path.join(V2, f"{vid}.enrich.json"), {})
        cr, dc, oa = v.get("crossref") or {}, v.get("datacite") or {}, v.get("openalex") or {}
        oa_ok = oa if (v.get("title_sim_openalex") or 0) >= 0.9 else {}
        title = TITLE_FIX.get(vid) or cr.get("title") or dc.get("title")
        title = html.unescape(title)
        doi = (cr and v["seed"]["doi"].strip().lower()) or ""
        ax = v["seed"]["arxiv"].strip() or (v.get("arxiv_ids") or [""])[0] or ((e.get("arxiv_found") or [{}])[0].get("arxiv") or "")
        ax_note = ""
        if not ax and vid in EXTRA_ARXIV:
            ax, ax_note = EXTRA_ARXIV[vid]
        y, ynote = year_of(e, oa_ok, dc)
        if vid in ICLR:
            y, venue, canon = ICLR[vid]
            ptype, review = "Conference paper", "Peer-reviewed"
        elif doi:
            venue = html.unescape(cr.get("venue") or "Not verified")
            canon = f"https://doi.org/{doi}"
            ptype = {"proceedings-article": "Conference paper", "journal-article": "Journal article"}.get(cr.get("type"), cr.get("type"))
            review = "Peer-reviewed"
        else:
            venue, canon, ptype, review = "arXiv", f"https://arxiv.org/abs/{ax}", "Preprint", "Not peer-reviewed"
        authors = cr.get("authors") or [" ".join(reversed([p.strip() for p in n.split(",", 1)])) if "," in n else n
                                        for n in dc.get("authors") or []]
        # verified PDFs (own probes only)
        pdf = pdfs_of(v)
        for k, p in extra_probes.items():
            if cid and k.rstrip("b") == cid and p.get("is_pdf"):
                pdf.append(p["final_url"])
        if xid and xid in codex_reprobe and codex_reprobe[xid].get("is_pdf"):
            pdf.append(codex_reprobe[xid]["final_url"])
        if vid in EXTRA_VERIFIED_PDF:
            pdf.insert(0, EXTRA_VERIFIED_PDF[vid])
        pdf = list(dict.fromkeys(pdf))
        pub = [u for u in pdf if "arxiv.org" not in u]
        arx = [u for u in pdf if "arxiv.org" in u]
        primary_pdf = (pub or arx or [""])[0]
        alt_pdf = "; ".join(u for u in pdf if u != primary_pdf)
        if not doi:
            access = "Open (arXiv / proceedings)"
        elif pub:
            access = "Open full text verified (publisher, proceedings, repository or author copy)"
        elif arx:
            access = "Legal preprint verified on arXiv; publisher version access not verified"
        else:
            access = "Full text not verified (paywalled or blocked); DOI landing page only"
        cand = []
        if xid and codex[xid]["pdf_url"].strip() and not (xid in codex_reprobe and codex_reprobe[xid].get("is_pdf")) \
                and codex[xid]["pdf_url"].strip() not in UNVERIFIED_CANDIDATES.get(vid, ""):
            cand.append(f"{codex[xid]['pdf_url'].strip()} (Codex-listed; our probe: NOT a PDF/blocked)")
        if vid in UNVERIFIED_CANDIDATES:
            cand.append(UNVERIFIED_CANDIDATES[vid])
        # conflicts between agents
        conf = []
        if xid:
            xr = codex[xid]
            if xr["doi"].strip() and doi and xr["doi"].strip().lower() != doi:
                conf.append(f"DOI: Codex {xr['doi']} vs registered {doi}")
            if re.sub(r"\W+", "", xr["title"].lower()) != re.sub(r"\W+", "", title.lower()):
                conf.append(f"title: Codex '{xr['title']}' vs registrar '{title}'")
            if str(xr["year"]) != str(y):
                conf.append(f"year: Codex {xr['year']} vs rule-based {y}")
        if cid and cid in claude and str(claude[cid]["year"]) != str(y):
            conf.append(f"year: Claude PhaseA {claude[cid]['year']} vs rule-based {y}")
        # cluster
        if cid and cid in claude:
            tcode = claude[cid]["taxonomy"].split(" ")[0]
            tcode = {"T11": "T9"}.get(tcode, tcode)
        elif cid:  # Claude PhaseA screened-out records
            tcode = {"C12": "T1", "C17": "T1", "C20": "T1", "C24": "T2", "C42": "T5", "C54": "T8"}[cid]
        else:
            tcode = CODEX_T_OVERRIDE.get(vid) or next(t for k, t in CODEX_AREA_TO_T.items() if codex[xid]["research_area"].startswith(k))
        abstract_src = "None"
        for k in ("crossref", "datacite", "openalex"):
            if len(((v.get(k) or {}).get("abstract") or "")) > 150 and not (k == "openalex" and not oa_ok):
                abstract_src = k; break
        if cid and cid in claude:
            abstract_src = claude[cid]["abstract_source"]
        out.append({
            "merged_id": f"M{i:03d}", "provenance": prov, "claude_id": cid or "", "claude_phaseA_status":
                ("included" if cid in claude else ("screened-out: " + claude_excl[cid][:80]) if cid else ""),
            "codex_id": xid or "", "title": title, "authors": "; ".join(authors), "year": y, "year_note": ynote,
            "venue": venue, "publication_type": ptype, "review_status": review,
            "doi": doi or "Not applicable", "arxiv_id": ax or "Not found", "arxiv_note": ax_note,
            "cluster": tcode, "cluster_name": CLUSTER[tcode],
            "canonical_url": canon, "verified_pdf_url": primary_pdf or "Not verified", "alt_verified_pdf": alt_pdf,
            "pdf_version_note": PDF_VERSION_NOTE.get(vid, "arXiv preprint — may differ from published version" if primary_pdf and "arxiv.org" in primary_pdf and doi else ""),
            "unverified_candidate_urls": "; ".join(cand), "access_status": access,
            "registrar_verified": "Crossref" if cr.get("title") else ("DataCite" if dc.get("title") else "NO"),
            "openalex_consistent": "yes" if oa_ok else ("MISMATCH" if oa.get("title") else "not checked"),
            "retraction_flag": "RETRACTED" if oa.get("retracted") else ("updated-by notice" if cr.get("updated_by") else "none found"),
            "cited_by_openalex": oa_ok.get("cited_by", ""), "abstract_source": abstract_src,
            "agent_conflicts": " | ".join(conf),
        })
    with open(os.path.join(D2, "merged_candidates.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()), quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(out)
    from collections import Counter
    print(len(out), "merged records;", Counter(r["provenance"] for r in out), Counter(r["cluster"] for r in out))
    print("registrar NO:", [r["merged_id"] for r in out if r["registrar_verified"] == "NO"])
    print("verified pdf:", sum(r["verified_pdf_url"] != "Not verified" for r in out))


if __name__ == "__main__":
    main()
