"""T26b read-only source smoke comparisons and local regression orchestration."""
import argparse
import contextlib
import hashlib
import json
import os
import io
from pathlib import Path
import subprocess
import sys
import runpy
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
SCRATCH = Path(__file__).resolve().parent
TOOLS = ROOT / '08_experiments/tools'
EMB = ROOT / '08_experiments/_external/emb'
SPECS = EMB / 'openapi-swagger'
SOURCES = {
    'scout': EMB / 'jdk_8_maven/cs/rest/original/scout-api',
    'market': EMB / 'jdk_11_maven/cs/rest-gui/market',
    'cwa': EMB / 'jdk_11_maven/cs/rest/cwa-verification-server',
    'petstore': EMB / 'jdk_8_maven/cs/rest/original/swagger-petstore',
}
CASES = [
    ('scout_roles', 'scout', 'scout-api', 'GET', '/v1/system/roles', ['--status', '418']),
    ('market_products', 'market', 'market', 'GET', '/products', ['--status', '200']),
    ('petstore_name', 'petstore', 'swagger-petstore', 'GET', '/pet/{petId}', ['--field', 'name']),
    ('earlier_scout', 'scout', 'scout-api', 'GET', '/v2/activities', ['--status', '200']),
    ('earlier_cwa', 'cwa', 'cwa-verification', 'POST', '/version/v1/tan', ['--status', '201']),
]


def save(name, value):
    (SCRATCH / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def snapshot():
    files = set(TOOLS.rglob('*'))
    files.update((ROOT / '08_experiments/E1_pilot/harness_v2').rglob('*'))
    for source in SOURCES.values():
        for directory, dirs, names in os.walk(source):
            dirs[:] = sorted(d for d in dirs if d not in {'target', 'node_modules', '.git', 'build'})
            files.update(Path(directory, name) for name in names)
    files.add(ROOT / '09_collab/reports/T26_report.md')
    save('protected_before.json', {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(files) if p.is_file() and not p.is_symlink()})


def smoke(phase):
    tool = TOOLS / 'intent_evidence.py' if phase == 'before' else SCRATCH / 'staged/intent_evidence.py'
    summary = []
    for name, source, spec, method, path, extra in CASES:
        command = [sys.executable, '-I', '-B', str(tool), str(SOURCES[source]),
                   str(SPECS / (spec + '.json')), '--method', method, '--path', path, *extra, '--json']
        start = time.monotonic()
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        elapsed = time.monotonic() - start
        (SCRATCH / (phase + '_' + name + '.json')).write_text(result.stdout)
        (SCRATCH / (phase + '_' + name + '.stderr.txt')).write_text(result.stderr)
        if result.returncode:
            raise RuntimeError(f'{name}: {result.stderr}')
        data = json.loads(result.stdout)
        hits = data['hits']
        entry = {'case': name, 'command': command, 'returncode': result.returncode,
                 'seconds': round(elapsed, 4), 'verdict': data['independent_evidence'],
                 'evidence_types': data['evidence_types_found'], 'scan': data['scan'],
                 'hits': {c: sum(h['category'] == c for h in hits)
                          for c in ['HANDLER', 'E-TEST', 'E-DOC', 'E-CONSIST', 'E-HISTORY']},
                 'independent_tests': sum(h['category'] == 'E-TEST' and h['independent'] for h in hits),
                 'other_module_tests': sum(h['category'] == 'E-TEST' and h.get('module_scope') == 'other_module' for h in hits)}
        if phase == 'after':
            repeated = subprocess.run(command, capture_output=True, text=True, timeout=30)
            entry['repeat_identical'] = result.returncode == repeated.returncode and result.stdout == repeated.stdout
            source_root = SOURCES[source]
            entry['locators_verified'] = all(
                h['snippet'] == (source_root / h['file']).read_text(encoding='utf-8-sig').splitlines()[h['line'] - 1].strip()[:160]
                for h in hits)
        summary.append(entry)
    save(phase + '_summary.json', summary)
    print(json.dumps([{k: v for k, v in row.items() if k != 'command'} for row in summary], indent=2))


def review():
    original = tempfile.TemporaryDirectory
    def temporary(*args, **kwargs):
        if 'dir' in kwargs:
            kwargs['dir'] = SCRATCH
        return original(*args, **kwargs)
    output = io.StringIO()
    rc = 0
    with patch.object(tempfile, 'TemporaryDirectory', side_effect=temporary), \
            contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        sys.argv = [str(TOOLS / 'test_review_fixes.py')]
        try:
            runpy.run_path(sys.argv[0], run_name='__main__')
        except SystemExit as exc:
            rc = int(exc.code or 0)
    print(output.getvalue(), end='')
    sys.exit(rc)


def tests():
    suites = [('staged_intent', [SCRATCH / 'staged/test_intent_evidence.py']),
              ('original_intent', [TOOLS / 'test_intent_evidence.py']),
              ('review_fixes', [Path(__file__).resolve(), 'review']),
              ('specmut', [TOOLS / 'test_specmut.py', SPECS]),
              ('pipeline', [TOOLS / 'test_pipeline.py', SPECS]),
              ('triage', [TOOLS / 'test_triage.py']),
              ('only_ops', [TOOLS / 'test_only_ops.py']),
              ('p001', [ROOT / '08_experiments/E1_pilot/p001_oas_analysis.py',
                        ROOT / '08_experiments/_external/p001', SCRATCH / 'p001_replay'])]
    rows = []
    for name, args in suites:
        command = [sys.executable, '-I', '-B', *map(str, args)]
        start = time.monotonic()
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        (SCRATCH / (name + '_tests.txt')).write_text(result.stdout + result.stderr)
        rows.append({'suite': name, 'command': command, 'returncode': result.returncode,
                     'seconds': round(time.monotonic() - start, 4),
                     'tail': (result.stdout + result.stderr).splitlines()[-6:]})
        print(f'{name}: exit {result.returncode}', flush=True)
    save('tests_summary.json', rows)
    if any(row['returncode'] for row in rows):
        sys.exit(1)


def performance():
    with tempfile.TemporaryDirectory(dir=SCRATCH) as temporary:
        source = Path(temporary)
        contract = source / 'spec.json'
        contract.write_text(json.dumps({'paths': {'/api/products': {'get': {'responses': {'200': {}}}}}}))
        (source / 'pom.xml').write_text('<project/>')
        (source / 'C.java').write_text('@Path("/api/products") class C { @GET public Object products() { return Response.status(418); } }')
        (source / 'README.md').write_text('GET /api/products returns 200')
        for i in range(5000):
            (source / f'Dto{i:05d}.java').write_text(f'class Dto{i:05d} {{ String value; }}')
        command = [sys.executable, '-I', '-B', str(SCRATCH / 'staged/intent_evidence.py'), str(source),
                   str(contract), '--method', 'GET', '--path', '/api/products', '--status', '418', '--json']
        start = time.monotonic()
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        elapsed = time.monotonic() - start
        data = json.loads(result.stdout)
        save('performance.json', {'fixture': '5000 DTO files, one handler, README and root build descriptor',
                                 'returncode': result.returncode, 'seconds': round(elapsed, 4),
                                 'scan': data['scan'], 'verdict': data['independent_evidence'],
                                 'under_30_seconds': elapsed < 30})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['snapshot', 'before', 'after', 'tests', 'review', 'performance'])
    action = parser.parse_args().action
    if action in {'before', 'after'}:
        smoke(action)
    else:
        {'snapshot': snapshot, 'tests': tests, 'review': review, 'performance': performance}[action]()
