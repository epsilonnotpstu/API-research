#!/usr/bin/python3
"""Finalize the current candidate before displaying the next one."""
import argparse,runpy,json
from pathlib import Path
R=runpy.run_path(str(Path(__file__).with_name('review_t49.py')))
p=argparse.ArgumentParser();p.add_argument('code');p.add_argument('reason',nargs='?');p.add_argument('--lines',type=int,default=12);p.add_argument('--paths',type=int,default=4)
a=p.parse_args();n=R['next_row']()
if a.code!='show':
    codes={'N':'NOT_CONTRACT_RELATED','F':'NEW_FEATURE_OR_ENDPOINT','R':'REFACTOR_OR_RENAME','G':'GENERATED_OR_DOCS_ONLY_CHURN','B':'BOTH_CHANGED_TO_NEW_BEHAVIOUR','D':'NO_PARENT_MISMATCH','T':'TEST_OR_CLIENT_ONLY','L':'TOO_LARGE_TO_ESTABLISH','O':'OTHER'}
    R['decide'](n['repo'],n['rank'],codes[a.code],a.reason)
n=R['next_row']()
if n:runpy.run_path(str(Path(__file__).with_name('triage_t49.py')))
else:print('Review stopping condition reached')
