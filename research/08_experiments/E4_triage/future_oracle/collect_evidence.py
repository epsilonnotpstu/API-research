#!/usr/bin/env python3
"""Collect safe static evidence and inspect the exact candidate witness subsets."""
import collections
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t41_miner", HERE / "mine_history.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

PET = "src/main/java/io/swagger/petstore/"
CWA = "src/main/java/app/coronawarn/verification/"
MARKET_REST = "market-rest/src/main/java/market/"
MARKET_CORE = "market-core/src/main/java/market/"
PATHS = {
    "swagger-petstore": ["src/main/resources/openapi.yaml", "inflector.yaml", "pom.xml"] + [PET + p for p in ["controller/PetController.java", "controller/OrderController.java", "controller/UserController.java", "data/PetData.java", "data/OrderData.java", "data/UserData.java", "model/Pet.java", "model/Order.java", "model/User.java", "utils/Util.java"]],
    "cwa-verification": ["api-docs.json", "pom.xml"] + [CWA + p for p in ["config/OpenApiConfig.java", "config/RequestSizeLimitFilter.java", "controller/ExternalTokenController.java", "controller/ExternalTanController.java", "controller/ExternalTestStateController.java", "controller/InternalTanController.java", "controller/VerificationExceptionHandler.java", "model/RegistrationTokenRequest.java", "model/RegistrationToken.java", "model/Tan.java", "model/AuthorizationToken.java", "validator/RegistrationTokenKeyConstraint.java", "validator/RegistrationTokenRequestValidator.java", "service/HashingService.java", "service/AppSessionService.java", "service/TanService.java"]],
    "market": ["pom.xml", "market-rest/pom.xml", "market-core/pom.xml", MARKET_REST + "RestConfig.java", MARKET_REST + "rest/exception/RestExceptionHandler.java"] + [MARKET_REST + "rest/" + p + "RestController.java" for p in ["Cart", "Contacts", "Customer", "Orders"]] + [MARKET_CORE + "dto/" + p + "DTO.java" for p in ["Cart", "CartItem", "CreditCard", "Contacts", "User"]],
}


def full_inventory(anchors):
    protected = json.loads((m.SCRATCH / "protected_hashes.json").read_text())
    for sut, a in anchors.items():
        source, repo = m.ROOT / a["emb_source"], m.ROOT / a["upstream_clone"]
        upstream = m.tree(repo, a["commit"])
        rows = []
        for p in sorted(source.rglob("*")):
            rel = p.relative_to(source).as_posix()
            if any(t in {"target", ".git", "node_modules"} for t in p.relative_to(source).parts) or not p.is_file():
                continue
            assert not p.is_symlink()
            data = p.read_bytes()  # Hash only; README/demo HTML are never decoded or quoted.
            protected[str(p.relative_to(m.ROOT))] = m.sha(data)
            upath = rel if rel in upstream else m.ALIASES.get(sut, {}).get(rel, rel)
            rows.append({"path": rel, "upstream_path": upath, "emb_blob": m.blob(data), "upstream_blob": upstream.get(upath), "state": "exact" if upstream.get(upath) == m.blob(data) else "different" if upath in upstream else "emb_only", "selected_for_anchor": m.relevant(rel)})
        m.dump(m.OUT / (sut + "_file_inventory.json"), rows)
    m.dump(m.SCRATCH / "protected_hashes.json", protected)


def collect_history(anchors):
    index = []
    for sut, a in anchors.items():
        repo = m.ROOT / a["upstream_clone"]
        # All ref descendants are also screened; the primary outcome is default HEAD.
        desc = m.git(repo, "rev-list", "--reverse", "--all", "--ancestry-path=" + a["commit"], "^" + a["commit"]).decode().splitlines()
        a["all_ref_post_anchor_descendants"] = desc
        a["all_ref_commit_count"] = len(m.git(repo, "rev-list", "--all").splitlines())
        a["head_commit_count"] = len(m.git(repo, "rev-list", "HEAD").splitlines())
        a["ref_tip_metadata"] = m.git(repo, "log", "--all", "--simplify-by-decoration", "--format=%H %D").decode().splitlines()
        rows = []
        for commit in desc:
            meta = m.git(repo, "show", "-s", "--format=%H%n%P%n%aI%n%cI%n%s", commit).decode().splitlines()
            parent = meta[1].split()[0]
            touched = m.git(repo, "diff", "--name-only", parent, commit).decode().splitlines()
            filtered = [p for p in touched if m.relevant(p)]
            patch_path = None
            text_paths = [p for p in filtered if not p.endswith('.sql')]
            if text_paths:
                patch_path = m.OUT / "history_diffs" / sut / (commit + ".diff")
                patch_path.parent.mkdir(parents=True, exist_ok=True)
                patch_path.write_text(m.sanitize(m.git(repo, "diff", "--no-ext-diff", "--no-textconv", "--unified=3", parent, commit, "--", *text_paths).decode(errors="replace")))
            rows.append({"commit": commit, "parent": parent, "author_date": meta[2], "committer_date": meta[3], "message": m.sanitize(meta[4][:160]), "in_default_head": commit in a["post_anchor_reachable_commits"], "files": touched, "selected_files": filtered, "patch": str(patch_path.relative_to(m.ROOT)) if patch_path else None})
        m.dump(m.OUT / (sut + "_all_descendant_history.json"), rows)
        # Save only reviewed source files, as inert text. Line numbers match Git blobs.
        for revision in [a["commit"], a["head"]]:
            tree = m.tree(repo, revision)
            for path in PATHS[sut]:
                if path not in tree:
                    continue
                data = m.git(repo, "show", revision + ":" + path)
                dest = m.OUT / "source_evidence" / sut / revision / (path + ".txt")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(m.sanitize(data.decode(errors="replace")))
                index.append({"sut": sut, "commit": revision, "path": path, "blob": tree[path], "sha256_original": m.sha(data), "line_count": len(data.decode(errors="replace").splitlines()), "copy": str(dest.relative_to(m.ROOT))})
    m.dump(m.OUT / "source_index.json", index)
    m.dump(m.OUT / "anchors.json", anchors)


def semantic_json_deltas(before, after, prefix=""):
    if isinstance(before, dict) and isinstance(after, dict):
        changes = []
        for key in sorted(set(before) | set(after)):
            ptr = prefix + "/" + key.replace("~", "~0").replace("/", "~1")
            if key not in before:
                changes.append({"pointer": ptr, "before_absent": True, "after": after[key]})
            elif key not in after:
                changes.append({"pointer": ptr, "before": before[key], "after_absent": True})
            else:
                changes.extend(semantic_json_deltas(before[key], after[key], ptr))
        return changes
    return [] if before == after else [{"pointer": prefix, "before": before, "after": after}]


def candidates(anchors, items):
    rows = []
    for item_id in ["P014", "P015", "C002"]:
        item = next(i for i in items if i["baseline"]["item_id"] == item_id)
        b = item["baseline"]
        path = re.search(r"(08_experiments/[^;]+/exchanges.jsonl):\d+", item["codex"]["evidence_locators"]).group(1)
        counts = collections.Counter()
        witnesses = []
        for n, line in enumerate((m.ROOT / path).read_text().split("\n"), 1):
            if not line:
                continue
            exchange = json.loads(line)
            req, res = exchange["request"], exchange.get("response") or {}
            reqpath = req.get("path", "").split("?", 1)[0]
            target = b["template"]
            if b["sut"] == "swagger-petstore":
                target = "/api/v3" + target
            if req.get("method") != b["method"] or reqpath != target or str(res.get("status")) != b["status"]:
                continue
            # Never serialize headers, cookie values, or raw request bodies.
            record = {"locator": path + ":" + str(n), "status": res["status"]}
            if item_id in {"P014", "P015"}:
                key = "status" if item_id == "P014" else "tags"
                query = req.get("query", [])
                if isinstance(query, dict):
                    names = list(query)
                    values = query.get(key, [])
                    if not isinstance(values, list):
                        values = [values]
                else:
                    names = [x[0] for x in query]
                    values = [x[1] for x in query if x[0] == key]
                record.update({"parameter": key, "query_parameter_present": key in names, "present_values_all_empty": key in names and bool(values) and all(v == "" for v in values), "response_matches_guard": res.get("body", {}).get("text", "").startswith("No " + key + " provided")})
                counts["parameter_present" if key in names else "parameter_absent"] += 1
            else:
                body = json.loads(req.get("body", {}).get("text", ""))
                is_object = isinstance(body, dict)
                absent = [key for key in ["key", "keyType"] if not is_object or key not in body]
                null = [key for key in ["key", "keyType"] if is_object and key in body and body[key] is None]
                dob_invalid = is_object and "keyDob" in body and body["keyDob"] is not None and (not isinstance(body["keyDob"], str) or re.fullmatch(r"[XxA-Fa-f0-9][A-Fa-f0-9]{63}", body["keyDob"]) is None)
                headers = req.get("headers", [])
                pairs = headers.items() if isinstance(headers, dict) else headers
                illegal = any(any(ord(c) < 32 and c != "\t" or ord(c) == 127 for c in str(v)) for k, v in pairs if k.lower() not in {"authorization", "cookie", "proxy-authorization", "set-cookie"})
                record.update({"absent_required_fields": absent, "null_required_fields": null, "invalid_keyDob_under_new_spec": dob_invalid, "illegal_non_auth_header_control": illegal})
                counts["missing_or_null_required" if absent or null else "required_present_nonnull"] += 1
                counts["absent_required_fields"] += bool(absent)
                counts["null_required_fields"] += bool(null)
                counts["new_spec_required_or_keyDob_rejects"] += bool(absent or null or dob_invalid)
                counts["illegal_non_auth_header_control"] += illegal
                counts["new_spec_rejects_without_illegal_headers"] += bool((absent or null or dob_invalid) and not illegal)
            witnesses.append(record)
        assert len(witnesses) == int(b["occurrences"]), (item_id, len(witnesses))
        rows.append({"item_id": item_id, "counts": dict(counts), "witnesses": witnesses})
    m.dump(m.OUT / "candidate_witnesses.json", rows)
    cwa = anchors["cwa-verification"]
    repo = m.ROOT / cwa["upstream_clone"]
    before = json.loads(m.git(repo, "show", cwa["commit"] + ":api-docs.json"))
    after = json.loads(m.git(repo, "show", cwa["head"] + ":api-docs.json"))
    m.dump(m.OUT / "cwa_spec_semantic_delta.json", semantic_json_deltas(before, after))
    provenance = {}
    for sut, a in anchors.items():
        deployed = (m.ROOT / a["deployed_spec"]).read_bytes()
        if sut == "cwa-verification":
            upstream = m.git(m.ROOT / a["upstream_clone"], "show", a["commit"] + ":api-docs.json")
            provenance[sut] = {"deployed_sha256": m.sha(deployed), "anchor_spec_sha256": m.sha(upstream), "byte_identical": deployed == upstream}
        else:
            provenance[sut] = {"deployed_sha256": m.sha(deployed)}
        item = next(i for i in items if i["baseline"]["sut"] == sut)
        run = re.search(r"(08_experiments/[^;]+/exchanges.jsonl):\d+", item["codex"]["evidence_locators"]).group(1)
        original = m.ROOT / Path(run).parent / "spec.original.json"
        provenance[sut]["baseline_run_spec"] = str(original.relative_to(m.ROOT))
        provenance[sut]["run_spec_semantic_equal"] = json.loads(original.read_bytes()) == json.loads(deployed)
    m.dump(m.OUT / "spec_provenance.json", provenance)
    print(json.dumps({r["item_id"]: r["counts"] for r in rows}, indent=2))


def origin_and_local_audit(anchors):
    origins = {}
    local = {}
    for sut, a in anchors.items():
        repo = m.ROOT / a["upstream_clone"]
        tree = m.tree(repo, a["commit"])
        specs = [p for p in tree if re.search(r"(?i)(openapi|api-docs|swagger)", Path(p).name) and Path(p).suffix in {".yaml", ".yml", ".json"}]
        tokens = []
        for path in PATHS[sut]:
            if path not in tree:
                continue
            for n, line in enumerate(m.git(repo, "show", a["commit"] + ":" + path).decode().splitlines(), 1):
                if any(t in line for t in ["springdoc", "springfox", "Docket(", "@Schema", "@ApiResponse", "swagger-inflector", "swaggerUrl", "@NotNull", "@Pattern"]):
                    tokens.append({"locator": a["commit"] + ":" + path + ":" + str(n), "text": m.sanitize(line.strip())})
        origins[sut] = {"candidate_spec_paths_at_anchor": specs, "generator_markers": tokens}
        selected = []
        for row in json.loads((m.OUT / (sut + "_file_inventory.json")).read_text()):
            if row["state"] == "different":
                path = row["path"]
                before = m.git(repo, "show", a["commit"] + ":" + row["upstream_path"])
                after = (m.ROOT / a["emb_source"] / path).read_bytes()
                # No SQL values or README text are retained, even in diffs.
                selected.append({"path": path, "equal_after_newline_normalization": before.replace(b"\r\n", b"\n") == after.replace(b"\r\n", b"\n"), "upstream_bytes": len(before), "emb_bytes": len(after), "upstream_lf_count": before.count(b"\n"), "emb_lf_count": after.count(b"\n"), "content_saved": path not in {"README.adoc", "market-core/src/main/resources/data.sql"}})
        local[sut] = selected
    m.dump(m.OUT / "spec_origins.json", origins)
    m.dump(m.OUT / "local_modification_audit.json", local)


def main():
    anchors = json.loads((m.OUT / "anchors.json").read_text())
    items = json.loads((m.OUT / "baseline_evidence.json").read_text())
    full_inventory(anchors)
    collect_history(anchors)
    candidates(anchors, items)
    origin_and_local_audit(anchors)


if __name__ == "__main__":
    main()
