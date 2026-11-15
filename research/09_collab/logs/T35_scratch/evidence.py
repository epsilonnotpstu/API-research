"""Derive T35 safe aggregates, source provenance and saved stack-frame locators."""
import collections
import hashlib
import io
import json
import re
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EMB = ROOT / '08_experiments/_external/emb'
TREE = EMB / 'jdk_11_maven/cs/rest-gui/market'


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, n):
        value = self.data[self.pos:self.pos+n]
        self.pos += n
        return value

    def u(self, n):
        return int.from_bytes(self.take(n), 'big')


def class_info(raw):
    """Parse JVM class DATA; never load or execute Java code."""
    r = Reader(raw)
    assert r.u(4) == 0xcafebabe
    r.take(4)
    cp = [None] * r.u(2)
    i = 1
    while i < len(cp):
        tag = r.u(1)
        if tag == 1:
            cp[i] = (tag, r.take(r.u(2)).decode('utf-8', 'replace'))
        elif tag in (3,4):
            cp[i] = (tag, r.take(4).hex())
        elif tag in (5,6):
            cp[i] = (tag, r.take(8).hex())
            i += 1
        elif tag in (7,8,16,19,20):
            cp[i] = (tag, r.u(2))
        elif tag in (9,10,11,12,17,18):
            cp[i] = (tag, r.u(2), r.u(2))
        elif tag == 15:
            cp[i] = (tag, r.u(1), r.u(2))
        else:
            raise ValueError('unsupported class constant tag')
        i += 1

    def resolve(i):
        x = cp[i]
        if x[0] == 1:
            return x[1]
        if x[0] in (7,8):
            return resolve(x[1])
        if x[0] in (9,10,11,12):
            return resolve(x[1]) + '.' + resolve(x[2])
        return str(x[0])

    def attrs(stream):
        result = {}
        for _ in range(stream.u(2)):
            name = resolve(stream.u(2))
            result[name] = stream.take(stream.u(4))
        return result

    r.take(6)
    r.take(2*r.u(2))
    for _ in range(r.u(2)):
        r.take(6)
        attrs(r)
    methods = []
    for _ in range(r.u(2)):
        r.take(2)
        name, desc = resolve(r.u(2)), resolve(r.u(2))
        a = attrs(r)
        item = {'name':name, 'descriptor':desc}
        if 'Code' in a:
            cr = Reader(a['Code'])
            cr.take(4)
            code = cr.take(cr.u(4))
            cr.take(8*cr.u(2))
            ca = attrs(cr)
            lr = Reader(ca.get('LineNumberTable', b'\0\0'))
            line_map = [(lr.u(2),lr.u(2)) for _ in range(lr.u(2))]
            item['line_numbers'] = sorted(set(line for pc,line in line_map))
            if b'Expected relation name' in raw and name == 'deserialize' and len(code) > 10:
                # Only the prefix up to the first explicit athrow is needed.
                simple = {0x2a:'aload_0',0x2b:'aload_1',0x2c:'aload_2',0x2d:'aload_3',
                          0x4e:'astore_3',0x59:'dup',0xbf:'athrow',0x00:'nop'}
                refs = {0xb2:'getstatic',0xb6:'invokevirtual',0xb7:'invokespecial',0xb8:'invokestatic',0xbb:'new'}
                dis = []
                pc = 0
                while pc < len(code) and pc < 120:
                    op, start = code[pc], pc
                    pc += 1
                    ins = {'pc':start,'line':next((ln for off,ln in reversed(line_map) if off<=start),None)}
                    if op in simple:
                        ins['opcode'] = simple[op]
                    elif op in refs:
                        ins.update(opcode=refs[op], reference=resolve(int.from_bytes(code[pc:pc+2],'big')))
                        pc += 2
                    elif op in (0x12,0x13):
                        n = 1 if op == 0x12 else 2
                        ins.update(opcode='ldc',reference=resolve(int.from_bytes(code[pc:pc+n],'big')))
                        pc += n
                    elif op in (0xa5,0xa6,0x99,0x9a,0xa7):
                        ins.update(opcode={0xa5:'if_acmpeq',0xa6:'if_acmpne',0x99:'ifeq',0x9a:'ifne',0xa7:'goto'}[op],
                                   target=start+int.from_bytes(code[pc:pc+2],'big',signed=True))
                        pc += 2
                    else:
                        ins.update(opcode='unparsed',byte=hex(op))
                        dis.append(ins)
                        break
                    dis.append(ins)
                    if op == 0xbf:
                        break
                item['prefix_data_disassembly'] = dis
        methods.append(item)
    a = attrs(r)
    return {'source_file':resolve(int.from_bytes(a['SourceFile'],'big')) if 'SourceFile' in a else None,
            'methods':methods}


def provenance():
    summaries = json.loads((OUT / 'traffic_summary.json').read_text())
    jar = TREE / 'market-rest/target/market-sut.jar'
    dist = EMB / 'dist/market-sut.jar'
    jar_raw = jar.read_bytes()
    result = {'source_tree':str(TREE.relative_to(ROOT)),
              'jar_sha256':sha(jar_raw),'dist_sha256':sha(dist.read_bytes()),
              'all_12_recorded_jars_match':all(x['metadata']['sut_jar_sha256']==sha(jar_raw) for x in summaries),
              'all_12_code_mutation_null':all(x['metadata']['code_mutation'] is None for x in summaries),
              'all_12_configured_auth_user':all(x['metadata']['auth']=='user' for x in summaries),
              'source_spec_sha256':sha((EMB/'openapi-swagger/market.json').read_bytes()),
              'all_12_source_spec_matches':all(x['metadata']['source_sha256']==sha((EMB/'openapi-swagger/market.json').read_bytes()) for x in summaries),
              'config_hashes':{}, 'classes':[], 'log_traces':[], 'generator_binding':[]}
    for entry in summaries:
        run = ROOT / '08_experiments/E1_pilot/runs/market' / entry['run']
        meta = json.loads((run/'run.json').read_text())
        if meta.get('fuzzer','schemathesis')=='evomaster':
            result['generator_binding'].append({'run':entry['run'],
                'argv_mentions_spec_test':any('spec.test.json' in str(v) for v in meta['evomaster_argv']),
                'recorded_spec_test_hash_matches':meta['file_sha256']['spec.test.json']==sha((run/'spec.test.json').read_bytes())})
    for f in ('dockerfiles/market.yaml','dockerfiles/market.dockerfile'):
        digest = sha((EMB / f).read_bytes())
        result['config_hashes'][f] = {'sha256':digest,'all_12_recorded_match':all(x['metadata']['emb_config_sha256'][f]==digest for x in summaries)}
    with zipfile.ZipFile(io.BytesIO(jar_raw)) as z:
        libname = 'BOOT-INF/lib/spring-hateoas-1.2.4.jar'
        with zipfile.ZipFile(io.BytesIO(z.read(libname))) as lib:
            cn = 'org/springframework/hateoas/mediatype/hal/Jackson2HalModule$HalLinkListDeserializer.class'
            result['hal_deserializer'] = {'jar_member':libname+'!/'+cn,**class_info(lib.read(cn))}
        core = zipfile.ZipFile(io.BytesIO(z.read('BOOT-INF/lib/market-core-0.1.2.jar')))
        for module, classpath in [
            ('market-rest','market/rest/ContactsRestController.class'),
            ('market-rest','market/rest/exception/RestExceptionHandler.class'),
            ('market-rest','market/rest/exception/RestErrorResponse.class'),
            ('market-core','market/dto/ContactsDTO.class'),
            ('market-core','market/service/impl/ContactsServiceImpl.class')]:
            raw = z.read('BOOT-INF/classes/'+classpath) if module=='market-rest' else core.read(classpath)
            target = TREE / module / 'target/classes' / classpath
            result['classes'].append({'class':classpath,'sha256':sha(raw),
                'target_class_matches':target.read_bytes()==raw,**class_info(raw)})
    for seed in (1,3):
        p = ROOT / f'08_experiments/E1_pilot/runs/market/20261114T183929Z_batch_940129_mutated_REQUEST_STRICT_p30_s{seed}/compose.log'
        raw = p.read_bytes()
        lines = raw.decode().split('\n')
        hit = next(i for i,l in enumerate(lines) if 'Expected relation name' in l)
        frames = []
        for n in range(hit,min(hit+400,len(lines))):
            line = lines[n]
            if 'at ' in line and any(x in line for x in ('Jackson2HalModule','AbstractJackson2HttpMessageConverter','readWithMessageConverters','RequestResponseBodyMethodProcessor.resolveArgument')):
                frame = line.split('at ',1)[1].strip()
                if re.fullmatch(r'[A-Za-z0-9_.$]+\([A-Za-z0-9_.]+:[0-9]+\)',frame):
                    frames.append({'line':n+1,'frame':frame})
        result['log_traces'].append({'capture':str(p.relative_to(ROOT)), 'sha256':sha(raw),
            'first_error_line':hit+1,
            'first_error_has_HttpMessageNotReadableException':'HttpMessageNotReadableException' in lines[hit],
            'first_HttpMessageNotReadableException_line':next(i+1 for i in range(hit,min(hit+400,len(lines))) if 'org.springframework.http.converter.HttpMessageNotReadableException:' in lines[i]),
            'first_JsonMappingException_line':next(i+1 for i in range(hit,min(hit+400,len(lines))) if 'Caused by: com.fasterxml.jackson.databind.JsonMappingException' in lines[i]),
            'first_JsonParseException_line':next(i+1 for i in range(hit,min(hit+400,len(lines))) if 'Caused by: com.fasterxml.jackson.core.JsonParseException: Expected relation name' in lines[i]),
            'frames':frames})
    dump('provenance.json',result)


def aggregates():
    contacts = [json.loads(l) for l in (OUT/'contacts.jsonl').open()]
    eligible = [json.loads(l) for l in (OUT/'eligible.jsonl').open()]
    result = {}
    for run in dict.fromkeys(r['run'] for r in contacts):
        allrows = [r for r in contacts if r['run']==run]
        groups = {'all_contacts':allrows,
                  'eligible_contacts':[r for r in allrows if r['eligible']],
                  'accepted_contacts':[r for r in allrows if 200<=r['status']<300]}
        entry = {}
        for name,rows in groups.items():
            entry[name] = {'n':len(rows),'lines':[r['line'] for r in rows],
                'counts':{key:dict(collections.Counter(json.dumps(r[key],sort_keys=True) for r in rows))
                  for key in ('auth_state','cookie_present','content_type','links_shape','links_count','phone_length',
                              'address_length','body_keys','body_json_parse_error','all_link_properties_present',
                              'all_link_strings_length_le_1','query_name_lengths','empty_field_errors',
                              'raw_links_array_prefix','first_body_key','null_entity_name')
                  if all(key in r for r in rows)},
                'no_preceding_delete':sum(r['previous_delete'] is None for r in rows),
                'preceding_delete_status':dict(collections.Counter(str(r['previous_delete']['status']) for r in rows if r['previous_delete']))}
        good=[r for r in eligible if r['run']==run and 200<=r['status']<300]
        entry['all_eligible_accepted_ops'] = dict(collections.Counter(r['operation'] for r in good))
        entry['first_accepted_by_op'] = {op:next(r for r in good if r['operation']==op) for op in dict.fromkeys(r['operation'] for r in good)}
        result[run] = entry
    dump('aggregates.json',result)


def freeze():
    inputs = json.loads((OUT/'inputs_sha256.json').read_text())
    for p in list((ROOT/'08_experiments/tools').glob('*.py')) + list((ROOT/'08_experiments/E1_pilot/harness_v2').rglob('*')) + list(TREE.rglob('*.java')) + list(TREE.rglob('pom.xml')):
        if p.is_file() and '__pycache__' not in p.parts:
            inputs[str(p.relative_to(ROOT))] = sha(p.read_bytes())
    for p in [EMB/'openapi-swagger/market.json',EMB/'dockerfiles/market.dockerfile',EMB/'dockerfiles/market.yaml',EMB/'dist/market-sut.jar',TREE/'market-rest/target/market-sut.jar',ROOT/'08_experiments/E1_pilot/pilot_results/fuzzer_trajectory_overlap.csv']:
        inputs[str(p.relative_to(ROOT))] = sha(p.read_bytes())
    for seed in (1,3):
        p=ROOT/f'08_experiments/E1_pilot/runs/market/20261114T183929Z_batch_940129_mutated_REQUEST_STRICT_p30_s{seed}/compose.log'
        inputs[str(p.relative_to(ROOT))] = sha(p.read_bytes())
    dump('protected_sha256.json',inputs)


def findings():
    data=json.loads((OUT/'aggregates.json').read_text())
    summaries=json.loads((OUT/'traffic_summary.json').read_text())
    contacts=[json.loads(l) for l in (OUT/'contacts.jsonl').open()]
    eligible=[json.loads(l) for l in (OUT/'eligible.jsonl').open()]
    output=[]
    for seed in (1,3):
        fresh=f'20261114T183929Z_batch_940129_mutated_REQUEST_STRICT_p30_s{seed}'
        base=f'20261114T183929Z_batch_940129_baseline_NONE_p0_s{seed}'
        fs=next(r for r in summaries if r['run']==fresh)
        bs=next(r for r in summaries if r['run']==base)
        valid=[r for r in contacts if r['run']==fresh and r['eligible']]
        good=[r for r in contacts if r['run']==base and r['status']==200]
        output.append({'seed':seed,'fresh_run':fresh,'baseline_run':base,
            'fresh_eligible_contacts':{k:v for k,v in data[fresh]['eligible_contacts'].items() if k!='lines'},
            'baseline_accepted_contacts':{k:v for k,v in data[base]['accepted_contacts'].items() if k!='lines'},
            'fresh_contacts_status':fs['contacts_status'], 'baseline_contacts_status':bs['contacts_status'],
            'baseline_all_eligible_accepted_ops':data[base]['all_eligible_accepted_ops'],
            'baseline_array_error_count':sum(r['run']==base and r['links_shape']=='array' and r['response_kind']=='Expected relation name' for r in contacts),
            'fresh_phone_breach':sum(any(p.endswith('/phone/maxLength') for p in r['breaches']) for r in valid),
            'fresh_address_breach':sum(any(p.endswith('/address/maxLength') for p in r['breaches']) for r in valid),
            'fresh_all_error_markers':all(all(r['response_evidence'].values()) for r in valid),
            'first_fresh_example':valid[0], 'first_baseline_accepted_example':good[0],
            'first_empty_links_example':next(r for r in valid if r['links_count']==0)})
    for seed in (1,2,3):
        run=f'20261114T104059Z_batch_339514_mutated_REQUEST_STRICT_p30_s{seed}'
        summary=next(r for r in summaries if r['run']==run)
        output.append({'seed':seed,'schemathesis_run':run,'contacts_status':summary['contacts_status'],
            'eligible_contacts_status':summary['contacts_eligible_status'],
            'accepted_by_operation':data[run]['all_eligible_accepted_ops'],
            'accepted_breach_keywords_by_operation':{op:dict(collections.Counter(p.rsplit('/',1)[-1]
                for row in eligible if row['run']==run and row['operation']==op and 200<=row['status']<300
                for p in row['breaches'])) for op in data[run]['all_eligible_accepted_ops']},
            'first_accepted_by_operation':data[run]['first_accepted_by_op']})
    run='20261114T183929Z_batch_940129_mutated_REQUEST_STRICT_p30_s2'
    summary=next(r for r in summaries if r['run']==run)
    output.append({'seed':2,'evomaster_run':run,'eligible_status':summary['eligible_status'],
        'contacts_status':summary['contacts_status'],'accepted_contacts_n':data[run]['accepted_contacts']['n'],
        'accepted_contacts_links_shapes':data[run]['accepted_contacts']['counts']['links_shape']})
    with (OUT/'findings.jsonl').open('w') as f:
        for row in output:
            f.write(json.dumps(row,ensure_ascii=False)+'\n')


if __name__ == '__main__':
    provenance()
    aggregates()
    findings()
    freeze()
