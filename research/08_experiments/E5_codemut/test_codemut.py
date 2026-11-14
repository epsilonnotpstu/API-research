"""Synthetic safety fixtures and read-only pinned-source copies; no Java execution."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRATCH = Path(os.environ.get('E5_TEST_SCRATCH', str(HERE.parent.parent / '09_collab/logs/T25_scratch')))
SPEC = importlib.util.spec_from_file_location("codemut_under_test", HERE / "codemut.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CodeMutationTests(unittest.TestCase):
    def setUp(self):
        # Keep temporary copies inside the explicitly assigned test scratch path.
        self.temp = tempfile.TemporaryDirectory(prefix=".test-", dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "original"
        (self.source / "src").mkdir(parents=True)
        self.text = ("class Handler {\n"
                     "  Object create(@Valid Object body) { return body; }\n"
                     "  int status() { return 201; }\n"
                     "  int length(String x) { if (x == null) return 0; return x.length(); }\n"
                     "  public String getName() { return name; }\n"
                     "  int read(int id) { return id; }\n"
                     "}\n")
        (self.source / "src/Handler.java").write_text(self.text)
        (self.source / "pom.xml").write_text("<project/>\n")
        self.sites = [
            self.site("validate", "DROP_VALIDATION", "@Valid Object body", "Object body", "I-ACCEPT-INVALID", ["INVALID_ACCEPTED"]),
            self.site("status", "WRONG_STATUS", "return 201;", "return 418;", "I-RESP-CONTRACT", ["UNDOCUMENTED_STATUS"]),
            self.site("null", "DROP_NULL_CHECK", "if (x == null) return 0; ", "", "I-CRASH", ["SERVER_ERROR"]),
            self.site("field", "RESP_FIELD", "public String getName()", "public String getRenamedName()", "I-RESP-CONTRACT", ["RESPONSE_SCHEMA"]),
            self.site("reject", "REJECT_VALID", "return id;", "if (id > 1) throw new BadRequest(); return id;", "I-REJECT-VALID", ["VALID_REJECTED"]),
        ]

    def site(self, sid, operator, before, after, l2, signals):
        return {"site_id": sid, "sut": "scout-api", "operator": operator, "file": "src/Handler.java",
                "line": self.text[:self.text.index(before)].count("\n") + 1,
                "before": before, "after": after, "source_sha256": hashlib.sha256(self.text.encode()).hexdigest(),
                "expected_L1": "IMPL", "expected_L2": l2, "expected_conformance_signal": signals,
                "operations": [{"path": "/things", "method": "post"}]}

    def apply(self, site, name="out", sites=None, seed=1):
        return MODULE.mutate(self.source, self.root / name, "scout-api", site["operator"],
                             sites or self.sites, seed, site["site_id"])

    def test_each_operator_changes_only_copy_and_emits_complete_manifest(self):
        for index, site in enumerate(self.sites):
            with self.subTest(operator=site["operator"]):
                out = self.root / f"out{index}"
                manifest = self.apply(site, out.name)
                self.assertEqual((self.source / "src/Handler.java").read_text(), self.text)
                self.assertEqual((out / "source/src/Handler.java").read_text(), self.text.replace(site["before"], site["after"], 1))
                self.assertEqual((out / "source/pom.xml").read_bytes(), (self.source / "pom.xml").read_bytes())
                self.assertEqual(json.loads((out / "manifest.json").read_text()), manifest)
                self.assertEqual(manifest["source_sha256"], hashlib.sha256(self.text.encode()).hexdigest())
                self.assertEqual(manifest["expected_L1"], "IMPL")
                self.assertEqual(manifest["catalogue_sha256"], MODULE.canonical_hash(self.sites))
                self.assertEqual(manifest["catalogue_site_sha256"], MODULE.canonical_hash(site))
                self.assertTrue(manifest["explicit_site"])
                self.assertEqual(manifest["candidate_site_ids"], [site["site_id"]])
                if site["operator"] == "DROP_VALIDATION":
                    self.assertEqual(manifest["expected_L2_by_signal"]["SERVER_ERROR"], "I-CRASH")
                self.assertFalse(manifest["validation"]["fault_observed"])
                self.assertEqual(manifest["validation"]["java_compile"], "not_run")
                self.assertEqual(manifest["mutations"][0]["fault"], site["operator"])
                self.assertTrue((out / "patch.diff").read_text().startswith("--- a/src/Handler.java\n+++ b/src/Handler.java\n"))
                self.assertEqual(manifest["patch_sha256"], hashlib.sha256((out / "patch.diff").read_bytes()).hexdigest())
                self.assertNotEqual(manifest["source_tree_sha256"], manifest["mutated_tree_sha256"])

    def test_seeded_selection_is_order_independent_and_explicit_site_wins(self):
        first = self.sites[1]
        second = self.site("status-other", "WRONG_STATUS", "return id;", "return 418;", "I-RESP-CONTRACT", ["UNDOCUMENTED_STATUS"])
        pool = [first, second]
        chosen = MODULE.select_site(pool, "scout-api", "WRONG_STATUS", 17)
        self.assertEqual(chosen, MODULE.select_site(pool[::-1], "scout-api", "WRONG_STATUS", 17))
        self.assertEqual(MODULE.select_site(pool, "scout-api", "WRONG_STATUS", 17, second["site_id"]), second)
        self.assertEqual({MODULE.select_site(pool, "scout-api", "WRONG_STATUS", seed)["site_id"] for seed in range(20)}, {first["site_id"], second["site_id"]})

    def test_repeated_invocations_have_identical_patch_and_manifest(self):
        first = self.apply(self.sites[1], "one")
        second = self.apply(self.sites[1], "two")
        self.assertEqual(first, second)
        self.assertEqual((self.root / "one/patch.diff").read_bytes(), (self.root / "two/patch.diff").read_bytes())

    def test_existing_output_is_never_overwritten(self):
        self.apply(self.sites[1])
        existing = (self.root / "out/manifest.json").read_bytes()
        with self.assertRaises(MODULE.MutationError): self.apply(self.sites[1])
        self.assertEqual((self.root / "out/manifest.json").read_bytes(), existing)

    def test_output_may_not_overlap_source_in_either_direction(self):
        for out in (self.source, self.source / "inside", self.root):
            with self.subTest(out=out), self.assertRaises(MODULE.MutationError):
                MODULE.mutate(self.source, out, "scout-api", "WRONG_STATUS", self.sites)

    def test_output_cannot_be_in_any_protected_emb_subtree(self):
        original = MODULE.EMB
        MODULE.EMB = self.root / "protected-emb"
        self.addCleanup(setattr, MODULE, "EMB", original)
        with self.assertRaises(MODULE.MutationError):
            MODULE.mutate(self.source, MODULE.EMB / "other-sut/out", "scout-api", "WRONG_STATUS", self.sites)
        self.assertFalse(MODULE.EMB.exists())

    def test_symlink_output_and_escaping_source_links_are_rejected(self):
        (self.root / "out").symlink_to(self.root / "missing", target_is_directory=True)
        with self.assertRaises(MODULE.MutationError): self.apply(self.sites[1])
        (self.root / "out").unlink()
        (self.source / "src/escape.java").symlink_to(self.root / "outside.java")
        with self.assertRaises(MODULE.MutationError): self.apply(self.sites[1])
        self.assertFalse((self.root / "out").exists())

    def test_symlink_directories_are_rejected(self):
        (self.source / "linked").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(MODULE.MutationError): self.apply(self.sites[1])

    def test_build_outputs_and_vcs_are_excluded(self):
        for directory in ("target", ".git", "node_modules", "__pycache__"):
            (self.source / directory).mkdir()
            (self.source / directory / "cached").write_text("not source")
        manifest = self.apply(self.sites[1])
        self.assertEqual(set(manifest["source_files"]), {"src/Handler.java", "pom.xml"})
        self.assertFalse((self.root / "out/source/target").exists())

    def test_preserves_executable_mode_and_resource_bytes(self):
        (self.source / "mvnw").write_bytes(b"#!/bin/sh\nexit 0\n")
        (self.source / "mvnw").chmod(0o755)
        (self.source / "data.bin").write_bytes(bytes(range(256)))
        self.apply(self.sites[1])
        self.assertEqual((self.root / "out/source/mvnw").stat().st_mode & 0o777, 0o755)
        self.assertEqual((self.root / "out/source/data.bin").read_bytes(), bytes(range(256)))

    def test_file_digest_drift_fails_before_output_creation(self):
        (self.source / "src/Handler.java").write_text(self.text + "// changed\n")
        with self.assertRaisesRegex(MODULE.MutationError, "digest"): self.apply(self.sites[1])
        self.assertFalse((self.root / "out").exists())

    def test_pinned_line_mismatch_is_rejected(self):
        sites = copy.deepcopy(self.sites); sites[1]["line"] += 1
        with self.assertRaisesRegex(MODULE.MutationError, "line"): self.apply(sites[1], sites=sites)

    def test_ambiguous_anchor_is_rejected_even_when_hash_matches(self):
        text = self.text.replace("return id;", "return 201;")
        (self.source / "src/Handler.java").write_text(text)
        sites = copy.deepcopy(self.sites); sites[1]["source_sha256"] = hashlib.sha256(text.encode()).hexdigest()
        with self.assertRaisesRegex(MODULE.MutationError, "exactly once"): self.apply(sites[1], sites=sites)

    def test_missing_anchor_is_rejected(self):
        sites = copy.deepcopy(self.sites); sites[1]["before"] = "does not exist"
        with self.assertRaisesRegex(MODULE.MutationError, "exactly once"): self.apply(sites[1], sites=sites)

    def test_path_traversal_absolute_windows_and_excluded_paths_rejected(self):
        for path in ("../evil.java", "/tmp/evil.java", "src/../evil.java", "src\\evil.java", "target/A.java", "src//A.java"):
            sites = copy.deepcopy(self.sites); sites[1]["file"] = path
            with self.subTest(path=path), self.assertRaises(MODULE.MutationError): self.apply(sites[1], sites=sites)
        self.assertFalse((self.root / "out").exists())

    def test_explicit_site_must_match_operator_and_sut(self):
        with self.assertRaises(MODULE.MutationError):
            MODULE.mutate(self.source, self.root / "out", "scout-api", "WRONG_STATUS", self.sites, site_id="validate")
        with self.assertRaises(MODULE.MutationError):
            MODULE.select_site(self.sites, "market", "WRONG_STATUS", 1)

    def test_duplicate_site_ids_invalid_labels_and_unknown_signals_fail_closed(self):
        cases = []
        duplicate = copy.deepcopy(self.sites); duplicate.append(copy.deepcopy(duplicate[0])); cases.append(duplicate)
        for key, value in (("expected_L1", "SPEC"), ("expected_L2", "I-CRASH"), ("expected_conformance_signal", ["INVENTED"]), ("line", 0), ("before", ""), ("operations", [])):
            sites = copy.deepcopy(self.sites); sites[1][key] = value; cases.append(sites)
        for sites in cases:
            with self.subTest(sites=sites[1]["expected_L2"]), self.assertRaises(MODULE.MutationError): MODULE.validate_sites(sites)

    def test_negative_seed_and_noop_edit_are_rejected(self):
        with self.assertRaises(MODULE.MutationError): MODULE.select_site(self.sites, "scout-api", "WRONG_STATUS", -1)
        sites = copy.deepcopy(self.sites); sites[1]["after"] = sites[1]["before"]
        with self.assertRaises(MODULE.MutationError): self.apply(sites[1], sites=sites)

    def test_no_final_newline_and_crlf_are_preserved_in_copy(self):
        for index, text in enumerate((self.text.rstrip("\n"), self.text.replace("\n", "\r\n"))):
            (self.source / "src/Handler.java").write_bytes(text.encode())
            sites = copy.deepcopy(self.sites); sites[1]["source_sha256"] = hashlib.sha256(text.encode()).hexdigest()
            manifest = self.apply(sites[1], f"format{index}", sites)
            result = (self.root / f"format{index}/source/src/Handler.java").read_bytes()
            self.assertEqual(result, text.replace("return 201;", "return 418;", 1).encode())
            self.assertEqual(manifest["line"], 3)

    def test_diff_marks_changed_line_without_final_newline(self):
        diff = MODULE.patch_text(b"class A {}", b"class B {}", "A.java")
        self.assertIn("-class A {}\n\\ No newline at end of file\n", diff)
        self.assertIn("+class B {}\n\\ No newline at end of file\n", diff)

    def test_shared_response_field_records_every_affected_operation(self):
        sites = copy.deepcopy(self.sites)
        sites[3]["operations"].append({"path": "/other", "method": "get"})
        manifest = self.apply(sites[3], sites=sites)
        self.assertEqual(manifest["operations_mutated"], 2)
        self.assertEqual({(m["path"], m["method"]) for m in manifest["mutations"]}, {("/things", "post"), ("/other", "get")})

    def test_cli_uses_json_catalogue_and_creates_output_without_execution(self):
        catalogue = self.root / "sites.json"
        catalogue.write_text(json.dumps({"sites": self.sites}))
        result = subprocess.run(["/usr/bin/python3", "-I", "-B", str(HERE / "codemut.py"),
                                 "--sut", "scout-api", "--operator", "WRONG_STATUS", "--site", "status",
                                 "--source", str(self.source), "--catalog", str(catalogue), "--out", str(self.root / "cli")],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["execution"], "not_run")
        self.assertTrue((self.root / "cli/patch.diff").exists())


class ReplacementSiteTests(unittest.TestCase):
    """Exercise the shipped v2 entries against the original checkout bytes."""

    IDS = ("market-response-field-v2", "petstore-reject-valid-v2")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="v2-site-", dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalogue = json.loads((HERE / "sites.json").read_text())
        self.sites = self.catalogue["sites"]
        self.selected = {s["site_id"]: s for s in self.sites if s["site_id"] in self.IDS}
        self.assertEqual(set(self.selected), set(self.IDS))

    def source(self, site):
        return MODULE.EMB / self.catalogue["roots"][site["sut"]]

    def mutate(self, source, output, site):
        return MODULE.mutate(source, output, site["sut"], site["operator"],
                             self.sites, site_id=site["site_id"])

    def verify_copy(self, site_id):
        site = self.selected[site_id]
        source = self.source(site)
        original = (source / site["file"]).read_bytes()
        before_inventory = MODULE.inventory(source)
        self.assertEqual(hashlib.sha256(original).hexdigest(), site["source_sha256"])
        self.assertEqual(original.count(site["before"].encode()), 1)
        self.assertEqual(original[:original.index(site["before"].encode())].count(b"\n") + 1, site["line"])
        out = self.root / "copy"
        manifest = self.mutate(source, out, site)
        expected = original.replace(site["before"].encode(), site["after"].encode(), 1)
        self.assertEqual((out / "source" / site["file"]).read_bytes(), expected)
        self.assertEqual(MODULE.inventory(source), before_inventory)
        after_inventory = MODULE.inventory(out / "source")
        self.assertEqual(set(after_inventory), set(before_inventory))
        self.assertEqual([p for p in before_inventory if before_inventory[p] != after_inventory[p]], [site["file"]])
        self.assertEqual(manifest["site_id"], site_id)
        self.assertEqual(manifest["source_sha256"], site["source_sha256"])
        self.assertEqual(manifest["mutated_file_sha256"], hashlib.sha256(expected).hexdigest())
        self.assertEqual(manifest["operations"], site["operations"])
        self.assertEqual(manifest["expected_conformance_signal"], site["expected_conformance_signal"])
        self.assertEqual(manifest["validation"]["java_compile"], "not_run")
        self.assertFalse(manifest["validation"]["fault_observed"])
        return out

    def test_market_v2_applies_once_to_original_tree_copy(self):
        self.verify_copy("market-response-field-v2")

    def test_petstore_v2_applies_once_to_original_tree_copy(self):
        self.verify_copy("petstore-reject-valid-v2")

    def test_v2_requires_all_catalogue_fields_and_explicit_selection(self):
        fields = set(self.sites[0])
        MODULE.validate_sites(self.sites)
        for site in self.selected.values():
            with self.subTest(site=site["site_id"]):
                self.assertEqual(set(site), fields)
                self.assertTrue(site["pilot"])
                self.assertEqual(MODULE.select_site(self.sites, site["sut"], site["operator"], 1, site["site_id"]), site)
                self.assertTrue(site["conditions"] and site["witness_plan"] and site["evidence"])

    def test_v2_source_digest_drift_refused_before_copy(self):
        for site in self.selected.values():
            with self.subTest(site=site["site_id"]):
                source = self.root / site["site_id"]
                file = source / site["file"]
                file.parent.mkdir(parents=True)
                file.write_bytes((self.source(site) / site["file"]).read_bytes() + b"\n// source drift\n")
                out = self.root / (site["site_id"] + "-out")
                with self.assertRaisesRegex(MODULE.MutationError, "digest"):
                    self.mutate(source, out, site)
                self.assertFalse(out.exists())

    def test_v2_ambiguous_anchor_refused_even_with_matching_digest(self):
        for original_site in self.selected.values():
            with self.subTest(site=original_site["site_id"]):
                site = copy.deepcopy(original_site)
                data = (self.source(site) / site["file"]).read_bytes() + b"\n" + site["before"].encode()
                site["source_sha256"] = hashlib.sha256(data).hexdigest()
                with self.assertRaisesRegex(MODULE.MutationError, "exactly once"):
                    MODULE.edit_bytes(data, site)

    def test_v2_missing_anchor_refused_even_with_matching_digest(self):
        for original_site in self.selected.values():
            with self.subTest(site=original_site["site_id"]):
                site = copy.deepcopy(original_site)
                data = (self.source(site) / site["file"]).read_bytes().replace(site["before"].encode(), b"// removed anchor", 1)
                site["source_sha256"] = hashlib.sha256(data).hexdigest()
                with self.assertRaisesRegex(MODULE.MutationError, "exactly once"):
                    MODULE.edit_bytes(data, site)

    def test_v2_existing_output_and_second_application_refused(self):
        for site in self.selected.values():
            with self.subTest(site=site["site_id"]):
                out = self.root / site["site_id"]
                self.mutate(self.source(site), out, site)
                frozen = (out / "manifest.json").read_bytes()
                with self.assertRaisesRegex(MODULE.MutationError, "must not exist"):
                    self.mutate(self.source(site), out, site)
                self.assertEqual((out / "manifest.json").read_bytes(), frozen)
                second = self.root / (site["site_id"] + "-second")
                with self.assertRaisesRegex(MODULE.MutationError, "digest"):
                    self.mutate(out / "source", second, site)
                self.assertFalse(second.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
