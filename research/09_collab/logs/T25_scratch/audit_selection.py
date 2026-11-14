"""Read saved E5 evidence only; never invoke a SUT or external program.

Run from research/ with /usr/bin/python3 -I -B. Output stays in this directory.
CSV exchange locators are physical 1-based JSONL lines; saved violations use
0-based exchange indices. Match operation templates with our existing checker.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
E5 = ROOT / "08_experiments/E5_codemut"
sys.path.insert(0, str(ROOT / "08_experiments/tools"))
import conformance


def relative(path):
    return str(path.relative_to(ROOT))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    inputs = {}
    counts = []
    witnesses = []
    attributions = []
    for pair in sorted((E5 / "work").glob("petstore-*_20*")):
        if not pair.is_dir():
            continue
        analyses = sorted(pair.glob("*analysis-s*-default/analysis.json"))
        assert len(analyses) == 6, pair
        for analysis_path in analyses:
            inputs[relative(analysis_path)] = digest(analysis_path)
            analysis = json.loads(analysis_path.read_text())
            assert analysis["status"] == "COMPLETE"
            attribution_path = analysis_path.parent / "attribution.csv"
            inputs[relative(attribution_path)] = digest(attribution_path)
            with attribution_path.open() as stream:
                attribution_rows = list(csv.DictReader(stream))
            for index, row in enumerate(attribution_rows, 2):
                if row["kind"] == "VALID_REJECTED":
                    attributions.append(dict(row, file=relative(attribution_path), line=index))
            for key in sorted(k for k in analysis if k.endswith("_run")):
                role = key[:-4]
                run = Path(analysis[key])
                exchanges = run / "exchanges.jsonl"
                original = run / "spec.original.json"
                metadata = run / "run.json"
                for path in (exchanges, original, metadata):
                    inputs[relative(path)] = digest(path)
                spec = conformance.Spec(json.loads(original.read_text()),
                                        deploy_origin=analysis["deploy_origin"])
                grouped = {}
                with exchanges.open() as stream:
                    for line_no, line in enumerate(stream, 1):
                        exchange = json.loads(line)
                        request = exchange["request"]
                        method = request["method"].upper()
                        template, params = spec.match(request["path"], method, request.get("origin"))
                        op_key = (method, template or request["path"])
                        item = grouped.setdefault(op_key, {
                            "statuses": collections.Counter(), "lines": [],
                            "valid_requests": 0, "invalid_requests": 0,
                            "uncheckable_requests": 0, "guard_hits": 0})
                        item["statuses"][int(exchange["response"]["status"])] += 1
                        item["lines"].append(line_no)
                        if template is not None:
                            operation, parameters = spec.operation(template, method)
                            problems = conformance.request_problems(spec, parameters, operation, exchange, params)
                            item["uncheckable_requests"] += bool(problems.uncheckable)
                            item["invalid_requests"] += bool(problems)
                            valid = not problems and not problems.uncheckable
                            item["valid_requests"] += valid
                            if op_key == ("GET", "/user/login"):
                                # The candidate makes this optional parameter mandatory.
                                guard_hit = "username" not in request.get("query", {})
                                item["guard_hits"] += guard_hit
                                witnesses.append({"pair": pair.name, "seed": analysis["seed"],
                                    "analysis": relative(analysis_path), "role": role,
                                    "file": relative(exchanges), "line": line_no,
                                    "request_valid": valid, "guard_hit": guard_hit,
                                    "status": exchange["response"]["status"],
                                    "query": request.get("query", {}),
                                    "saved_response_kinds": sorted(v["kind"] for v in conformance.check(spec, exchange))})
                violations = analysis_path.parent / f"{role}.violations.jsonl"
                inputs[relative(violations)] = digest(violations)
                vr = collections.Counter()
                with violations.open() as stream:
                    for line in stream:
                        v = json.loads(line)
                        if v["kind"] == "VALID_REJECTED":
                            vr[(v["method"], v["template"])] += 1
                for (method, template), item in sorted(grouped.items()):
                    counts.append({"row_id": f"P{len(counts)+1:04}", "pair": pair.name,
                        "seed": analysis["seed"], "kind": analysis.get("kind", "mutant"),
                        "role": role, "method": method, "template": template,
                        "total": sum(item["statuses"].values()),
                        "statuses": dict(sorted(item["statuses"].items())),
                        "valid_requests_current_checker": item["valid_requests"],
                        "invalid_requests_current_checker": item["invalid_requests"],
                        "uncheckable_requests_current_checker": item["uncheckable_requests"],
                        "saved_VALID_REJECTED": vr[(method, template)],
                        "candidate_guard_hits": item["guard_hits"],
                        "exchanges": relative(exchanges), "lines": item["lines"],
                        "attribution": relative(attribution_path)})
    assert len(witnesses) == 48
    assert all(w["request_valid"] and w["guard_hit"] and w["status"] == 200 for w in witnesses)
    selected = [c for c in counts if (c["method"], c["template"]) == ("GET", "/user/login")]
    assert len(selected) == 24
    assert all(c["statuses"] == {200: 2} and c["saved_VALID_REJECTED"] == 0 for c in selected)
    assert not any(r["method"] == "GET" and r["template"] == "/user/login" for r in attributions)
    for path in (ROOT / "08_experiments/tools").glob("*.py"):
        inputs[relative(path)] = digest(path)
    dump("input_sha256.json", inputs)
    dump("petstore_operation_counts.json", counts)
    dump("petstore_login_witnesses.json", witnesses)
    dump("petstore_saved_valid_rejected.json", attributions)
    with (OUT / "petstore_operation_counts.csv").open("w", newline="") as stream:
        fields = list(counts[0])
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        for row in counts:
            writer.writerow({k: json.dumps(v, separators=(",", ":")) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})
    dump("selection_summary.json", {
        "analysis_files": 12, "saved_runs": 24, "operation_rows": len(counts),
        "login_requests": len(witnesses), "login_control_requests": sum(w["role"] != "mutant" for w in witnesses),
        "login_mutant_requests": sum(w["role"] == "mutant" for w in witnesses),
        "login_400_or_422": 0, "login_saved_VALID_REJECTED": 0,
        "login_valid_requests_current_checker": len(witnesses),
        "login_optional_username_absent": len(witnesses),
        "limitation": "Two login exchanges per run; repeated empty-query shape, not 48 independent input shapes."})
    print(json.dumps(json.loads((OUT / "selection_summary.json").read_text())))


if __name__ == "__main__":
    main()
