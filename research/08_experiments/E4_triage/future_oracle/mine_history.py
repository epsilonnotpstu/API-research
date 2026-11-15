#!/usr/bin/env python3
"""T41 offline metadata miner. Never imports or executes external project code.

Run from research/: /usr/bin/python3 -I -B .../mine_history.py
Only the seven explicitly permitted, read-only Git verbs are allowed.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "08_experiments/E4_triage/future_oracle"
SCRATCH = ROOT / "09_collab/logs/T41_scratch"
EMB = ROOT / "08_experiments/_external/emb"
UP = ROOT / "08_experiments/_external/upstream"
LABELS = ROOT / "08_experiments/E2_labelling"
SUTS = {
    "swagger-petstore": ("jdk_8_maven/cs/rest/original/swagger-petstore", "swagger-petstore"),
    "cwa-verification": ("jdk_11_maven/cs/rest/cwa-verification-server", "cwa-verification-server"),
    "market": ("jdk_11_maven/cs/rest-gui/market", "market"),
}
VERBS = {"log", "show", "rev-list", "ls-tree", "diff", "cat-file"}
EXTS = {".java", ".json", ".yaml", ".yml", ".xml", ".properties", ".sql"}
ALIASES = {"swagger-petstore": {"src/main/webapp/openapi.yaml": "src/main/resources/openapi.yaml"}}


def sanitize(value):
    """Redact header values without printing them. Never read README/demo HTML."""
    value = re.sub(r"(?im)(authorization|proxy-authorization|cookie|set-cookie)(\s*[\"']?\s*[:=]\s*)[^\r\n]*", r"\1\2[REDACTED]", value)
    value = re.sub(r"(?i)\b(Basic|Bearer)\s+[A-Za-z0-9+/=._~-]{8,}", r"\1 [REDACTED]", value)
    return value


def git(repo, *args):
    assert args[0] in VERBS, args
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-c", "core.pager=cat", "-C", str(repo), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_NO_REPLACE_OBJECTS": "1", "GIT_TERMINAL_PROMPT": "0", "GIT_NO_LAZY_FETCH": "1"},
    ).stdout


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def relevant(path):
    p = Path(path)
    return p.suffix in EXTS and (
        "src" in p.parts or path in {"api-docs.json", "inflector.yaml", "pom.xml"}
        or (p.name == "pom.xml" and len(p.parts) == 2)
    )


def tree(repo, commit):
    result = {}
    for row in git(repo, "ls-tree", "-r", "-z", commit).split(b"\0"):
        if row:
            meta, path = row.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            if kind == "blob":
                result[path.decode()] = oid
    return result


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    final = [r for r in read_csv(LABELS / "final_labels_baseline_s1.csv") if r["sut"] in SUTS]
    assert len(final) == 62
    protected = {}
    for name in ["final_labels_baseline_s1.csv"] + [s + suffix for s in SUTS for suffix in ["_adjudication.csv", "_baseline_s1_labels_codex.csv"]]:
        p = LABELS / name
        protected[str(p.relative_to(ROOT))] = sha(p.read_bytes())
    items = []
    for sut in SUTS:
        adjud = {r["item_id"]: r for r in read_csv(LABELS / (sut + "_adjudication.csv"))}
        lab = {r["item_id"]: r for r in read_csv(LABELS / (sut + "_baseline_s1_labels_codex.csv"))}
        for row in final:
            if row["sut"] == sut:
                item_id = row["item_id"]
                items.append({"baseline": row, "adjudication": adjud[item_id], "codex": lab[item_id]})
    # These inputs contain locators/rationales, not raw HTTP headers or bodies.
    dump(OUT / "baseline_evidence.json", json.loads(sanitize(json.dumps(items, ensure_ascii=False))))
    anchors = {}
    scores = []
    for sut, (emb_rel, clone_name) in SUTS.items():
        source, repo = EMB / emb_rel, UP / clone_name
        emb = {}
        for p in sorted(source.rglob("*")):
            rel = p.relative_to(source).as_posix()
            if any(part in {"target", ".git", "node_modules"} for part in p.relative_to(source).parts):
                continue
            if p.is_file() and relevant(rel):
                assert not p.is_symlink(), p
                data = p.read_bytes()
                emb[rel] = blob(data)
                protected[str(p.relative_to(ROOT))] = sha(data)
        spec = EMB / "openapi-swagger" / (sut + ".json")
        protected[str(spec.relative_to(ROOT))] = sha(spec.read_bytes())
        commits = git(repo, "rev-list", "--all").decode().splitlines()
        head = git(repo, "rev-list", "-1", "HEAD").decode().strip()
        reachable = set(git(repo, "rev-list", "HEAD").decode().splitlines())
        all_scores = []
        for commit in commits:
            upstream = tree(repo, commit)
            mapped = {p: p if p in upstream else ALIASES.get(sut, {}).get(p, p) for p in emb}
            matches = sum(upstream.get(mapped[p]) == oid for p, oid in emb.items())
            common = sum(mapped[p] in upstream for p in emb)
            java = [p for p in emb if p.endswith(".java")]
            java_matches = sum(upstream.get(p) == emb[p] for p in java)
            score = {"sut": sut, "commit": commit, "matches": matches, "literal_path_matches": sum(upstream.get(p) == oid for p, oid in emb.items()), "denominator": len(emb), "fraction": matches / len(emb), "common_paths": common, "java_matches": java_matches, "java_total": len(java), "reachable_from_head": commit in reachable}
            all_scores.append(score)
        best = max(r["matches"] for r in all_scores if r["reachable_from_head"])
        # rev-list is reverse topological/date traversal; retain all tied maxima.
        ties = [r["commit"] for r in all_scores if r["matches"] == best and r["reachable_from_head"]]
        chosen = ties[-1]
        selected = tree(repo, chosen)
        per_file = []
        for p, oid in emb.items():
            mapped_path = p if p in selected else ALIASES.get(sut, {}).get(p, p)
            per_file.append({"path": p, "upstream_path": mapped_path, "emb_blob": oid, "upstream_blob": selected.get(mapped_path), "state": "exact" if selected.get(mapped_path) == oid else "different" if mapped_path in selected else "emb_only"})
        upstream_only = [p for p in selected if relevant(p) and p not in {r['upstream_path'] for r in per_file}]
        metadata = git(repo, "show", "-s", "--format=%H%n%aI%n%cI%n%s", chosen).decode().splitlines()
        post = git(repo, "rev-list", "--reverse", "--ancestry-path", chosen + ".." + head).decode().splitlines()
        reachable_post = git(repo, "rev-list", "--reverse", head, "^" + chosen).decode().splitlines()
        headmeta = git(repo, "show", "-s", "--format=%H%n%aI%n%cI%n%s", head).decode().splitlines()
        anchors[sut] = {
            "emb_source": str(source.relative_to(ROOT)), "upstream_clone": str(repo.relative_to(ROOT)),
            "deployed_spec": str(spec.relative_to(ROOT)), "head": head, "head_author_date": headmeta[1], "head_committer_date": headmeta[2], "head_message": sanitize(headmeta[3][:160]),
            "commit": chosen, "author_date": metadata[1], "committer_date": metadata[2], "message": sanitize(metadata[3][:160]),
            "selection": "oldest tied maximum in rev-list --all traversal, restricted to HEAD ancestors; all ties retained",
            "scope": "All Java/JSON/YAML/XML/properties/SQL under src, plus module/root pom.xml, api-docs.json, inflector.yaml; target/.git/node_modules excluded",
            "path_aliases": ALIASES.get(sut, {}),
            "matches": best, "denominator": len(emb), "fraction": best / len(emb), "tied_best_commits": ties,
            "global_best_matches": max(r["matches"] for r in all_scores),
            "java_matches": sum(r["state"] == "exact" and r["path"].endswith(".java") for r in per_file),
            "java_total": sum(r["path"].endswith(".java") for r in per_file),
            "per_file": per_file, "upstream_only_relevant_files": upstream_only,
            "post_anchor_ancestry_commits": post, "post_anchor_reachable_commits": reachable_post,
        }
        # Do not include README/HTML patches; these are known to contain credentials.
        # SQL seed data may contain credentials: retain hashes/paths only.
        changed = [r for r in per_file if r["state"] == "different" and not r["path"].endswith('.sql')]
        patches = []
        for row in changed:
            p = row['path']
            old = git(repo, "show", chosen + ":" + row['upstream_path']).decode(errors="replace").splitlines(True)
            new = (source / p).read_text(errors="replace").splitlines(True)
            import difflib
            patches.extend(difflib.unified_diff(old, new, fromfile=chosen + ":" + p, tofile="EMB:" + p))
        (OUT / (sut + "_emb_local.diff")).write_text(sanitize("".join(patches)))
        logs = []
        for commit in reachable_post:
            meta = git(repo, "show", "-s", "--format=%H%n%P%n%aI%n%cI%n%s", commit).decode().splitlines()
            parents = meta[1].split()
            touched = git(repo, "diff", "--name-only", parents[0], commit).decode().splitlines() if parents else []
            logs.append({"commit": commit, "parents": parents, "author_date": meta[2], "committer_date": meta[3], "message": sanitize(meta[4][:160]), "ancestry_descendant": commit in post, "files": touched})
        dump(OUT / (sut + "_history.json"), logs)
        scores.extend(all_scores)
    dump(OUT / "anchors.json", anchors)
    with (OUT / "anchor_scores.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(scores[0]))
        writer.writeheader()
        writer.writerows(scores)
    dump(SCRATCH / "protected_hashes.json", protected)
    print(json.dumps({s: {k: a[k] for k in ["commit", "matches", "denominator", "fraction", "java_matches", "java_total", "tied_best_commits"]} for s, a in anchors.items()}, indent=2))


if __name__ == "__main__":
    main()
