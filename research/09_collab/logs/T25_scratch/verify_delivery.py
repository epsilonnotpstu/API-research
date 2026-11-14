"""Retain reviewed source copies and oracle models; no Java/build/network calls."""
import ast
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
E5 = ROOT / "08_experiments/E5_codemut"
sys.path.insert(0, str(E5))
sys.path.insert(0, str(ROOT / "08_experiments/tools"))
import codemut
import conformance


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    catalogue = json.loads((E5 / "sites.json").read_text())
    old = json.loads((OUT / "sites_before.json").read_text())
    assert catalogue["sites"][:-2] == old["sites"]
    assert {k: v for k, v in catalogue.items() if k != "sites"} == {k: v for k, v in old.items() if k != "sites"}
    assert len(catalogue["sites"]) == 22
    # Preserve every original test body. Only fixture storage location changes.
    old_tests = ast.parse((OUT / "test_codemut_before.py").read_text())
    new_tests = ast.parse((E5 / "test_codemut.py").read_text())
    def test_methods(tree):
        return {n.name: ast.dump(n) for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")}
    previous = test_methods(old_tests)
    current = test_methods(new_tests)
    assert all(current[k] == v for k, v in previous.items())
    proof = {}
    for site in catalogue["sites"][-2:]:
        source = codemut.EMB / catalogue["roots"][site["sut"]]
        dest = OUT / "source_proofs" / site["site_id"]
        if not dest.exists():
            manifest = codemut.mutate(source, dest, site["sut"], site["operator"],
                                      catalogue["sites"], site_id=site["site_id"])
        else:
            manifest = json.loads((dest / "manifest.json").read_text())
        original = (source / site["file"]).read_bytes()
        assert original.count(site["before"].encode()) == 1
        assert (dest / "source" / site["file"]).read_bytes() == original.replace(site["before"].encode(), site["after"].encode(), 1)
        assert codemut.inventory(source) == manifest["source_files"]
        actual = codemut.inventory(dest / "source")
        assert codemut.canonical_hash(actual) == manifest["mutated_tree_sha256"]
        assert [p for p in actual if actual[p] != manifest["source_files"][p]] == [site["file"]]
        proof[site["site_id"]] = {
            "manifest": str((dest / "manifest.json").relative_to(ROOT)),
            "patch": str((dest / "patch.diff").relative_to(ROOT)),
            "source_sha256": manifest["source_sha256"],
            "mutated_file_sha256": manifest["mutated_file_sha256"],
            "source_file_count": len(actual), "exact_before_matches": 1,
            "java_compile": "not_run", "runtime": "not_run"}
    # This counterfactual tests the Python oracle, not the Java mutation.
    login_models = []
    witnesses = json.loads((OUT / "petstore_login_witnesses.json").read_text())
    for w in witnesses:
        path = ROOT / w["file"]
        with path.open() as stream:
            exchange = json.loads(next(itertools.islice(stream, w["line"] - 1, None)))
        assert exchange["request"]["method"] == "GET"
        assert exchange["request"]["path"] == "/api/v3/user/login"
        spec = conformance.Spec(json.loads((path.parent / "spec.original.json").read_text()),
                                deploy_origin="http://sut-swagger-petstore:8080")
        modeled = copy.deepcopy(exchange)
        modeled["response"]["status"] = 400
        signals = conformance.check(spec, modeled)
        vr = [s for s in signals if s["kind"] == "VALID_REJECTED"]
        assert len(vr) == 1
        login_models.append({"file": w["file"], "line": w["line"],
                             "modeled_fingerprint": vr[0]["fingerprint"]})
    market_analysis = E5 / "work/market-wrong-status_20261114T114420Z/analysis-s1-default/analysis.json"
    market_run = Path(json.loads(market_analysis.read_text())["control_run"])
    spec = conformance.Spec(json.loads((market_run / "spec.original.json").read_text()),
                            deploy_origin="http://sut-market:8080")
    market_model = None
    for line_no, line in enumerate((market_run / "exchanges.jsonl").open(), 1):
        x = json.loads(line)
        if x["request"]["method"] != "GET" or x["request"]["path"] != "/products" or x["response"]["status"] != 200:
            continue
        try:
            body = json.loads(x["response"]["body"]["text"])
        except (ValueError, KeyError):
            continue
        if not isinstance(body, list) or not body or not all(isinstance(v, dict) and v.get("price") is not None for v in body):
            continue
        modeled = copy.deepcopy(x)
        for product in body:
            del product["price"]
        modeled["response"]["body"]["text"] = json.dumps(body)
        baseline = conformance.check(spec, x)
        signals = conformance.check(spec, modeled)
        missing_price = [s for s in signals if s["kind"] == "RESPONSE_SCHEMA" and s.get("property") == "price" and s.get("keyword") == "required"]
        assert len(missing_price) == len(body)
        market_model = {"file": str((market_run / "exchanges.jsonl").relative_to(ROOT)),
            "line": line_no, "products": len(body), "modeled_missing_price_diagnostics": len(missing_price),
            "baseline_kinds": sorted({s["kind"] for s in baseline}),
            "modeled_required_price_pointers": sorted({s["pointer"] for s in missing_price}),
            "modeled_fingerprint_examples": [s["fingerprint"] for s in missing_price[:2]],
            "note": "Python counterfactual deletion only; no Java/Jackson serialization was executed."}
        break
    assert market_model is not None
    save("oracle_models.json", {"login_counterfactual_400": login_models, "market_counterfactual_price_removal": market_model})
    before = json.loads((OUT / "before_sha256.json").read_text())
    editable = {str((E5 / p).relative_to(ROOT)) for p in ("sites.json", "test_codemut.py", "README.md", "OPERATORS.md")}
    protected = {p: h for p, h in before.items() if p not in editable}
    drift = [p for p, h in protected.items() if sha(ROOT / p) != h]
    assert not drift, drift
    inputs = json.loads((OUT / "input_sha256.json").read_text())
    assert all(sha(ROOT / p) == h for p, h in inputs.items())
    tests = json.loads((OUT / "test_results.json").read_text())
    assert tests["success"] and tests["tests"] == 124 and tests["skipped"] == 0
    save("verification.json", {"catalogue_entries": 22, "old_entries_preserved": 20,
        "original_test_methods_preserved": len(previous), "new_test_methods": len(current) - len(previous),
        "codemut_py_unchanged": True, "protected_files_unchanged": len(protected),
        "selection_input_hashes_unchanged": len(inputs), "tests": tests,
        "source_proofs": proof, "oracle_model_only": True,
        "market_model": market_model, "login_model_requests": len(login_models),
        "external_code_execution": False})
    print(json.dumps({"old_sites_preserved": 20, "test_methods_preserved": len(previous),
        "protected_unchanged": len(protected), "input_hashes_unchanged": len(inputs), "tests": tests}))


if __name__ == "__main__":
    main()
