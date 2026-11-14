"""Break $ref cycles in a Swagger 2.0 / OpenAPI 3 spec for the *generator input only*.

Recursive schemas (e.g. scout-api: Activity <-> ActivityProperties) make
Schemathesis/hypothesis-jsonschema data generation stall for minutes per
operation. A back-edge $ref found by DFS over the definitions is replaced with
an unconstrained object. Conformance checking always uses the untouched spec.

Usage: python3 derecurse.py IN.json OUT.json   (prints the cut edges as JSON)
"""
import json
import sys


def main(src, dst):
    spec = json.load(open(src, encoding='utf-8'))
    defs = spec.get('definitions') or spec.get('components', {}).get('schemas') or {}
    cuts = []

    def walk(node, stack, where):
        if isinstance(node, dict):
            ref = node.get('$ref')
            if isinstance(ref, str) and ref.startswith('#/'):
                name = ref.rsplit('/', 1)[-1]
                if name in stack:  # back edge: cut here
                    node.clear()
                    node.update({'type': 'object', 'x-derecursed-from': ref})
                    cuts.append({'in': where, 'ref': ref})
                return
            for key, value in node.items():
                walk(value, stack, where)
        elif isinstance(node, list):
            for value in node:
                walk(value, stack, where)

    def visit(name, stack):
        walk(defs[name], stack + [name], name)
        # descend into remaining (non-cut) refs
        for ref_name in sorted(refs(defs[name])):
            if ref_name in defs and ref_name not in stack + [name]:
                visit(ref_name, stack + [name])

    def refs(node, acc=None):
        acc = set() if acc is None else acc
        if isinstance(node, dict):
            if isinstance(node.get('$ref'), str):
                acc.add(node['$ref'].rsplit('/', 1)[-1])
            for value in node.values():
                refs(value, acc)
        elif isinstance(node, list):
            for value in node:
                refs(value, acc)
        return acc

    for name in sorted(defs):
        visit(name, [])
    json.dump(spec, open(dst, 'w', encoding='utf-8'), indent=2)
    print(json.dumps(cuts))


if __name__ == '__main__':
    main(*sys.argv[1:3])
