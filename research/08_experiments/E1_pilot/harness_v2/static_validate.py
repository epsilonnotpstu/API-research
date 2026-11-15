"""T14/T17/T27 static validation and the permitted stdlib derecurse tests.

No harness scripts, third-party project code, Docker, Java, network, or SUT
commands are executed. Run from any directory with /usr/bin/python3 -I -B.
"""
import ast
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

import yaml

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1]
EMB = EXP / "_external" / "emb"
SUTS = ("scout-api", "swagger-petstore", "market", "cwa-verification")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    print("T14/T17/T27 validation:", datetime.datetime.now(datetime.timezone.utc).isoformat(), flush=True)
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
        if sut == "cwa-verification":
            cwa = EMB / "jdk_11_maven/cs/rest/cwa-verification-server"
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            pom = ET.parse(cwa / "pom.xml").getroot()
            plugin = next(p for p in pom.findall("m:build/m:plugins/m:plugin", ns)
                          if p.findtext("m:artifactId", namespaces=ns) == "spring-boot-maven-plugin")
            execution = next(e for e in plugin.findall("m:executions/m:execution", ns)
                             if "repackage" in [g.text for g in e.findall("m:goals/m:goal", ns)])
            final_name = execution.findtext("m:configuration/m:finalName", namespaces=ns)
            classifier = execution.findtext("m:configuration/m:classifier", namespaces=ns)
            assert final_name == "cwa-verification" and classifier == "sut"
            assert (EMB / config["JAR_SOURCE"]) == cwa / "target" / f"{final_name}-{classifier}.jar"
            assert config["AUTH_ROLE_DEFAULT"] == "none"
            assert not list((EMB / "auth").glob("cwa-verification*.yaml"))
            assert config["BASE_PATH_DEFAULT"] == "/" and count == 5
            assert all(urlsplit(server["url"]).path in ("", "/") for server in spec["servers"])
            assert config["HEALTH_PATH_DEFAULT"] == "/version/v1/tan/verify"
            assert config["HEALTH_METHOD_DEFAULT"] == "POST" and config["HEALTH_STATUS_DEFAULT"] == "400"
            assert "--management.server.port=-1" in (EMB / config["DOCKERFILE"]).read_text()
            assert 'mvcMatchers("/version/**").permitAll()' in (
                cwa / "src/main/java/app/coronawarn/verification/config/SecurityConfig.java").read_text()
            app = yaml.safe_load((cwa / "src/main/resources/application.yml").read_text())
            assert app["jwt"]["enabled"] is False
            module_spec = importlib.util.spec_from_file_location("t17_derecurse", HERE / "derecurse.py")
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            generated, cuts = module.derecurse(spec)
            assert generated["paths"] == spec["paths"]
            assert module.derecurse(generated) == (generated, [])
            print(f"PASS CWA_SOURCE pom-derived-jar/root-base/POST-empty-400/no-auth-fixture/JWT-disabled; "
                  f"static_derecurse_cuts={len(cuts)}; runtime unverified", flush=True)
            print("REVIEW CWA_ORIGIN absolute localhost server versus Docker proxy/upstream origins; "
                  "verify authority matching before interpreting conformance results (README CWA section)", flush=True)

    common = (HERE / "common.sh").read_text()
    allowlist = re.search(r"case .*? in ([^)]+)\)", common).group(1)
    assert set(allowlist.split("|")) == set(SUTS)
    assert "HOST_PORT=127.0.0.1:18080 JACOCO_PORT=127.0.0.1:16300" in common
    assert 'exec 8<"$HERE/../harness/.run.lock"' in common
    run = (HERE / "run_pilot.sh").read_text()
    fuzzer_args = (HERE / "fuzzer_args.sh").read_text()
    assert 'export PILOT_EVOMASTER_SCHEMA_ORACLES=${EVOMASTER_SCHEMA_ORACLES:-true}' in run
    assert 'export PILOT_EVOMASTER_INPUT=${EVOMASTER_INPUT:-spec}' in run
    assert 'build_strict_args "$fault"' in run
    assert run.index('build_strict_args "$fault"') < run.index('for tool in docker')
    assert run.count('"${only_args[@]}" "${strict_args[@]}" --out') == 2
    assert 'build_strict_args() {' in fuzzer_args
    assert "data['strict_keywords']" in (HERE / 'run_metadata.py').read_text()
    assert 'build_derecursed_generator_input() {' in run
    assert run.count('build_derecursed_generator_input\n') == 2
    assert '"${evomaster_mounts[@]}"' in run
    assert '$schema_source:/work/spec.test.json:ro' in fuzzer_args
    assert "'generator_input_sha256':" in (HERE / "run_metadata.py").read_text()
    assert "'evomaster_input':" in (HERE / "run_metadata.py").read_text()
    assert '--schemaOracles "$PILOT_EVOMASTER_SCHEMA_ORACLES"' in fuzzer_args
    assert "'evomaster_schema_oracles':" in (HERE / "run_metadata.py").read_text()
    for marker in ('SCHEMA_CHECKS', '--request-timeout', 'explicit,generate', 'acquire_run_lock',
                   'mkdir "$run_dir"', '--no-build', 'derecurse.py" "$original_spec"',
                   'mutation_gen', 'Generator mutation selected different operations',
                   'redact_auth.py', 'run_metadata.py', 'jacococli.jar'):
        assert marker in run + fuzzer_args, marker
    batch = (HERE / "run_batch.sh").read_text()
    assert batch.index('build_strict_args REQUEST_STRICT') < batch.index('mkdir -p "$runs/batches"')
    assert 'STRICT_KEYWORDS= PILOT_RUN_ID="$id"' in batch
    assert 'STRICT_KEYWORDS requires FAULTS=REQUEST_STRICT' in batch
    assert 'PILOT_RUN_ID="$id"' in batch and 'baseline=$LAST_RUN' in batch
    assert 'HEALTH_METHOD_DEFAULT:-GET' in run and 'HEALTH_STATUS_DEFAULT:?' in run
    assert '--only-ops' in run and 'pull failed; using local copy' in run
    assert 'FAULTS:-' in batch and 'ORACLE_POOL:-all' in batch and 'eligible_ops.py' in batch
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
    for task in ("T14", "T17"):
        report = EXP.parent / "09_collab" / "reports" / f"{task}_report.md"
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
    print("BEGIN FUZZER ARGV/ROUTING/REDACTION/PROVENANCE UNIT TESTS", flush=True)
    subprocess.run(["/usr/bin/python3", "-I", "-B", str(HERE / "test_fuzzer_args.py")],
                   check=True, stderr=subprocess.STDOUT)
    print("PASS ALL STATIC CHECKS AND PERMITTED UNIT TESTS", flush=True)
    print("NOT EXECUTED: harness orchestration, Docker, Compose, Java, Schemathesis, EvoMaster, SUTs, "
          "network/downloads, builds, dependency installs, tool-pipeline execution.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Keep fixture/parser exceptions from echoing input credential values.
        print("FAIL STATIC VALIDATION; inspect this validator and the last completed check", file=sys.stderr)
        raise SystemExit(1) from None
