"""Build the pilot labelling sheet for P001's 73 confirmed F_OAS faults (roadmap E2).

Each row = one fault, with pre-computed evidence and a machine-suggested label derived
from R1_triage_codebook.md rules. The suggestion is a rule-based BASELINE, not ground
truth: labellers fill label_A / label_B independently (hide the suggested_* columns
during labelling to avoid anchoring).

Usage: python3 build_labelling_sheet.py P001_DIR REPLAY_AGREEMENT_CSV OUT_CSV
"""
import glob
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'E1_pilot'))
import p001_oas_analysis as P  # noqa: E402


def unsatisfiable_pattern(reason):
    """Double-escaped regex (literal backslash) can never match the reported value."""
    for pat, val in re.findall(r'ECMA 262 regex "([^"]*)" does not match input string "([^"]*)"', reason):
        fixed = pat.replace('\\\\', '\\')
        if fixed != pat and re.search(fixed, val):
            return True
    return False


def suggest(row, types, strict_only):
    """Return (L1, L2, rule, confidence 1-3) per codebook §3 tie-breaks and §8."""
    status, reason = int(row['statusCode']), str(row['failReason'])
    if status >= 500:
        return 'IMPL', 'I-CRASH', 'R1: 5xx', 3
    if 'PATTERN' in types and unsatisfiable_pattern(reason):
        return 'SPEC', 'S-RESP-TYPE', '§8.4: pattern matches value once un-escaped', 3
    if types == {'ADDITIONAL_PROPERTIES'}:
        return 'SPEC', 'S-RESP-MISSING', '§8.1 strict-only' if strict_only else 'R2: undeclared property', 2
    if types == {'TYPE_NULL'}:
        return 'SPEC', 'S-RESP-TYPE', '§8.3: nullable missing (needs E-CONSIST)', 1
    if types == {'STATUS_UNDEFINED'}:
        if status in (401, 403, 429):
            return 'SPEC', 'S-STATUS', 'standard auth/rate status undocumented', 2
        if 400 <= status < 500 and str(row['faulty']).lower() == 'true':
            return 'SPEC', 'S-STATUS', 'invalid input correctly rejected; status undocumented', 2
        return 'UNDECIDABLE', '', 'undocumented status on valid input', 1
    if types == {'CONTENT_TYPE'}:
        return 'SPEC', 'S-STATUS', 'media type undocumented', 1
    if types <= {'ADDITIONAL_PROPERTIES', 'TYPE_NULL'}:
        return 'SPEC', 'S-RESP-MISSING|S-RESP-TYPE', 'R2 + §8.3', 1
    return 'UNDECIDABLE', '', 'no rule applies', 1


def main(p001_dir, agreement_csv, out_csv):
    df = pd.concat([pd.read_csv(f, low_memory=False).assign(api_file=Path(f).stem.split('_', 1)[1])
                    for f in sorted(glob.glob(f'{p001_dir}/faultClustersConfirmedBugs_*.csv'))], ignore_index=True)
    df = df[df.failReasonCategory == 'OAS disconformity']
    ag = pd.read_csv(agreement_csv).set_index('testCaseId')
    bugs = pd.read_csv(f'{p001_dir}/bugs_reported.csv').set_index('testCaseId')
    rows = []
    for i, r in enumerate(df.to_dict('records'), 1):
        types = P.message_types(r['failReason'])
        a = ag.loc[r['testCaseId']]
        strict_only = bool(a.reproduced_strict and not a.reproduced_default)
        l1, l2, rule, conf = suggest(r, types, strict_only)
        msgs = [m.strip() for m in str(r['failReason']).split(':', 1)[-1].split(' --- ') if m.strip()]
        b = bugs.loc[r['testCaseId']] if r['testCaseId'] in bugs.index else {}
        rows.append({
            'fault_id': f'F{i:03d}', 'api': r['api_file'], 'testCaseId': r['testCaseId'],
            'operation': f"{r['httpMethod']} {r['path']}", 'http_status': r['statusCode'],
            'request_was_invalid': r['faulty'], 'violation_types': ';'.join(sorted(types)),
            'n_messages': len(msgs), 'messages': ' || '.join(msgs)[:600], 'strict_only': strict_only,
            'dev_replied': b.get('replied', ''), 'dev_confirmed': b.get('confirmed', ''), 'dev_fixed': b.get('fixed', ''),
            'suggested_L1': l1, 'suggested_L2': l2, 'suggested_rule': rule, 'suggested_confidence': conf,
            'label_A_L1': '', 'label_A_L2': '', 'evidence_A': '', 'label_B_L1': '', 'label_B_L2': '', 'evidence_B': '',
            'final_L1': '', 'note': ''})
    out = pd.DataFrame(rows)
    out.to_csv(out_csv, index=False)
    print(out.suggested_L1.value_counts().to_string())
    print(pd.crosstab(out.suggested_L1, out.suggested_confidence).to_string())
    print(pd.crosstab(out.suggested_L1, out.dev_confirmed.astype(str)).to_string())


if __name__ == '__main__':
    main(*sys.argv[1:4])
