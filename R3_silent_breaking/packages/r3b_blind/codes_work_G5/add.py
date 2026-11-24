import csv, sys, json, os
rows = json.load(open(sys.argv[1]))
path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), 'rows.csv')
with open(path, 'a', newline='') as f:
    w = csv.writer(f)
    for r in rows:
        assert len(r) == 9, r
        w.writerow(r)
print(len(rows), 'appended')
