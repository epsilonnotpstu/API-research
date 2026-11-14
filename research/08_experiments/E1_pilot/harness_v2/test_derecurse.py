"""Standard-library regression tests; no generator, Docker, or SUT execution."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
MODULE_SPEC = importlib.util.spec_from_file_location("derecurse_v2", HERE / "derecurse.py")
MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(MODULE)
derecurse = MODULE.derecurse


def schema_spec(group, oas3=False):
    header = {"openapi": "3.0.4", "components": {"schemas": group}} if oas3 else {
        "swagger": "2.0", "definitions": group}
    header["paths"] = {"/things": {"get": {"responses": {"200": {"description": "OK"}}}}}
    return header


class DerecurseTests(unittest.TestCase):
    def assert_stable(self, original, expected_cuts):
        snapshot = copy.deepcopy(original)
        output, cuts = derecurse(original)
        self.assertEqual(original, snapshot, "caller document was modified")
        self.assertEqual(len(cuts), expected_cuts)
        self.assertEqual(output["paths"], original["paths"])
        again, again_cuts = derecurse(output)
        self.assertEqual(again, output)
        self.assertEqual(again_cuts, [], "a supported cycle remains")
        self.assertEqual(derecurse(original), (output, cuts), "nondeterministic output")
        return output, cuts

    def test_swagger_self_cycle(self):
        source = schema_spec({"Node": {"type": "object", "properties": {
            "next": {"$ref": "#/definitions/Node"}}}})
        output, cuts = self.assert_stable(source, 1)
        self.assertEqual(cuts[0]["in"], "#/definitions/Node/properties/next")
        self.assertEqual(output["definitions"]["Node"]["properties"]["next"], {
            "type": "object", "x-derecursed-from": "#/definitions/Node"})

    def test_oas3_mutual_cycle(self):
        output, cuts = self.assert_stable(schema_spec({
            "A": {"properties": {"b": {"$ref": "#/components/schemas/B"}}},
            "B": {"properties": {"a": {"$ref": "#/components/schemas/A"}}},
        }, True), 1)
        self.assertEqual(cuts[0]["ref"], "#/components/schemas/A")
        self.assertEqual(output["components"]["schemas"]["A"]["properties"]["b"], {
            "$ref": "#/components/schemas/B"})

    def test_three_node_cycle_in_array_and_composition(self):
        self.assert_stable(schema_spec({
            "A": {"allOf": [{"$ref": "#/components/schemas/B"}]},
            "B": {"type": "array", "items": {"$ref": "#/components/schemas/C"}},
            "C": {"additionalProperties": {"$ref": "#/components/schemas/A"}},
        }, True), 1)

    def test_acyclic_shared_reference_is_unchanged(self):
        source = schema_spec({
            "A": {"allOf": [{"$ref": "#/definitions/Leaf"}, {"$ref": "#/definitions/Leaf"}]},
            "B": {"$ref": "#/definitions/Leaf"}, "Leaf": {"type": "string"},
        })
        output, _ = self.assert_stable(source, 0)
        self.assertEqual(output, source)

    def test_escaped_schema_names(self):
        _, cuts = self.assert_stable(schema_spec({"A/B~C": {"$ref": "#/components/schemas/A~1B~0C"}}, True), 1)
        self.assertEqual(cuts[0]["in"], "#/components/schemas/A~1B~0C")

    def test_both_schema_namespaces_are_processed(self):
        source = schema_spec({"Node": {"$ref": "#/definitions/Node"}}, True)
        source["definitions"] = {"Node": {"$ref": "#/definitions/Node"}}
        # The OAS schema points across namespaces; only the real back edge is cut.
        output, _ = self.assert_stable(source, 1)
        self.assertEqual(output["components"]["schemas"]["Node"], {"$ref": "#/definitions/Node"})

    def test_equal_basenames_do_not_alias(self):
        source = schema_spec({"Node": {"properties": {
            "parameter": {"$ref": "#/components/parameters/Node"}}}}, True)
        source["components"]["parameters"] = {"Node": {"name": "q", "in": "query"}}
        self.assertEqual(self.assert_stable(source, 0)[0], source)

    def test_independent_cycles_in_both_namespaces(self):
        source = schema_spec({"Node": {"$ref": "#/components/schemas/Node"}}, True)
        source["definitions"] = {"Node": {"$ref": "#/definitions/Node"}}
        self.assert_stable(source, 2)

    def test_external_and_dangling_refs_are_untouched(self):
        source = schema_spec({"Node": {"allOf": [
            {"$ref": "other.json#/definitions/Node"}, {"$ref": "#/definitions/Absent"}]}})
        self.assertEqual(self.assert_stable(source, 0)[0], source)

    def test_schema_ref_siblings_are_walked(self):
        source = schema_spec({"A": {"$ref": "#/components/schemas/B", "properties": {
            "next": {"$ref": "#/components/schemas/A"}}}, "B": {"type": "object"}}, True)
        _, cuts = self.assert_stable(source, 1)
        self.assertEqual(cuts[0]["in"], "#/components/schemas/A/properties/next")

    def test_independent_cycles(self):
        self.assert_stable(schema_spec({
            "A": {"$ref": "#/definitions/A"}, "B": {"$ref": "#/definitions/B"}}), 2)

    def test_spec_without_schema_components(self):
        source = {"openapi": "3.0.4", "paths": {}}
        self.assertEqual(self.assert_stable(source, 0)[0], source)

    def test_actual_sut_documents_static_transform(self):
        emb = HERE.parents[1] / "_external" / "emb"
        for sut in ("scout-api", "swagger-petstore", "market"):
            with self.subTest(sut=sut):
                source = json.loads((emb / "openapi-swagger" / f"{sut}.json").read_text())
                output, cuts = derecurse(source)
                self.assert_stable(source, len(cuts))
                self.assertEqual(output["paths"], source["paths"])
                if sut == "scout-api":
                    self.assertGreater(len(cuts), 0, "scout regression fixture lost its cycles")


if __name__ == "__main__":
    unittest.main(verbosity=2)
