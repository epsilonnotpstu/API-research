"""Build evidence_matrix.csv and comparative_matrix.md from per-paper matrix JSONs."""
import csv, glob, json, sys
from pathlib import Path

root = Path(sys.argv[1])
meta = {r['final_id']: r for r in csv.DictReader(open(root / '02_screening/final_papers.csv'))}
papers = [json.load(open(f)) for f in sorted(glob.glob(str(root / '04_paper_analysis/matrix/P*.json')))]

NAMES = {'T1': 'REST testing/fuzzing', 'T2': 'GraphQL/RPC', 'T3': 'Security/authorization',
         'T4': 'Spec inference', 'T5': 'Evolution/breaking changes', 'T6': 'Docs/design/governance',
         'T7': 'API misuse', 'T8': 'LLM tool use/MCP', 'T9': 'Microservices/observability'}

# P038: the analysed document differs from the selected paper
OVERRIDE = {'P038': {'title': '[SUBSTITUTE] Microservice Testing Approaches: A Systematic Literature Review (Ghani et al.)',
                     'year': '2019', 'venue': 'International Journal of Integrated Engineering',
                     'doi': '10.30880/ijie.2019.11.08.008'}}

fields = ['paper_id', 'title', 'year', 'venue', 'doi', 'cluster', 'cluster_name', 'secondary_clusters',
          'research_problem', 'technical_approach', 'primary_contribution', 'dataset_benchmark',
          'evaluation_metrics', 'baselines', 'key_findings', 'author_limitations', 'analyst_limitations',
          'reproducibility', 'suggested_extensions', 'evidence_location', 'confidence', 'integrity']
out = root / '04_paper_analysis/evidence_matrix.csv'
with open(out, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=fields, quoting=csv.QUOTE_ALL)
    w.writeheader()
    for p in papers:
        m = {**meta[p['paper_id']], **OVERRIDE.get(p['paper_id'], {})}
        row = {k: p.get(k, '') for k in fields}
        row.update(title=m['title'], year=m['year'], venue=m['venue'], doi=m['doi'],
                   cluster_name=NAMES[p['cluster']], secondary_clusters='; '.join(p['secondary_clusters']),
                   confidence=p['confidence'].split(' ')[0])
        w.writerow(row)

def cell(s, n=None):
    s = str(s).replace('|', '/').replace('\n', ' ')
    return s if n is None or len(s) <= n else s[:n].rsplit(' ', 1)[0] + ' …'

md = ['# Comparative Evidence Matrix (P001–P038)', '',
      'উৎস: `04_paper_analysis/matrix/*.json` (পূর্ণ পাঠ্য `evidence_matrix.csv`-এ)। সংক্ষিপ্ত cell-এ “…” = ছাঁটা। '
      'Analyst limitation = অনুমান (⚠️)। P038 = substitute document (IDENTITY MISMATCH)।', '']
for t in NAMES:
    group = [p for p in papers if p['cluster'] == t]
    if not group:
        continue
    md += [f'## {t} — {NAMES[t]} ({len(group)})', '',
           '| ID | Year | Approach | Dataset/benchmark | Key findings | Author limits | ⚠️ Analyst limits | Repro | Conf. |',
           '|---|---|---|---|---|---|---|---|---|']
    for p in group:
        m = {**meta[p['paper_id']], **OVERRIDE.get(p['paper_id'], {})}
        md.append('| ' + ' | '.join([p['paper_id'], m['year'], cell(p['technical_approach'], 160),
                                     cell(p['dataset_benchmark'], 110), cell(p['key_findings'], 200),
                                     cell(p['author_limitations'], 120), cell(p['analyst_limitations'], 140),
                                     cell(p['reproducibility'].split(':')[0], 20),
                                     p['confidence'].split(' ')[0]]) + ' |')
    md.append('')
(root / '04_paper_analysis/comparative_matrix.md').write_text('\n'.join(md))
print(len(papers), 'papers ->', out)
