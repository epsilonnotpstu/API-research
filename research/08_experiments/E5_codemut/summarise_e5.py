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
SIGNAL_NOISE_RULE = 'EXPECTED_CHANGED_FP_ABSENT_BOTH_NOISE_RUNS_V1'
FIELDS = ['kind','signal_exceeds_noise','signal_noise_rule','signal_noise_detail','mut_dir','site_id','sut','operator','seed','oracle','validation_status','excluded_ops','pipeline_snapshot_status','analysis_status','error',
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


def verify_analysis(directory, mut, seed, oracle, pair, report, kind='pair'):
    prefix, second = c.layout(kind)
    record = c.load(directory / 'analysis.json'); m = c.load(mut / 'manifest.json')
    c.require(record.get('kind','pair') == kind, 'Analysis comparison kind differs')
    c.require(record['status'] == 'COMPLETE' and record['format'] == 'e5-analysis-v1', 'Analysis incomplete')
    c.require((record['seed'],record['oracle'],record['sut'],record['mode']) == (seed,oracle,m['sut'],'fresh'), 'Analysis identity/oracle mismatch')
    reject = '400,406,422' if m['sut'] == 'market' and oracle == 'sut' else '400,422'
    c.require(record['reject_statuses'] == reject and record['deploy_origin'] == f'http://sut-{m["sut"]}:8080', 'Wrong analysis oracle/origin')
    c.require(record['manifest_sha256'] == c.sha(mut / 'manifest.json'), 'Analysis manifest changed')
    c.require(record['pair_validation_sha256'] == c.sha(mut / f'{prefix}pair-validation-s{seed}.json'), 'Validation report changed')
    c.require(record['control_run'] == str(pair['control']) and record[second + '_run'] == str(pair[second]), 'Analysis pair paths differ')
    c.require(record['run_metadata_sha256'] == {r:c.sha(p / 'run.json') for r,p in pair.items()}, 'Analysis run metadata changed')
    c.require(report['status'] in ('PASS','PASS_WITH_EXCLUSION'), 'Pair did not pass validation')
    excluded = c.excluded_operations(report)
    c.require(record.get('excluded_ops',[]) == report.get('excluded_ops',[]) and
              record.get('validation_status','PASS') == report['status'], 'Analysis exclusion/validation policy differs')
    c.snapshot(c.TOOLS, record['tool_sha256'])
    c.require({'control.violations.jsonl',second + '.violations.jsonl','attribution.csv'} <= set(record['file_sha256']), 'Missing analysis output')
    c.snapshot(directory, record['file_sha256'])
    prior = False
    for name, digest in record['pipeline_sha256'].items():
        if c.sha(name) != digest:
            path = Path(name).resolve()
            c.require(path.parent == c.HERE and path.name in {'validate_pair.py','e5_common.py','e5_pipeline.py','summarise_e5.py'}
                      and isinstance(digest,str) and len(digest)==64 and all(x in '0123456789abcdef' for x in digest), 'Analysis pipeline changed outside reviewed E5 policy files')
            prior = True
    base = violations(directory / 'control.violations.jsonl'); treat = violations(directory / (second + '.violations.jsonl'))
    for role, data in [('control',base),(second,treat)]:
        c.require(all((v['method'].upper(),v['template']) not in excluded for v in data), 'Excluded operation leaked into scoped violations')
        raw = directory / f'{role}.raw.violations.jsonl'
        if raw.is_file():
            c.require(raw.name in record['file_sha256'], 'Raw violations are not hashed')
            c.require([v for v in violations(raw) if (v['method'].upper(),v['template']) not in excluded] == data, 'Scoped violations differ from exact paired exclusion')
        else:
            c.require(not excluded, 'Excluded analysis lacks raw violation evidence')
    expected = load_attribute().attribute(base, treat, m, mode='fresh')
    with (directory / 'attribution.csv').open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream); rows = list(reader)
        c.require(reader.fieldnames == (list(expected[0]) if expected else ['fingerprint']), 'Unexpected attribution CSV schema')
    c.require(rows == [{k:str(v) for k,v in row.items()} for row in expected], 'Attribution CSV differs from fresh recomputation')
    return rows, ('PRIOR_E5_PIPELINE_RECOMPUTED' if prior else 'CURRENT')


def metrics(rows, manifest, excluded_ops=()):
    result = {key:0 for key in METRICS}
    expected = set(manifest['expected_conformance_signal'])
    ops = {(o['method'].upper(),o['path']) for o in manifest['operations']}
    signal_new = signal_inc = 0; present = False; l1 = Counter(); seen = set()
    for row in rows:
        if (row['method'],row['template']) in excluded_ops: continue
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


def summarise_kind(mut_dirs, kind, evidence):
    prefix, second = c.layout(kind)
    result = []
    for mut in sorted(Path(p).resolve() for p in mut_dirs):
        m = c.load(mut / 'manifest.json')
        # Retain failed/pending/unpaired seeds as explicit error rows, never zero effects.
        ledger_path = mut / (prefix + 'runs.tsv')
        if not ledger_path.exists() and not (mut / (prefix + 'run-plan.json')).exists(): continue
        ledger = c.ledger(ledger_path, kind) if ledger_path.exists() else []
        seeds = sorted({int(r['seed']) for r in ledger})
        c.require(len({r['run_dir'] for r in ledger}) == len(ledger), 'Reused run directory across seed/role')
        if (mut / (prefix + 'run-plan.json')).exists():
            plan = c.load(mut / (prefix + 'run-plan.json'))
            c.require(plan['manifest_sha256'] == c.sha(mut / 'manifest.json'), 'Run plan manifest differs')
            c.require(all(type(s) is int and s >= 0 for s in plan['seeds']) and len(set(plan['seeds'])) == len(plan['seeds']), 'Invalid planned seeds')
            seeds = sorted(set(seeds) | set(plan['seeds']))
        for seed in seeds:
            group = [r for r in ledger if int(r['seed']) == seed]
            pair = {r['role']:Path(r['run_dir']).resolve() for r in group}
            report = None; error = ''
            try:
                c.require(set(pair) == {'control',second} and all(r['status'] == 'COMPLETE' and r['harness_exit'] == '0' for r in group), 'Failed/pending/incomplete run pair')
                saved = c.load(mut / f'{prefix}pair-validation-s{seed}.json')
                report = vp.validate(pair['control'],pair[second],mut,kind)
                # Older PASS reports have no exclusions key; all existing fields must match.
                saved = dict(saved, excluded_ops=saved.get('excluded_ops',[]))
                c.require(saved == report and report['status'] in ('PASS','PASS_WITH_EXCLUSION'), 'Pair validation missing, stale or FAIL')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                error = str(exc)
            for oracle in ('default','sut'):
                row = dict.fromkeys(FIELDS, '')
                row.update(kind=kind,signal_exceeds_noise='NOT_APPLICABLE' if kind == 'noise' else 'UNKNOWN',
                           signal_noise_rule=SIGNAL_NOISE_RULE,mut_dir=str(mut),site_id=m['site_id'],sut=m['sut'],operator=m['operator'],seed=seed,oracle=oracle,
                           validation_status='FAIL' if error else report['status'],excluded_ops=json.dumps(report.get('excluded_ops',[]) if report else []),analysis_status='FAIL',error=error,
                           expected_signals=json.dumps(sorted(m['expected_conformance_signal'])), triage_status='NOT_APPLICABLE_P001_CLI',
                           causal_kill_status='NEEDS_INDEPENDENT_WITNESS')
                if not error:
                    try:
                        rows, version = verify_analysis(mut / f'{prefix}analysis-s{seed}-{oracle}', mut,seed,oracle,pair,report,kind)
                        row.update(metrics(rows,m,c.excluded_operations(report)),analysis_status='COMPLETE',pipeline_snapshot_status=version)
                        evidence[(str(mut),seed,oracle,kind)] = (rows,pair,report)
                    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
                        row['error'] = str(exc)
                result.append(row)
    return result



def expected_changed(rows, manifest):
    ops = {(op['method'].upper(),op['path']) for op in manifest['operations']}
    expected = set(manifest['expected_conformance_signal'])
    return [r for r in rows if (r['method'],r['template']) in ops and r['kind'] in expected
            and int(r['mutated_occurrences']) > int(r['baseline_occurrences'])]


def observed_operations(run):
    # Use the same route matcher as conformance, including concrete-route priority
    # and deployment origin. Zero violations alone do not establish op exposure.
    spec = importlib.util.spec_from_file_location('e5_own_conformance', c.TOOLS / 'conformance.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    meta = c.load(run / 'run.json')
    matcher = module.Spec(c.load(run / 'spec.original.json'),
                          deploy_origin=f"http://{meta['sut_service']}:{meta['internal_port']}")
    result = set()
    for exchange in violations(run / 'exchanges.jsonl'):
        req = exchange['request']; method = req['method'].upper()
        template, _ = matcher.match(req['path'], method, req.get('origin'))
        if template: result.add((method,template))
    return result


def compare_noise(mut, pair_data, noise_data):
    """A finite observed absence rule, not statistical significance or a kill."""
    rows, pair, _ = pair_data; noise_rows, noise_pair, _ = noise_data
    c.require(len(set(pair.values()) | set(noise_pair.values())) == 4, 'Pair/noise reuse a run directory')
    runs = [*pair.values(),*noise_pair.values()]
    metas = [c.load(run / 'run.json') for run in runs]
    c.require(len({m['compose_project'] for m in metas}) == 4, 'Pair/noise reuse a Compose project')
    volumes = set()
    for service in (metas[0]['sut_service'], 'mitmproxy'):
        containers = [c.inspection(run / (service + '-container.json')) for run in runs]
        c.require(len({obj['Id'] for obj in containers}) == 4, 'Pair/noise reuse a container')
        if service == 'mitmproxy':
            for obj in containers:
                names = {mount['Name'] for mount in obj['Mounts'] if mount['Type'] == 'volume'}
                c.require(not volumes.intersection(names), 'Pair/noise share a proxy volume')
                volumes.update(names)
    # Establish same seed, control build and scenario across the two comparisons,
    # in addition to each comparison's own validation and oracle verification.
    bridge = vp.validate(pair['control'],noise_pair['control'],mut,'noise')
    c.require(bridge['status'] in ('PASS','PASS_WITH_EXCLUSION'), 'Pair/noise control scenario mismatch')
    candidates = expected_changed(rows,c.load(mut / 'manifest.json'))
    if not candidates: return False, 'No expected-kind mapped-operation NEW/INCREASED fingerprint'
    reached = set.intersection(*(observed_operations(run) for run in runs))
    covered = [r for r in candidates if (r['method'],r['template']) in reached]
    noise_fps = {r['fingerprint'] for r in noise_rows}  # Union of both noise runs, including VANISHED.
    passing = [r['fingerprint'] for r in covered if r['fingerprint'] not in noise_fps]
    if passing: return True, json.dumps({'qualifying_fingerprints':sorted(passing)})
    if len(covered) < len(candidates): return 'UNKNOWN', 'Candidate operation not captured in all four runs'
    return False, 'Every expected changed fingerprint occurs in at least one noise run'


def summarise(mut_dirs):
    evidence = {}; mut_dirs = list(mut_dirs)
    result = summarise_kind(mut_dirs,'pair',evidence) + summarise_kind(mut_dirs,'noise',evidence)
    for row in result:
        if row['kind'] == 'noise': continue
        key = (row['mut_dir'],row['seed'],row['oracle'])
        if (*key,'pair') not in evidence:
            row['signal_noise_detail'] = 'Pair analysis unavailable or invalid'; continue
        if (*key,'noise') not in evidence:
            row['signal_noise_detail'] = 'Same-seed, same-oracle validated noise analysis unavailable'; continue
        try:
            value, detail = compare_noise(Path(row['mut_dir']),evidence[(*key,'pair')],evidence[(*key,'noise')])
            row.update(signal_exceeds_noise=value,signal_noise_detail=detail)
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            row['signal_noise_detail'] = str(exc)
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
        selected = args.mut_dirs or sorted({p.parent for name in ('runs.tsv','noise-runs.tsv','run-plan.json','noise-run-plan.json') for p in args.root.glob('work/*/' + name)})
        c.require(len(set(p.resolve() for p in selected)) == len(selected), 'Duplicate pair directory')
        rows = summarise(selected); write_csv(args.out,rows)
        print(json.dumps({'output':str(args.out),'rows':len(rows),'status':'NO_RUNS' if not rows else 'FAIL' if any(r['error'] for r in rows) else 'PASS'}))
        return int(any(r['error'] for r in rows))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('E5 summary: ' + str(error),file=sys.stderr); return 1


if __name__ == '__main__':
    sys.exit(main())
