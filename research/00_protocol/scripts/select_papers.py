#!/usr/bin/env python3
"""PHASE B3: transparent, quota-constrained selection.

score = 0.25*R + 0.25*E + 0.20*V + 0.15*T + 0.15*A   (all on 1-5)
  T: foundational -> 4; year>=2023 -> 5; 2021-2022 -> 3; <=2020 -> 2
  A: verified publisher/proceedings/repository/author PDF or arXiv-only paper -> 5;
     legal arXiv preprint of a published paper -> 4; not verified -> 2
Greedy per-cluster selection by score, subject to:
  * group cap (Arcuri/Zhang; Orso/Sinha) — see GROUPS
  * preprint cap
Ties broken by E, then V. Output: research/02_screening/_selection.json
"""
import csv, json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D2 = os.path.join(ROOT, "02_screening")
cfg = json.load(open(os.path.join(D2, "screening_scores.json"), encoding="utf-8"))
rows = {r["merged_id"]: r for r in csv.DictReader(open(os.path.join(D2, "merged_candidates.csv"), encoding="utf-8"))}
GROUPS = {"Arcuri/Zhang (EvoMaster)": ("Andrea Arcuri", "Man Zhang"),
          "Orso/Sinha (Georgia Tech/IBM)": ("Alessandro Orso", "Saurabh Sinha")}


def T(r, f):
    if f:
        return 4
    y = int(r["year"])
    return 5 if y >= 2023 else 3 if y >= 2021 else 2


def A(r):
    a = r["access_status"]
    if a.startswith("Open"):
        return 5
    if a.startswith("Legal preprint"):
        return 4
    return 2


def group_of(r):
    return [g for g, names in GROUPS.items() if any(n in r["authors"] for n in names)]


scored = []
for mid, (R, E, V, F) in cfg["scores"].items():
    r = rows[mid]
    t, a = T(r, F), A(r)
    s = round(0.25 * R + 0.25 * E + 0.20 * V + 0.15 * t + 0.15 * a, 3)
    scored.append({"mid": mid, "cluster": r["cluster"], "R": R, "E": E, "V": V, "T": t, "A": a, "F": F,
                   "score": s, "groups": group_of(r), "preprint": r["publication_type"] == "Preprint"})
scored.sort(key=lambda x: (-x["score"], -x["E"], -x["V"]))
sel, gcount, pcount, reasons = [], {}, 0, {}
quota_left = dict(cfg["quotas"])
for x in scored:
    if quota_left.get(x["cluster"], 0) <= 0:
        reasons[x["mid"]] = f"cluster {x['cluster']} quota filled by higher-scoring papers" if cfg["quotas"].get(x["cluster"]) else f"cluster {x['cluster']} not retained in final set"
        continue
    if any(gcount.get(g, 0) >= cfg["group_cap"] for g in x["groups"]):
        reasons[x["mid"]] = f"research-group cap ({cfg['group_cap']}) reached: {', '.join(x['groups'])}"
        continue
    if x["preprint"] and pcount >= cfg["preprint_cap"]:
        reasons[x["mid"]] = "preprint cap reached"
        continue
    sel.append(x["mid"]); quota_left[x["cluster"]] -= 1
    for g in x["groups"]:
        gcount[g] = gcount.get(g, 0) + 1
    pcount += x["preprint"]
# documented manual overrides (screening_scores.json -> overrides)
for out_id, in_id, why in cfg.get("overrides", {}).get("swap", []):
    if out_id in sel:
        sel[sel.index(out_id)] = in_id
        reasons[out_id] = "manual override (swapped out): " + why
        reasons.pop(in_id, None)
json.dump({"scored": scored, "selected": sel, "not_selected_reasons": reasons, "group_counts": gcount,
           "preprints": pcount, "unfilled_quota": {k: v for k, v in quota_left.items() if v > 0}},
          open(os.path.join(D2, "_selection.json"), "w", encoding="utf-8"), indent=1)
print(len(sel), "selected; groups", gcount, "preprints", pcount, "unfilled", {k: v for k, v in quota_left.items() if v > 0})
for x in scored:
    mark = "SEL" if x["mid"] in sel else "   "
    print(f"{mark} {x['mid']} {x['cluster']:<3} {x['score']:.2f} R{x['R']}E{x['E']}V{x['V']}T{x['T']}A{x['A']} {rows[x['mid']]['title'][:62]} | {reasons.get(x['mid'], '')[:55]}")
