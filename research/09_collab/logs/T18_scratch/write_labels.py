"""Materialize the independent T18 decisions using the established CSV schema."""
import collections
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from replay import OUT, ROOT, RUN, SOURCE, save

LABELS = ROOT / '08_experiments/E2_labelling/cwa-verification_baseline_s1_labels_codex.csv'
ROOTS = ROOT / '08_experiments/E2_labelling/cwa-verification_root_causes_codex.csv'
HEADERS = ['item_id', 'L1', 'L2', 'proposed_L2', 'confidence', 'evidence_types',
           'evidence_locators', 'root_cause_id', 'both_candidate', 'rationale']


def ref(path, line):
    return f'{path.relative_to(ROOT)}:{line}'


def main():
    mapping = json.loads((OUT / 'exchange_map.json').read_text())
    cases = json.loads((OUT / 'case_labels.json').read_text())
    spec = RUN / 'spec.original.json'
    checker = ROOT / '08_experiments/tools/conformance.py'
    book = ROOT / '08_experiments/R1_triage_codebook.md'
    logs = RUN / 'compose.log'
    definitions = {
        'C001': ('TEST', '', 'T-PROBE', 'RC01',
                 [(checker, 395), (book, 226), (logs, 382)],
                 'The null-byte capability probe fails HTTP parsing at an undocumented base path; treating setup traffic as an API operation contaminates the sample.'),
        'C002': ('SPEC_PARTIAL', 'S-REQ-LOOSE', '', 'RC02;RC03;RC04',
                 [(spec, 314), (SOURCE / 'model/RegistrationTokenRequest.java', 47),
                  (SOURCE / 'validator/RegistrationTokenRequestValidator.java', 60),
                  (SOURCE / 'service/HashingService.java', 37),
                  (SOURCE / 'service/TanService.java', 82),
                  (SOURCE / 'model/RegistrationTokenRequest.java', 53), (book, 226), (book, 229)],
                 'Sixty-two rejections expose omitted required fields or source validation patterns; seven requests contain illegal header controls. SPEC plus TEST aggregates to SPEC_PARTIAL.'),
        'C003': ('TEST', '', 'T-ORACLE-STATE', 'RC05',
                 [(spec, 57), (SOURCE / 'controller/ExternalTanController.java', 154),
                  (SOURCE / 'service/AppSessionService.java', 155), (logs, 250), (checker, 438)],
                 'Syntactically valid generated tokens lack established application sessions. Source, documented 400, and missing-session logs support rejection; the oracle assumes schema validity guarantees success.'),
        'C004': ('TEST', '', 'T-ORACLE-COVERAGE', 'RC06',
                 [(spec, 170), (spec, 357), (checker, 327), (checker, 434),
                  (SOURCE / 'controller/InternalTanController.java', 142), (logs, 1398)],
                 'The checker cannot validate object-shaped Authorization header serialization. All responses succeed with 201; this diagnostic records oracle coverage rather than an observed implementation failure.'),
        'C005': ('SPEC', 'S-RESP-MISSING', '', 'RC07',
                 [(spec, 232), (checker, 418),
                  (SOURCE / 'controller/InternalTanController.java', 120),
                  (SOURCE / 'controller/VerificationExceptionHandler.java', 93), (logs, 1731)],
                 'The declared 404 object body conflicts with deliberate empty exception-handler responses. Remove the error response content schema; the not-found status itself is intended.'),
        'C006': ('TEST', '', 'T-ORACLE-STATE', 'RC05',
                 [(spec, 105), (SOURCE / 'controller/ExternalTestStateController.java', 149),
                  (SOURCE / 'controller/ExternalTestStateController.java', 111),
                  (SOURCE / 'service/AppSessionService.java', 155), (logs, 532), (checker, 438)],
                 'All generated tokens are syntactically valid but lack application sessions. Missing-token logs corroborate deliberate 400 rejection before any backend call; the oracle ignores business state.'),
    }
    rows = []
    for iid, (label, l2, proposed, roots, evidence, rationale) in definitions.items():
        locators = [ref(RUN / 'exchanges.jsonl', n) for n in mapping[iid]]
        locators += [ref(path, line) for path, line in evidence]
        rows.append(dict(zip(HEADERS, [iid, label, l2, proposed, '3',
                    'E-OBS;E-CODE-INTENT;E-LOG' if iid != 'C001' else 'E-OBS;E-LOG',
                    ';'.join(locators), roots, 'false', '⚠️ ' + rationale])))
    with LABELS.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    root_definitions = [
        ('RC01', 'A capability probe contaminates undocumented-operation diagnostics.', 'test', 'C001', [(RUN / 'exchanges.jsonl', 1)]),
        ('RC02', 'RegistrationTokenRequest omits required key and keyType despite explicit non-null validation.', 'spec', 'C002', [(spec, 314), (SOURCE / 'model/RegistrationTokenRequest.java', 47), (SOURCE / 'model/RegistrationTokenRequest.java', 59)]),
        ('RC03', 'RegistrationTokenRequest omits GUID, keyDob and conditional TELETAN syntax constraints enforced by source validation.', 'spec', 'C002', [(spec, 317), (SOURCE / 'validator/RegistrationTokenRequestValidator.java', 63), (SOURCE / 'model/RegistrationTokenRequest.java', 53), (SOURCE / 'service/TanService.java', 82)]),
        ('RC04', 'Illegal HTTP header controls are mistaken for schema-valid business requests.', 'test', 'C002', [(RUN / 'exchanges.jsonl', 164), (book, 226), (checker, 438)]),
        ('RC05', 'VALID_REJECTED assumes syntactic token validity establishes persistent application-session state.', 'test', 'C003;C006', [(checker, 438), (SOURCE / 'controller/ExternalTanController.java', 154), (SOURCE / 'controller/ExternalTestStateController.java', 149), (logs, 250), (logs, 532)]),
        ('RC06', 'Object-shaped Authorization header validation is outside the checker serialization coverage.', 'test', 'C004', [(spec, 170), (checker, 327)]),
        ('RC07', 'The 404 response advertises object content while the intentional exception response is empty.', 'spec', 'C005', [(spec, 232), (SOURCE / 'controller/VerificationExceptionHandler.java', 93)]),
    ]
    with ROOTS.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['root_cause_id', 'description', 'fix_site', 'items'])
        for rid, description, site, items, evidence in root_definitions:
            writer.writerow([rid, '⚠️ ' + description + ' Evidence: ' + ';'.join(ref(p, n) for p, n in evidence), site, items])
    summary = {'items': len(rows), 'L1': dict(collections.Counter(r['L1'] for r in rows)),
               'strict_L1': dict(collections.Counter('UNDECIDABLE' if r['L1'] == 'SPEC_PARTIAL' else r['L1'] for r in rows)),
               'lenient_L1': dict(collections.Counter('SPEC' if r['L1'] == 'SPEC_PARTIAL' else r['L1'] for r in rows)),
               'root_causes': len(root_definitions), 'both_candidates': 0,
               'diagnostic_cases': len(cases),
               'max_rationale_words': max(len(r['rationale'].split()) for r in rows)}
    save('label_summary.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
