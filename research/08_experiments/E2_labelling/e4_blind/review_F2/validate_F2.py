"""Structural and evidence-locator audit of F2 deliverables; no package imports."""
import collections
import csv
import datetime
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
HEADERS='item_id,L1,L2,proposed_L2,confidence,evidence_types,evidence_locators,both_candidate,intent_search_status,intent_search_verdict,intent_review_verdict,adjudication_flag,history_scope,rationale'.split(',')
ALLOWED_L1={'SPEC','SPEC_PARTIAL','IMPL','IMPL_PARTIAL','TEST','ENV','UNDECIDABLE','DEFERRED'}
CHECKS=['a_explicit_behavior','b_target_scenario_linkage','c_independent_basis','d_applicable_revision','e_opposing_evidence_reviewed']
EXPECTED_ABSENT_ITEMS={1,5,6,10,11,13,16,17,18,21,23,29,30,32,33,39,43,44,47}

def run():
    original=list(csv.DictReader((ROOT/'items.csv').open()))
    with (ROOT/'labels_F2.csv').open() as f:
        reader=csv.DictReader(f);assert reader.fieldnames==HEADERS;rows=list(reader)
    assert len(rows)==50
    assert [r['item_id'] for r in rows]==[r['item_id'] for r in original]==[f'I{n:03}' for n in range(1,51)]
    documents={p:json.loads((ROOT/p/'spec.json').read_text()) for p in ['K01','K02','K03','K04']}
    traces={p:list((ROOT/p/'r1/exchanges.jsonl').open()) for p in documents}
    assert len(list((ROOT/'review_F2').glob('I[0-9][0-9][0-9].json')))==50
    counts=collections.Counter();by_package={p:collections.Counter() for p in documents}
    expected_absent=[];integrity=[];hit_count=0;max_words=0
    for r,item in zip(rows,original):
        iid=r['item_id'];n=int(iid[1:]);package=item['package']
        assert r['L1'] in ALLOWED_L1 and r['confidence'] in {'1','2','3'}
        assert r['both_candidate'] in {'true','false'}
        assert r['history_scope']=='unavailable'
        assert r['intent_search_status'] in {'complete','incomplete','not_run'}
        assert r['intent_search_verdict'] in {'supports_code','supports_spec','conflicting','none_found','NA'}
        assert r['intent_review_verdict'] in {'supports_impl_behavior','supports_spec_behavior','conflicting','none_found','not_applicable'}
        words=len(r['rationale'].split());assert words<=40;max_words=max(words,max_words)
        review=json.loads((ROOT/'review_F2'/f'{iid}.json').read_text())
        assert review['item_id']==iid and review['decision']['L1']==r['L1']
        assert datetime.datetime.fromisoformat(review['start_time'])<=datetime.datetime.fromisoformat(review['search_run']['start_time'])<=datetime.datetime.fromisoformat(review['end_time'])
        assert review['target_proposition']['method']==item['method']
        assert review['target_proposition']['path_template']==item['template']
        assert isinstance(review['mandatory_search']['required'],bool) and review['mandatory_search']['reason']
        for suffix in ['json','stderr','exitcode']:
            p=ROOT/'search_F2'/f'{iid}.{suffix}';assert p.is_file()
            content=p.read_bytes();integrity.append({'file':str(p.relative_to(ROOT)),'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
        rawbytes=(ROOT/'search_F2'/f'{iid}.json').read_bytes()
        code=int((ROOT/'search_F2'/f'{iid}.exitcode').read_text())
        if code==0:
            raw=json.loads(rawbytes)
            assert raw['scan']['complete']
            assert raw['independent_evidence']==r['intent_search_verdict']
            assert len(raw['hits'])==len(review['hits'])
        else:
            assert code==2 and not rawbytes and r['intent_search_verdict']=='NA'
            assert 'operation missing or ambiguous' in (ROOT/'search_F2'/f'{iid}.stderr').read_text()
            if r['intent_search_status']=='complete':
                assert any(m['disposition']=='accept' for m in review['manual_additions'])
        assert [h['index'] for h in review['hits']]==list(range(len(review['hits'])))
        for h in review['hits']+review['manual_additions']:
            assert h['disposition'] in {'accept','reject','context','unresolved'}
            assert all(k in h['checklist'] for k in CHECKS)
            if h['disposition']=='accept':assert all(h['checklist'][k] is True for k in CHECKS)
        hit_count+=len(review['hits'])
        if r['intent_search_status']=='incomplete':assert r['L1']=='DEFERRED' and r['intent_review_verdict']!='none_found'
        exchange=json.loads(traces[package][int(item['example_exchange'])])
        assert exchange['request']['method']==item['method']
        assert exchange['response']['status']==int(item['status'])
        evidence=r['evidence_locators'].split(';')
        assert f"{package}/r1/exchanges.jsonl:{int(item['example_exchange'])+1}" in evidence
        assert any('/source/' in e for e in evidence)
        for e in evidence:
            if '/spec.json#' in e:
                filename,pointer=e.split('#',1);node=documents[filename.split('/')[0]]
                try:
                    for k in pointer.lstrip('/').split('/'):
                        k=k.replace('~1','/').replace('~0','~')
                        node=node[int(k)] if isinstance(node,list) else node[k]
                except (KeyError,IndexError):
                    assert n in EXPECTED_ABSENT_ITEMS,(iid,e)
                    expected_absent.append({'item_id':iid,'locator':e,'reason':'Explicitly cited absent operation/status/required constraint'})
            elif ':' in e:
                filename,line=e.rsplit(':',1);p=ROOT/filename
                assert p.is_file() and 1<=int(line)<=sum(1 for _ in p.open()),e
            else:assert (ROOT/e).is_file(),e
        counts[r['L1']]+=1;by_package[package][r['L1']]+=1
    assert (ROOT/'report_F2.md').is_file()
    result={'passed':True,'validation_time':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'items':50,'review_files':50,'raw_result_sets':50,'reviewed_raw_hits':hit_count,
        'maximum_rationale_words':max_words,'primary_labels':dict(counts),
        'by_package':{k:dict(v) for k,v in by_package.items()},
        'search_statuses':dict(collections.Counter(r['intent_search_status'] for r in rows)),
        'checks':['exact headers, unique item order and full coverage','allowed labels/verdicts/flags','physical exchange lines match method and status','source and log file:line references exist','spec pointers resolve or document an expected absence','review start/search/end timestamps','every raw hit has indexed disposition and checklist','accepted evidence passes all five criteria','failed searches retain empty raw stdout, stderr and exit code','incomplete retrieval is deferred','all rationales are at most 40 words','raw artifact SHA-256 manifest'],
        'expected_absent_spec_pointers':expected_absent,'raw_artifact_integrity':integrity,
        'limitations':'Structural checks do not independently validate the human semantic judgments; no package code was executed.'}
    (ROOT/'review_F2'/'validation_F2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'raw_artifact_integrity','expected_absent_spec_pointers','checks'}},ensure_ascii=False,indent=2))

if __name__=='__main__':run()
