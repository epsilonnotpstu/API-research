"""Write atomic, standard-library-only provenance for a pilot (called by run_pilot.sh)."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    (run, emb, sut, source, mode, fault, severity, seed, budget, examples, image,
     project, started, phase, schema_rc, coverage_rc, cleanup_rc, harness_rc,
     health, base_path) = sys.argv[1:]
    run, emb = Path(run), Path(emb)
    commit = subprocess.check_output(['git', '-C', str(emb), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(emb), 'status', '--porcelain'], text=True)
    images = {}
    for path in sorted(run.glob('*-image.json')):
        try:
            inspected = json.loads(path.read_text())[0]
            images[path.stem] = {'id': inspected['Id'], 'repo_digests': inspected.get('RepoDigests', []),
                                'repo_tags': inspected.get('RepoTags', [])}
        except (ValueError, IndexError, KeyError) as error:
            images[path.stem] = {'inspection_error': str(error)}
    files = {p.name: sha(p) for p in sorted(run.iterdir())
             if p.is_file() and p.name != 'run.json' and not p.name.endswith('.tmp')}
    fuzzer = os.environ.get('PILOT_FUZZER', 'schemathesis')
    data = {
        'fuzzer': fuzzer,
        'generator_input_sha256': sha(run / ('spec.test.json' if fuzzer == 'evomaster' and
                                            os.environ.get('PILOT_EVOMASTER_INPUT', 'spec') == 'spec'
                                            else 'generator-input.json')),
        'run_id': run.name, 'sut': sut, 'source_spec': source,
        'source_sha256': sha(next(run.glob('spec.original.*'), Path(source))),
        'mode': mode, 'fault': fault, 'severity': int(severity), 'seed': int(seed),
        'budget_seconds': int(budget), 'max_examples': int(examples),
        'schemathesis_image': image, 'compose_project': project,
        'started_at': started, 'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'finished_at': None if harness_rc == 'pending' else datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'phase': phase, 'schemathesis_exit': schema_rc, 'coverage_exit': coverage_rc,
        'cleanup_exit': cleanup_rc, 'harness_exit': harness_rc,
        'complete': harness_rc == '0', 'emb_commit': commit, 'emb_status_porcelain': dirty,
        'health_path': health, 'base_path': base_path, 'auth': os.environ.get('PILOT_AUTH_ROLE', 'none (pilot assumption)'),
        'request_timeout_ms': int(os.environ.get('PILOT_REQUEST_TIMEOUT_MS', '10000')),
        'hypothesis_phases': os.environ.get('PILOT_HYPOTHESIS_PHASES', 'explicit,generate'),
        'schema_checks': os.environ['SCHEMA_CHECKS'],
        'harness_version': 2,
        'sut_service': os.environ['SUT_SERVICE'],
        'sut_image': os.environ['SUT_IMAGE'],
        'internal_port': int(os.environ['INTERNAL_PORT']),
        'auth_source': os.environ['PILOT_AUTH_SOURCE'],
        'auth_source_sha256': (sha(emb / os.environ['PILOT_AUTH_SOURCE'])
                               if os.environ['PILOT_AUTH_SOURCE'] not in ('none', 'runtime-override') else None),
        'logger_max_body': int(os.environ['MITM_MAX_BODY']),
        'host_port': os.environ['HOST_PORT'], 'jacoco_port': os.environ['JACOCO_PORT'],
        'sut_jar_sha256': sha(Path(os.environ.get('PILOT_SUT_JAR_PATH', str(emb / 'dist' / f'{sut}-sut.jar')))),
        'code_mutation': ({'role': os.environ['PILOT_CODE_ROLE'],
                           'source_tree_sha256': os.environ['PILOT_CODE_SOURCE_SHA256'],
                           'manifest_sha256': sha(run / 'code.manifest.json')}
                          if os.environ.get('PILOT_CODE_ROLE') else None),
        'jacoco_agent_sha256': sha(emb / 'dist' / 'jacocoagent.jar'),
        'jacoco_cli_sha256': sha(emb / 'dist' / 'jacococli.jar'),
        'images': images, 'file_sha256': files,
        'tool_sha256': {p.name: sha(p) for p in sorted((emb.parent.parent / 'tools').glob('*.py'))},
        'harness_sha256': {str(p.relative_to(Path(__file__).parent)): sha(p)
                           for p in sorted(Path(__file__).parent.rglob('*'))
                           if p.is_file() and not any(part.startswith('.') for part in p.relative_to(Path(__file__).parent).parts)},
        'emb_config_sha256': {name: sha(emb / name) for name in
                              (os.environ['COMPOSE_FILE'], os.environ['DOCKERFILE'])},
        'limitations': ['fresh traffic is observational', 'fixed seed does not guarantee identical traffic',
                         'generator schema back edges are cut; conformance uses the original or mutated oracle',
                         'equal mutation operation sets do not imply equal generator and oracle constraints',
                         'transport-error and truncation coverage require review',
                         'locally built SUT may have only image ID, no registry digest'],
    }
    if os.environ.get('STRICT_KEYWORDS'):
        data['strict_keywords'] = sorted(os.environ['STRICT_KEYWORDS'].split(','))
    if fuzzer == 'evomaster':
        # Legacy image key identifies the selected generator for unchanged analysis.
        # Do not claim that Schemathesis ran in an EvoMaster collection.
        data['schemathesis_exit'] = 'not_started'
        data.update({
            'evomaster_input': os.environ.get('PILOT_EVOMASTER_INPUT', 'spec'),
            'evomaster_image': os.environ['PILOT_EVOMASTER_IMAGE'],
            'evomaster_version': os.environ['PILOT_EVOMASTER_VERSION'],
            'evomaster_schema_oracles': os.environ.get('PILOT_EVOMASTER_SCHEMA_ORACLES', 'true') == 'true',
            'evomaster_exit': schema_rc,
            'evomaster_argv_file': 'evomaster-argv.txt',
            'evomaster_argv': ((run / 'evomaster-argv.txt').read_text().splitlines()
                               if (run / 'evomaster-argv.txt').is_file() else []),
            'evomaster_watchdog_seconds': int(budget) + 120,
        })
        data['file_sha256'].update({str(p.relative_to(run)): sha(p)
                                   for p in sorted((run / 'evomaster').rglob('*')) if p.is_file()})
        if data['evomaster_input'] == 'spec':
            data['limitations'] = [line for line in data['limitations']
                                   if not line.startswith(('generator schema back edges',
                                                           'equal mutation operation sets'))]
            data['limitations'].append('EvoMaster uses spec.test unchanged; schema path checked against base_path')
    tmp = run / 'run.json.tmp' 
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(run / 'run.json')


if __name__ == '__main__':
    main()
