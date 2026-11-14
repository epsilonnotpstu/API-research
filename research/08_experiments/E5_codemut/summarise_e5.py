"""Summarise validated E5 pairs; signal matches are observations, not causal kills.

Counts are fingerprint counts. INCREASED/DECREASED count only PERSISTENT rows.
The P001-specific triage CLI cannot label E5 JSONL: triage L1 stays unavailable.
"""
import argparse
from collections import Counter
import csv
import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e5_common as c
import validate_pair as vp

METRICS = [f'{scope}_{name}' for scope in ('mutated','non_mutated')
           for name in ('NEW','VANISHED','INCREASED','DECREASED')]
FIELDS = ['mut_dir','site_id','sut','operator','seed','oracle','validation_status','analysis_status','error',
          *METRICS,'expected_signals','expected_signal_observed','expected_signal_present_mutant',
          'expected_signal_NEW','expected_signal_INCREASED','fresh_L1_NEW_mutated',
          'triage_status','triage_L1_NEW_mutated','causal_kill_status']


def load_attribute():
    spec = importlib.util.spec_from_file_location('e5_own_attribute', c.TOOLS / 'attribute.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def violations(path):
    # Only physical LF separates JSONL records (a JSON string may contain U+2028).
    return [json.loads(line) for line in path.read_bytes().split(b'\n') if line.strip()]


def verify_analysis(directory, mut, seed, oracle, pair, report):
    record = c.load(directory / 'analysis.json'); m = c.load(mut / 'manifest.json')
    c.require(record['status'] == 'COMPLETE' and record['format'] == 'e5-analysis-v1', 'Analysis incomplete')
    c.require((record['seed'],record['oracle'],record['sut'],record['mode']) == (seed,oracle,m['sut'],'fresh'), 'Analysis identity/oracle mismatch')
    reject = '400,406,422' if m['sut'] == 'market' and oracle == 'sut' else '400,422'
    c.require(record['reject_statuses'] == reject and record['deploy_origin'] == f'http://sut-{m["sut"]}:8080', 'Wrong analysis oracle/origin')
    c.require(record['manifest_sha256'] == c.sha(mut / 'manifest.json'), 'Analysis manifest changed')
    c.require(record['pair_validation_sha256'] == c.sha(mut / f'pair-validation-s{seed}.json'), 'Validation report changed')
    c.require(record['control_run'] == str(pair['control']) and record['mutant_run'] == str(pair['mutant']), 'Analysis pair paths differ')
    c.require(record['run_metadata_sha256'] == {r:c.sha(p / 'run.json') for r,p in pair.items()}, 'Analysis run metadata changed')
    c.require(report['status'] == 'PASS', 'Pair did not pass validation')
    c.snapshot(c.TOOLS, record['tool_sha256'])
    c.require({'control.violations.jsonl','mutant.violations.jsonl','attribution.csv'} <= set(record['file_sha256']), 'Missing analysis output')
    c.snapshot(directory, record['file_sha256'])
    for name, digest in record['pipeline_sha256'].items():
        c.require(c.sha(name) == digest, 'Analysis pipeline changed')
    base = violations(directory / 'control.violations.jsonl'); treat = violations(directory / 'mutant.violations.jsonl')
    expected = load_attribute().attribute(base, treat, m, mode='fresh')
    with (directory / 'attribution.csv').open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream); rows = list(reader)
        c.require(reader.fieldnames == (list(expected[0]) if expected else ['fingerprint']), 'Unexpected attribution CSV schema')
    c.require(rows == [{k:str(v) for k,v in row.items()} for row in expected], 'Attribution CSV differs from fresh recomputation')
    return rows


def metrics(rows, manifest):
    result = {key:0 for key in METRICS}
    expected = set(manifest['expected_conformance_signal'])
    ops = {(o['method'].upper(),o['path']) for o in manifest['operations']}
    signal_new = signal_inc = 0; present = False; l1 = Counter(); seen = set()
    for row in rows:
        c.require(row['fingerprint'] not in seen, 'Duplicate attributed fingerprint'); seen.add(row['fingerprint'])
        c.require(row['mode'] == 'fresh' and row['status'] in ('NEW','VANISHED','PERSISTENT'), 'Non-fresh/unknown status')
        before, after = int(row['baseline_occurrences']), int(row['mutated_occurrences'])
        c.require(before >= 0 and after >= 0, 'Negative occurrences')
        c.require((before == 0 and after > 0) if row['status'] == 'NEW' else
                  (before > 0 and after == 0) if row['status'] == 'VANISHED' else (before > 0 and after > 0), 'Status/count mismatch')
        mapped = (row['method'], row['template']) in ops
        c.require(row['op_mutated'] == str(mapped), 'Affected-operation flag differs from manifest')
        scope = 'mutated' if mapped else 'non_mutated'
        direction = row['status'] if row['status'] != 'PERSISTENT' else ('INCREASED' if after > before else 'DECREASED' if after < before else None)
        if direction: result[scope + '_' + direction] += 1
        if mapped and row['status'] == 'NEW': l1[row['label_L1']] += 1
        if mapped and row['kind'] in expected:
            present |= after > 0
            signal_new += row['status'] == 'NEW'
            signal_inc += direction == 'INCREASED'
    result.update(expected_signals=json.dumps(sorted(expected)), expected_signal_observed=bool(signal_new or signal_inc),
                  expected_signal_present_mutant=present, expected_signal_NEW=signal_new, expected_signal_INCREASED=signal_inc,
                  fresh_L1_NEW_mutated=json.dumps(dict(sorted(l1.items()))), triage_status='NOT_APPLICABLE_P001_CLI',
                  triage_L1_NEW_mutated='', causal_kill_status='NEEDS_INDEPENDENT_WITNESS')
    return result


def summarise(mut_dirs):
    result = []
    for mut in sorted(Path(p).resolve() for p in mut_dirs):
        m = c.load(mut / 'manifest.json')
        # Retain failed/pending/unpaired seeds as explicit error rows, never zero effects.
        ledger = c.ledger(mut / 'runs.tsv'); seeds = sorted({int(r['seed']) for r in ledger})
        c.require(len({r['run_dir'] for r in ledger}) == len(ledger), 'Reused run directory across seed/role')
        if (mut / 'run-plan.json').exists():
            plan = c.load(mut / 'run-plan.json')
            c.require(plan['manifest_sha256'] == c.sha(mut / 'manifest.json'), 'Run plan manifest differs')
            c.require(all(type(s) is int and s >= 0 for s in plan['seeds']) and len(set(plan['seeds'])) == len(plan['seeds']), 'Invalid planned seeds')
            seeds = sorted(set(seeds) | set(plan['seeds']))
        for seed in seeds:
            group = [r for r in ledger if int(r['seed']) == seed]
            pair = {r['role']:Path(r['run_dir']).resolve() for r in group}
            report = None; error = ''
            try:
                c.require(set(pair) == {'control','mutant'} and all(r['status'] == 'COMPLETE' and r['harness_exit'] == '0' for r in group), 'Failed/pending/incomplete run pair')
                saved = c.load(mut / f'pair-validation-s{seed}.json')
                report = vp.validate(pair['control'],pair['mutant'],mut)
                c.require(saved == report and report['status'] == 'PASS', 'Pair validation missing, stale or FAIL')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                error = str(exc)
            for oracle in ('default','sut'):
                row = dict.fromkeys(FIELDS, '')
                row.update(mut_dir=str(mut),site_id=m['site_id'],sut=m['sut'],operator=m['operator'],seed=seed,oracle=oracle,
                           validation_status='FAIL' if error else 'PASS',analysis_status='FAIL',error=error,
                           expected_signals=json.dumps(sorted(m['expected_conformance_signal'])), triage_status='NOT_APPLICABLE_P001_CLI',
                           causal_kill_status='NEEDS_INDEPENDENT_WITNESS')
                if not error:
                    try:
                        rows = verify_analysis(mut / f'analysis-s{seed}-{oracle}', mut,seed,oracle,pair,report)
                        row.update(metrics(rows,m),analysis_status='COMPLETE')
                    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
                        row['error'] = str(exc)
                result.append(row)
    return result


def write_csv(path, rows):
    path = Path(path)
    c.require(not path.is_symlink(), 'Refusing symlink summary output')
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('x', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    tmp.replace(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mut_dirs', nargs='*', type=Path)
    parser.add_argument('--root', type=Path, default=c.HERE, help='Discovery root containing work/*/runs.tsv')
    parser.add_argument('--out', type=Path, default=c.HERE / 'e5_summary.csv')
    args = parser.parse_args(argv)
    try:
        selected = args.mut_dirs or [p.parent for p in args.root.glob('work/*/runs.tsv')]
        c.require(len(set(p.resolve() for p in selected)) == len(selected), 'Duplicate pair directory')
        rows = summarise(selected); write_csv(args.out,rows)
        print(json.dumps({'output':str(args.out),'rows':len(rows),'status':'NO_RUNS' if not rows else 'FAIL' if any(r['error'] for r in rows) else 'PASS'}))
        return int(any(r['error'] for r in rows))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('E5 summary: ' + str(error),file=sys.stderr); return 1


if __name__ == '__main__':
    sys.exit(main())
