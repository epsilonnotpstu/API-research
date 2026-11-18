"""Independent T55 review; reads metadata and prints aggregates, never runs scorer."""
import collections
import csv
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def rows(path):
    with (ROOT / path).open(newline="") as stream:
        return list(csv.DictReader(stream))


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, c - h, c + h]


FIELDS = ("observable_change", "change_kind", "client_impact", "contract_specified")


def load(paths):
    result = {}
    for path in paths:
        for row in rows(path):
            item = row["item_id"]
            assert item not in result
            result[item] = {f: row[f].strip().upper() for f in FIELDS}
            if result[item]["observable_change"] != "YES":
                result[item].update({f: "NA" for f in FIELDS[1:]})
    return result


def final(a, b):
    obs = a[FIELDS[0]] if a[FIELDS[0]] == b[FIELDS[0]] else "UNCLEAR"
    return {FIELDS[0]: obs, **{
        f: (a[f] if a[f] == b[f] else "UNCLEAR") if obs == "YES" else "NA"
        for f in FIELDS[1:]
    }}


def kappa(a, b):
    observed = sum(x == y for x, y in zip(a, b)) / len(a)
    ca, cb = collections.Counter(a), collections.Counter(b)
    expected = sum(ca[x] * cb[x] for x in ca.keys() | cb.keys()) / len(a) ** 2
    return (observed - expected) / (1 - expected)


aggregate = {r["measure"]: r for r in rows(Path("plan/r3_scores.csv"))}
result = {"from_scores_csv": {}}
for measure, row in aggregate.items():
    k, n = int(row["k"]), int(row["n"])
    result["from_scores_csv"][measure] = {"k": k, "n": n, "wilson": wilson(k, n)}
k, n = int(aggregate["H-R3-1"]["k"]), int(aggregate["H-R3-1"]["n"])
result["H-R3-1_p"] = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
g1 = load([Path("packages/r3_blind/codes_G1.csv")])
g2 = load([Path("packages/r3_blind/codes_G2.csv")])
h1 = load(sorted((ROOT / "packages").glob("r3_kb*/codes_H1.csv")))
h2 = load(sorted((ROOT / "packages").glob("r3_kb*/codes_H2.csv")))
key = {r["item_id"]: r for r in rows(Path("mining/key/r3_key.csv"))}
assert set(key) == set(g1) == set(g2) == set(h1) == set(h2)
items = []
for item in sorted(key):
    metadata = key[item]
    items.append({"g": final(g1[item], g2[item]), "h": final(h1[item], h2[item]),
                  "repo": metadata["repo"], "lang": metadata["language"],
                  "ann": metadata["annotation_touched"].lower() == "true",
                  "upd": metadata["spec_updated_90d"].lower() == "true"})


def observable(item, family="g"):
    return item[family]["observable_change"] == "YES"


def breaking(item, family="g"):
    return observable(item, family) and item[family]["client_impact"] == "BREAKING"


yes = [i for i in items if observable(i)]
brk = [i for i in items if breaking(i)]
result["families"] = {f: {"observable": sum(observable(i, f) for i in items),
                          "breaking": sum(breaking(i, f) for i in items),
                          "observable_labels": dict(collections.Counter(i[f]["observable_change"] for i in items))}
                      for f in ("g", "h")}
result["kinds"] = {kind: {"total": sum(i["g"]["change_kind"] == kind for i in yes),
                           "breaking": sum(i["g"]["change_kind"] == kind for i in brk),
                           "compatible": sum(i["g"]["change_kind"] == kind and i["g"]["client_impact"] == "COMPATIBLE" for i in yes)}
                   for kind in sorted({i["g"]["change_kind"] for i in yes})}
result["annotations"] = {name: {"touched": sum(i["ann"] for i in subset), "n": len(subset)}
                         for name, subset in (("all", items), ("observable", yes), ("breaking", brk))}
result["specified"] = {name: dict(collections.Counter(i["g"]["contract_specified"] for i in subset))
                       for name, subset in (("observable", yes), ("breaking", brk))}
result["languages"] = {lang: {"n": sum(i["lang"] == lang for i in items),
                              "observable": sum(i["lang"] == lang and observable(i) for i in items),
                              "breaking": sum(i["lang"] == lang and breaking(i) for i in items)}
                       for lang in sorted({i["lang"] for i in items})}
result["within_kappa"] = {f: {"g": kappa([g1[i][f] for i in sorted(key)], [g2[i][f] for i in sorted(key)]),
                               "h": kappa([h1[i][f] for i in sorted(key)], [h2[i][f] for i in sorted(key)])}
                          for f in FIELDS}
decided = [i for i in items if i["g"][FIELDS[0]] in ("YES", "NO") and i["h"][FIELDS[0]] in ("YES", "NO")]
result["cross_kappa"] = {"n": len(decided), "agree": sum(i["g"][FIELDS[0]] == i["h"][FIELDS[0]] for i in decided),
                         "kappa": kappa([i["g"][FIELDS[0]] for i in decided], [i["h"][FIELDS[0]] for i in decided])}
specified = [i for i in brk if i["g"]["contract_specified"] == "SPECIFIED"]
result["H-R3-2"] = {"n": len(specified), "no_update": sum(not i["upd"] for i in specified)}
repos = sorted({i["repo"] for i in items})
by_repo = {r: [i for i in items if i["repo"] == r] for r in repos}
result["bootstrap"] = {}
for name, predicate in (("observable", observable), ("breaking", breaking)):
    rng = random.Random(1)
    values = []
    for _ in range(2000):
        sample = [i for _ in repos for i in by_repo[rng.choice(repos)]]
        values.append(sum(predicate(i) for i in sample) / len(sample))
    values.sort()
    result["bootstrap"][name] = [values[50], values[1949]]
loo = [sum(breaking(i) for i in items if i["repo"] != r) / sum(i["repo"] != r for i in items) for r in repos]
result["leave_one_out"] = {"min": min(loo), "max": max(loo),
                           "largest_delta": max(abs(x - len(brk) / len(items)) for x in loo)}
assert len(yes) == int(aggregate["E-R3-1 YES"]["k"])
assert len(brk) == int(aggregate["E-R3-1 BREAKING"]["k"])
assert sum(not i["ann"] for i in brk) == int(aggregate["H-R3-1"]["k"])
print(json.dumps(result, indent=2))
