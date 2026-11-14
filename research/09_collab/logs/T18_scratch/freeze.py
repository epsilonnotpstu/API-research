"""Freeze validated T18 deliverables, then update only the T18 board status/log."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from replay import OUT, ROOT, save
from write_labels import LABELS, ROOTS


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    validation = json.loads((OUT / 'validation.json').read_text())
    assert validation['status'] == 'PASS'
    inputs = json.loads((OUT / 'input_sha256.json').read_text())
    manifest = json.loads((OUT / 'sha256_manifest.json').read_text())
    assert all(digest(ROOT / rel) == sha for rel, sha in inputs.items())
    assert all(digest(ROOT / rel) == sha for rel, sha in manifest.items())
    report = ROOT / '09_collab/reports/T18_report.md'
    frozen = {'status': 'FROZEN', 'utc': datetime.now(timezone.utc).isoformat(),
              'validation': 'PASS', 'manifest_files_unchanged': len(manifest),
              'input_files_unchanged': len(inputs),
              'deliverables_sha256': {str(p.relative_to(ROOT)): digest(p) for p in [LABELS, ROOTS, report]},
              'manifest_sha256': digest(OUT / 'sha256_manifest.json'),
              'report_citations_checked': validation['report_citations_checked'],
              'blind_labels_A_opened': False, 'blind_pilot_RESULTS_reports_opened': False,
              'external_execution': False}
    save('freeze.json', frozen)
    for rel, line in re.findall(r'`((?:08_experiments|09_collab)/[^`]+):(\d+)`', report.read_text()):
        contents = (ROOT / rel).read_text().splitlines()
        assert 1 <= int(line) <= len(contents) and contents[int(line) - 1].strip()
    board = ROOT / '09_collab/COLLAB_BOARD.md'
    original = board.read_text()
    matches = re.findall(r'^\| T18 \|.*$', original, re.M)
    assert len(matches) == 1
    row = matches[0]
    cells = row.split('|')
    assert cells[5].strip() == 'IN PROGRESS'
    cells[5] = ' DONE '
    updated = original.replace(row, '|'.join(cells), 1)
    local = datetime.now(timezone(timedelta(hours=6))).strftime('%Y-%m-%d %H:%M +06')
    log = (f'\n- {local} | Codex | T18 | DONE: six blind labels under v0.4: TEST 4, SPEC 1, '
           'SPEC_PARTIAL 1 (C002: 62 SPEC + 7 invalid-HTTP TEST); zero BOTH candidates, seven root families. '
           'Exact deploy-origin CLI replay: 430 captured exchanges/430 diagnostics, all six blind counts match. '
           '483 CSV/root locators, 74 report citations, reciprocal roots, aggregation and 56 input hashes PASS; '
           'outputs frozen before final board read. C003/C006 are state-oracle false positives, C004 is header coverage, '
           'C005 is intentional empty 404 vs body schema. Log encoding losses limit claims to captured traffic; '
           'no unique request/log identity joins claimed. No labels_A/RESULTS report opened, external execution, '
           'or writes to runs/harness/tools. Evidence: E2_labelling/cwa-verification_baseline_s1_labels_codex.csv:C001-C006; '
           'cwa-verification_root_causes_codex.csv:RC01-RC07; reports/T18_report.md; '
           'logs/T18_scratch/validation.json and freeze.json.\n')
    board.write_text(updated + log)
    assert all(digest(ROOT / rel) == sha for rel, sha in frozen['deliverables_sha256'].items())
    print(json.dumps({'status': 'DONE', 'frozen_utc': frozen['utc'], 'manifest_files': len(manifest),
                      'report_citations': validation['report_citations_checked']}))


if __name__ == '__main__':
    main()
