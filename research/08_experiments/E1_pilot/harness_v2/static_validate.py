"""T14 static validation and the explicitly permitted stdlib derecurse tests.

No harness scripts, third-party project code, Docker, Java, network, or SUT
commands are executed. Run from any directory with /usr/bin/python3 -I -B.
"""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import yaml

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1]
EMB = EXP / "_external" / "emb"
SUTS = ("scout-api", "swagger-petstore", "market")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    print("T14 validation:", datetime.datetime.now(datetime.timezone.utc).isoformat(), flush=True)
    for path in sorted(HERE.glob("*.sh")):
        subprocess.run(["bash", "-n", str(path)], check=True)
        source = path.read_text()
        if path.name != "common.sh":
            assert "set -euo pipefail" in source, path.name
            assert path.stat().st_mode & 0o111, path.name
        for code in re.findall(r"<<'PY'\n(.*?)^PY$", source, re.M | re.S):
            ast.parse(code, filename=path.name + ":heredoc")
        for code in re.findall(r" -c '([^']*)'", source):
            ast.parse(code, filename=path.name + ":inline")
        assert not re.search(r"docker\s+(?:system|container|image|volume)\s+prune", source)
        assert not re.search(r"(?:pip\s+install|curl[^\n]+\|\s*(?:bash|sh))", source)
        print("PASS SHELL/INLINE_AST", path.name, flush=True)
    for path in sorted(HERE.glob("*.py")):
        ast.parse(path.read_text(), filename=path.name)
        print("PASS PYTHON_AST", path.name, flush=True)

    fixture_values = set()
    fixture_tokens = set()
    public_roles = set()
    for sut in SUTS:
        path = HERE / "suts" / f"{sut}.env"
        config = dict(line.split("=", 1) for line in path.read_text().splitlines()
                      if line and not line.startswith("#"))
        assert config["SUT_ID"] == sut
        assert config["SUT_IMAGE"] == f"r1-{sut}-sut:pilot"
        assert config["SUT_SERVICE"] == f"sut-{sut}"
        assert config["INTERNAL_PORT"] == "8080"
        for key in ("HEALTH_PATH_DEFAULT", "BASE_PATH_DEFAULT"):
            assert config[key].startswith("/")
        for key in ("JAR_SOURCE", "COMPOSE_FILE", "DOCKERFILE", "SPEC_SOURCE"):
            assert (EMB / config[key]).is_file(), (sut, key)
        assert (EMB / config["JAR_SOURCE"]).stat().st_size > 0
        original = yaml.safe_load((EMB / config["COMPOSE_FILE"]).read_text())
        override = yaml.safe_load((HERE / f"compose.override.{sut}.yaml").read_text())
        service = override["services"][config["SUT_SERVICE"]]
        proxy = override["services"]["mitmproxy"]
        assert service["image"] == config["SUT_IMAGE"]
        assert service["build"]["dockerfile"] == config["DOCKERFILE"]
        assert service["build"]["context"] == "${EMB_DIR:?Set EMB_DIR}"
        assert proxy["entrypoint"] == ["mitmdump"]
        assert f"reverse:http://{config['SUT_SERVICE']}:8080" in proxy["command"]
        assert proxy["environment"]["MITM_FULLLOG_FILE"] == "exchanges.jsonl"
        # This validates the port interpolation inputs, not Docker's merge engine.
        assert original["services"]["mitmproxy"]["ports"] == ["${HOST_PORT:-8080}:8080"]
        assert original["services"][config["SUT_SERVICE"]]["ports"] == ["${JACOCO_PORT:-6300}:6300"]
        assert all("ports" not in entry for entry in override["services"].values())
        spec = json.loads((EMB / config["SPEC_SOURCE"]).read_text())
        count = sum(method in {"get", "put", "post", "delete", "patch", "head", "options", "trace"}
                    for item in spec["paths"].values() for method in item)
        if config["AUTH_ROLE_DEFAULT"] != "none":
            auth = yaml.safe_load((EMB / config["AUTH_SOURCE"]).read_text())
            selected = [role for role in auth["auth"] if role["name"] == config["AUTH_ROLE_DEFAULT"]]
            assert len(selected) == 1 and len(selected[0]["fixedHeaders"]) == 1
            assert selected[0]["fixedHeaders"][0]["name"].lower() == "authorization"
            for role in auth["auth"]:
                public_roles.add(role["name"])
                for header in role.get("fixedHeaders", []):
                    value = header["value"]
                    fixture_values.add(value)
                    fixture_tokens.add(value.split(" ", 1)[-1])
        else:
            assert config["AUTH_SOURCE"] == ""
            assert not (EMB / "auth" / f"{sut}-auth.yaml").exists()
        print(f"PASS CONFIG:{sut} jar/paths/YAML/proxy/auth-shape; declared_operations={count}; "
              f"spec_version={spec.get('swagger', spec.get('openapi'))}", flush=True)

    common = (HERE / "common.sh").read_text()
    assert "HOST_PORT=127.0.0.1:18080 JACOCO_PORT=127.0.0.1:16300" in common
    assert 'exec 8<"$HERE/../harness/.run.lock"' in common
    run = (HERE / "run_pilot.sh").read_text()
    for marker in ('SCHEMA_CHECKS', '--request-timeout', 'explicit,generate', 'acquire_run_lock',
                   'mkdir "$run_dir"', '--no-build', 'derecurse.py" "$original_spec"',
                   'mutation_gen', 'Generator mutation selected different operations',
                   'redact_auth.py', 'run_metadata.py', 'jacococli.jar'):
        assert marker in run, marker
    batch = (HERE / "run_batch.sh").read_text()
    assert 'PILOT_RUN_ID="$id"' in batch and 'baseline=$LAST_RUN' in batch
    analysis = (HERE / "analyse_run.sh").read_text()
    for marker in ('schema_checks', 'harness_sha256', 'auth_source', 'r["sut"]',
                   'Current tool differs', 'generator-input.json', 'mkdir "$analysis"'):
        assert marker in analysis, marker
    print("PASS PRESERVED_FIXES loopback/locks/image-reuse/de-recursion/checks/timeout/no-shrink/provenance/exclusive-output", flush=True)

    snapshot = json.loads((HERE / "source-harness-sha256.json").read_text())
    for name, expected in snapshot.items():
        assert digest(HERE.parent / "harness" / name) == expected, name
    print(f"PASS SOURCE_HARNESS_UNCHANGED {len(snapshot)} original file digests", flush=True)
    # Public role identifiers are explicitly required in these non-secret configs.
    # Do not mistake a plain role identifier for a copied Authorization header.
    fixture_values.update(fixture_tokens - public_roles)
    outputs = list(HERE.rglob("*"))
    report = EXP.parent / "09_collab" / "reports" / "T14_report.md"
    if report.exists():
        outputs.append(report)
    for path in outputs:
        if path.is_file():
            data = path.read_bytes()
            assert not any(value.encode() in data for value in fixture_values if value), path.name
    print("PASS SECRET_ABSENCE no EMB full fixed-header values or non-role tokens in v2 artifacts; "
          "public role identifiers permitted; values withheld", flush=True)
    print("BEGIN DERECURSE UNIT TESTS", flush=True)
    subprocess.run(["/usr/bin/python3", "-I", "-B", str(HERE / "test_derecurse.py")],
                   check=True, stderr=subprocess.STDOUT)
    print("PASS ALL STATIC CHECKS AND PERMITTED UNIT TESTS", flush=True)
    print("NOT EXECUTED: harness orchestration, Docker, Compose, Java, Schemathesis, SUTs, "
          "network/downloads, builds, dependency installs, tool-pipeline execution.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Keep fixture/parser exceptions from echoing input credential values.
        print("FAIL STATIC VALIDATION; inspect this validator and the last completed check", file=sys.stderr)
        raise SystemExit(1) from None
