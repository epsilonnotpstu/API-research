from pathlib import Path
import csv
import re
from collections import Counter

expected_header = 'item_id,ac_relevant,ac_kind,principals_needed,observable_via_http,contract_operation,contract_security,policy_in_contract,fix_location,confidence,locators,rationale'.split(',')
with Path('codes_G1.csv').open(newline='') as file:
    reader = csv.DictReader(file)
    assert reader.fieldnames == expected_header, reader.fieldnames
    rows = list(reader)
with Path('items.csv').open(newline='') as file:
    expected_items = [r['item_id'] for r in csv.DictReader(file)]
assert [r['item_id'] for r in rows] == expected_items
allowed = {
    'ac_relevant': {'YES', 'NO', 'UNCLEAR'},
    'ac_kind': {'OBJECT_LEVEL', 'FUNCTION_LEVEL', 'PROPERTY_LEVEL', 'MISSING_AUTHENTICATION', 'TENANT_ISOLATION', 'OTHER'},
    'principals_needed': {'NONE', 'ONE', 'TWO_SAME_ROLE', 'TWO_ROLES', 'UNCLEAR'},
    'observable_via_http': {'YES', 'NO', 'UNCLEAR'},
    'contract_operation': {'PRESENT', 'ABSENT', 'NO_CONTRACT', 'UNCLEAR'},
    'contract_security': {'DECLARED', 'NOT_DECLARED', 'UNCLEAR', 'NA'},
    'policy_in_contract': {'YES', 'NO', 'UNCLEAR'},
    'fix_location': {'HANDLER', 'MIDDLEWARE_FILTER', 'SERVICE_LOGIC', 'DATA_QUERY', 'MODEL_BINDING', 'OTHER'},
    'confidence': {'1', '2', '3'},
}
for row in rows:
    assert None not in row, row
    for field, values in allowed.items():
        if row['ac_relevant'] != 'YES' and field in expected_header[2:9]:
            assert row[field] == 'NA', (row['item_id'], field)
        else:
            assert row[field] in values, (row['item_id'], field, row[field])
    if row['ac_relevant'] == 'YES' and row['contract_operation'] != 'PRESENT':
        assert row['contract_security'] == 'NA', row['item_id']
    words = len(row['rationale'].split())
    assert words <= 40, (row['item_id'], words)
    for locator in row['locators'].split('; '):
        path, number = locator.rsplit(':', 1)
        assert path.startswith(row['item_id'] + '/'), locator
        assert Path(path).is_file(), locator
        assert 1 <= int(number) <= len(Path(path).read_text().splitlines()), locator
print(f'Validated {len(rows)} ordered rows, all enums, conditional NA fields, rationale lengths, and locator targets.')
print('Relevance:', dict(Counter(row['ac_relevant'] for row in rows)))
print('Contract coverage among YES:', dict(Counter(row['contract_operation'] for row in rows if row['ac_relevant'] == 'YES')))
