"""Bounded, sanitized parent/child line inspection for the current candidate only."""
import argparse,runpy,re
from pathlib import Path
R=runpy.run_path(str(Path(__file__).with_name('review_t49.py')))
p=argparse.ArgumentParser();p.add_argument('path');p.add_argument('first',type=int,nargs='?',default=1);p.add_argument('last',type=int,nargs='?',default=180);p.add_argument('--child',action='store_true');p.add_argument('--list',action='store_true');a=p.parse_args()
n=R['next_row']();R['require_current'](n);R['record_preview'](n,'child line inspection' if a.child else 'parent line inspection')
rev=n['fix_commit'] if a.child else n['parent_commit']
paths=R['M']['git'](n['repo'],'ls-tree','-r','--name-only',rev).decode().splitlines()
for path in paths:
 if not re.search(a.path,path):continue
 print('PATH',path)
 if a.list:continue
 lines=R['M']['git'](n['repo'],'show',rev+':'+path).decode('utf-8','replace').splitlines()
 for i in range(a.first-1,min(len(lines),a.last)):
  print(str(i+1)+': '+R['display'](lines[i]))
