#!/usr/bin/python3
"""Audit the two-pass continuation and the strictly sequential preview ledger."""
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
KEY = HERE / 'key'
R = runpy.run_path(str(HERE / 'review_t48.py'))


def validate_previews(ordered, events, evidence_ids):
    """Reject lookahead, missing finals, reopened candidates and unlogged evidence."""
    ordinal = {d['candidate_id']: i for i, d in enumerate(ordered)}
    assert len(ordinal) == len(ordered)
    seen = set()
    previous_index = -1
    for sequence, event in enumerate(events, 1):
        cid = event['candidate_id']
        assert event['sequence'] == sequence
        assert cid in ordinal, 'Preview without final decision'
        index = ordinal[cid]
        assert index >= previous_index, 'Preview reopened a completed candidate'
        assert event['final_decisions_before'] == index, 'Lookahead before the prior final decision'
        assert (event['repo'], event['rank']) == (ordered[index]['repo'], ordered[index]['rank'])
        seen.add(cid)
        previous_index = index
    assert seen == set(ordinal), 'Final decision without a preview'
    assert evidence_ids == set(ordinal), 'Unrecorded patch preview'
    return seen


def audit():
    R['guard']()
    new = R['accepted']()
    previous = R['previous_items']()
    old_counts = Counter(r['repo'] for r in previous)
    decisions = R['decisions']()
    by_pair = {(d['repo'], d['rank']): d for d in decisions}
    assert len(by_pair) == len(decisions)
    by_candidate = {}
    for row in new:
        by_candidate.setdefault(row['candidate_id'], []).append(row)
    rows = {(r['repo'], r['rank']): r for r in R['sources']()}
    expected = []
    new_counts = Counter()
    phase_counts = {1: Counter(), 2: Counter()}
    phase_accepts = {1: Counter(), 2: Counter()}
    total = 0
    for phase, repo, rank in R['plan']():
        if total >= 40:
            break
        if old_counts[repo] + new_counts[repo] >= 10:
            continue
        pair = repo, rank
        assert pair in by_pair, 'Missing individual ranked decision: ' + str(pair)
        d = by_pair[pair]
        row = rows[pair]
        assert d['candidate_id'] == row['candidate_id']
        assert d['reason_code'] in R['CODES']
        assert 0 < len(d['reason'].split()) <= 25
        assert hashlib.sha256((HERE / d['review_evidence']).read_bytes()).hexdigest() == d['patch_sha256']
        additions = by_candidate.get(d['candidate_id'], [])
        assert bool(additions) == (d['review_status'] == 'accepted') == (d['reason_code'] == 'ACCEPT')
        assert all(a['repo'] == repo and a['rank'] == rank for a in additions)
        total += len(additions)
        new_counts[repo] += len(additions)
        phase_counts[phase][repo] += 1
        phase_accepts[phase][repo] += len(additions)
        assert old_counts[repo] + new_counts[repo] <= 10
        expected.append(pair)
    assert set(expected) == set(by_pair), 'Decision lies outside the permitted stopping prefix'
    assert total == len(new)
    ordered = [by_pair[pair] for pair in expected]

    # Every view must belong to the one candidate currently under final decision.
    events = [json.loads(p.read_text()) for p in sorted((KEY / 't48_previews').glob('*.json'))]
    evidence_ids = {p.stem for p in (KEY / 't48_evidence').glob('*.diff')}
    seen = validate_previews(ordered, events, evidence_ids)

    old = list(csv.DictReader(io.StringIO((HERE.parent / 'E6_realfix/combined_accepted.csv').read_text())))
    identities = [(r['repo'], r['operation'], r['fix_family']) for r in old + previous + new]
    assert len(identities) == len(set(identities))
    for row in new:
        assert row['source_task'] == 'T48' and row['set'] == 'new'
        assert row['proposition'].startswith(row['operation'] + ': contract says ')
        assert '; implementation does ' in row['proposition']
        check = json.loads(row['proposition_check'])
        assert check['contract'] and check['implementation']
        for loc in sum(check.values(), []):
            assert loc.rsplit(':', 2)[0] == row['parent_commit']

    yields = []
    for prior in R['prior_yield']():
        repo = prior['repo']
        reviewed = [d['rank'] for d in ordered if d['repo'] == repo]
        last = max(reviewed, default=int(prior['last_reviewed_rank']))
        combined = old_counts[repo] + new_counts[repo]
        stopped = ('combined repo cap' if combined >= 10 else
                   'available pool exhausted' if last >= int(prior['pool2']) else
                   'top 250' if last >= 250 else
                   'T48 target reached' if total >= 40 else 'rank limit reached')
        yields.append(dict(repo=repo, pool2=int(prior['pool2']),
                           previous_last_rank=int(prior['last_reviewed_rank']),
                           reviewed_phase1=phase_counts[1][repo], reviewed_phase2=phase_counts[2][repo],
                           reviewed_T48=len(reviewed), last_reviewed_rank=last,
                           accepted_previous=old_counts[repo], accepted_T48=new_counts[repo],
                           accepted_combined=combined, stopped=stopped))
    triaged = len(list((KEY / 't48_triage').glob('*.json')))
    final = ordered[-1]
    summary = dict(reviewed=len(ordered), accepted_T48=len(new),
                   accepted_candidates=len(by_candidate), accepted_previous=len(previous),
                   accepted_combined_new=len(previous) + len(new),
                   reason_code_counts=dict(Counter(d['reason_code'] for d in ordered)),
                   review_status_counts=dict(Counter(d['review_status'] for d in ordered)),
                   T48_direction_counts=dict(Counter(r['truth_direction'] for r in new)),
                   combined_new_direction_counts=dict(Counter(r['truth_direction'] for r in previous + new)),
                   phase1_reviewed=sum(phase_counts[1].values()), phase2_reviewed=sum(phase_counts[2].values()),
                   phase1_accepted=sum(phase_accepts[1].values()), phase2_accepted=sum(phase_accepts[2].values()),
                   stopping_reason=('T48 acceptance threshold reached after the complete final candidate.' if total >= 40
                                    else 'Every repository exhausted, capped or reviewed to its permitted rank limit.'),
                   final_repo=final['repo'], final_rank=final['rank'],
                   preview_record=dict(events=len(events), unique_candidates=len(seen),
                                       outside_final_prefix=0, without_final_decision=0,
                                       lookahead_before_prior_decision=0, chronological_sequence_verified=True),
                   conservative_static_triage=triaged, additional_model_patch_reviews=len(ordered) - triaged,
                   frozen_pool_verified=True, existing_key_verified=True, rank_order_verified=True,
                   two_pass_order_verified=True, caps_verified=True, dedup_verified=True)
    return ordered, yields, summary


def main():
    decisions, yields, summary = audit()
    for path, rows in [(KEY / 'review_decisions_t48.csv', decisions), (HERE / 'yield_t48.csv', yields)]:
        with path.open('x', newline='') as stream:
            writer = csv.DictWriter(stream, list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    R['private_json'](HERE / 'summary_t48.json', summary)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
