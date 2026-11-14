"""Validate EvoMaster-only settings and schema routing, without network or SUT code."""
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit


def validate_options(mode, seed, budget, data_gen, only_ops):
    if data_gen:
        raise ValueError("EvoMaster does not support DATA_GEN; unset it")
    if only_ops and mode != "mutated":
        raise ValueError("EvoMaster ONLY_OPS selects mutation candidates; requires mutated mode")
    if not seed.isascii() or not seed.isdecimal() or not 0 <= int(seed) <= 9223372036854775807:
        raise ValueError("EvoMaster seed must fit a non-negative Long")
    if not budget.isascii() or not budget.isdecimal() or not 1 <= int(budget) <= 2147483527:
        raise ValueError("EvoMaster budget exceeds the supported seconds range")


def server_path(server):
    url = server.get("url")
    if not isinstance(url, str) or "{" in url or "}" in url:
        raise ValueError("EvoMaster requires concrete schema server URLs")
    parts = urlsplit(url)
    if parts.query or parts.fragment or parts.username or parts.password:
        raise ValueError("EvoMaster schema server URLs cannot contain credentials, query or fragment")
    if parts.scheme and parts.scheme not in ("http", "https"):
        raise ValueError("EvoMaster schema server URL must use HTTP(S)")
    path = parts.path or "/"
    if not path.startswith("/") or "//" in path or any(p in (".", "..") for p in path.split("/")):
        raise ValueError("EvoMaster requires an absolute, normalized schema base path")
    return path.rstrip("/") or "/"


def validate_schema(document, base_path):
    # --base replaces only the authority; EvoMaster infers the path from the schema.
    # Reject ambiguous server overrides rather than risk direct/non-proxy traffic.
    if "swagger" in document:
        paths = {server_path({"url": document.get("basePath", "/")})}
    elif "openapi" in document:
        servers = document.get("servers", [{"url": "/"}])
        if not isinstance(servers, list) or not servers:
            raise ValueError("EvoMaster requires a nonempty schema servers list")
        paths = {server_path(server) for server in servers}
        for item in document.get("paths", {}).values():
            if not isinstance(item, dict):
                raise ValueError("EvoMaster requires object path items")
            if "servers" in item or any(isinstance(op, dict) and "servers" in op for op in item.values()):
                raise ValueError("EvoMaster path/operation server overrides are unsupported")
    else:
        raise ValueError("EvoMaster requires a Swagger/OpenAPI document")
    expected = server_path({"url": base_path})
    if paths != {expected}:
        raise ValueError("EvoMaster schema base path differs from BASE_PATH; refusing a different target")


def validate_outputs(directory):
    directory = Path(directory)
    stats = directory / "statistics.csv"
    tests = directory / "tests"
    if not stats.is_file() or not stats.stat().st_size:
        raise ValueError("Missing EvoMaster statistics")
    if not any(p.is_file() and p.stat().st_size for p in tests.rglob("*.java")):
        raise ValueError("Missing EvoMaster generated tests")


def main():
    action, *args = sys.argv[1:]
    if action == "options":
        validate_options(*args)
    elif action == "schema":
        validate_schema(json.loads(Path(args[0]).read_text()), args[1])
    elif action == "outputs":
        validate_outputs(args[0])
    else:
        raise ValueError("Unknown EvoMaster validation action")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        # Messages contain no supplied header, schema URL, or environment value.
        raise SystemExit(str(error)) from None
