#!/usr/bin/python3
"""Audit the frozen continuation, byte-order cap and sequential preview ledger."""
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
KEY = HERE / 'key'
R = runpy.run_path(str(HERE / 'review_t49.py'))
validate_previews = runpy.run_path(str(HERE / 'finalize_t48.py'))['validate_previews']


def audit():
    R['guard']()
    freeze = json.loads((HERE / 'freeze2.json').read_text())
    for name, field in [('pool2.json', 'pool_sha256'),
                        ('key/pool2_sources.json', 'source_sha256'), ('mine2.py', 'code_sha256')]:
        assert freeze[field] == hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    new, previous, decisions = R['accepted'](), R['previous_items'](), R['decisions']()
    old_counts = Counter(r['repo'] for r in previous)
    by_pair = {(d['repo'], d['rank']): d for d in decisions}
    assert len(by_pair) == len(decisions)
    by_candidate = {}
    for row in new:
        by_candidate.setdefault(row['candidate_id'], []).append(row)
    sources = {(r['repo'], r['rank']): r for r in R['sources']()}
    capped = [json.loads(p.read_text()) for p in sorted((KEY / 't49_capped').glob('*.json'))]
    expected, ordered, cap_rows = [], [], []
    counts = Counter()
    total = 0
    valid_counts = []
    for _, repo, rank in R['plan']():
        if total >= 40:
            break
        if old_counts[repo] + counts[repo] >= 10:
            continue
        pair = repo, rank
        assert pair in by_pair, 'Missing ranked final decision: ' + str(pair)
        d, source = by_pair[pair], sources[pair]
        assert d['candidate_id'] == source['candidate_id']
        assert d['reason_code'] in R['CODES']
        assert 0 < len(d['reason'].split()) <= 25
        assert hashlib.sha256((HERE / d['review_evidence']).read_bytes()).hexdigest() == d['patch_sha256']
        additions = by_candidate.get(d['candidate_id'], [])
        valid = R['valid_items'](d['candidate_id'])
        excluded = [r for r in capped if r['candidate_id'] == d['candidate_id']]
        assert bool(additions) == (d['review_status'] == 'accepted') == (d['reason_code'] == 'ACCEPT')
        assert bool(valid) == bool(additions)
        assert all(r['repo'] == repo and r['rank'] == rank for r in additions + valid + excluded)
        if valid:
            selected, fix_cap, repo_cap = R['select_operations'](valid, 10 - old_counts[repo] - counts[repo])
            assert {r['operation'] for r in additions} == {r['operation'] for r in selected}
            assert len(additions) <= 2
            assert {r['operation'] for r in excluded} == {r['operation'] for r in fix_cap + repo_cap}
            assert all(r['review_status'] == 'accepted_capped' for r in excluded)
            for reason, subset in [('FIX_CAP', fix_cap), ('REPO_CAP', repo_cap)]:
                assert {r['operation'] for r in excluded if r['reason_code'] == reason} == {r['operation'] for r in subset}
            valid_counts.append(len(valid))
            cap_rows.extend(excluded)
        total += len(additions)
        counts[repo] += len(additions)
        assert old_counts[repo] + counts[repo] <= 10
        expected.append(pair)
        ordered.append(d)
    assert set(expected) == set(by_pair), 'Decision outside permitted stopping prefix'
    assert total == len(new)
    assert len(cap_rows) == len(capped)
    assert R['next_row']() is None
    events = [json.loads(p.read_text()) for p in sorted((KEY / 't49_previews').glob('*.json'))]
    evidence_ids = {p.stem for p in (KEY / 't49_evidence').glob('*.diff')}
    seen = validate_previews(ordered, events, evidence_ids)
    exploratory = list(csv.DictReader(io.StringIO((HERE.parent / 'E6_realfix/combined_accepted.csv').read_text())))
    identities = [(r['repo'], r['operation'], r['fix_family']) for r in exploratory + previous + new]
    assert len(identities) == len(set(identities))
    for row in new:
        assert row['source_task'] == 'T49' and row['set'] == 'new'
        assert row['proposition'].startswith(row['operation'] + ': contract says ')
        assert '; implementation does ' in row['proposition']
        check = json.loads(row['proposition_check'])
        assert check['contract'] and check['implementation']
        assert all(loc.rsplit(':', 2)[0] == row['parent_commit'] for loc in sum(check.values(), []))
    yields = []
    for prior in R['prior_yield']():
        repo = prior['repo']
        reviewed = [d['rank'] for d in ordered if d['repo'] == repo]
        last = max(reviewed, default=int(prior['last_reviewed_rank']))
        combined = old_counts[repo] + counts[repo]
        assert old_counts[repo] == int(prior['accepted_combined'])
        stopped = ('combined repo cap' if combined >= 10 else
                   'available pool exhausted' if last >= int(prior['pool2']) else 'T49 target reached')
        assert total >= 40 or stopped != 'T49 target reached'
        yields.append(dict(repo=repo, pool2=int(prior['pool2']),
                           previous_last_rank=int(prior['last_reviewed_rank']), reviewed_T49=len(reviewed),
                           last_reviewed_rank=last, accepted_previous=old_counts[repo],
                           accepted_T49=counts[repo], accepted_combined=combined, stopped=stopped))
    triaged = len(list((KEY / 't49_triage').glob('*.json')))
    summary = dict(reviewed=len(ordered), accepted_T49=len(new), accepted_candidates=len(by_candidate),
                   valid_operations=len(new) + len(capped),
                   items_per_accepted_candidate={str(k): v for k, v in sorted(Counter(map(len, by_candidate.values())).items())},
                   valid_operations_per_accepted_candidate={str(k): v for k, v in sorted(Counter(valid_counts).items())},
                   FIX_CAP_exclusions=sum(r['reason_code'] == 'FIX_CAP' for r in capped),
                   REPO_CAP_exclusions=sum(r['reason_code'] == 'REPO_CAP' for r in capped),
                   accepted_previous=len(previous), accepted_combined_new=len(previous) + len(new),
                   reason_code_counts=dict(Counter(d['reason_code'] for d in ordered)),
                   review_status_counts=dict(Counter(d['review_status'] for d in ordered)),
                   capped_reason_code_counts=dict(Counter(r['reason_code'] for r in capped)),
                   T49_direction_counts=dict(Counter(r['truth_direction'] for r in new)),
                   combined_new_direction_counts=dict(Counter(r['truth_direction'] for r in previous + new)),
                   stopping_reason=('T49 acceptance threshold reached after the complete final candidate.' if total >= 40
                                    else 'Every eligible repository is capped or exhausted.'),
                   final_repo=ordered[-1]['repo'], final_rank=ordered[-1]['rank'],
                   preview_record=dict(events=len(events), unique_candidates=len(seen),
                                       outside_final_prefix=0, without_final_decision=0,
                                       lookahead_before_prior_decision=0, chronological_sequence_verified=True),
                   conservative_static_triage=triaged, additional_model_patch_reviews=len(ordered) - triaged,
                   frozen_pool_verified=True, existing_key_verified=True, rank_order_verified=True,
                   caps_verified=True, cap_selection_direction_neutral=True, dedup_verified=True)
    # Keep cap exclusions beside candidate finals; no hidden direction is exported here.
    fields = list(ordered[0]) + ['operation', 'source_item']
    exported = [dict(d, operation='', source_item='') for d in ordered]
    for row in cap_rows:
        d = next(d for d in ordered if d['candidate_id'] == row['candidate_id'])
        exported.append(dict(d, review_status='accepted_capped', reason_code=row['reason_code'],
                             reason=row['reason'], operation=row['operation'], source_item=row['item_id']))
    assert all(set(r) == set(fields) and 0 < len(r['reason'].split()) <= 25 for r in exported)
    return ordered, yields, summary, exported


def main():
    _, yields, summary, decisions = audit()
    for path, rows in [(KEY / 'review_decisions_t49.csv', decisions), (HERE / 'yield_t49.csv', yields)]:
        with path.open('x', newline='') as stream:
            writer = csv.DictWriter(stream, list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    R['private_json'](HERE / 'summary_t49.json', summary)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
