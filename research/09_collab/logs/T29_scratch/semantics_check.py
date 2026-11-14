"""Small offline semantic/cache checks with fake exchanges; no raw run scans."""
import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RESULTS = ROOT / '08_experiments/E1_pilot/pilot_results'
sys.path.insert(0, str(RESULTS))
import fuzzer_compare as fc
import fuzzer_noise_cross_seed as fn
import noise_floor_spec as nf
import attribute


def v(fp, method='GET', path='/p'):
    return dict(fingerprint=fp, kind='SERVER_ERROR', method=method, template=path, status=500, pointer='')


def main():
    manifest = {'mutations': [dict(method='get', path='/p', fault='REQUEST_LOOSE', expected_L1='SPEC', expected_L2='S-REQ-LOOSE')]}
    before = [v('newlater')]*0 + [v('up')]*2 + [v('down')]*3 + [v('gone')]
    after = [v('newlater')]*4 + [v('up')]*3 + [v('down')]*2
    attributed = attribute.attribute(before, after, manifest)
    got, old = fc.counts(attributed), nf.counts(attributed)
    assert all(got[k] == 1 for k in ('mut_NEW', 'mut_INCREASED', 'mut_DECREASED'))
    assert old['mut_VANISHED'] == 1 and got['mut_VANISHED'] == 0
    expected = json.dumps(attributed, sort_keys=True)
    fc.counts(attributed)
    assert json.dumps(attributed, sort_keys=True) == expected
    original_spec, original_check = fc.c.Spec, fc.c.check
    calls = []
    try:
        fc.c.Spec = lambda *args, **kwargs: None
        fc.c.check = lambda spec, ex: calls.append(ex) or [v('synthetic')]
        with TemporaryDirectory(dir=OUT) as tmp:
            root = Path(tmp)
            for i in range(10):
                run = root / str(i)
                run.mkdir()
                (run / 'exchanges.jsonl').write_text('{}\n')
                spec = run / 'spec.original.json'
                spec.write_text('{}')
                a = fc.violations(run, spec, 'market')
                b = fc.violations(run, spec, 'market', cache=False)
                assert a == b
                assert len(fc._cache) <= 5
                c = fn.base_violations(run, 'market')
                assert c == a[0]
                assert fn.base_violations(run, 'market') is c
                assert len(fn._cache) <= 7
    finally:
        fc.c.Spec, fc.c.check = original_spec, original_check
        fc._cache.clear()
        fn._cache.clear()
    result = {'counts': dict(got), 'noise_floor_spec_counts': dict(old),
              'cache_bypass_equal': True, 'compare_max_entries': 5, 'noise_max_entries': 7,
              'input_unchanged': True, 'fake_exchange_checks': len(calls)}
    (OUT / 'semantics_check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
