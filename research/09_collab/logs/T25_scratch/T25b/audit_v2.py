"""Read saved v2 pair/noise evidence; output login counts and physical locators."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PAIR = ROOT / "08_experiments/E5_codemut/work/petstore-reject-valid-v2_20261114T161810Z"
inputs = {}
counts = []
attributions = []


def read(path):
    data = path.read_bytes()
    inputs[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return data


for seed in (1, 2, 3):
    for prefix in ("", "noise-"):
        analysis_dir = PAIR / f"{prefix}analysis-s{seed}-default"
        metadata = json.loads(read(analysis_dir / "analysis.json"))
        validation = json.loads(read(PAIR / f"{prefix}pair-validation-s{seed}.json"))
        assert metadata["status"] == "COMPLETE" and validation["status"] == "PASS"
        attr_path = analysis_dir / "attribution.csv"
        # Decode to a stream with LF records; quoted CSV fields may contain commas.
        import io
        for line_no, row in enumerate(csv.DictReader(io.StringIO(read(attr_path).decode())), 2):
            if row["method"] == "GET" and row["template"] == "/user/login":
                attributions.append(dict(row, file=str(attr_path.relative_to(ROOT)), line=line_no))
        for role in ("control", "control_repeat" if prefix else "mutant"):
            run = Path(metadata[role + "_run"])
            exchanges = run / "exchanges.jsonl"
            read(exchanges)
            statuses = Counter()
            records = []
            # Physical JSONL lines, not str.splitlines (bodies may contain U+2028).
            with exchanges.open() as stream:
                for line_no, line in enumerate(stream, 1):
                    x = json.loads(line)
                    req = x["request"]
                    if req["method"] != "GET" or req["path"] != "/api/v3/user/login":
                        continue
                    statuses[x["response"]["status"]] += 1
                    record = {"file": str(exchanges.relative_to(ROOT)), "line": line_no,
                              "status": x["response"]["status"], "query_keys": sorted(req.get("query", {})),
                              "username_absent": "username" not in req.get("query", {})}
                    if record["status"] == 500:
                        record["response_body"] = x["response"]["body"]["text"]
                    records.append(record)
            counts.append({"row_id": f"V2-{seed}-{'noise' if prefix else 'pair'}-{role}",
                           "seed": seed, "comparison": "noise" if prefix else "pair", "role": role,
                           "validation": validation["status"], "statuses": dict(sorted(statuses.items())),
                           "exchanges": records})

for seed in (1, 2, 3):
    rows = [r for r in attributions if f"/analysis-s{seed}-default/" in r["file"]]
    assert any(r["kind"] == "SERVER_ERROR" and r["status"] == "NEW" and int(r["mutated_occurrences"]) == 2 for r in rows)
    assert not any(r["kind"] == "VALID_REJECTED" for r in rows)
    noise = [r for r in attributions if f"/noise-analysis-s{seed}-default/" in r["file"]]
    assert not any(r["status"] == "NEW" or r["kind"] == "VALID_REJECTED" for r in noise)

for name, value in (("v2_login_counts.json", counts), ("v2_login_attribution.json", attributions), ("v2_input_hashes.json", inputs)):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
print(json.dumps([{k: v for k, v in row.items() if k != "exchanges"} for row in counts], indent=2))
