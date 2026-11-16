#!/usr/bin/python3
"""Final byte preservation, delivered-file and known-preview-value audits."""
import base64
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE = Path(__file__).resolve().parent
KEY = HERE / 'key'
ROOT = HERE.parents[1]
B = runpy.run_path(str(HERE / 'build_t49.py'))


def main():
    B['R']['guard']()
    baseline = json.loads((KEY / 'preservation_t49_start.json').read_text())
    after = {p: hashlib.sha256((HERE / p).read_bytes()).hexdigest() for p in baseline}
    assert after == baseline
    B['R']['private_json'](KEY / 'preservation_t49_after.json', after)
    files = {p.relative_to(B['OUT']).as_posix(): p.read_bytes() for p in B['OUT'].rglob('*') if p.is_file()}
    log = json.loads((KEY / 'e12_build_log.json').read_text())
    assert {p: B['B']['sha'](data) for p, data in files.items()} == log['package_hashes']
    # Recheck the encoded value that escaped the early terminal display filter.
    # No value or source line is printed or copied into a public artifact.
    d = next(d for d in B['R']['decisions']() if d['repo'] == 'dockstore' and d['rank'] == 159)
    patch = (HERE / d['review_evidence']).read_text()
    encoded = set(re.findall(r'\bencoding\s*=\s*"([A-Za-z0-9+/=]{32,})"', patch))
    assert encoded, 'Known preview incident evidence missing'
    needles = {value.encode() for value in encoded}
    for value in encoded:
        try:
            decoded = base64.b64decode(value, validate=True)
        except ValueError:
            continue
        if len(decoded) >= 8:
            try:
                decoded.decode('utf-8', 'strict')
            except UnicodeDecodeError:
                continue
            needles.add(decoded)
    variants = B['B']['O']['variants'](needles)
    hits = sum(any(needle in data for needle in variants) for data in files.values())
    assert hits == 0, 'Known preview value in delivered package (suppressed)'
    assert all(B['R']['display']('encoding="' + value + '"').find(value) < 0 for value in encoded)
    incident = dict(earlier_preview_incidents=1, literal_count=len(encoded), scanned_variants=len(variants),
                    delivered_files_scanned=len(files), delivered_files_containing_observed_value=hits,
                    strengthened_display_filter_verified=True, value_not_repeated_in_report=True)
    B['R']['private_json'](KEY / 'e12_preview_privacy_incident_audit.json', incident)
    refs = json.loads((KEY / 'e12_reference_audit.json').read_text())
    cross = json.loads((KEY / 'e12_cross_item_all.json').read_text())
    excluded = {p['later'] + '/contract/' + path for p in log['cross_item_pairs']
                for path in p['excluded'] if path.endswith(('.yaml', '.yml', '.json'))}
    assert {r['target'] for r in refs['missing_references']} <= excluded
    result = dict(existing_files_checked=len(baseline), existing_private_files_checked=sum(p.startswith('key/') for p in baseline),
                  changed_existing_files=0, frozen_pool_and_sources_and_code_verified=True,
                  delivered_hashes_verified=True, package=log['summary'], preview_privacy_incident=incident,
                  reference_audit={k: v for k, v in refs.items() if k != 'missing_references'},
                  cross_item_audit=cross['summary'], earlier_packages_opened=False,
                  no_upstream_code_execution=True, no_network=True, board_read=False)
    B['R']['private_json'](ROOT / '09_collab/logs/T49_scratch/final_audit.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
