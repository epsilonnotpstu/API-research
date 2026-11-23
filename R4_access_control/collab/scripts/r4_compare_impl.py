"""R4 D1 safeguard: compare Claude's pipeline outputs (mining/*.json written by mining/claude/r4p.py) with Codex's independent
implementation run into a scratch directory. Compares eligible pool (item set; repo, fix, parent; mechanical fields), exclusion
counts and sample. Prints differences as ids/field names only (never advisory text).
Run from R4_access_control/: /usr/bin/python3 -I -B collab/scripts/r4_compare_impl.py <codex_output_dir>"""
import json, sys
from pathlib import Path

B = Path(__file__).resolve().parents[2]; M = B / 'mining'
FIELDS = ('repo', 'fix_sha', 'parent_sha', 'fix_lines', 'fix_touches_contract', 'fix_touches_annotation', 'fix_silent', 'test_in_fix', 'language')


def load_pool(p):
    items = json.load(open(p))
    out = {}
    for it in items:
        ids = it.get('ghsa_ids') or [it.get('ghsa_id')]
        out[sorted(ids)[0]] = it
    return out


def main():
    X = Path(sys.argv[1]); diffs = 0
    a, b = load_pool(M / 'pool.json'), load_pool(X / 'pool.json')
    only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    print(f'pool: claude {len(a)}  codex {len(b)}  only-claude {len(only_a)} {only_a[:10]}  only-codex {len(only_b)} {only_b[:10]}')
    diffs += len(only_a) + len(only_b)
    for k in sorted(set(a) & set(b)):
        for f in FIELDS:
            va, vb = a[k].get(f), b[k].get(f)
            if isinstance(va, str) and isinstance(vb, str) and f == 'repo': va, vb = va.lower(), vb.lower()
            if va != vb and not (f in ('fix_touches_contract', 'fix_touches_annotation', 'fix_silent', 'test_in_fix') and str(va).lower() == str(vb).lower()):
                print(f'  field {k} {f}: claude={va!r} codex={vb!r}'); diffs += 1
        if sorted(a[k].get('ghsa_ids', [])) != sorted(b[k].get('ghsa_ids', [b[k].get('ghsa_id')])):
            print(f'  ghsa set {k} differs'); diffs += 1
    ia, ib = json.load(open(M / 'pool_inventory.json')), json.load(open(X / 'pool_inventory.json'))
    ea = ia.get('exclusions', ia); eb = ib.get('exclusions', ib.get('exclusion_counts', ib))
    print('exclusions claude:', ea); print('exclusions codex :', eb)
    if (X / 'sample.json').exists():
        sa = sorted(sorted(i.get('ghsa_ids') or [i.get('ghsa_id')])[0] for i in json.load(open(M / 'sample.json')))
        sb = sorted(sorted(i.get('ghsa_ids') or [i.get('ghsa_id')])[0] for i in json.load(open(X / 'sample.json')))
        print(f'sample: equal={sa == sb} claude {len(sa)} codex {len(sb)}'); diffs += sa != sb
    print('TOTAL DIFFERENCES:', diffs)


if __name__ == '__main__':
    main()
