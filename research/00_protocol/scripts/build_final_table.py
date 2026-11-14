"""Build the final paper x cluster table (CSV + Markdown) from evidence_matrix.csv plus curated short summaries."""
import csv, sys
from pathlib import Path

root = Path(sys.argv[1])
ev = {r['paper_id']: r for r in csv.DictReader(open(root / '04_paper_analysis/evidence_matrix.csv'))}

VENUE = {'P001': 'ESEC/FSE 2022', 'P002': 'TOSEM', 'P003': 'TOSEM', 'P004': 'ISSTA 2022', 'P005': 'PACMSE (FSE 2025)',
         'P006': 'ICSE 2019', 'P007': 'ICSE 2025', 'P008': 'ISSTA 2023', 'P009': 'ACM CSUR', 'P010': 'ESEC/FSE 2020',
         'P011': 'TOSEM', 'P012': 'ICSE 2023', 'P013': 'IEEE S&P 2018', 'P014': 'IJIS', 'P015': 'ISSRE 2025',
         'P016': 'IEEE TSC', 'P017': 'JSS', 'P018': 'ICSE 2024', 'P019': 'PACMPL', 'P020': 'JSS', 'P021': 'ACM CSUR',
         'P022': 'ICLR 2025', 'P023': 'EMSE', 'P024': 'ICSE 2025', 'P025': 'ISSTA 2020', 'P026': 'EMSE', 'P027': 'ICSA 2024',
         'P028': 'SANER 2021', 'P029': 'ACM CSUR', 'P030': 'TSE', 'P031': 'TSE', 'P032': 'arXiv (preprint)',
         'P033': 'ICLR 2024', 'P034': 'NeurIPS 2024', 'P035': 'ICSE-SEIP 2025', 'P036': 'TOSEM', 'P037': 'PROMISE 2025',
         'P038': 'IST 2025'}

TYPE = {'P002': 'SLR', 'P009': 'Mapping', 'P021': 'SLR', 'P029': 'SLR', 'P038': 'SLR', 'P037': 'Dataset',
        'P026': 'Experiment', 'P020': 'Interview', 'P003': 'Tool comparison', 'P004': 'Tool comparison',
        'P001': 'Empirical', 'P023': 'Empirical (replication)', 'P030': 'Benchmark eval', 'P036': 'Empirical',
        'P032': 'Empirical + tool', 'P024': 'Empirical + fix', 'P031': 'Empirical + repair', 'P035': 'Empirical + mitigation'}

# (one-line contribution, headline result, main limitation) — Bengali summaries of the analysis files
S = {
'P001': ('RESTest-কে multi-bot online testing-এ রূপান্তর; ১৩টি industrial API-তে ১৫ দিন', '৩,৮৯,২১৬ failure; ১৪৭ fault, ৫০% spec-disconformity', 'Black-box; quota-সীমিত; triage manual'),
'P002': ('REST API testing-এর ৯২ article-এর SLR', '৭৩% black-box; oracle মূলত 5xx/schema', 'জুন ২০২২ পর্যন্ত; LLM-যুগের আগে'),
'P003': ('৭টি fuzzer × ১৯ SUT তুলনা ও open problem বিশ্লেষণ', 'কোনো tool >৬০% coverage নয়; WB +৭.৫% cov, +৩.৪ fault', 'EvoMaster লেখকদের নিজস্ব মূল্যায়ন'),
'P004': ('১০টি tool × ২০ service-এর independent তুলনা', 'EvoMasterWB line ৫২.৭৬%; ~৯৯% spec-এ mismatch', 'Java-only; LLM tool-এর আগে'),
'P005': ('Fine-tuned ছোট LLM (Llama3-8B) দিয়ে value ও IPD', 'Value validity ৭২.৪৪%; method coverage +১০–২২.৭ pp', 'অসম budget; একই গোষ্ঠীর benchmark'),
'P006': ('Swagger-ভিত্তিক stateful fuzzing (RESTler)', 'GitLab-এ ২৮টি bug; dependency inference অপরিহার্য', 'কেবল 5xx oracle'),
'P007': ('Semantic dependency graph + multi-agent RL + LLM input', 'Method coverage ৫৮.৩%; ৪২টি 500-error', 'GPT-3.5 ও live API নির্ভর'),
'P008': ('OAS + traffic থেকে test oracle (invariant) inference — AGORA', 'Precision ৮১.২%; ১১টি বাস্তব bug', 'Seeded error; frequency ধারণা'),
'P009': ('GraphQL-এর systematic mapping', 'Testing study মাত্র ৪টি; ৩৯.৭৩% schema-তে cycle', '২০২১ পর্যন্ত; পুরোনো'),
'P010': ('GraphQL query cost-এর formal বিশ্লেষণ', 'Under-estimation শূন্য; GitHub DoS প্রকাশ', 'Resolver configuration manual'),
'P011': ('EvoMaster দিয়ে RPC API white-box fuzzing, industrial', '৫০টি industrial API-তে ১২৬টি real fault; coverage ১৭.৪৯%', 'Industrial data গোপন; self-evaluation'),
'P012': ('Mass assignment vulnerability-র black-box detection', 'CRUD ৯৮%; zero false positive', 'Seeded/vulnerable-by-design SUT'),
'P013': ('Mobile app থেকে web API reconnaissance', '১০,০০০-এর মধ্যে ৪,৫৬২ app flagged; ৮৮.৪% invalid request গৃহীত', 'Tool/data অপ্রকাশিত; ২০১৮'),
'P014': ('OpenAPI → Colored Petri Net দিয়ে BOLA attack detection', 'Attempt-স্তরে সব ধরা; V2 precision ০.২২', 'Juice Shop + একটি OSS'),
'P015': ('Access-policy violation-এর fuzzing oracle', '২৭টি নতুন fault; real API-তে Missed-Check নেই', 'Ownership অনুমান; self-evaluation'),
'P016': ('Inter-parameter dependency-র IDL ও CSP-ভিত্তিক বিশ্লেষণ', '১৪৯টি বাস্তব dependency প্রকাশযোগ্য', 'IDL manually লেখা'),
'P017': ('LLM দিয়ে source code থেকে OpenAPI generation (OOPS)', 'Endpoint F1 ~৯৮.৮%; ~$০.৪১/API', 'Downstream মূল্যায়ন নেই'),
'P018': ('Static analysis দিয়ে spec generation (Respector)', 'Developer spec-এ ২২৮ endpoint অনুপস্থিত; constraint recall ৫০%', 'Java/Spring; downstream মূল্যায়ন নেই'),
'P019': ('Path-sensitive response type inference (RestPi)', 'Response type +৭১.৯৭%; non-200 +১২৯%', 'Feasibility যাচাই নেই'),
'P020': ('Microservice API evolution — ১৭ সাক্ষাৎকার', 'মাত্র ৫/১৭ behavioural change-কে breaking ধরে', 'Qualitative; ছোট নমুনা'),
'P021': ('API evolution-এর SLR', '৬৩.৯% কেবল Java; ৭৪%-এ statistics নেই', '২০২০ পর্যন্ত; সংখ্যায় অসঙ্গতি'),
'P022': ('Evolving tool-এ LLM অভিযোজন (ToolEVO, MCTS)', 'Static-SFT deprecated call পুনরাবৃত্তি করে', 'GPT-4-generated পরিবর্তন; synthetic'),
'P023': ('Maven Central-এ semver ও breaking change replication', 'Non-major-এর ২০.১% breaking; মাত্র ৭.৯% client প্রভাবিত', 'Java-only; syntactic'),
'P024': ('LLM code completion-এ deprecated API usage', 'Outdated context-এ DUR ৭০–৯০%', 'Python library; ছোট open model'),
'P025': ('REST API-র differential regression testing', '১৪টি regression (৯টি service-side)', 'Azure-নির্দিষ্ট; manual triage'),
'P026': ('RESTful design rule-এর understandability পরীক্ষা', '১২টির ১১টি rule violation বোঝাপড়া কমায়', 'প্রতি rule-এ একটি stimulus'),
'P027': ('Design-rule violation detector (RESTRuler)', '১,৬৯,০৬১টি violation; precision ৯১.২%, recall ৬৭.৬%', 'Syntactic rule; বড় ফাইলে RAM'),
'P028': ('API documentation smell detection', '৭৮% unit-এ smell; BERT F1 ০.৭৫–০.৯৭', 'Java docs; REST নয়'),
'P029': ('Security API misuse detection-এর SLR', 'Benchmark মাত্র ৫টি, সবই Java crypto/SSL', 'LLM-যুগ অনাবৃত'),
'P030': ('Static API-misuse detector-এর মূল্যায়ন (MUBench)', 'সব detector-এর precision <১২%', 'Java; ২০১৯'),
'P031': ('LLM code-এ API misuse ও Dr.Fix repair', 'Hallucination সবচেয়ে সাধারণ misuse', 'Execution-ভিত্তিক যাচাই নেই'),
'P032': ('REST→MCP wrapping-এর empirical অধ্যয়ন ও AutoMCP/SpecFix', '৯২% bare wrapper; tool success ৭৬%→৯৪.২%', 'Preprint; সংখ্যায় অসঙ্গতি'),
'P033': ('১৬,০০০+ real API-তে tool use (ToolLLM, DFSDT)', 'ToolLLaMA ChatGPT-এর কাছাকাছি', 'LLM judge; live API'),
'P034': ('Retrieval-aware API call generation (Gorilla)', 'Zero-shot GPT-4-এর চেয়ে +২০.৪৩%', 'AST match; ML API'),
'P035': ('Documentation দিয়ে code-LLM hallucination হ্রাস', 'Spec যোগে ৪১.৮০%→৮৬.৮২%', 'AWS-কেন্দ্রিক; benchmark অনিশ্চিত'),
'P036': ('MCP server-এর health, security ও maintainability', '৭.২%-এ vulnerability, ৫.৫%-এ tool poisoning', 'Static ও sample-ভিত্তিক'),
'P037': ('Microservice API-error anomaly dataset (LO2)', 'সব service-এর log একত্রে ব্যর্থ (F1 ~০.৬৬৭)', 'Anomaly = documented 4xx'),
'P038': ('৭৪টি microservice testing study-র SLR (SWEBOK, TRL, SUT)', 'System testing ৪৭; API ৮; TRL ৩–৪; TrainTicket প্রধান', 'Title-only query; security gap-দাবি সংকীর্ণ'),
}
NAMES = {'T1': 'REST testing/fuzzing', 'T2': 'GraphQL/RPC', 'T3': 'Security/authz', 'T4': 'Spec inference',
         'T5': 'Evolution', 'T6': 'Docs/design', 'T7': 'API misuse', 'T8': 'LLM tool use/MCP', 'T9': 'Microservices'}

cols = ['paper_id', 'title', 'year', 'venue', 'type', 'primary_cluster', 'secondary_clusters', 'contribution_bn',
        'headline_result_bn', 'main_limitation_bn', 'reproducibility', 'confidence', 'doi']
rows = []
for pid, r in ev.items():
    c, h, l = S[pid]
    rows.append({'paper_id': pid, 'title': r['title'], 'year': r['year'], 'venue': VENUE[pid],
                 'type': TYPE.get(pid, 'Technique'), 'primary_cluster': r['cluster'],
                 'secondary_clusters': r['secondary_clusters'], 'contribution_bn': c, 'headline_result_bn': h,
                 'main_limitation_bn': l, 'reproducibility': r['reproducibility'].split(':')[0].split(';')[0][:40],
                 'confidence': r['confidence'], 'doi': r['doi']})
with open(root / '05_research_clusters/final_paper_cluster_table.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(rows)

md = ['# Final Table — সব paper × cluster × মূল তথ্য (P001–P038)', '',
      'উৎস: `04_paper_analysis/evidence_matrix.csv` + প্রতিটি `Pxxx_analysis.md`। Machine-readable: `final_paper_cluster_table.csv`।',
      'Cluster: ' + ' · '.join(f'**{k}** {v}' for k, v in NAMES.items()) + '।',
      '']
for t, name in NAMES.items():
    grp = [r for r in rows if r['primary_cluster'] == t]
    sec = [pid for pid, r in ev.items() if t in r['secondary_clusters'].split('; ')]
    md += [f'## {t} — {name} (primary {len(grp)}; secondary: {", ".join(sec) or "—"})', '',
           '| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for r in grp:
        md.append('| ' + ' | '.join([r['paper_id'], r['title'].replace('|', '/'), r['year'], r['venue'], r['type'],
                                     r['secondary_clusters'] or '—', r['contribution_bn'], r['headline_result_bn'],
                                     r['main_limitation_bn'], r['confidence']]) + ' |')
    md.append('')
# membership matrix
md += ['## Cluster membership matrix (● primary, ○ secondary)', '',
       '| ID | ' + ' | '.join(NAMES) + ' |', '|---|' + '---|' * len(NAMES)]
for r in rows:
    sec = r['secondary_clusters'].split('; ')
    md.append(f"| {r['paper_id']} | " + ' | '.join('●' if r['primary_cluster'] == t else ('○' if t in sec else '')
                                                   for t in NAMES) + ' |')
tot_p = {t: sum(r['primary_cluster'] == t for r in rows) for t in NAMES}
tot_s = {t: sum(t in r['secondary_clusters'].split('; ') for r in rows) for t in NAMES}
md.append('| **মোট (●/○)** | ' + ' | '.join(f'{tot_p[t]}/{tot_s[t]}' for t in NAMES) + ' |')
(root / '05_research_clusters/final_paper_cluster_table.md').write_text('\n'.join(md) + '\n')
print(len(rows), 'rows')
