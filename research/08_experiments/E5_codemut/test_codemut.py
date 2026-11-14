"""Synthetic Java fixtures only; no real SUT copies, compilers, or builds."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("codemut_under_test", HERE / "codemut.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CodeMutationTests(unittest.TestCase):
    def setUp(self):
        # All test writes remain within the task's allowed E5 directory.
        self.temp = tempfile.TemporaryDirectory(prefix=".test-", dir=HERE)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
