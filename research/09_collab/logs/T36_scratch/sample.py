"""Freeze the pre-specified T36 sample before evidence searches (stdlib only)."""
import csv
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / '08_experiments/E2_labelling/final_labels_baseline_s1.csv'
OUT = Path(__file__).resolve().parent
EXCLUDED = {'B065', 'M003', 'M005', 'M007', 'M012'}
ORDER = ['SPEC', 'SPEC_PARTIAL', 'UNDECIDABLE', 'BOTH', 'IMPL']
HIDDEN = {'final_L1', 'A_L1', 'B_L1', 'note', 'source'}

def main():
    rows = list(csv.DictReader(SOURCE.open(newline='')))
    assert len(rows) == 161
    rng = random.Random(20261115)
    selected, adjustments = [], []
    for stratum in ORDER:
        pool = sorted((r for r in rows if r['final_L1'] == stratum
                       and r['item_id'] not in EXCLUDED), key=lambda r: r['item_id'])
        count = 4 if stratum == 'SPEC_PARTIAL' else 6
        assert len(pool) >= count
        # Sample also when selecting the whole four-item stratum: its random
        # ordering consumes the same RNG, as prescribed for every stratum.
        draw = rng.sample(pool, count)
        non_scout = [r for r in pool if r['sut'] != 'scout-api']
        if non_scout and all(r['sut'] == 'scout-api' for r in draw):
            replacement = rng.sample(non_scout, 1)[0]
            adjustments.append({'removed': draw[-1]['item_id'],
                                'added': replacement['item_id']})
            draw[-1] = replacement
        selected.extend({k: v for k, v in r.items() if k not in HIDDEN} for r in draw)
    assert len(selected) == len({r['item_id'] for r in selected}) == 28
    assert not EXCLUDED.intersection(r['item_id'] for r in selected)
    assert all(r['kind'] != 'UNDOCUMENTED_OPERATION' for r in selected)
    payload = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'seed': 20261115, 'population_count': len(rows),
        'population_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'excluded_ids': sorted(EXCLUDED),
        'algorithm': 'random.Random.sample on sorted strata in prescribed order; '
                     'sample all four SPEC_PARTIAL; replacement via sample(sorted non-scout, 1)',
        'stratum_order': ORDER, 'stratum_sizes': [6, 4, 6, 6, 6],
        'non_scout_replacements': adjustments,
        'items': selected,
    }
    target = OUT / 'sample.json'
    if target.exists():
        raise SystemExit('Refusing to overwrite frozen sample.json')
    target.write_text(json.dumps(payload, indent=2) + '\n')
    with (OUT / 'working_sheet.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(selected[0]))
        writer.writeheader()
        writer.writerows(selected)
    print(json.dumps({'sample_path': str(target.relative_to(ROOT)),
                      'item_ids': [r['item_id'] for r in selected],
                      'non_scout_replacements': adjustments}))

if __name__ == '__main__':
    main()
