"""Validate explicit physical-line locators in the report without printing data."""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
EXP=ROOT/'08_experiments/E1_pilot'
TREE=ROOT/'08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market'
prefixes={'M':TREE,'R':TREE/'market-rest/src/main/java/market',
          'C':TREE/'market-core/src/main/java/market','harness_v2':EXP/'harness_v2'}
for label,stem in [('E','20261114T183929Z_batch_940129_mutated_REQUEST_STRICT_p30_s'),
                   ('B','20261114T183929Z_batch_940129_baseline_NONE_p0_s'),
                   ('S','20261114T104059Z_batch_339514_mutated_REQUEST_STRICT_p30_s'),
                   ('SB','20261114T104059Z_batch_339514_baseline_NONE_p0_s')]:
    for seed in range(1,4):
        prefixes[label+str(seed)]=EXP/'runs/market'/(stem+str(seed))
special={'F':OUT/'findings.jsonl','P':OUT/'provenance.json','specmut.py':ROOT/'08_experiments/tools/specmut.py'}
failures=[]
checked=[]
text=(ROOT/'09_collab/reports/T35_report.md').read_text()
for item in re.findall(r'`([^`\n]+)`',text):
    if not re.fullmatch(r'[A-Za-z0-9_./-]+:[0-9,–-]+',item):
        continue
    path,numbers=item.rsplit(':',1)
    if path in special:
        p=special[path]
    elif re.fullmatch(r'(?:E|B|S|SB)[1-3]',path):
        p=prefixes[path]/'exchanges.jsonl'
    elif path.split('/')[0] in prefixes:
        p=prefixes[path.split('/')[0]].joinpath(*path.split('/')[1:])
    else:
        p=next((p for p in (ROOT/path,OUT/path) if p.exists()),None)
    if p is None:
        failures.append({'locator':item,'error':'unresolved'})
        continue
    raw=p.read_bytes()
    count=len(raw.split(b'\n'))-int(raw.endswith(b'\n'))
    if max(map(int,re.findall(r'\d+',numbers)))>count:
        failures.append({'locator':item,'error':'out of bounds','lines':count})
    checked.append(item)
assert not failures,failures
result={'checked_locators':len(checked),'failures':failures}
(OUT/'report_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
