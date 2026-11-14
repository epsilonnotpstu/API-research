"""Check append-only catalogue/report, source proof, retained tests and input hashes."""
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
E5 = ROOT / "08_experiments/E5_codemut"
sys.path.insert(0, str(E5))
import codemut


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def methods(text):
    return {node.name: ast.dump(node) for node in ast.walk(ast.parse(text))
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}


previous_bytes = (OUT / "before_sites.json").read_bytes()
previous = json.loads(previous_bytes)
current_bytes = (E5 / "sites.json").read_bytes()
current = json.loads(current_bytes)
assert len(previous["sites"]) == 22 and len(current["sites"]) == 23
assert current["sites"][:-1] == previous["sites"]
assert current_bytes.startswith(previous_bytes.removesuffix(b"\n  ]\n}\n") + b",\n")
assert {k: v for k, v in current.items() if k != "sites"} == {k: v for k, v in previous.items() if k != "sites"}
codemut.validate_sites(current["sites"])
site = current["sites"][-1]
assert site["site_id"] == "petstore-reject-valid-v3"
assert set(site) == set(previous["sites"][-1]) and site["pilot"] is True
old_methods = methods((OUT / "before_test_codemut.py").read_text())
new_methods = methods((E5 / "test_codemut.py").read_text())
assert all(new_methods.get(name) == body for name, body in old_methods.items())
assert len(new_methods) == len(old_methods) + 2
source = codemut.EMB / current["roots"][site["sut"]]
proof = OUT / "v3-source-proof"
manifest = json.loads((proof / "manifest.json").read_text())
original = (source / site["file"]).read_bytes()
assert sha(source / site["file"]) == site["source_sha256"]
assert original.count(site["before"].encode()) == 1
expected = original.replace(site["before"].encode(), site["after"].encode(), 1)
assert (proof / "source" / site["file"]).read_bytes() == expected
assert codemut.inventory(source) == manifest["source_files"]
actual = codemut.inventory(proof / "source")
assert codemut.canonical_hash(actual) == manifest["mutated_tree_sha256"]
assert set(actual) == set(manifest["source_files"])
assert [p for p in actual if actual[p] != manifest["source_files"][p]] == [site["file"]]
report = ROOT / "09_collab/reports/T25_report.md"
assert report.read_bytes().startswith((OUT / "before_T25_report.md").read_bytes())
assert b"T25b" in report.read_bytes()[len((OUT / "before_T25_report.md").read_bytes()):]
protected = json.loads((OUT / "protected_before.json").read_text())
inputs = json.loads((OUT / "v2_input_hashes.json").read_text())
assert all(sha(ROOT / p) == digest for p, digest in protected.items())
assert all(sha(ROOT / p) == digest for p, digest in inputs.items())
tests = json.loads((OUT / "test_results.json").read_text())
assert tests == {"tests": 126, "failures": 0, "errors": 0, "skips": 0, "success": True}
result = {"old_entries_preserved": 22, "v2_entry_unchanged": True, "catalogue_entries": 23,
          "previous_test_methods_preserved": len(old_methods), "new_test_methods": 2, "tests": tests,
          "old_report_preserved_as_byte_prefix": True, "codemut_unchanged": True,
          "protected_files_unchanged": len(protected), "v2_evidence_hashes_unchanged": len(inputs),
          "source_sha256": site["source_sha256"], "exact_before_matches": 1,
          "retained_source_files": len(actual), "changed_files": [site["file"]],
          "mutated_file_sha256": sha(proof / "source" / site["file"]),
          "java_compile": "not_run", "sut_execution": "not_run"}
(OUT / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
