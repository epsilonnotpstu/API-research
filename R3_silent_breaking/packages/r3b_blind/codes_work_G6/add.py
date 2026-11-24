import csv, sys, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rows.csv')
rows = [l.rstrip('\n').split('\t') for l in sys.stdin if l.strip()]
for r in rows:
    assert len(r) == 9, r
with open(p, 'a', newline='') as f:
    w = csv.writer(f)
    for r in rows:
        w.writerow(r)
print(len(rows), 'appended')
