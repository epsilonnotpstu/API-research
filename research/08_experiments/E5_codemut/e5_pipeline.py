"""Future E5 launcher/analysis orchestration. T20 writes this; Claude executes it.

The run command executes the reviewed harness; the analyse command executes only
our conformance/attribution tools. No commands run merely by importing this file.
"""
import argparse
import csv
import datetime
import json
import os
import signal
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e5_common as c
import validate_pair as vp


def seeds(values):
    result = [int(x) for x in (values or ['1', '2', '3'])]
    c.require(all(str(n) == str(v) and n >= 0 for n, v in zip(result, values or ['1','2','3'])), 'Seeds must be canonical nonnegative integers')
    c.require(len(set(result)) == len(result), 'Duplicate seeds')
    return result


def trusted_files():
    paths = [p for p in c.HARNESS.rglob('*') if p.is_file() and not any(x.startswith('.') or x == '__pycache__' for x in p.relative_to(c.HARNESS).parts)]
    paths += list(c.TOOLS.glob('*.py'))
    paths += [c.HERE / n for n in ('codemut.py','e5_common.py','e5_pipeline.py','validate_pair.py','summarise_e5.py','run_pair.sh','analyse_pair.sh','run_noise.sh','analyse_noise.sh')]
    return {str(p): c.sha(p) for p in sorted(paths)}


def write_ledger(path, rows):
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('x', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=c.LEDGER_FIELDS, delimiter='\t')
        writer.writeheader(); writer.writerows(rows); stream.flush(); os.fsync(stream.fileno())
    tmp.replace(path)


class PipelineInterrupted(KeyboardInterrupt):
    def __init__(self, signum):
        self.signum = signum


def harness_process(command, *, env, log):
    # Forward an interrupt to the harness and allow its EXIT trap to finish.
    with subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT) as child:
        try:
            return child.wait()
        except KeyboardInterrupt as error:
            try:
                child.send_signal(getattr(error, 'signum', signal.SIGINT))
            except ProcessLookupError:
                pass
            child.wait()
            raise


def run_pair(mut, values, kind='pair'):
    prefix, second = c.layout(kind)
    roles = ('control', second)
    mut = mut.resolve(); chosen = seeds(values)
    c.require(not (mut / (prefix + 'runs.tsv')).exists() and not (mut / (prefix + 'run-plan.json')).exists(), 'Pair already has a launch ledger; use a fresh pair directory, no implicit resume')
    checks = vp.Checks()
    m, images = vp.build_checks(mut, checks)
    c.atomic_json(mut / (prefix + 'run-preflight.json'), {'status': 'PASS' if checks.passed else 'FAIL', 'checks': checks.rows})
    c.require(checks.passed, f'Build preflight failed; see {prefix}run-preflight.json')
    frozen = trusted_files()
    tag = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + str(os.getpid())
    plan = {'format':'e5-run-plan-v1', 'kind':kind, 'mut_dir':str(mut), 'site_id':m['site_id'], 'sut':m['sut'],
            'seeds':chosen, 'budget_seconds':300, 'data_generation':'all', 'checks':'response_headers_conformance',
            'manifest_sha256':c.sha(mut / 'manifest.json'), 'trusted_files_sha256': frozen,
            'build_image_ids':{r:images['control' if kind == 'noise' else r]['Id'] for r in roles}}
    # Exclusive creation claims this pair even if two launchers passed preflight.
    # A partial plan after a host/process failure is retained, never reused.
    with (mut / (prefix + 'run-plan.json')).open('x', encoding='utf-8') as stream:
        json.dump(plan, stream, indent=2, sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    rows = []; write_ledger(mut / (prefix + 'runs.tsv'), rows)
    for seed in chosen:
        paths = {}
        for role in roles:
            build_role = 'control' if kind == 'noise' else role
            equal_frozen = all(c.sha(p) == digest for p, digest in frozen.items())
            c.require(equal_frozen and c.sha(mut / 'manifest.json') == plan['manifest_sha256'], 'Frozen launcher/tool/harness/manifest changed; stopping')
            run_id = f'{tag}_e5_{prefix}{m["site_id"]}_{role}_s{seed}'
            c.require(len(run_id) <= 181, 'Run ID too long')
            run_dir = c.EXP / 'E1_pilot/runs' / m['sut'] / run_id
            c.require(not run_dir.exists(), 'Refusing existing run directory')
            paths[role] = run_dir
            env = os.environ.copy()
            for key in ('AUTH_HEADER','AUTH_ROLE','HEALTH_PATH','BASE_PATH','ONLY_OPS','CODE_ROLE','CODE_SOURCE_TREE_SHA256',
                        'CODE_MANIFEST','SUT_IMAGE_OVERRIDE','SUT_JAR_OVERRIDE','PILOT_RUN_ID'):
                env.pop(key, None)
            env.update(SCHEMA_CHECKS='response_headers_conformance', DATA_GEN='all', MAX_EXAMPLES='100',
                       REQUEST_TIMEOUT_MS='10000', MITM_MAX_BODY='65536', PILOT_RUN_ID=run_id, CODE_ROLE=build_role,
                       CODE_SOURCE_TREE_SHA256=m['source_tree_sha256' if build_role == 'control' else 'mutated_tree_sha256'],
                       CODE_MANIFEST=str(mut / 'manifest.json'), SUT_IMAGE_OVERRIDE=images[build_role]['Id'],
                       SUT_JAR_OVERRIDE=str(mut / f'context-{build_role}/dist/{m["sut"]}-sut.jar'))
            row = {'seed':seed,'role':role,'run_dir':str(run_dir),'harness_exit':'','status':'RUNNING'}
            rows.append(row); write_ledger(mut / (prefix + 'runs.tsv'), rows)
            command = [str(c.HARNESS / 'run_pilot.sh'), m['sut'], str(c.EMB / f'openapi-swagger/{m["sut"]}.json'),
                       'baseline','NONE','0',str(seed),'300']
            code = 1
            try:
                with (mut / f'{prefix}run-s{seed}-{role}.log').open('x') as log:
                    code = harness_process(command, env=env, log=log)
                if code < 0: code = 128 - code
                complete = c.load(run_dir / 'run.json') if code == 0 else {}
                row['status'] = 'COMPLETE' if code == 0 and isinstance(complete,dict) and complete.get('complete') is True and complete.get('harness_exit') == '0' else 'FAILED'
            except KeyboardInterrupt as error:
                code = 128 + getattr(error, 'signum', signal.SIGINT); row['status'] = 'INTERRUPTED'
            except (OSError, ValueError):
                row['status'] = 'FAILED'
            finally:
                row['harness_exit'] = str(code); write_ledger(mut / (prefix + 'runs.tsv'), rows)
            c.require(row['status'] == 'COMPLETE', f'Run failed; stopped at seed {seed}/{role}. See {prefix}runs.tsv and run log')
        report = vp.validate(paths['control'], paths[second], mut, kind)
        c.atomic_json(mut / f'{prefix}pair-validation-s{seed}.json', report)
        c.require(report['status'] in ('PASS','PASS_WITH_EXCLUSION'), f'Pair validation failed for seed {seed}; stopping')
    print(str(mut / (prefix + 'runs.tsv')))


def tool(script, arguments, out, error_log):
    wrapper = 'import pathlib,runpy,sys; p=pathlib.Path(sys.argv.pop(1)).resolve(); sys.path.insert(0,str(p.parent)); sys.argv[0]=str(p); runpy.run_path(str(p),run_name="__main__")'
    with out.open('x') as stream, error_log.open('a') as errors:
        result = subprocess.run(['/usr/bin/python3','-I','-B','-c',wrapper,str(c.TOOLS / script),*map(str,arguments)],
                                stdout=stream, stderr=errors, check=False)
    c.require(result.returncode == 0, f'{script} failed with exit {result.returncode}; see tools.log')


def filter_violations(source, dest, excluded):
    with dest.open('x',encoding='utf-8') as stream:
        for line in source.read_bytes().split(b'\n'):
            if not line.strip(): continue
            record = json.loads(line)
            if (record['method'].upper(),record['template']) not in excluded:
                stream.write(json.dumps(record,ensure_ascii=False) + '\n')


def analyse_pair(mut, kind='pair'):
    prefix, second = c.layout(kind)
    roles = ('control', second)
    mut = mut.resolve(); pairs = c.paired_rows(mut / (prefix + 'runs.tsv'), allow_incomplete=True, kind=kind)
    m = c.load(mut / 'manifest.json')
    skipped = sorted({int(r['seed']) for r in c.ledger(mut / (prefix + 'runs.tsv'), kind)} - set(pairs))
    if skipped:
        print('Skipping failed/incomplete seeds: ' + ','.join(map(str,skipped)),file=sys.stderr)
    # Refuse before any output if an analysis already exists; partial output is evidence.
    c.require(not any((mut / f'{prefix}analysis-s{s}-{o}').exists() for s in pairs for o in ('default','sut')), 'Analysis output already exists; retain it and investigate, no implicit overwrite')
    for seed, pair in sorted(pairs.items()):
        report = vp.validate(pair['control'], pair[second], mut, kind)
        validation_path = mut / f'{prefix}pair-validation-s{seed}.json'
        c.atomic_json(validation_path, report)
        c.require(report['status'] in ('PASS','PASS_WITH_EXCLUSION'), f'Pair validation failed for seed {seed}')
        meta = c.load(pair['control'] / 'run.json')
        for oracle in ('default','sut'):
            reject = '400,406,422' if m['sut'] == 'market' and oracle == 'sut' else '400,422'
            origin = f'http://{meta["sut_service"]}:{meta["internal_port"]}'
            out = mut / f'{prefix}analysis-s{seed}-{oracle}'; out.mkdir()
            record = {'format':'e5-analysis-v1','kind':kind,'status':'RUNNING','seed':seed,'sut':m['sut'],'oracle':oracle,
                      'reject_statuses':reject,'deploy_origin':origin,'mode':'fresh',
                      'control_run':str(pair['control']), (second + '_run'):str(pair[second]),
                      'manifest_sha256':c.sha(mut / 'manifest.json'), 'pair_validation_sha256':c.sha(validation_path),
                      'run_metadata_sha256':{r:c.sha(p / 'run.json') for r,p in pair.items()},
                      'tool_sha256':meta['tool_sha256'], 'pipeline_sha256':trusted_files(),
                      'excluded_ops':report.get('excluded_ops',[]), 'validation_status':report['status']}
            c.atomic_json(out / 'analysis.json', record)
            try:
                for role in roles:
                    tool('conformance.py', [pair['control'] / 'spec.original.json', pair[role] / 'exchanges.jsonl',
                                           '--deploy-origin', origin,'--reject-statuses',reject],
                         out / f'{role}.raw.violations.jsonl', out / 'tools.log')
                    filter_violations(out / f'{role}.raw.violations.jsonl', out / f'{role}.violations.jsonl', c.excluded_operations(report))
                tool('attribute.py', [out / 'control.violations.jsonl', out / f'{second}.violations.jsonl', mut / 'manifest.json', '--mode','fresh'],
                     out / 'attribution.csv', out / 'tools.log')
                c.snapshot(c.TOOLS, meta['tool_sha256'])
                equal = vp.validate(pair['control'], pair[second], mut, kind)
                c.require(equal == report, 'Pair evidence changed during analysis')
                record['status'] = 'COMPLETE'
            except (OSError, ValueError, KeyboardInterrupt) as error:
                record['status'] = 'FAIL'; record['error'] = str(error)
            finally:
                record['file_sha256'] = {p.name:c.sha(p) for p in out.iterdir() if p.is_file() and p.name != 'analysis.json'}
                c.atomic_json(out / 'analysis.json', record)
            c.require(record['status'] == 'COMPLETE', f'Analysis failed: {out}')
    print(str(mut))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('run', 'run-noise'):
        run = sub.add_parser(name); run.add_argument('mut_dir', type=Path); run.add_argument('seeds', nargs='*')
    for name in ('analyse', 'analyse-noise'):
        analysis = sub.add_parser(name); analysis.add_argument('mut_dir', type=Path)
    args = parser.parse_args(argv)
    def interrupted(signum, frame):
        raise PipelineInterrupted(signum)
    signal.signal(signal.SIGTERM, interrupted)
    try:
        kind = 'noise' if args.command.endswith('-noise') else 'pair'
        if args.command.startswith('run'): run_pair(args.mut_dir, args.seeds, kind)
        else: analyse_pair(args.mut_dir, kind)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('E5: ' + str(error), file=sys.stderr); return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
