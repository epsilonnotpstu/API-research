"""Apply one reviewed Java edit to a fresh source-tree copy; never run/build code.

The JSON catalogue is data, not a Java parser or an executable extension point.
Each entry pins one file digest, line and unique exact before/after anchor.
"""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
EMB = EXP / "_external" / "emb"
ROOTS = {
    "scout-api": "jdk_8_maven/cs/rest/original/scout-api",
    "swagger-petstore": "jdk_8_maven/cs/rest/original/swagger-petstore",
    "market": "jdk_11_maven/cs/rest-gui/market",
    "cwa-verification": "jdk_11_maven/cs/rest/cwa-verification-server",
}
OPERATORS = {
    "DROP_VALIDATION": {"I-ACCEPT-INVALID", "I-CRASH"},
    "WRONG_STATUS": {"I-RESP-CONTRACT"},
    "DROP_NULL_CHECK": {"I-CRASH"},
    "RESP_FIELD": {"I-RESP-CONTRACT"},
    "REJECT_VALID": {"I-REJECT-VALID"},
}
SIGNALS = {"SERVER_ERROR", "INVALID_ACCEPTED", "VALID_REJECTED", "RESPONSE_SCHEMA", "UNDOCUMENTED_STATUS"}
EXCLUDED = {".git", ".hg", ".svn", ".idea", ".venv", "venv", "__pycache__", "target", "node_modules"}


class MutationError(ValueError):
    """An input/snapshot safety check failed; no ready manifest is produced."""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def relative_java(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise MutationError("Site file must be a relative POSIX Java path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ("", ".", "..") for p in value.split("/")):
        raise MutationError("Site file cannot escape the source tree")
    if path.suffix != ".java" or any(p in EXCLUDED for p in path.parts):
        raise MutationError("Site must target a non-excluded .java source file")
    return path.as_posix()


def validate_sites(sites):
    if not isinstance(sites, list) or not sites:
        raise MutationError("Catalogue must contain a nonempty sites list")
    ids = set()
    for site in sites:
        if not isinstance(site, dict):
            raise MutationError("Each catalogue site must be an object")
        try:
            sid, sut, operator = site["site_id"], site["sut"], site["operator"]
            if not isinstance(sid, str) or not sid or sid in ids:
                raise MutationError("Site IDs must be nonempty and unique")
            ids.add(sid)
            if sut not in ROOTS or operator not in OPERATORS:
                raise MutationError("Unknown SUT or operator")
            relative_java(site["file"])
            if type(site["line"]) is not int or site["line"] < 1:
                raise MutationError("Site line must be a positive integer")
            before, after = site["before"], site["after"]
            if not isinstance(before, str) or not isinstance(after, str) or not before or before == after:
                raise MutationError("Site needs a nonempty before and a different after snippet")
            digest = site["source_sha256"]
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise MutationError("Site must pin the original file SHA-256")
            if site["expected_L1"] != "IMPL" or site["expected_L2"] not in OPERATORS[operator]:
                raise MutationError("Expected labels do not match the operator")
            signals = site["expected_conformance_signal"]
            if not isinstance(signals, list) or any(s not in SIGNALS for s in signals):
                raise MutationError("Unknown conformance signal")
            operations = site["operations"]
            if not isinstance(operations, list) or not operations:
                raise MutationError("A reviewed affected-operation list is required")
            seen = set()
            for op in operations:
                path, method = op["path"], op["method"]
                if not isinstance(path, str) or not path.startswith("/") or method not in {
                    "get", "post", "put", "delete", "patch", "head", "options", "trace"}:
                    raise MutationError("Invalid affected operation")
                if (path, method) in seen:
                    raise MutationError("Duplicate affected operation")
                seen.add((path, method))
        except (KeyError, TypeError) as error:
            raise MutationError("Malformed catalogue entry") from error
    return sites


def select_site(sites, sut, operator, seed, site_id=None):
    validate_sites(sites)
    if type(seed) is not int or seed < 0:
        raise MutationError("Seed must be a non-negative integer")
    pool = sorted((s for s in sites if s["sut"] == sut and s["operator"] == operator),
                  key=lambda s: s["site_id"])
    if not pool:
        raise MutationError("No reviewed site for this SUT/operator")
    if site_id is not None:
        selected = [s for s in pool if s["site_id"] == site_id]
        if len(selected) != 1:
            raise MutationError("Explicit site does not belong to this SUT/operator")
        return selected[0]
    # Stable across Python random implementation changes and catalogue ordering.
    index = int(sha(f"{sut}:{operator}:{seed}".encode()), 16) % len(pool)
    return pool[index]


def inventory(root):
    """Return copied-file digests/modes; reject links and non-regular retained files."""
    files = {}
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for name in dirs + names:
            path = Path(directory) / name
            if name in EXCLUDED:
                continue
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise MutationError("Symlinks in the copied source set are not supported")
            if stat.S_ISDIR(info.st_mode):
                continue
            if not stat.S_ISREG(info.st_mode):
                raise MutationError("Non-regular source files are not supported")
            relative = path.relative_to(root).as_posix()
            files[relative] = {"sha256": sha(path.read_bytes()), "mode": stat.S_IMODE(info.st_mode) & 0o777}
    return dict(sorted(files.items()))


def edit_bytes(original, site):
    if sha(original) != site["source_sha256"]:
        raise MutationError("Source file digest differs from the reviewed site")
    before, after = site["before"].encode(), site["after"].encode()
    if original.count(before) != 1:
        raise MutationError("Before snippet must occur exactly once")
    start = original.index(before)
    if original[:start].count(b"\n") + 1 != site["line"]:
        raise MutationError("Source line differs from the reviewed site")
    return original[:start] + after + original[start + len(before):]


def patch_text(original, mutated, relative):
    result = []
    for line in difflib.unified_diff(original.decode("utf-8").splitlines(keepends=True),
                                     mutated.decode("utf-8").splitlines(keepends=True),
                                     fromfile="a/" + relative, tofile="b/" + relative):
        result.append(line)
        if not line.endswith("\n"):
            result.append("\n\\ No newline at end of file\n")
    return "".join(result)


def mutate(source, out, sut, operator, sites, seed=1, site_id=None):
    source, out = Path(source).resolve(), Path(out).absolute()
    if out.is_symlink() or out.exists():
        raise MutationError("Output must not exist (including symlinks)")
    out = out.resolve()
    if not source.is_dir() or source == out or source in out.parents or out in source.parents:
        raise MutationError("Source and output trees must be separate and non-overlapping")
    if out == EMB.resolve() or EMB.resolve() in out.parents or out in EMB.resolve().parents:
        raise MutationError("Output may not write to or contain the protected EMB tree")
    site = select_site(sites, sut, operator, seed, site_id)
    files = inventory(source)
    relative = relative_java(site["file"])
    if relative not in files:
        raise MutationError("Site file is absent from the copy inventory")
    original = (source / relative).read_bytes()
    changed = edit_bytes(original, site)
    patch = patch_text(original, changed, relative)
    # All semantic preflight failures precede output creation. Partial copy failure
    # leaves an output without a ready manifest; it is never silently reused.
    out.mkdir(parents=True, exist_ok=False)
    tree = out / "source"
    tree.mkdir()
    for name, expected in files.items():
        src, dst = source / name, tree / name
        fd = os.open(src, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as stream:
            data = stream.read()
        if sha(data) != expected["sha256"]:
            raise MutationError("Source changed while copying; discard this incomplete output")
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("xb") as stream:
            stream.write(changed if name == relative else data)
        dst.chmod(expected["mode"])
    if inventory(source) != files:
        raise MutationError("Source changed during mutation; discard this incomplete output")
    result_files = inventory(tree)
    changed_files = [p for p in files if result_files.get(p) != files[p]]
    if changed_files != [relative] or set(result_files) != set(files):
        raise MutationError("Copy differs outside the single reviewed source file")
    edits = [{"file": relative, "line": site["line"], "before": site["before"], "after": site["after"]}]
    manifest = {
        "format": "codemut-v1", "injection_side": "IMPL", "sut": sut, "operator": operator,
        "site_id": site["site_id"], "seed": seed, "file": relative, "line": site["line"],
        "before": site["before"], "after": site["after"], "operations": site["operations"],
        "expected_L1": site["expected_L1"], "expected_L2": site["expected_L2"],
        "expected_conformance_signal": site["expected_conformance_signal"],
        "source_spec": None, "source_root": str(source), "source_sha256": sha(original),
        "mutated_file_sha256": sha(changed), "source_tree_sha256": canonical_hash(files),
        "mutated_tree_sha256": canonical_hash(result_files), "source_files": files,
        "excluded_names": sorted(EXCLUDED), "catalogue_site_sha256": canonical_hash(site),
        "catalogue_sha256": canonical_hash(sites),
        "candidate_site_ids": sorted(s["site_id"] for s in sites if s["sut"] == sut and s["operator"] == operator),
        "explicit_site": site_id is not None,
        "expected_L2_by_signal": ({"INVALID_ACCEPTED": "I-ACCEPT-INVALID", "SERVER_ERROR": "I-CRASH"}
                                  if operator == "DROP_VALIDATION" else {s: site["expected_L2"] for s in site["expected_conformance_signal"]}),
        "patch_sha256": sha(patch.encode()), "operations_mutated": len(site["operations"]),
        "mutations": [dict(op, fault=operator, operator=operator, edits=edits,
                           expected_L1=site["expected_L1"], expected_L2=site["expected_L2"])
                      for op in site["operations"]],
        "selection_algorithm": "sha256(sut:operator:decimal_seed) modulo sorted candidate count",
        "conditions": site.get("conditions", "See reviewed catalogue"),
        "validation": {"source_copy": "one changed file; source rechecked", "java_compile": "not_run",
                       "sut_execution": "not_run", "fault_observed": False, "attribution": "NEEDS_MANUAL"},
        "limitations": ["operation mapping is source-reviewed, not measured reachability",
                        "expected labels are injection intent, not observed causal attribution",
                        "fresh attribution only; replay of unchanged exchanges/spec cannot test a code mutant"],
    }
    with (out / "patch.diff").open("x", encoding="utf-8") as stream:
        stream.write(patch)
    with (out / "manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sut", choices=sorted(ROOTS), required=True)
    parser.add_argument("--operator", choices=sorted(OPERATORS), required=True)
    parser.add_argument("--source", type=Path, help="SUT root; defaults to its EMB source checkout")
    parser.add_argument("--catalog", type=Path, default=HERE / "sites.json")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--site", help="Reviewed site_id, constrained to the selected SUT/operator")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        catalogue = json.loads(args.catalog.read_text(encoding="utf-8"))
        manifest = mutate(args.source or EMB / ROOTS[args.sut], args.out, args.sut, args.operator,
                          catalogue["sites"], args.seed, args.site)
    except (MutationError, OSError, UnicodeError, json.JSONDecodeError, KeyError) as error:
        parser.exit(2, f"codemut: {error}\n")
    print(json.dumps({"site_id": manifest["site_id"], "operator": manifest["operator"],
                      "out": str(args.out.resolve()), "execution": "not_run"}, sort_keys=True))


if __name__ == "__main__":
    main()
