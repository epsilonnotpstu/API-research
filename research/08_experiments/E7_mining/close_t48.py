#!/usr/bin/python3
"""Write a final preservation proof and aggregate completion checks only."""
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KEY = HERE / 'key'
R = runpy.run_path(str(HERE / 'review_t48.py'))


def main():
    R['guard']()
    tests = json.loads((ROOT / '09_collab/logs/T48_scratch/test_summary.json').read_text())
    assert tests['passed'] and tests['tests_run'] == 52 and tests['failures'] == tests['errors'] == 0
    verification = json.loads((HERE / 'verification_t48.json').read_text())
    assert all(verification['checks'].values())
    log = json.loads((KEY / 'e10_build_log.json').read_text())
    output = ROOT / '08_experiments/E2_labelling/e10_blind'
    hashes = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in output.rglob('*') if p.is_file()}
    assert hashes == log['package_hashes']
    baseline = json.loads((KEY / 'preservation_t48_start.json').read_text())
    final_hashes = {p: hashlib.sha256((HERE / p).read_bytes()).hexdigest() for p in baseline}
    assert final_hashes == baseline
    R['private_json'](KEY / 'preservation_t48_final.json',
                      dict(unchanged=True, existing_key_files=sum(p.startswith('key/') for p in baseline),
                           total_baseline_files=len(baseline), hashes=final_hashes))
    references = json.loads((KEY / 'e10_reference_audit.json').read_text())
    excluded = {pair['later'] + '/contract/' + p for pair in log['cross_item_pairs'] for p in pair['excluded']}
    assert excluded == {r['target'] for r in references['missing_references']}
    cross = json.loads((KEY / 'e10_cross_item_all.json').read_text())
    checks = dict(existing_key_files_preserved=sum(p.startswith('key/') for p in baseline),
                  all_baseline_files_preserved=len(baseline), frozen_pool_verified=True,
                  tests=tests, package=verification['summary'], auth_fixtures=verification['auth_fixtures'],
                  auth_value_variants=verification['auth_value_variants'], cross_item=cross['summary'],
                  omitted_helper_occurrences=sum(len(d['omitted_helpers']) for d in log['items']),
                  maximum_implementation_files=max(sum(p.startswith('impl/') for p in d['files']) for d in log['items']),
                  references={k: v for k, v in references.items() if k != 'missing_references'},
                  unresolved_reference_targets_equal_mandatory_cross_item_exclusions=True,
                  old_blind_packages_read=False, existing_package_replacement=False,
                  required_locators_preserved=True)
    R['private_json'](HERE / 'checks_t48.json', checks)
    print(json.dumps(checks))


if __name__ == '__main__':
    main()
