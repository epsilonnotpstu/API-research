"""Cut schema-reference DFS back edges in a COPY used only for generation.

Supports Swagger definitions and OpenAPI components/schemas, including both
namespaces in one document and escaped schema names. External refs and refs to
non-schema components are left intact. Conformance must use the original spec.
"""
import copy
import json
from pathlib import Path
import sys


def escape(value):
    return str(value).replace("~", "~0").replace("/", "~1")


def derecurse(document):
    spec = copy.deepcopy(document)
    schemas = {}
    for prefix, group in (
        ("#/definitions/", spec.get("definitions", {})),
        ("#/components/schemas/", spec.get("components", {}).get("schemas", {})),
    ):
        for name, schema in group.items():
            schemas[prefix + escape(name)] = schema
    state, cuts = {}, []

    def walk(node, location):
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref in schemas:
                if state.get(ref) == "active":
                    # Preserve the existing harness's object replacement policy.
                    node.clear()
                    node.update({"type": "object", "x-derecursed-from": ref})
                    cuts.append({"in": location, "ref": ref})
                    return
                visit(ref)
            # Siblings can themselves contain recursive refs (notably OAS 3.1).
            for key, value in node.items():
                walk(value, location + "/" + escape(key))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, location + "/" + str(index))

    def visit(ref):
        if state.get(ref) == "done":
            return
        state[ref] = "active"
        walk(schemas[ref], ref)
        state[ref] = "done"

    for ref in sorted(schemas):
        visit(ref)
    return spec, cuts


def main(src, dst):
    result, cuts = derecurse(json.loads(Path(src).read_text(encoding="utf-8")))
    # Exclusive creation prevents accidental replacement of a generator snapshot.
    with Path(dst).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(cuts))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: derecurse.py IN.json OUT.json")
    main(*sys.argv[1:])
