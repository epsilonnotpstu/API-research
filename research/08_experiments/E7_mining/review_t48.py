#!/usr/bin/python3
"""Immutable, private continuation evidence and individual review records."""
import argparse
from collections import Counter
import csv
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE = Path(__file__).resolve().parent
KEY = HERE / 'key'
M = runpy.run_path(str(HERE / 'mine2.py'))
CODES = set('ACCEPT NOT_CONTRACT_RELATED NEW_FEATURE_OR_ENDPOINT REFACTOR_OR_RENAME GENERATED_OR_DOCS_ONLY_CHURN BOTH_CHANGED_TO_NEW_BEHAVIOUR NO_PARENT_MISMATCH TEST_OR_CLIENT_ONLY TOO_LARGE_TO_ESTABLISH OTHER'.split())


def guard():
    baseline = json.loads((KEY / 'preservation_t48_start.json').read_text())
    assert all(hashlib.sha256((HERE / p).read_bytes()).hexdigest() == digest
               for p, digest in baseline.items()), 'Existing private or frozen bytes changed'


@lru_cache(maxsize=1)
def sources():
    return json.loads((KEY / 'pool2_sources.json').read_text())


def private_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def display(text):
    text = M['safe'](text)
    text = re.sub(r'(?im)^([+ -]*\s*(?:password|refreshToken|accessToken|trustKey):)\s*[^\n]+', r'\1 <redacted>', text)
    text = re.sub(r'(?i)\bpre[- ]+[\w\x27-]+\s+(?=commit\b)', '[attribution] ', text)
    text = re.sub(r'\b[0-9a-f]{7,64}\b', '[history]', text, flags=re.I)
    text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '[date]', text)
    return text


def evidence(row):
    require_current(row)
    record_preview(row, 'patch')
    path = KEY / 't48_evidence' / (row['candidate_id'] + '.diff')
    if not path.exists():
        path.parent.mkdir(exist_ok=True)
        text = M['safe'](M['git'](row['repo'], 'diff', '--no-ext-diff', '--no-textconv',
                                  '--unified=3', row['parent_commit'], row['fix_commit']).decode('utf-8', 'replace'))
        with path.open('x') as stream:
            stream.write(text)
    return path, path.read_text()


def chunks(row, text):
    result = []
    for chunk in text.split('diff --git ')[1:]:
        path = chunk.splitlines()[0].split(' b/')[-1]
        if M['excluded'](path) or not (M['production'](path) or path in row['surface_paths']):
            continue
        lines = chunk.splitlines()[1:]
        delta = [line for line in lines if line.startswith(('+', '-'))
                 and not line.startswith(('+++', '---', '+import ', '-import ', '+package ', '-package '))
                 and line[1:].strip() and not re.match(r'^[+-]\s*(?:/\*|\*|//|#|\[REDACTED)', line)]
        result.append((path, lines, delta))
    return result


def prior_yield():
    with (HERE/'yield_t47.csv').open() as stream:
        return list(csv.DictReader(stream))


def prior_counts():
    return {r['repo']:int(r['last_reviewed_rank']) for r in prior_yield()}


def previous_items():
    return (json.loads((KEY/'new_accepted.json').read_text())
            + json.loads((KEY/'new_accepted2.json').read_text())
            + [json.loads(p.read_text()) for p in sorted((KEY/'t47_items').glob('*.json'))])


def decisions():
    return [json.loads(p.read_text()) for p in (KEY/'t48_decisions').glob('*.json')]


def plan():
    previous=prior_yield()
    for phase,limit,rows in [(1,150,[r for r in previous if r['stopped']=='T47 target reached']),
                              (2,250,previous)]:
        for old in rows:
            for rank in range(int(old['last_reviewed_rank'])+1,min(limit,int(old['pool2']))+1):
                if phase==2 and old['stopped']=='T47 target reached' and rank<=150:
                    continue
                yield phase,old['repo'],rank


def next_row():
    done={(r['repo'],r['rank']) for r in decisions()}
    decided={r['candidate_id'] for r in decisions()}
    new=[r for r in accepted() if r['candidate_id'] in decided]
    if len(new)>=40:return None
    counts=Counter(r['repo'] for r in previous_items()+new)
    source={(r['repo'],r['rank']):r for r in sources()}
    for phase,repo,rank in plan():
        if counts[repo]>=10 or (repo,rank) in done:continue
        return dict(source[repo,rank],review_phase=phase)
    return None


def require_current(row):
    current=next_row()
    assert current and row['candidate_id']==current['candidate_id'], 'Candidate is outside current final decision'


def record_preview(row,kind):
    folder=KEY/'t48_previews';folder.mkdir(exist_ok=True)
    paths=list(folder.glob('*.json'))
    # No next candidate can be opened until the current candidate is final.
    prior={p.stem.split('_',1)[1] for p in paths}
    done={d['candidate_id'] for d in decisions()}
    assert prior-done <= {row['candidate_id']}
    private_json(folder/(str(len(paths)+1).zfill(6)+'_'+row['candidate_id']+'.json'),
                 dict(sequence=len(paths)+1,candidate_id=row['candidate_id'],repo=row['repo'],rank=row['rank'],
                      action=kind,final_decisions_before=len(done)))


def select(repo, start, end):
    prior = prior_counts()
    assert start > prior[repo], 'Already reviewed before T48'
    return [r for r in sources() if r['repo'] == repo and start <= r['rank'] <= end]


def screen(repo, start, end, limit=8, paths=4, full=False):
    assert start == end, 'Only the candidate under final decision may be opened'
    for row in select(repo, start, end):
        _, text = evidence(row)
        cs = chunks(row, text)
        title = re.sub(r'(?<!\w)@[\w.-]+', '[attribution]', display(row['message_excerpt']))
        print(f"{repo} {row['rank']} [{len(text.splitlines())} lines] {title}")
        for path, lines, delta in cs[:paths]:
            print(' ', path)
            chosen = [line for line in lines if not line.startswith(('index ', '---', '+++'))] if full else delta
            for line in chosen[:limit]:
                print('  ' + display(line)[:350])
            if len(chosen) > limit:
                print(f'  [{len(chosen)-limit} additional lines saved privately]')
        if len(cs) > paths:
            print(f' [{len(cs)-paths} additional paths saved privately]')


def decide(repo, rank, code, reason=None):
    assert code in CODES
    row = next(r for r in sources() if r['repo'] == repo and r['rank'] == rank)
    path, text = evidence(row)
    if reason is None:
        cs = chunks(row, text)
        first = next((c for c in cs if c[2]), cs[0] if cs else (row['surface_paths'][0], [], []))
        title = re.sub(r'\([^)]*\)|#\d+|\bfix(?:ed|es)?\b|(?<!\w)@[\w.-]+', '', display(row['message_excerpt']), flags=re.I).strip(' :')
        delta = next((line[1:].strip() for line in first[2] if line[1:].strip()), '')
        tails = {
            'NOT_CONTRACT_RELATED': 'Internal concern; no established operation discrepancy.',
            'NEW_FEATURE_OR_ENDPOINT': 'Adds behaviour; existing discrepancy unestablished.',
            'REFACTOR_OR_RENAME': 'Refactoring; wire discrepancy unestablished.',
            'GENERATED_OR_DOCS_ONLY_CHURN': 'Documentation or generated churn; parent discrepancy unestablished.',
            'BOTH_CHANGED_TO_NEW_BEHAVIOUR': 'Both surfaces adopt new behaviour.',
            'NO_PARENT_MISMATCH': 'Parent contract discrepancy unestablished.',
            'TEST_OR_CLIENT_ONLY': 'Test or client concern.',
            'TOO_LARGE_TO_ESTABLISH': 'Patch exceeds bounded static comparison.',
            'OTHER': 'Excluded after individual screen.',
        }
        tail = tails.get(code, 'Exact-parent evidence verified.')
        prefix = Path(first[0]).name + ': ' + ' '.join(title.split()[:6]) + '; ' + ' '.join(delta.split()[:5])
        reason = ' '.join(prefix.split()[:25-len(tail.split())]) + ' ' + tail
    assert reason.strip() and len(reason.split()) <= 25
    target = KEY / 't48_decisions' / (repo + '_' + str(rank).zfill(3) + '.json')
    private_json(target, dict(candidate_id=row['candidate_id'], repo=repo, rank=rank,
                 review_status='accepted' if code == 'ACCEPT' else 'deferred' if code in {'NO_PARENT_MISMATCH', 'TOO_LARGE_TO_ESTABLISH'} else 'rejected',
                 reason_code=code, reason=reason, review_evidence=str(path.relative_to(HERE)),
                 patch_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), patch_lines=len(text.splitlines()),
                 review_depth='exact parent contract/implementation and resolving patch' if code == 'ACCEPT' else 'individual sanitized patch screen; unproved pairs deferred'))


def probe(repo, rank, path_pattern, pattern, context=4, limit=180, child=False):
    row = next(r for r in sources() if r['repo'] == repo and r['rank'] == rank)
    require_current(row)
    record_preview(row, 'child probe' if child else 'parent probe')
    rev = row['fix_commit'] if child else row['parent_commit']
    tree = M['git'](repo, 'ls-tree', '-r', '--name-only', rev).decode().splitlines()
    count = 0
    for path in tree:
        if not re.search(path_pattern, path):
            continue
        lines = M['safe'](M['git'](repo, 'show', rev + ':' + path).decode('utf-8', 'replace')).splitlines()
        hits = [i for i, line in enumerate(lines) if re.search(pattern, line)]
        nums = sorted({j for i in hits for j in range(max(0, i-context), min(len(lines), i+context+1))})
        if nums:
            print('PATH', path)
        for j in nums[:limit-count]:
            print(str(j+1) + ': ' + display(lines[j])[:600])
        count += min(len(nums), limit-count)
        if count >= limit:
            print('[bounded view; complete parent file available read-only]')
            break


def accepted():
    return [json.loads(p.read_text()) for p in sorted((KEY/'t48_items').glob('*.json'))]


def accept(repo, rank, operation, x, y, direction, kind, family, contract,
           implementation, route=(), helpers=(), confidence=3):
    row = dict(next(r for r in sources() if r['repo'] == repo and r['rank'] == rank))
    tree = M['git'](repo, 'ls-tree', '-r', '--name-only', row['parent_commit']).decode().splitlines()
    checks = {}; excerpts = {}
    for role, selectors in [('contract', contract), ('implementation', implementation), ('route', route)]:
        checks[role] = []
        for suffix, pattern in selectors:
            paths = [p for p in tree if p.endswith(suffix)]
            assert len(paths) == 1, (repo, rank, 'ambiguous path', suffix)
            path = paths[0]
            text = M['safe'](M['git'](repo, 'show', row['parent_commit']+':'+path).decode('utf-8', 'replace'))
            lines = text.splitlines()
            hits = [i for i, line in enumerate(lines, 1) if re.search(pattern, line)]
            assert hits, (repo, rank, 'missing parent selector', suffix)
            checks[role].extend(row['parent_commit']+':'+path+':'+str(i) for i in hits)
            excerpts[path] = dict(parent_lines=hits, parent_numbered_excerpt='\n'.join(
                str(i)+': '+line for i, line in enumerate(lines, 1) if any(abs(i-h)<=5 for h in hits)))
    helper_paths = []
    for suffix in helpers:
        matches = [p for p in tree if p.endswith(suffix)]
        assert len(matches) == 1
        helper_paths.extend(matches)
    path, patch = evidence(row)
    previous = previous_items()
    with (HERE.parent/'E6_realfix/combined_accepted.csv').open() as stream:
        exploratory = list(csv.DictReader(stream))
    additions = accepted()
    assert (repo, operation, family) not in {(r['repo'],r['operation'],r['fix_family']) for r in previous+exploratory+additions}
    assert Counter(r['repo'] for r in previous+additions)[repo] < 10
    assert direction in {'SPEC','IMPL','BOTH'} and checks['contract'] and checks['implementation']
    row.update(item_id='N48_'+str(len(additions)+1).zfill(3), set='new', source_task='T48',
               operation=operation, proposition=operation+': contract says '+x+'; implementation does '+y,
               truth_direction=direction, confidence=confidence, contract_kind=kind,
               mismatch_type=family.split('.')[0], fix_family=family,
               proposition_check=json.dumps(checks,separators=(',',':')),
               evidence=json.dumps(dict(parent=excerpts,patch=str(path.relative_to(HERE)),
                   patch_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                   gate='Explicit static parent comparison and resolving patch; no runtime execution.'),ensure_ascii=False),
               helper_paths=helper_paths,
               inference_notes='⚠️ Dispatch, validation and serialization inferred statically; no upstream execution.')
    private_json(KEY/'t48_items'/(row['item_id']+'.json'),row)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['screen', 'decide', 'probe', 'status'])
    parser.add_argument('repo', nargs='?')
    parser.add_argument('--start', type=int, default=61)
    parser.add_argument('--end', type=int, default=150)
    parser.add_argument('--lines', type=int, default=8)
    parser.add_argument('--paths', type=int, default=4)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--codes')
    parser.add_argument('--path')
    parser.add_argument('--pattern')
    parser.add_argument('--child', action='store_true')
    args = parser.parse_args()
    if args.action == 'screen':
        screen(args.repo, args.start, args.end, args.lines, args.paths, args.full)
    elif args.action == 'probe':
        probe(args.repo, args.start, args.path, args.pattern, limit=args.lines, child=args.child)
    elif args.action == 'decide':
        codes = {'N':'NOT_CONTRACT_RELATED', 'F':'NEW_FEATURE_OR_ENDPOINT', 'R':'REFACTOR_OR_RENAME', 'G':'GENERATED_OR_DOCS_ONLY_CHURN', 'B':'BOTH_CHANGED_TO_NEW_BEHAVIOUR', 'D':'NO_PARENT_MISMATCH', 'T':'TEST_OR_CLIENT_ONLY', 'L':'TOO_LARGE_TO_ESTABLISH', 'O':'OTHER'}
        entries = args.codes.split(',')
        planned = []
        for entry in entries:
            ranks, code = entry.split('=')
            ends = [int(v) for v in ranks.split(':')]
            for rank in range(ends[0], ends[-1]+1):
                planned.append((rank, codes[code]))
        assert len(planned)==len({rank for rank, _ in planned})
        assert all(not (KEY/'t48_decisions'/(args.repo+'_'+str(rank).zfill(3)+'.json')).exists() for rank,_ in planned)
        for rank, code in planned:
            decide(args.repo, rank, code)
        print('Individual decisions saved:', len(list((KEY/'t48_decisions').glob(args.repo+'_*.json'))))
    else:
        guard()
        print(json.dumps(dict(preserved=True, prior_reviewed=dict(prior_counts()))))


if __name__ == '__main__':
    main()
