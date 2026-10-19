#!/usr/bin/env python3
"""Render research/01_discovery/claude_candidates.md from claude_candidates.csv (single source of truth)."""
import csv, json, os
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "01_discovery")
rows = list(csv.DictReader(open(os.path.join(D, "claude_candidates.csv"), encoding="utf-8")))
build = json.load(open(os.path.join(D, "raw", "verify", "_catalog_build.json"), encoding="utf-8"))


def cell(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def short_access(r):
    a = r["access_status"]
    if a.startswith("Open (") or a.startswith("Open access"):
        return "🟢 OA"
    if a.startswith("Publisher version not verified"):
        return "🟡 Preprint OA"
    return "🔴 Not verified"


def link(u, label):
    return f"[{label}]({u})" if u and u.startswith("http") else (u or "—")


out = []
out.append("# Claude Candidate Catalog — PHASE A (স্বাধীন অনুসন্ধান)\n")
out.append("**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19 | **মেশিন-পাঠযোগ্য উৎস:** `claude_candidates.csv` (এই ফাইল সেখান থেকে script দিয়ে তৈরি — `00_protocol/scripts/build_catalog_md.py`)\n")
out.append("> **প্রমাণের স্তর:** কোনো paper-এর full text পড়া হয়নি। Problem/Contribution/Methods/Findings কলাম **শুধু যাচাইকৃত abstract-এর** paraphrase (ইংরেজিতে রাখা হয়েছে যাতে অনুবাদে অর্থবিকৃতি না ঘটে)। “author claim/author-reported” মানে লেখকের দাবি — স্বাধীনভাবে যাচাই নয়। Inclusion reason, relevance ও uncertainty Claude-এর বিশ্লেষণ।\n")
out.append("**Legend (Access):** 🟢 OA = publisher/proceedings/repository বা arXiv-only paper-এর PDF যাচাইকৃত · 🟡 Preprint OA = publisher version OA হিসেবে যাচাই হয়নি, কিন্তু বৈধ preprint PDF (arXiv) যাচাইকৃত (published version থেকে ভিন্ন হতে পারে) · 🔴 = শুধু landing page; unrestricted full text যাচাই হয়নি।\n")
out.append("**PDF যাচাই পদ্ধতি:** URL-এ ranged GET; response body `%PDF` দিয়ে শুরু হলেই কেবল ‘verified’।\n")

# summary stats
c_area = Counter(r["taxonomy"].split(" ")[0] for r in rows)
c_sec = Counter(r["taxonomy"].split("+")[1].rstrip(")") for r in rows if "+" in r["taxonomy"])
TNAME = {"T1": "REST/Web API testing & fuzzing", "T2": "GraphQL, RPC/gRPC & architecture styles", "T3": "API security & authorization",
         "T4": "API specification (OpenAPI) inference & enrichment", "T5": "API evolution, breaking changes & deprecation",
         "T6": "API documentation, design quality & governance", "T7": "API misuse detection", "T8": "LLM tool use, API calling & MCP",
         "T9": "Microservice APIs", "T10": "API recommendation", "T11": "API monitoring & anomaly detection"}
c_kind = Counter(r["paper_kind"].split(" –")[0].split(" /")[0] for r in rows)
c_rev = Counter("Preprint" if r["publication_type"] == "Preprint" else "Peer-reviewed" for r in rows)
c_era = Counter(r["era"] for r in rows)
c_acc = Counter(short_access(r) for r in rows)
c_year = Counter(r["year"] for r in rows)
out.append("## সারসংক্ষেপ\n")
out.append(f"- মোট included candidate: **{len(rows)}** (যাচাইকৃত seed ৭০টি থেকে; ৬টি screened-out — নিচে)")
out.append(f"- Review status: " + ", ".join(f"{k}: {v}" for k, v in c_rev.items()))
out.append(f"- Era: " + ", ".join(f"{k}: {v}" for k, v in c_era.items()))
out.append(f"- Paper kind: " + ", ".join(f"{k}: {v}" for k, v in c_kind.most_common()))
out.append(f"- Access: " + ", ".join(f"{k}: {v}" for k, v in c_acc.most_common()))
out.append(f"- বছর: " + ", ".join(f"{k}: {v}" for k, v in sorted(c_year.items())))
out.append("")
out.append("### Taxonomy অনুযায়ী (code-এর সংজ্ঞা: `00_protocol/api_research_landscape.md`)\n")
out.append("| Code | Area | Primary | Secondary membership |\n|---|---|---|---|")
for k in sorted(TNAME, key=lambda x: int(x[1:])):
    out.append(f"| {k} | {TNAME[k]} | {c_area.get(k, 0)} | {c_sec.get(k, 0)} |")
out.append("")

out.append("## মূল তালিকা (human review table)\n")
out.append("| ID | Title | Year | Venue | Type / Review | Kind | Tax. | Access | Paper link | PDF (verified) | Conf. |")
out.append("|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    typ = "Preprint" if r["publication_type"] == "Preprint" else f"{r['publication_type']} (PR)"
    out.append(f"| {r['temp_id']} | {cell(r['title'])} | {r['year']} | {cell(r['venue'])} | {typ} | {cell(r['paper_kind'])} | {r['taxonomy']} | {short_access(r)} | {link(r['canonical_url'], 'landing')} | {link(r['direct_pdf_url_verified'], 'PDF') if r['direct_pdf_url_verified'].startswith('http') else 'Not verified'} | {r['selection_confidence']} |")
out.append("\n(PR = peer-reviewed)\n")

out.append("## প্রতিটি candidate-এর বিস্তারিত\n")
for r in rows:
    out.append(f"### {r['temp_id']} — {r['title']}\n")
    out.append(f"- **Authors:** {r['authors']}")
    out.append(f"- **Year / Venue:** {r['year']} — {r['venue']}" + (f" _(note: {r['year_note']})_" if r["year_note"] else ""))
    out.append(f"- **Type / Review:** {r['publication_type']} — {r['review_status']} | **Kind:** {r['paper_kind']} | **Era:** {r['era']}")
    out.append(f"- **DOI:** {r['doi']} | **arXiv:** {r['arxiv_id']}")
    out.append(f"- **Canonical landing:** {r['canonical_url']}")
    out.append(f"- **Direct PDF (verified):** {r['direct_pdf_url_verified']}" + (f" | **Alternative legal OA:** {r['alt_oa_url']}" if r["alt_oa_url"] else ""))
    out.append(f"- **Access:** {r['access_status']}")
    out.append(f"- **Area:** {r['research_area']} — **Taxonomy:** {r['taxonomy']}")
    out.append(f"- **Problem:** {r['main_problem']}")
    out.append(f"- **Claimed contribution:** {r['claimed_contribution']}")
    out.append(f"- **Methods:** {r['methods']}")
    out.append(f"- **Key findings (abstract-level):** {r['key_findings']}")
    out.append(f"- **অন্তর্ভুক্তির কারণ:** {r['inclusion_reason']}")
    out.append(f"- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** {r['potential_research_relevance']}")
    out.append(f"- **Metadata verification:** {r['metadata_verification']}")
    out.append(f"- **Evidence level:** {r['evidence_access_level']} (abstract source: {r['abstract_source']})")
    out.append(f"- **Sources:** {r['source_databases']}")
    out.append(f"- **Confidence:** {r['selection_confidence']} — **অনিশ্চয়তা:** {r['uncertainty']}\n")

out.append("## Screened-out (যাচাইকৃত কিন্তু PHASE A তালিকা থেকে বাদ)\n")
out.append("| Temp ID | Title | বাদের কারণ |\n|---|---|---|")
for cid, title, why in build["excluded"]:
    out.append(f"| {cid} | {cell(title)} | {cell(why)} |")
out.append("\nএগুলোর পূর্ণ verification record `raw/verify/<ID>.json`-এ সংরক্ষিত; PHASE B-তে প্রয়োজনে পুনর্বিবেচনা করা যাবে।\n")
open(os.path.join(D, "claude_candidates.md"), "w", encoding="utf-8").write("\n".join(out))
print("written", len(rows))
