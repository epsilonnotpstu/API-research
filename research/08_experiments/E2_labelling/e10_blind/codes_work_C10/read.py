import sys,re
from pathlib import Path
root=Path.cwd().resolve()
mode=sys.argv[1]; target=sys.argv[2]
p=Path(target)
assert p.parts[0] in {f"V{i:02d}" for i in range(1,41)}
assert p.resolve().is_relative_to(root)
files=[p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
def clean(s):
    if re.search(r"(?i)owner|createdBy|(?:NOTE|TODO|FIXME)\([^)]*\)|@author|copyright|SPDX|mailto:|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|BEGIN .*PRIVATE KEY|(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"\'][^\"\']{8,}",s): return "[REDACTED]"
    return s
if mode=="list":
    for f in files: print(f)
else:
    for f in files:
        ls=f.read_text(errors="replace").splitlines()
        if mode=="search":
            pat=re.compile(sys.argv[3],re.I); context=int(sys.argv[4]) if len(sys.argv)>4 else 3
            selected=set()
            for i,s in enumerate(ls):
                if pat.search(s): selected.update(range(max(0,i-context),min(len(ls),i+context+1)))
        else:
            a,b=map(int,sys.argv[3].split(":")); selected=range(a-1,min(b,len(ls)))
        if selected:
            print("\n"+str(f))
            for i in sorted(selected): print(f"{i+1}: {clean(ls[i])}")
