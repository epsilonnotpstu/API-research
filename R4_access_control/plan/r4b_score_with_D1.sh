#!/bin/bash
# R4b deviation D1: Claude coders H3/H4 wrote policy_in_contract=NA (not an allowed value) on items whose contract_operation is not
# PRESENT. The frozen scorer rejects NA. Normalisation (documented, conservative): NA -> UNCLEAR, applied to COPIES of the code files in
# a scratch root; the frozen score_r4b.py is run UNCHANGED on that root (contracts symlinked for the locator check). Original codes untouched.
# H-R4-3b uses only PRESENT items, so the normalisation cannot affect it.
set -euo pipefail
B="$(cd "$(dirname "$0")/.." && pwd)"; S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
mkdir -p "$S/plan" "$S/mining/key"; cp "$B/plan/score_r4b.py" "$B/plan/score_r4.py" "$S/plan/"; cp "$B/mining/key/r4b_key.csv" "$S/mining/key/"
for d in "$B"/packages/r4b_* "$B"/packages/r4_blind; do n=$(basename "$d"); mkdir -p "$S/packages/$n"; done
for d in "$B"/packages/r4b_blind/C*; do ln -s "$d" "$S/packages/r4b_blind/$(basename "$d")"; done
cp "$B"/packages/r4_blind/codes_G1.csv "$B"/packages/r4_blind/codes_G2.csv "$S/packages/r4_blind/"
/usr/bin/python3 -I -B - "$B" "$S" <<'PY'
import csv, sys
from pathlib import Path
csv.field_size_limit(sys.maxsize)
B, S = Path(sys.argv[1]), Path(sys.argv[2]); n = 0
for f in sorted(B.glob('packages/r4b_*/codes_[GH]?.csv')):
    rows = list(csv.DictReader(open(f, newline='', encoding='utf-8-sig'))); fields = list(rows[0].keys())
    for r in rows:
        if (r.get('policy_in_contract') or '').strip().upper() in ('NA', ''): r['policy_in_contract'] = 'UNCLEAR'; n += 1
    out = S / f.relative_to(B)
    with open(out, 'w', newline='', encoding='utf-8') as g:
        w = csv.DictWriter(g, fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f'D1 normalisation: policy_in_contract NA/empty -> UNCLEAR in {n} rows', file=sys.stderr)
PY
cd "$S" && /usr/bin/python3 -I -B plan/score_r4b.py --root "$S" --out "$S/r4b_scores.csv"
cp "$S/r4b_scores.csv" "$B/plan/r4b_scores.csv"
