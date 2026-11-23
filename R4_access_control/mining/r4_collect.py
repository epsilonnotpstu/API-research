#!/usr/bin/python3
"""Collect reviewed access-control advisories. Counts are the only stdout."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r4_common import (ROOT, CWES, ECOSYSTEMS, QUERY, PipelineError, cli,
                       guard_upstream, run, write_json)


def decode_pages(raw):
    decoder = json.JSONDecoder()
    pages = []
    remainder = raw.lstrip()
    while remainder:
        page, end = decoder.raw_decode(remainder)
        if not isinstance(page, list):
            raise PipelineError('INVALID_ADVISORY_PAGE')
        pages.append(page)
        remainder = remainder[end:].lstrip()
    return pages


def normalize(advisory, ecosystem):
    return {
        'ghsa_id': advisory['ghsa_id'], 'cve_id': advisory.get('cve_id'),
        'ecosystem': ecosystem,
        'cwes': sorted({c['cwe_id'] if isinstance(c, dict) else c
                        for c in advisory.get('cwes', [])}),
        **{k: advisory.get(k) for k in ('severity', 'published_at', 'withdrawn_at',
                                       'summary', 'description', 'source_code_location')},
        'references': [r['url'] if isinstance(r, dict) else r
                       for r in advisory.get('references', [])],
        'packages': sorted({v['package']['name'] for v in advisory.get('vulnerabilities', [])
                            if v['package'].get('ecosystem', '').lower() == ecosystem}),
    }


def main(root=ROOT):
    mining = Path(root) / 'mining'
    guard_upstream(root, 'advisories.json', 'collect_inventory.json',
                    *(f'cache/advisories_{e}.json' for e in ECOSYSTEMS))
    items, counts = {}, {}
    for ecosystem in ECOSYSTEMS:
        endpoint = ('/advisories?ecosystem=' + ecosystem + '&type=reviewed&cwes=' +
                    ','.join('CWE-' + str(c) for c in CWES) + '&per_page=100')
        pages = decode_pages(run(['gh', 'api', '--paginate', endpoint]))
        write_json(mining / f'cache/advisories_{ecosystem}.json', pages)
        withdrawn = 0
        for page in pages:
            for raw in page:
                if raw.get('withdrawn_at'):
                    withdrawn += 1
                    continue
                item = normalize(raw, ecosystem)
                items[(item['ghsa_id'], ecosystem)] = item
        counts[ecosystem] = {'fetched': sum(map(len, pages)), 'WITHDRAWN': withdrawn,
                             'kept': sum(k[1] == ecosystem for k in items)}
    write_json(mining / 'advisories.json', [items[k] for k in sorted(items)])
    write_json(mining / 'collect_inventory.json', {'counts': counts, 'query': QUERY})
    print('advisories=' + str(len(items)) + ' WITHDRAWN=' +
          str(sum(v['WITHDRAWN'] for v in counts.values())))


if __name__ == '__main__':
    cli(main)
