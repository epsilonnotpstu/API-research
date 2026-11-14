"""Validate an E5 pair from saved files only. Missing evidence is a FAIL, never a skip.

Usage: validate_pair.py CONTROL_RUN MUTANT_RUN MUT_DIR
Writes MUT_DIR/pair-validation-s<seed>.json; exits 1 on any failed check.
With --kind noise, the second run must use the original control image/JAR/tree
and CODE_ROLE=control; writes noise-pair-validation-s<seed>.json instead.
"""
import argparse
import copy
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codemut
import e5_common as c


class Checks:
    def __init__(self):
        self.rows = []

    def run(self, name, function):
        try:
            function()
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, ET.ParseError) as error:
            self.rows.append({'check': name, 'status': 'FAIL', 'detail': str(error)})
        else:
            self.rows.append({'check': name, 'status': 'PASS'})

    @property
    def passed(self):
        return bool(self.rows) and all(r['status'] == 'PASS' for r in self.rows)


def equal(a, b, message):
    c.require(a == b, message)


def context_inventory(root, checksum_path):
    recorded = {}
    for line in checksum_path.read_text().splitlines():
        digest, name = line.split('  ', 1)
        name = c.safe_relative(name)
        c.require(name not in recorded, 'Duplicate context checksum path')
        recorded[name] = digest
    c.snapshot(root, recorded)
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    equal(actual, set(recorded), 'Unrecorded/missing context file')
    c.require(not any(p.is_symlink() for p in root.rglob('*')), 'Symlink in build context')
    return recorded


def dependencies(root):
    return {p.relative_to(root).as_posix(): c.sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.suffix in ('.jar', '.pom')}


def build_checks(mut, checks):
    """Checks also used by the future launcher before starting external execution."""
    m = c.load(mut / 'manifest.json')
    sut = m['sut']
    c.require(sut in c.SUTS and m['format'] == 'codemut-v1' and m['injection_side'] == 'IMPL', 'Not an E5 IMPL manifest')
    c.require(re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,70}', m['site_id']), 'Invalid site ID')
    c.require(m['operator'] in codemut.OPERATORS and m['expected_L1'] == 'IMPL', 'Invalid injection expectation')
    c.require(m['expected_L2'] in codemut.OPERATORS[m['operator']], 'Invalid expected L2')
    c.require(set(m['expected_conformance_signal']) <= codemut.SIGNALS, 'Unknown expected signal')
    ops = {(x['method'], x['path']) for x in m['operations']}
    c.require(ops and len(ops) == len(m['operations']), 'Invalid/duplicate affected operation mapping')
    equal({(x['method'], x['path']) for x in m['mutations']}, ops, 'Inconsistent mutations/operations')
    for x in m['mutations']:
        equal((x['fault'], x['expected_L1'], x['expected_L2']), (m['operator'], 'IMPL', m['expected_L2']), 'Inconsistent mutation label')

    def sources():
        original = codemut.inventory(mut / 'control.source'); changed = codemut.inventory(mut / 'source')
        c.require(original and changed, 'Missing/empty source tree')
        equal(original, m['source_files'], 'Original source inventory differs from manifest')
        equal(codemut.canonical_hash(original), m['source_tree_sha256'], 'Original tree hash differs')
        equal(codemut.canonical_hash(changed), m['mutated_tree_sha256'], 'Mutant tree hash differs')
        equal(set(original), set(changed), 'Mutant file set differs')
        equal([p for p in original if original[p] != changed[p]], [m['file']], 'More than the one intended file changed')
        a = (mut / 'control.source' / m['file']).read_bytes()
        b = (mut / 'source' / m['file']).read_bytes()
        equal(codemut.edit_bytes(a, m), b, 'Mutant is not the exact reviewed edit')
        equal(c.sha(mut / 'patch.diff'), m['patch_sha256'], 'Patch digest differs')
        equal((mut / 'patch.diff').read_text(), codemut.patch_text(a, b, m['file']), 'Patch does not encode edit')
        equal(c.sha(mut / 'source' / m['file']), m['mutated_file_sha256'], 'Mutated file digest differs')
    checks.run('build.source_and_patch', sources)

    def deps():
        saved = c.load(mut / 'resolved-artifacts.json')
        c.require(saved['control'], 'Empty dependency inventory')
        equal(saved['control'], saved['mutant'], 'Resolved dependency hashes differ')
        for role in ('control', 'mutant'):
            equal(dependencies(mut / ('m2-' + role)), saved[role], 'Current dependency cache differs from recorded artifacts')
        image = c.inspection(mut / 'maven-image.json')
        c.require(c.image_id(image['Id']), 'Missing immutable Maven image ID')
        c.require((mut / 'maven-arguments.txt').read_text().strip(), 'Missing Maven arguments')
        for role in ('control', 'mutant'):
            c.require((mut / ('build-' + role + '.log')).is_file(), 'Missing Maven build log')
    checks.run('build.maven_and_dependencies', deps)
    images, contexts = {}, {}
    base = c.inspection(mut / 'runtime-base.json')
    c.require(c.image_id(base['Id']) and base['RepoDigests'] and base['RootFS']['Layers'], 'Missing pinned runtime base')
    for role, folder, key in [('control', 'control.source', 'source_tree_sha256'), ('mutant', 'source', 'mutated_tree_sha256')]:
        def built(role=role, folder=folder, key=key):
            image = c.inspection(mut / f'image-{role}.json'); images[role] = image
            c.require(c.image_id(image['Id']), 'Invalid built SUT image ID')
            ctx = mut / ('context-' + role)
            contexts[role] = context_inventory(ctx, mut / f'context-{role}.sha256')
            jar = ctx / 'dist' / f'{sut}-sut.jar'
            equal(c.sha(jar), c.sha(mut / folder / c.JARS[sut]), 'Staged JAR differs from built JAR')
            equal(image['Config']['Labels']['org.r1.jar_sha256'], c.sha(jar), 'Image JAR label differs')
            equal(image['Config']['Labels']['org.r1.source_tree_sha256'], m[key], 'Image source label differs')
            c.require((mut / f'tag-{role}.txt').read_text().strip() in image['RepoTags'], 'Built image tag not recorded')
            layers = base['RootFS']['Layers']
            equal(image['RootFS']['Layers'][:len(layers)], layers, 'SUT image not derived from pinned runtime base')
            equal((image['Os'], image['Architecture']), (base['Os'], base['Architecture']), 'Runtime platform differs')
            dockerfile = (ctx / 'dockerfiles' / f'{sut}.dockerfile').read_text()
            c.require(dockerfile.splitlines()[0].removeprefix('FROM ') in base['RepoDigests'], 'Dockerfile FROM differs from runtime digest')
        checks.run(f'build.{role}.image_context', built)

    def same_context():
        c.require(images['control']['Id'] != images['mutant']['Id'], 'Identical control/mutant image IDs')
        jar = f'dist/{sut}-sut.jar'
        c.require(contexts['control'][jar] != contexts['mutant'][jar], 'Identical control/mutant JARs')
        equal({k:v for k,v in contexts['control'].items() if k != jar},
              {k:v for k,v in contexts['mutant'].items() if k != jar}, 'Non-JAR runtime inputs differ')
        a, b = (copy.deepcopy(images[r]['Config']) for r in ('control', 'mutant'))
        for config in (a, b):
            for key in ('org.r1.jar_sha256', 'org.r1.source_tree_sha256'):
                config['Labels'].pop(key, None)
        equal(a, b, 'Built image runtime configuration differs')
    checks.run('build.equal_non_jar_inputs', same_context)
    return m, images


# These may differ because they identify a run or the code treatment. Every other
# metadata field must exist in both runs and compare equal (strict allowlist).
ALLOWED_META = {'run_id', 'compose_project', 'started_at', 'updated_at', 'finished_at', 'source_spec',
                'sut_image', 'sut_jar_sha256', 'code_mutation', 'images', 'file_sha256',
                'schemathesis_exit', 'limitations'}


def generator_argv(run, meta):
    argv = (run / 'schemathesis-argv.txt').read_text().splitlines()
    def flag(name):
        c.require(argv.count(name) == 1 and argv.index(name) + 1 < len(argv), 'Missing/duplicate generator flag ' + name)
        return argv[argv.index(name) + 1]
    equal(argv[:2], ['run', '/work/generator-input.json'], 'Unexpected generator input')
    for name, value in {'--data-generation-method': 'all', '--checks': 'response_headers_conformance',
                        '--hypothesis-seed': str(meta['seed']), '--hypothesis-max-examples': str(meta['max_examples']),
                        '--request-timeout': str(meta['request_timeout_ms']), '--hypothesis-phases': meta['hypothesis_phases'],
                        '--base-url': 'http://mitmproxy:8080' + meta['base_path'], '--sanitize-output': 'true'}.items():
        equal(flag(name), value, 'Generator option differs: ' + name)
    if '-H' in argv:
        equal(flag('-H'), '<redacted>', 'Auth header not redacted')
    return argv


def normalized_runtime(container, meta, run, proxy=False):
    """Ignore only Docker identity/network addresses and known Compose bookkeeping."""
    config = copy.deepcopy(container['Config']); host = copy.deepcopy(container['HostConfig'])
    config.pop('Hostname', None); config.pop('Image', None)
    labels = config.get('Labels') or {}
    for key in list(labels):
        if key.startswith('com.docker.compose.') and key not in ('com.docker.compose.service', 'com.docker.compose.version'):
            labels.pop(key)
        if key in ('org.r1.jar_sha256', 'org.r1.source_tree_sha256'):
            labels.pop(key)
    config['Labels'] = labels
    # Compare the full environment multiset: order is incidental, multiplicity
    # and every key/value remain strict, including duplicate-key entries.
    env = config.get('Env')
    if env is not None:
        c.require(isinstance(env,list) and all(isinstance(x,str) and '=' in x for x in env), 'Invalid container environment')
        names = [x.split('=',1)[0] for x in env]
        c.require(all(names), 'Empty container environment key')
        config['Env'] = sorted(env)
    network = host.get('NetworkMode')
    project = meta['compose_project']
    c.require(isinstance(network,str) and project and network.startswith(project + '_'), 'Unexpected network mode')
    host['NetworkMode'] = '<compose-project>' + network[len(project):]
    # NetworkSettings (including per-run SandboxID/IP addresses) is not part of
    # the runtime-settings projection; HostConfig network suffix remains strict.
    c.require(not host.get('Links') and not host.get('VolumesFrom'), 'Unexpected container links/shared state')
    mounts = []
    for mount in container['Mounts']:
        mount = copy.deepcopy(mount)
        if proxy and mount['Type'] == 'bind' and mount['Destination'] == '/custom-logs':
            equal(Path(mount['Source']).resolve(), run, 'Proxy log mount is not its own run')
            mount['Source'] = '<run>'
        elif proxy and mount['Type'] == 'volume' and mount['Destination'] == '/home/mitmproxy/.mitmproxy':
            mount['Name'] = '<anonymous-volume>'; mount['Source'] = '<anonymous-volume>'
        else:
            c.require(proxy and not mount.get('RW'), 'Unexpected writable SUT/shared mount')
        mounts.append(mount)
    if not proxy:
        equal(container['Mounts'], [], 'SUT must use a fresh container without mounts')
        c.require(not config.get('Volumes'), 'SUT image declares persistent volumes')
    host['Binds'] = sorted({s.replace(str(run), '<run>') for s in (host.get('Binds') or [])})
    return {'Config': config, 'HostConfig': host, 'Mounts': sorted(mounts, key=lambda x: x['Destination']),
            'Platform': container.get('Platform'), 'Driver': container.get('Driver'),
            'AppArmorProfile': container.get('AppArmorProfile'), 'Path': container['Path'], 'Args': container['Args']}


def junit_error_set(root):
    """Exact paired generator errors; ordinary assertion failures remain evidence."""
    return {(case.get('name', ''), ''.join(error.itertext()))
            for case in root.iter('testcase') for error in case.iter('error')}


def validate(control, mutant, mut, kind='pair'):
    _, second = c.layout(kind)
    control, mutant, mut = (Path(p).resolve() for p in (control, mutant, mut))
    checks = Checks(); inputs = {}; junit_errors = {}; notes = []; excluded_ops = []
    def build():
        inputs['manifest'], inputs['images'] = build_checks(mut, checks)
    checks.run('build.manifest_and_base', build)
    metas = {}
    for role, run in [('control', control), (second, mutant)]:
        def read_metadata(role=role, run=run):
            meta = c.load(run / 'run.json')
            c.require(isinstance(meta, dict), 'run.json must be an object')
            metas[role] = meta
        checks.run(role + '.metadata_read', read_metadata)
    seed = metas.get('control', {}).get('seed')
    if type(seed) is not int or seed < 0:
        seed = 'unknown'
    for role, run in [('control', control), (second, mutant)]:
        def artifacts(role=role, run=run):
            meta = metas[role]
            c.require(run != mut and mut not in run.parents and run not in mut.parents, 'Overlapping run/build directories')
            equal(meta['run_id'], run.name, 'Run ID differs from directory')
            c.require(meta['complete'] is True and meta['harness_exit'] == '0' and meta['phase'] == 'complete', 'Run is incomplete')
            equal((meta['mode'], meta['fault'], meta['severity']), ('baseline', 'NONE', 0), 'E5 spec must remain unchanged')
            c.require(meta['seed'] == seed and type(meta['seed']) is int, 'Seed mismatch/invalid')
            equal((meta['budget_seconds'], meta['max_examples'], meta['schema_checks']), (300, 100, 'response_headers_conformance'), 'Unexpected E5 scenario')
            equal((meta['coverage_exit'], meta['cleanup_exit']), ('0', '0'), 'Coverage/cleanup failed')
            c.require(meta['schemathesis_exit'] in ('0', '1') and meta['finished_at'], 'Generator did not complete')
            c.require(meta['auth_source'] != 'runtime-override', 'Runtime auth override lacks a fixture hash')
            c.require(meta['auth_source'] == 'none' or re.fullmatch('[a-f0-9]{64}', str(meta['auth_source_sha256'])), 'Missing auth fixture hash')
            required = {'spec.original.json','spec.test.json','generator-input.json','derecurse-cuts.json',
                        'sut-config.env','code.manifest.json','compose.code-image.json','exchanges.jsonl','jacoco.exec',
                        'schemathesis-argv.txt','schemathesis-help.txt','schemathesis.junit.xml','compose.resolved.yaml',
                        'schema-image.json','mitmproxy-image.json','mitmproxy-container.json',
                        f'sut-{meta["sut"]}-image.json', f'sut-{meta["sut"]}-container.json'}
            c.require(required <= set(meta['file_sha256']), 'Missing required snapshot artifact')
            c.snapshot(run, meta['file_sha256'])
            for name in ('exchanges.jsonl', 'jacoco.exec'):
                c.require((run / name).stat().st_size > 0, 'Empty captured artifact')
            root = ET.parse(run / 'schemathesis.junit.xml').getroot()
            c.require(root.tag in ('testsuites','testsuite'), 'Invalid JUnit root')
            c.require(any(True for _ in root.iter('testcase')), 'JUnit contains no test cases')
            junit_errors[role] = junit_error_set(root)
            equal(c.sha(run / 'spec.original.json'), meta['source_sha256'], 'Original spec hash differs')
            equal(c.sha(run / 'spec.original.json'), c.sha(run / 'spec.test.json'), 'E5 changed the test spec')
            c.require(meta['sut'] in c.SUTS and meta['sut_service'] == 'sut-' + meta['sut'] and meta['internal_port'] == 8080, 'Unexpected SUT deployment')
            equal(meta['harness_version'], 2, 'Unexpected harness version')
            c.require(isinstance(meta['emb_commit'],str) and meta['emb_commit'] and isinstance(meta['emb_status_porcelain'],str), 'Missing EMB provenance')
            c.require(isinstance(meta['schemathesis_image'],str) and meta['schemathesis_image'], 'Missing generator image reference')
            # Historical identities remain strict within the pair. Later local
            # tool/harness edits are analysis drift, not changed run evidence.
            c.runtime_snapshots(meta)
            c.snapshot(c.EMB, meta['emb_config_sha256'])
            equal(c.sha(c.EMB / 'dist/jacocoagent.jar'), meta['jacoco_agent_sha256'], 'Current JaCoCo agent changed')
            equal(c.sha(c.EMB / 'dist/jacococli.jar'), meta['jacoco_cli_sha256'], 'Current JaCoCo CLI changed')
            if meta['auth_source'] != 'none':
                equal(c.sha(c.EMB / c.safe_relative(meta['auth_source'])), meta['auth_source_sha256'], 'Current auth fixture changed')
            generator_argv(run, meta)
        checks.run(role + '.completion_snapshots_tools', artifacts)

        def treatment(role=role, run=run):
            meta = metas[role]; m = inputs['manifest']; built = inputs['images']['control' if kind == 'noise' else role]
            equal(meta['sut'], m['sut'], 'SUT differs from code manifest')
            equal(c.sha(run / 'code.manifest.json'), c.sha(mut / 'manifest.json'), 'Copied code manifest differs')
            build_role = 'control' if kind == 'noise' else role
            key = 'source_tree_sha256' if build_role == 'control' else 'mutated_tree_sha256'
            equal(meta['code_mutation'], {'role': build_role, 'source_tree_sha256': m[key], 'manifest_sha256': c.sha(mut / 'manifest.json')}, 'Role/tree/manifest provenance differs')
            c.require(meta['sut_image'] in (built['Id'], (mut / f'tag-{build_role}.txt').read_text().strip()), 'Selected SUT image reference differs')
            equal(meta['sut_jar_sha256'], c.sha(mut / f'context-{build_role}/dist/{m["sut"]}-sut.jar'), 'Selected JAR hash differs')
            image = c.inspection(run / f'sut-{m["sut"]}-image.json')
            container = c.inspection(run / f'sut-{m["sut"]}-container.json')
            equal(image['Id'], built['Id'], 'Run SUT image differs from built image')
            for key in ('Config','RootFS','Os','Architecture'):
                equal(image[key], built[key], 'Run image inspection differs: ' + key)
            equal(container['Image'], image['Id'], 'Actual SUT container image differs')
            equal(container['Config']['Image'], image['Id'], 'SUT container was not pinned to immutable ID')
            equal(c.load(run / 'compose.code-image.json'), {'services': {meta['sut_service']: {'image': image['Id']}}}, 'Compose E5 image override differs')
            equal(image['Config']['Labels']['org.r1.jar_sha256'], meta['sut_jar_sha256'], 'Run JAR label differs')
            equal(c.sha(mut / f'context-{build_role}/dist/jacocoagent.jar'), meta['jacoco_agent_sha256'], 'Context JaCoCo agent differs from run')
            for image_key in ('schema-image', 'mitmproxy-image', f'sut-{m["sut"]}-image'):
                actual = c.inspection(run / (image_key + '.json'))
                c.require(c.image_id(actual['Id']), 'Missing immutable collected image ID')
                equal(meta['images'][image_key]['id'], actual['Id'], 'run.json image ID differs from saved inspect')
                equal(meta['images'][image_key]['repo_digests'], actual.get('RepoDigests', []), 'Recorded image digest differs')
            proxy = c.inspection(run / 'mitmproxy-container.json')
            equal(proxy['Image'], meta['images']['mitmproxy-image']['id'], 'Actual proxy image differs')
        checks.run(role + '.treatment_image_chain', treatment)

    def paired_junit():
        c.require(set(junit_errors) == {'control',second}, 'Missing parsed JUnit evidence')
        difference = junit_errors['control'] ^ junit_errors[second]
        if difference:
            manifest = inputs['manifest']
            mutated = {(op['method'].upper(),op['path']) for op in manifest['operations']}
            spec = c.load(control / 'spec.original.json')
            operations = set()
            for name,text in sorted(difference):
                match = re.fullmatch(r'(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS|TRACE) (/\S*)', name)
                c.require(match is not None, 'Cannot map asymmetric JUnit error to an operation: ' + name)
                method,path = match.groups()
                c.require(method.lower() in spec.get('paths',{}).get(path,{}), 'Asymmetric JUnit operation is absent from spec: ' + name)
                c.require((method,path) not in mutated, 'Asymmetric JUnit error on mutated operation: ' + name)
                operations.add((method,path))
            excluded_ops.extend({'method':method,'path':path,'reason':'Asymmetric JUnit generator error on a non-mutated operation; excluded from both roles.'}
                                for method,path in sorted(operations))
            notes.append({'check':'pair.equal_junit_errors','note':'Non-mutated operations with asymmetric JUnit errors are excluded from both roles.',
                          'differing_errors':[{'testcase_name':name,'error_text':text} for name,text in sorted(difference)]})
        elif junit_errors['control']:

            notes.append({'check':'pair.equal_junit_errors',
                          'note':'Identical JUnit execution errors in both roles; affected test cases did not generate normally.',
                          'errors':[{'testcase_name':name,'error_text':text} for name,text in sorted(junit_errors['control'])]})
    checks.run('pair.equal_junit_errors', paired_junit)

    def pair_metadata():
        a, b = metas['control'], metas[second]
        equal(set(a), set(b), 'Metadata key set differs')
        c.require({'sut','seed','tool_sha256','harness_sha256','emb_config_sha256','auth_source_sha256',
                   'health_path','base_path','request_timeout_ms','hypothesis_phases','schema_checks',
                   'logger_max_body','host_port','jacoco_port','jacoco_agent_sha256','jacoco_cli_sha256'} <= set(a), 'Missing pair metadata field')
        for key in sorted(set(a) - ALLOWED_META):
            equal(a[key], b[key], 'Unexpected metadata difference: ' + key)
        equal(a['limitations'], b['limitations'], 'Run limitations differ')
        c.require(a['compose_project'] != b['compose_project'], 'Reused Compose project')
        sut_key = 'sut-' + a['sut'] + '-image'
        known_images = {'schema-image','mitmproxy-image',sut_key}
        extra_a = {k:v for k,v in a['images'].items() if k not in known_images}
        extra_b = {k:v for k,v in b['images'].items() if k not in known_images}
        # run_metadata's glob also sees compose.code-image.json, which is a
        # Compose document rather than an image inspect. It is checked above.
        c.require(set(extra_a) <= {'compose.code-image'} and set(extra_b) <= {'compose.code-image'}, 'Unexpected collected image entry')
        equal(extra_a, extra_b, 'Unexpected image metadata difference')
        for key in ('schema-image','mitmproxy-image'):
            equal(a['images'][key]['id'], b['images'][key]['id'], 'Generator/proxy image changed: ' + key)
            equal(a['images'][key]['repo_digests'], b['images'][key]['repo_digests'], 'Generator/proxy digest changed: ' + key)
        for name in ('spec.original.json','spec.test.json','generator-input.json','derecurse-cuts.json','sut-config.env','code.manifest.json','schemathesis-argv.txt','schemathesis-help.txt'):
            equal(c.sha(control / name), c.sha(mutant / name), 'Paired artifact differs: ' + name)
        for service, proxy in [(a['sut_service'], False), ('mitmproxy', True)]:
            ca, cb = (c.inspection(run / (service + '-container.json')) for run in (control, mutant))
            c.require(ca['Id'] != cb['Id'], 'Reused container')
            equal(normalized_runtime(ca, a, control, proxy), normalized_runtime(cb, b, mutant, proxy), 'Container runtime settings differ: ' + service)
            if proxy:
                va = {x.get('Name') for x in ca['Mounts'] if x['Type'] == 'volume'}
                vb = {x.get('Name') for x in cb['Mounts'] if x['Type'] == 'volume'}
                c.require(not va.intersection(vb), 'Shared proxy volume')
    checks.run('pair.equal_scenario_runtime_and_provenance', pair_metadata)
    evidence = {}
    for prefix, directory in [('control', control), (second, mutant)]:
        for p in directory.iterdir() if directory.is_dir() else []:
            if p.is_file() and p.name in ('run.json','code.manifest.json','exchanges.jsonl','spec.original.json','spec.test.json','generator-input.json'):
                try: evidence[f'{prefix}/{p.name}'] = c.sha(p)
                except (OSError, ValueError): pass
    return {**({'kind':'noise'} if kind == 'noise' else {}), 'format': 'e5-pair-validation-v1', 'status': ('PASS_WITH_EXCLUSION' if excluded_ops else 'PASS') if checks.passed else 'FAIL', 'seed': seed,
            'control_run': str(control), (second + '_run'): str(mutant), 'mut_dir': str(mut),
            'checks': checks.rows, 'input_sha256': evidence, 'notes': notes, 'excluded_ops':excluded_ops,
            'junit_errors':{role:[{'testcase_name':name,'error_text':text} for name,text in sorted(junit_errors.get(role,set()))]
                            for role in ('control',second)},
            'limitations': ['Saved evidence and current snapshots only; no Docker/build execution.',
                            'Fresh containers and no SUT mounts do not prove equal business state or identical traces.',
                            'Generator container is ephemeral; its launch settings are evidenced by frozen harness and argv.',
                            'Runtime-base provenance is relative to the rebuilt pair, not the historical SUT image.',
                            'Provenance PASS is not a causal mutation kill or independent IMPL attribution; review JUnit failures manually.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('control_run', type=Path); parser.add_argument('mutant_run', type=Path); parser.add_argument('mut_dir', type=Path)
    parser.add_argument('--report-staging-dir', type=Path, help='Stage the atomic report outside MUT_DIR (same filesystem)')
    parser.add_argument('--kind', choices=('pair','noise'), default='pair')
    args = parser.parse_args(argv)
    try:
        report = validate(args.control_run, args.mutant_run, args.mut_dir, args.kind)
    except (OSError, ValueError, KeyError, TypeError) as error:
        report = {**({'kind':'noise'} if args.kind == 'noise' else {}),
                  'format': 'e5-pair-validation-v1', 'status': 'FAIL', 'seed': 'unknown',
                  'checks': [{'check':'input', 'status':'FAIL', 'detail':str(error)}]}
    prefix, _ = c.layout(args.kind)
    dest = args.mut_dir / (prefix + 'pair-validation-s' + str(report['seed']) + '.json')
    c.atomic_json(dest, report, staging_dir=args.report_staging_dir)
    print(str(dest) + ': ' + report['status'])
    return 0 if report['status'] in ('PASS','PASS_WITH_EXCLUSION') else 1


if __name__ == '__main__':
    sys.exit(main())
