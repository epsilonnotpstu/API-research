"""Synthetic checks of the reviewed trajectory key; fixtures contain no secrets."""
import copy
import importlib.util
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
path = ROOT / '08_experiments/E1_pilot/pilot_results/fuzzer_trajectory_overlap.py'
spec = importlib.util.spec_from_file_location('reviewed_trajectory', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def key(e, label):
    p = HERE / 'fixtures' / label
    p.mkdir(parents=True, exist_ok=True)
    (p / 'exchanges.jsonl').write_text(json.dumps(e) + '\n')
    return module.seq(p)[0]


base = {'request': {'method': 'POST', 'origin': 'http://example.test:8080', 'path': '/items', 'query': {},
                    'headers': {'content-type': 'application/json'},
                    'body': {'text': '{}', 'truncated': False, 'size': 2, 'base64': 'e30=', 'decode_error': False}},
        'response': {'status': 200, 'body': {'text': '{"ok":true}'}}}
results = {}
a = key(base, 'base')
e = copy.deepcopy(base)
e['response']['status'] = 500
results['identical_request_different_response_status_key_equal'] = a == key(e, 'response_status')
e = copy.deepcopy(base)
e['request']['headers']['content-type'] = 'text/plain'
results['different_content_type_key_equal'] = a == key(e, 'content_type')
e = copy.deepcopy(base)
e['request']['origin'] = 'http://other.test:8080'
results['different_origin_key_equal'] = a == key(e, 'origin')
e = copy.deepcopy(base)
e['response']['body']['text'] = '{"ok":false}'
results['different_response_body_key_equal'] = a == key(e, 'response_body')
e = copy.deepcopy(base)
e['request']['body'] = dict(reversed(list(e['request']['body'].items())))
results['same_body_object_reordered_metadata_key_equal'] = a == key(e, 'body_order')
e = copy.deepcopy(base)
e['request']['body']['text'] = 'x' * 2500 + 'A'
e['request']['body']['size'] = 2501
f = copy.deepcopy(e)
f['request']['body']['text'] = 'x' * 2500 + 'B'
results['distinct_body_tail_key_equal'] = key(e, 'tail_a') == key(f, 'tail_b')
results['prefix_versus_prefix_plus_99_extra_requests_overlap'] = module.overlap([a], [a] * 100)
results['printed_median_of_0_and_1'] = sorted([0.0, 1.0])[2 // 2]
results['correct_median_of_0_and_1'] = statistics.median([0.0, 1.0])
assert results == {
    'identical_request_different_response_status_key_equal': False,
    'different_content_type_key_equal': True,
    'different_origin_key_equal': True,
    'different_response_body_key_equal': True,
    'same_body_object_reordered_metadata_key_equal': False,
    'distinct_body_tail_key_equal': True,
    'prefix_versus_prefix_plus_99_extra_requests_overlap': (1.0, 1.0),
    'printed_median_of_0_and_1': 1.0, 'correct_median_of_0_and_1': 0.5,
}
(HERE / 'key_probes.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
