#!/usr/bin/env python3
"""PHASE B4: permanent IDs + all generated screening deliverables.

Inputs : 02_screening/merged_candidates.csv, _selection.json, screening_scores.json,
         final_annotations.json, 01_discovery/claude_annotations.json
Outputs: 02_screening/merged_candidates.csv (screening columns appended),
         final_papers.csv, final_papers.md, excluded_papers.md, download_checklist.md,
         paper_manifest.csv
"""
import csv, json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D2 = os.path.join(ROOT, "02_screening")
J = lambda p: json.load(open(p, encoding="utf-8"))
rows = list(csv.DictReader(open(os.path.join(D2, "merged_candidates.csv"), encoding="utf-8")))
base_fields = [k for k in rows[0].keys() if k not in ("eligibility", "R", "E", "V", "T", "A", "score", "decision", "decision_reason", "final_id")]
byid = {r["merged_id"]: r for r in rows}
sel = J(os.path.join(D2, "_selection.json"))
cfg = J(os.path.join(D2, "screening_scores.json"))
fa = J(os.path.join(D2, "final_annotations.json"))
ca = J(os.path.join(ROOT, "01_discovery", "claude_annotations.json"))["included"]
sc = {x["mid"]: x for x in sel["scored"]}
CN = {"T1": "REST/Web API testing & fuzzing", "T2": "GraphQL, RPC/gRPC & architecture styles", "T3": "API security & authorization",
      "T4": "API specification inference & enrichment", "T5": "API evolution, breaking changes & deprecation",
      "T6": "API documentation, design quality & governance", "T7": "API misuse detection", "T8": "LLM tool use, API calling & MCP",
      "T9": "Microservice APIs, reliability & observability", "T10": "API recommendation & composition"}

order = sorted(sel["selected"], key=lambda m: (int(byid[m]["cluster"][1:]), -sc[m]["score"], m))
pid = {m: f"P{i:03d}" for i, m in enumerate(order, 1)}

# ---- merged_candidates.csv with screening columns
for r in rows:
    m = r["merged_id"]
    s = sc.get(m)
    r["eligibility"] = "ineligible: " + cfg["ineligible"][m] if m in cfg["ineligible"] else "eligible"
    for k in "REVTA":
        r[k] = s[k] if s else ""
    r["score"] = s["score"] if s else ""
    r["decision"] = "SELECTED" if m in pid else "excluded"
    r["decision_reason"] = ("selected" + (" (manual override)" if any(m == o[1] for o in cfg["overrides"]["swap"]) else "")) if m in pid \
        else (cfg["ineligible"].get(m) or sel["not_selected_reasons"].get(m, ""))
    r["final_id"] = pid.get(m, "")
with open(os.path.join(D2, "merged_candidates.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=base_fields + ["eligibility", "R", "E", "V", "T", "A", "score", "decision", "decision_reason", "final_id"], quoting=csv.QUOTE_ALL)
    w.writeheader(); w.writerows(rows)


import re as _re


def map_ids(t):
    """Replace merged IDs in free text with final P-IDs (or mark as excluded)."""
    return _re.sub(r"\bM(\d{3})\b", lambda mo: pid.get(mo.group(0)) or f"{mo.group(0)} [excluded]", t) if isinstance(t, str) else t


def ann(m):
    r = byid[m]; a = {k: map_ids(v) for k, v in fa[m].items()}
    c = ca.get(r["claude_id"]) if r["claude_id"] else None
    for k_src, k_dst in (("problem", "problem"), ("contribution", "contribution"), ("findings", "findings"), ("methods", "methods")):
        if k_dst not in a:
            a[k_dst] = (c or {}).get(k_src, "Not assessed")
    return a


def pdf_cell(r):
    return r["verified_pdf_url"] if r["verified_pdf_url"] != "Not verified" else "Not verified"


def access_short(r):
    a = r["access_status"]
    if a.startswith("Open"):
        return "OA (verified)"
    if a.startswith("Legal preprint"):
        return "Preprint OA (verified arXiv)"
    return "Not verified"


# ---- final_papers.csv
FF = ["final_id", "merged_id", "provenance", "claude_id", "codex_id", "title", "authors", "year", "year_note", "venue", "publication_type",
      "review_status", "role", "cluster", "cluster_name", "importance", "main_contribution", "research_question", "problem", "methods",
      "key_findings_abstract", "why_selected", "why_read_full_text", "needs_verification", "doi", "arxiv_id", "canonical_url",
      "verified_pdf_url", "pdf_version_note", "alt_verified_pdf", "unverified_candidate_urls", "access_status", "score", "expected_markdown"]
final = []
for m in order:
    r = byid[m]; a = ann(m)
    final.append({"final_id": pid[m], "merged_id": m, "provenance": r["provenance"], "claude_id": r["claude_id"], "codex_id": r["codex_id"],
                  "title": r["title"], "authors": r["authors"], "year": r["year"], "year_note": r["year_note"], "venue": r["venue"],
                  "publication_type": r["publication_type"], "review_status": r["review_status"], "role": a["role"], "cluster": r["cluster"],
                  "cluster_name": CN[r["cluster"]], "importance": a["importance"], "main_contribution": a["short"], "research_question": a["question"],
                  "problem": a["problem"], "methods": a["methods"], "key_findings_abstract": a["findings"], "why_selected": a["why"],
                  "why_read_full_text": a["read"], "needs_verification": a["verify"], "doi": r["doi"], "arxiv_id": r["arxiv_id"],
                  "canonical_url": r["canonical_url"], "verified_pdf_url": pdf_cell(r), "pdf_version_note": r["pdf_version_note"],
                  "alt_verified_pdf": r["alt_verified_pdf"], "unverified_candidate_urls": r["unverified_candidate_urls"],
                  "access_status": r["access_status"], "score": sc[m]["score"], "expected_markdown": f"{pid[m]}.md"})
with open(os.path.join(D2, "final_papers.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=FF, quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(final)
with open(os.path.join(D2, "paper_manifest.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, quoting=csv.QUOTE_ALL)
    w.writerow(["final_id", "title", "doi", "arxiv_id", "source_link", "pdf_link", "pdf_status", "expected_markdown", "conversion_status"])
    for f in final:
        w.writerow([f["final_id"], f["title"], f["doi"], f["arxiv_id"], f["canonical_url"], f["verified_pdf_url"], access_short(byid[f["merged_id"]]),
                    f["expected_markdown"], "PENDING"])


def esc(s):
    return (str(s) or "").replace("|", "\\|").replace("\n", " ")


def lk(u, t):
    return f"[{t}]({u})" if u and u.startswith("http") else "—"


# ---- final_papers.md
from collections import Counter
L = ["# Final Paper Catalog — PHASE B (Human-Download Catalog)\n",
     "**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19 | **উৎস:** `final_papers.csv` (script-generated: `00_protocol/scripts/final_build.py`)\n",
     f"**মোট নির্বাচিত:** {len(final)} | Cluster: " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(f['cluster'] for f in final).items(), key=lambda x: int(x[0][1:]))) +
     f" | Provenance: " + ", ".join(f"{k} {v}" for k, v in Counter(f['provenance'] for f in final).items()) +
     f" | Access: " + ", ".join(f"{k} {v}" for k, v in Counter(access_short(byid[f['merged_id']]) for f in final).items()) + "\n",
     "> **Link নীতি:** *Paper Link* = canonical landing (DOI বা proceedings/arXiv abs)। *PDF Link* = শুধু আমাদের নিজস্ব probe-এ `%PDF` signature-সহ যাচাইকৃত URL। “Preprint OA” মানে বৈধ arXiv/repository কপি — published version থেকে ভিন্ন হতে পারে। “Not verified” হলে নিচের subsection-এ unverified candidate route দেওয়া আছে (যেমন ACM PDF যা script-এ 403 দেয় কিন্তু browser-এ খুলতে পারে)।\n",
     "> **প্রমাণের স্তর:** সব বর্ণনা abstract-ভিত্তিক; কোনো full text পড়া হয়নি (PHASE C-র কাজ)।\n",
     "## মূল তালিকা\n",
     "| ID | Paper Title | Year | Venue | Research Area | Main Contribution | Importance | Paper Link | PDF Link | Access |",
     "|---|---|---|---|---|---|---|---|---|---|"]
for f in final:
    r = byid[f["merged_id"]]
    L.append(f"| {f['final_id']} | {esc(f['title'])} | {f['year']} | {esc(f['venue'])} | {f['cluster']} — {esc(f['cluster_name'])} | {esc(f['main_contribution'])} | {f['importance']} | {lk(f['canonical_url'], 'Link')} | {lk(f['verified_pdf_url'], 'PDF') if f['verified_pdf_url'] != 'Not verified' else '**Not verified**'} | {access_short(r)}{' · PREPRINT' if f['publication_type'] == 'Preprint' else ''} |")
L.append("\n## প্রতিটি নির্বাচিত paper-এর বিস্তারিত\n")
cur = None
for f in final:
    if f["cluster"] != cur:
        cur = f["cluster"]; L.append(f"### {cur} — {CN[cur]}\n")
    L.append(f"#### {f['final_id']} — {f['title']}\n")
    L.append(f"- **Authors:** {f['authors']}")
    L.append(f"- **Year / Venue:** {f['year']} — {f['venue']} ({f['publication_type']}; {f['review_status']})" + (f" _[year note: {f['year_note']}]_" if f["year_note"] else ""))
    L.append(f"- **ধরন:** {f['role']} | **Importance:** {f['importance']} | **Provenance:** {f['provenance']} (Claude {f['claude_id'] or '—'}, Codex {f['codex_id'] or '—'}, merged {f['merged_id']}) | **Score:** {f['score']}")
    L.append(f"- **DOI:** {f['doi']} | **arXiv:** {f['arxiv_id']}")
    L.append(f"- **Paper link:** {f['canonical_url']}")
    L.append(f"- **PDF (verified):** {f['verified_pdf_url']}" + (f" — _{f['pdf_version_note']}_" if f["pdf_version_note"] else ""))
    if f["alt_verified_pdf"]:
        L.append(f"- **বিকল্প verified PDF:** {f['alt_verified_pdf']}")
    if f["unverified_candidate_urls"]:
        L.append(f"- **Unverified candidate route:** {f['unverified_candidate_urls']}")
    L.append(f"- **প্রশ্ন যা paper-টি সমাধান করে:** {f['research_question']}")
    L.append(f"- **কেন নির্বাচিত:** {f['why_selected']}")
    L.append(f"- **বর্তমানে যা জানা (abstract-level):** Problem — {f['problem']} · Contribution — {f['main_contribution']} · Findings — {f['key_findings_abstract']}")
    L.append(f"- **Full paper পড়লে কী লাভ:** {f['why_read_full_text']}")
    L.append(f"- **যা যাচাই করতে হবে:** {f['needs_verification']}\n")
open(os.path.join(D2, "final_papers.md"), "w", encoding="utf-8").write("\n".join(L))

# ---- excluded_papers.md
E = ["# Excluded Papers — PHASE B\n", "**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19 | merged pool ১০৪ → নির্বাচিত ৩৮ → বাদ ৬৬\n",
     "> বাদ পড়া মানে paper-টি খারাপ নয় — এটি এই নির্দিষ্ট গবেষণার উদ্দেশ্য, কভারেজ quota, research-group cap ও প্রমাণ-প্রাপ্যতার ভিত্তিতে নেওয়া সিদ্ধান্ত। স্কোর: `selection_methodology.md`।\n",
     "## ক. অযোগ্য (eligibility stage)\n", "| Merged | Title | Provenance | কারণ |", "|---|---|---|---|"]
for m, why in cfg["ineligible"].items():
    E.append(f"| {m} | {esc(byid[m]['title'])} | {byid[m]['provenance']} | {esc(why)} |")
E += ["\n## খ. যোগ্য কিন্তু নির্বাচিত হয়নি (scored)\n",
      "‘Priority alternate’ = PHASE C/D-তে gap যাচাইয়ের সময় প্রথমে বিবেচ্য (প্রতি cluster-এ সর্বোচ্চ স্কোরের বাদপড়া ২টি)।\n",
      "| Merged | Cluster | Title | Year | Provenance | Score | কারণ | Priority alternate |", "|---|---|---|---|---|---|---|---|"]
excl = [x for x in sel["scored"] if x["mid"] not in pid]
alt = {}
for x in excl:
    alt.setdefault(x["cluster"], [])
    if len(alt[x["cluster"]]) < 2:
        alt[x["cluster"]].append(x["mid"])
altset = {m for v in alt.values() for m in v}
for x in sorted(excl, key=lambda x: (int(x["cluster"][1:]), -x["score"])):
    r = byid[x["mid"]]
    E.append(f"| {x['mid']} | {x['cluster']} | {esc(r['title'])} | {r['year']} | {r['provenance']} | {x['score']:.2f} | {esc(sel['not_selected_reasons'].get(x['mid'], ''))} | {'✅' if x['mid'] in altset else ''} |")
open(os.path.join(D2, "excluded_papers.md"), "w", encoding="utf-8").write("\n".join(E))

# ---- download_checklist.md
C = ["# Download Checklist — HUMAN CHECKPOINT 2\n",
     "**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19 | মেশিন-পাঠযোগ্য manifest: `paper_manifest.csv`\n",
     "## নির্দেশনা\n",
     "1. প্রতিটি paper ডাউনলোড করে Markdown-এ রূপান্তর করুন এবং `research/03_papers_markdown/` ফোল্ডারে **ঠিক নিচের ফাইলনামে** রাখুন (যেমন `P001.md`)।",
     "2. **সংস্করণ অগ্রাধিকার:** (ক) publisher-এর published version (institutional access বা browser-এ ACM OA থাকলে) → (খ) তালিকার verified PDF → (গ) arXiv/repository preprint। Preprint ব্যবহার করলে নিচের ‘ব্যবহৃত version’ কলামে লিখুন — PHASE C-তে সংখ্যা মিলানোর সময় দরকার হবে।",
     "3. Conversion-এর সময় **table, equation, figure caption ও reference list** যেন হারিয়ে না যায়; সম্ভব হলে page marker (যেমন `<!-- page 5 -->`) রাখুন — PHASE C-তে evidence location উল্লেখের জন্য।",
     f"4. “Not verified” চিহ্নিত {sum(f['verified_pdf_url'] == 'Not verified' for f in final)}টির জন্য নিচে candidate route (থাকলে) দেওয়া আছে; কাজ না করলে institutional access লাগবে। পাওয়া না গেলে ‘missing’ লিখে জানান — অন্য কিছু দিয়ে প্রতিস্থাপন করবেন না।",
     "5. arXiv-এ একাধিক version থাকলে কোন version নেওয়া হলো তা লিখুন — বিশেষত " + ", ".join(f"{f['final_id']} ({f['title'][:40]}…)" for f in final if f["merged_id"] in ("M061", "M066", "M053")) + " (প্রত্যেকটির ২–৪টি arXiv version আছে; M061-এ শিরোনাম ও সংখ্যাও বদলেছে)।\n",
     "## Checklist\n",
     "| ✓ | ID | Expected file | Title | DOI / arXiv | PDF link (verified) | Access | ব্যবহৃত version | Conversion |", "|---|---|---|---|---|---|---|---|---|"]
for f in final:
    r = byid[f["merged_id"]]
    ident = f["doi"] if f["doi"] != "Not applicable" else f"arXiv:{f['arxiv_id']}"
    C.append(f"| ☐ | {f['final_id']} | `{f['expected_markdown']}` | {esc(f['title'])} | {ident} | {lk(f['verified_pdf_url'], 'PDF') if f['verified_pdf_url'] != 'Not verified' else '**Not verified** — see final_papers.md'} | {access_short(r)} | | PENDING |")
C += ["\n## ‘Not verified’ paper-গুলোর জন্য সম্ভাব্য পথ\n"]
for f in final:
    if f["verified_pdf_url"] == "Not verified":
        C.append(f"- **{f['final_id']}** {f['title']} — landing: {f['canonical_url']}" + (f" — candidate: {f['unverified_candidate_urls']}" if f["unverified_candidate_urls"] else " — কোনো OA candidate পাওয়া যায়নি (institutional access প্রয়োজন)"))
open(os.path.join(D2, "download_checklist.md"), "w", encoding="utf-8").write("\n".join(C))
print("final:", len(final), "| not verified:", sum(f["verified_pdf_url"] == "Not verified" for f in final))
for f in final:
    print(f["final_id"], f["merged_id"], f["cluster"], f["title"][:60])
