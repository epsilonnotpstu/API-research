from pathlib import Path
E = Path('08_experiments/E5_codemut')
text = r'''# E5 code mutation: tool and future execution plan

T19 delivers source edits and a plan, with **no Maven, Java, Docker, SUT or
Schemathesis execution**. All anticipated runtime outcomes are [H]. Claude runs
the commands below only after the live batch chain ends and the supervisor
approves external execution (`09_collab/PROTOCOL.md:12–14`;
`09_collab/tasks/T19.md`, Constraints). The current harness remains unchanged.

`OPERATORS.md` lists five families, all 20 digest-pinned sites and the ten
first-batch choices (2–3 per SUT). `sites.json` rows use `site_id`;
`exposure.json` rows use `evidence_id`. Captured operation traffic is evidence of
HTTP exposure, not proof of reaching the edited branch (`OPERATORS.md:32–41`).

## Using the tool without building

Run from the repository root with the system Python. A fresh output directory is
required. This example selects the reviewed missing-product absence check:

```bash
E5="$PWD/08_experiments/E5_codemut"
/usr/bin/python3 -I -B "$E5/codemut.py" --sut market \
  --operator DROP_NULL_CHECK --site market-drop-null --seed 1 \
  --out "$E5/work/market-drop-null-s1"
/usr/bin/python3 -I -B "$E5/test_codemut.py" -v
```

Omit `--site` to choose by SHA-256 of `sut:operator:decimal_seed`, modulo the
sorted matching pool. The present catalogue has one site per SUT/operator, so
changing the seed currently cannot change that choice. `--source` accepts a
separate checkout only if its target bytes match the pinned site; `--catalog`
accepts reviewed JSON data (`codemut.py:102–119,239–259`; `sites.json`, all rows).

The output contains `source/`, `patch.diff` and `manifest.json`. The manifest
records before/after, relative file and original line, original file SHA-256,
original/mutated retained-tree digests, per-file hashes/modes, patch/catalogue/site
digests, selection provenance, affected operations and expected labels/signals.
`source_tree_sha256` hashes canonical JSON of retained file digests and modes;
it is not a Git commit or a digest of build outputs. `source_sha256` is the
original edited file. `mutations` mirrors the specmut operation records so that
`attribute.py` can read it. `operations_mutated` counts reviewed affected-operation
mappings, not measured coverage. `expected_L2_by_signal` preserves both possible
DROP_VALIDATION outcomes (`codemut.py:202–234`; `../tools/specmut.py:246–291`; `../tools/attribute.py:25–31`).

Only one reviewed Java file changes. Build directories, VCS metadata and caches
listed in `EXCLUDED` are omitted; resources and executable modes are retained.
Existing output, overlapping source/output, output under EMB, retained symlinks,
nonregular files, anchor/hash/line drift and mismatched site/operator fail closed.
The original inventory is rechecked after copying. A copy/I/O failure can leave
an incomplete output without a ready manifest: retain it for diagnosis and choose
a new output path. This is an exact-edit tool, not a Java compiler or concurrent
filesystem security boundary; freeze the checkout while copying
(`codemut.py:33,122–200`; `test_codemut.py`, synthetic safety cases).

## Future build commands for Claude

The commands in this and the next two sections are **unexecuted plans**. Use a
fresh Bash session at the repository root with `set -euo pipefail`. Do not run
`prepare_dist.sh` to stage a mutant: that would replace the shared EMB jar.

**Required unresolved input:** `MAVEN8_IMAGE` and `MAVEN11_IMAGE` must identify the
actual Maven images used by the coordinator's original builds. T19 has no
recorded identity for those containers. A POM's Java version or market's source
Dockerfile does not establish which Maven image the coordinator used. If those
original build containers still exist, Claude can recover their immutable image
IDs with the following commands; otherwise supply their recorded IDs/digests
before building. Do not substitute a guessed Maven tag.

```bash
: "${ORIGINAL_MAVEN8_CONTAINER:?supply the original JDK8 build container identity}"
: "${ORIGINAL_MAVEN11_CONTAINER:?supply the original JDK11 build container identity}"
export MAVEN8_IMAGE=$(docker inspect --format '{{.Image}}' "$ORIGINAL_MAVEN8_CONTAINER")
export MAVEN11_IMAGE=$(docker inspect --format '{{.Image}}' "$ORIGINAL_MAVEN11_CONTAINER")
```

The command template covers all four SUTs. Change the three selection variables
together using a `sites.json` row. The first batch uses scout-wrong-status,
scout-drop-null, scout-reject-valid; petstore-response-field,
petstore-reject-valid; market-wrong-status, market-drop-null,
market-response-field; cwa-drop-validation, cwa-drop-null
(`OPERATORS.md`, First E5 batch table).

```bash
set -euo pipefail
E5="$PWD/08_experiments/E5_codemut"
H="$PWD/08_experiments/E1_pilot/harness_v2"
EMB="$PWD/08_experiments/_external/emb"
sut=market
operator=DROP_NULL_CHECK
site=market-drop-null
stamp=$(date -u +%Y%m%dT%H%M%SZ)
MUT="$E5/work/${site}_${stamp}"
case "$sut" in
  scout-api)
    : "${MAVEN8_IMAGE:?confirmed original Maven/JDK8 image required}"
    BUILD_IMAGE=$MAVEN8_IMAGE
    ROOT="$EMB/jdk_8_maven/cs/rest/original/scout-api"
    JAR_REL=api/target/scout-api-sut.jar
    MVN_ARGS=(-B -pl api -am -Dmaven.test.skip=true package)
    RUNTIME_TAG=amazoncorretto:8-alpine-jdk ;;
  swagger-petstore)
    : "${MAVEN8_IMAGE:?confirmed original Maven/JDK8 image required}"
    BUILD_IMAGE=$MAVEN8_IMAGE
    ROOT="$EMB/jdk_8_maven/cs/rest/original/swagger-petstore"
    JAR_REL=target/swagger-petstore-sut.jar
    MVN_ARGS=(-B -Dmaven.test.skip=true package)
    RUNTIME_TAG=amazoncorretto:8-alpine-jdk ;;
  market)
    : "${MAVEN11_IMAGE:?confirmed original Maven/JDK11 image required}"
    BUILD_IMAGE=$MAVEN11_IMAGE
    ROOT="$EMB/jdk_11_maven/cs/rest-gui/market"
    JAR_REL=market-rest/target/market-sut.jar
    MVN_ARGS=(-B -pl market-rest -am -Dmaven.test.skip=true package)
    RUNTIME_TAG=amazoncorretto:11-alpine-jdk ;;
  cwa-verification)
    : "${MAVEN11_IMAGE:?confirmed original Maven/JDK11 image required}"
    BUILD_IMAGE=$MAVEN11_IMAGE
    ROOT="$EMB/jdk_11_maven/cs/rest/cwa-verification-server"
    JAR_REL=target/cwa-verification-sut.jar
    MVN_ARGS=(-B -Dmaven.test.skip=true -Dcheckstyle.skip=true package)
    RUNTIME_TAG=amazoncorretto:11-alpine-jdk ;;
  *) exit 2 ;;
esac
BUILD_IMAGE=$(docker image inspect --format '{{.Id}}' "$BUILD_IMAGE")
RUNTIME_BASE=$(docker image inspect --format '{{index .RepoDigests 0}}' "$RUNTIME_TAG")
[[ $BUILD_IMAGE == sha256:* && $RUNTIME_BASE == *@sha256:* ]]
: "${MAVEN_CACHE:?absolute path to the original warmed Maven repository}"
[[ $MAVEN_CACHE == /* && -d $MAVEN_CACHE ]]
/usr/bin/python3 -I -B "$E5/codemut.py" --sut "$sut" --operator "$operator" \
  --source "$ROOT" --site "$site" --seed 1 --out "$MUT"
# Fresh control copy from exactly the manifest's original retained inventory.
/usr/bin/python3 -I -B - "$MUT/manifest.json" "$MUT/control.source" <<'CONTROL_PY'
import hashlib, json, pathlib, shutil, sys
m = json.loads(pathlib.Path(sys.argv[1]).read_text())
root, out = pathlib.Path(m['source_root']), pathlib.Path(sys.argv[2])
out.mkdir(exist_ok=False)
for name, entry in m['source_files'].items():
    src, dst = root / name, out / name
    assert not src.is_symlink()
    assert hashlib.sha256(src.read_bytes()).hexdigest() == entry['sha256']
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    dst.chmod(entry['mode'])
CONTROL_PY
docker image inspect "$BUILD_IMAGE" > "$MUT/maven-image.json"
docker image inspect "$RUNTIME_BASE" > "$MUT/runtime-base.json"
printf '%s\n' "${MVN_ARGS[@]}" > "$MUT/maven-arguments.txt"
# Clone the same warmed repository for both builds; never mount original SUT source.
for role in control mutant; do
  mkdir "$MUT/m2-$role"
  cp -a "$MAVEN_CACHE/." "$MUT/m2-$role/"
  tree="$MUT/source"
  [[ $role != control ]] || tree="$MUT/control.source"
  docker run --rm --user "$(id -u):$(id -g)" \
    --env MAVEN_CONFIG=/tmp/maven-config --env JAVA_TOOL_OPTIONS=-Duser.home=/tmp \
    --mount "type=bind,src=$tree,dst=/work" \
    --mount "type=bind,src=$MUT/m2-$role,dst=/m2" --workdir /work \
    "$BUILD_IMAGE" mvn -Dmaven.repo.local=/m2 "${MVN_ARGS[@]}" \
    > "$MUT/build-$role.log" 2>&1
  test -s "$tree/$JAR_REL"
done
# Abort if Maven changed a retained source/resource file. target/ is excluded.
/usr/bin/python3 -I -B - "$E5/codemut.py" "$MUT" <<'VERIFY_PY'
import importlib.util, json, pathlib, sys
spec = importlib.util.spec_from_file_location('codemut', sys.argv[1])
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
p = pathlib.Path(sys.argv[2]); m = json.loads((p / 'manifest.json').read_text())
for folder, key in [('control.source', 'source_tree_sha256'), ('source', 'mutated_tree_sha256')]:
    assert c.canonical_hash(c.inventory(p / folder)) == m[key], folder
# Compare resolved Maven artifacts as well as the source inventories.
deps = {}
for role in ('control', 'mutant'):
    root = p / ('m2-' + role)
    deps[role] = {f.relative_to(root).as_posix(): c.sha(f.read_bytes())
                  for f in sorted(root.rglob('*')) if f.is_file() and f.suffix in ('.jar', '.pom')}
assert deps['control'] == deps['mutant'], 'Resolved Maven artifacts differ'
(p / 'resolved-artifacts.json').write_text(json.dumps(deps, indent=2) + '\n')
VERIFY_PY
```

Module/JAR selection follows the four `harness_v2/suts/<sut>.env` rows
`JAR_SOURCE` and the source POMs: scout `api/pom.xml:114–146`; petstore
`pom.xml:40–42`; market `market-rest/pom.xml:25–47`; CWA
`pom.xml:272–285` (paths under the `ROOT` above). These are proposed package
commands, not a claim to reproduce the coordinator's exact original argv.
CWA's checkstyle skip is deliberate for small injected guards; use it for both
roles. Missing dependencies or any compile failure are recorded as build-invalid,
not replaced by an old jar. Some Maven plugins can download artifacts outside
`.m2` (petstore `pom.xml:181–199`); record URLs/checksums and compare resolved
artifact hashes for both builds. Frozen starting caches and the same Maven image
do not alone prove identical dependency resolution. If artifacts differ, repair
and rebuild both roles before accepting a pair. JAR timestamps may also differ.

Stage private runtime contexts. The source Dockerfile's entrypoint and additional
files are reused; only its FROM line is pinned to one already installed digest
for both roles. Distinct E5 tags never overwrite a `:pilot` tag. The two image
labels below are checked by the proposed harness patch.

```bash
for role in control mutant; do
  tree="$MUT/source"
  key=mutated_tree_sha256
  [[ $role != control ]] || { tree="$MUT/control.source"; key=source_tree_sha256; }
  ctx="$MUT/context-$role"
  mkdir -p "$ctx/dist" "$ctx/dockerfiles" "$ctx/scripts/dockerize/data/additional_files"
  cp "$tree/$JAR_REL" "$ctx/dist/$sut-sut.jar"
  cp "$EMB/dist/jacocoagent.jar" "$ctx/dist/jacocoagent.jar"
  if [[ $sut == scout-api || $sut == swagger-petstore ]]; then
    cp -a "$EMB/scripts/dockerize/data/additional_files/$sut" \
      "$ctx/scripts/dockerize/data/additional_files/"
  fi
  /usr/bin/python3 -I -B - "$EMB/dockerfiles/$sut.dockerfile" \
    "$ctx/dockerfiles/$sut.dockerfile" "$RUNTIME_BASE" <<'DOCKERFILE_PY'
import pathlib, sys
src, dst, base = sys.argv[1:]
lines = pathlib.Path(src).read_text().splitlines(keepends=True)
assert lines[0].startswith('FROM ') and sum(x.startswith('FROM ') for x in lines) == 1
lines[0] = 'FROM ' + base + '\n'
pathlib.Path(dst).write_text(''.join(lines))
DOCKERFILE_PY
  source_sha=$(/usr/bin/python3 -I -B -c \
    'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$MUT/manifest.json" "$key")
  jar_sha=$(sha256sum "$ctx/dist/$sut-sut.jar"); jar_sha=${jar_sha%% *}
  image="r1-$sut-sut:e5-${site}-${stamp}-${role}"
  if docker image inspect "$image" >/dev/null 2>&1; then exit 2; fi
  docker build --pull=false --label "org.r1.jar_sha256=$jar_sha" \
    --label "org.r1.source_tree_sha256=$source_sha" --tag "$image" \
    --file "$ctx/dockerfiles/$sut.dockerfile" "$ctx" > "$MUT/image-$role.log" 2>&1
  printf '%s\n' "$image" > "$MUT/tag-$role.txt"
  docker image inspect "$image" > "$MUT/image-$role.json"
  (cd "$ctx" && find . -type f -print0 | sort -z | xargs -0 sha256sum) \
    > "$MUT/context-$role.sha256"
done
```

Runtime inputs: `../_external/emb/dockerfiles/{scout-api,swagger-petstore,market,
cwa-verification}.dockerfile`, FROM/COPY/ENTRYPOINT rows; fixed harness tags:
`harness_v2/suts/<sut>.env`, SUT_IMAGE. Keep all context/build logs and hashes.
The pinned runtime digest must match the intended original runtime base; if it
cannot be recovered, record that limitation and use a new same-base control,
never describe the historical baseline as a byte-identical control.

## Proposed harness changes — review only

The exact diff below is also `harness.proposed.diff`; original file hashes are in
`harness.proposal.base-sha256.json` (path-keyed rows). Claude must review against
the current files after all live batches end. Rebase if these hashes changed;
do not apply while a run can read the harness. Only Claude's later integration
would write harness files. This proposal adds prebuilt image/JAR overrides,
source/manifest provenance, image labels and an immutable Compose image override.
It leaves `analyse_run.sh`'s safety checks intact: its spec-mutation pair contract
is inappropriate for intentionally different code images
(`../E1_pilot/harness_v2/analyse_run.sh:13–81`).

```diff
'''
text += (E/'harness.proposed.diff').read_text()
text += r'''```

## Future paired harness runs

After Claude integrates and checks the proposal, use the following in the same
Bash session as the build. Both harness invocations use baseline/NONE/0 because
the spec is unchanged; `run.json.code_mutation.role` identifies the E5 treatment.
The code manifest is copied into **both** run directories. The proposal verifies
its tree hash for the corresponding role; `sut_jar_sha256` is the selected jar,
not the shared EMB jar (`harness.proposed.diff`, both file hunks).

```bash
unset AUTH_HEADER AUTH_ROLE HEALTH_PATH BASE_PATH ONLY_OPS
export SCHEMA_CHECKS=response_headers_conformance
export DATA_GEN=all MAX_EXAMPLES=100 REQUEST_TIMEOUT_MS=10000 MITM_MAX_BODY=65536
SPEC="$EMB/openapi-swagger/$sut.json"
for seed in 1 2 3; do
  for role in control mutant; do
    key=mutated_tree_sha256
    [[ $role != control ]] || key=source_tree_sha256
    source_sha=$(/usr/bin/python3 -I -B -c \
      'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$MUT/manifest.json" "$key")
    image=$(cat "$MUT/tag-$role.txt")
    PILOT_RUN_ID="${stamp}_e5_${site}_${role}_s${seed}" \
      CODE_ROLE="$role" CODE_SOURCE_TREE_SHA256="$source_sha" \
      CODE_MANIFEST="$MUT/manifest.json" SUT_IMAGE_OVERRIDE="$image" \
      SUT_JAR_OVERRIDE="$MUT/context-$role/dist/$sut-sut.jar" \
      "$H/run_pilot.sh" "$sut" "$SPEC" baseline NONE 0 "$seed" 300
  done
done
```

Start with one pair for build/readiness/witness inspection, then complete the
three seeds and repeated same-seed controls to measure the noise floor. Retain
failed attempts; a complete run and JUnit review are required before analysis.
Use fresh SUT containers with equal DB/state fixtures and auth, no shared mutable
volumes. Freeze generator/proxy IDs, dependencies and scenario settings before
the pair; a common seed does not guarantee identical HTTP traces. Save directed
witnesses separately under E5 with the exact request, clean state, control result,
mutant result and relevant stack/JSON pointer. A directed witness is distinct
from a fuzzing-detected kill (`OPERATORS.md`, each Witness plan;
`harness_v2/run_pilot.sh`, finish and completion blocks;
`../E1_pilot/pilot_results/PILOT_SUMMARY.md:79–91,93–112`).

## Pair validation, fresh analysis and independent attribution

Do **not** relax or call `analyse_run.sh` on code pairs: it rejects different SUT
images/JARs and requires a spec-mutated treatment. Before the commands below,
Claude must compare both `run.json` files and record the validation in E5:

- Both complete; same SUT, seed, budget, max examples, auth role/source/fixture
  hash, spec.original and spec.test hashes, derecursion output, data generation,
  Schemathesis checks/phases/timeout, logger body limit, readiness/base path and
  container runtime settings. Both harness modes are baseline/NONE/0.
- Same tool and frozen harness hashes, JaCoCo jars, generator/proxy image IDs,
  runtime base digest, non-JAR runtime context inputs and resolved dependencies.
- Expected differences only: SUT JAR, SUT image, source tree, run IDs/timestamps
  and actual captured traces. Verify the role-specific source and JAR hash
  against manifest, image labels and context inventory; record immutable SUT
  image IDs from actual containers. The two copied code manifests must have the
  same hash. Reject unexplained differences. Source and image label assertions
  are provenance checks, not evidence of behavioral equivalence.

These checks extend the current provenance contract (`../E1_pilot/harness_v2/run_metadata.py:20–74`; `../E1_pilot/harness_v2/analyse_run.sh:13–81`; `harness.proposed.diff`). Historical
`exposure.json` baselines are site-selection evidence only, never E5 controls.

After recording a valid pair, run the **existing own Python tools** as follows.
Set BASE and TREAT to that pair's absolute run directories (seed 1 below). Paths
with spaces are preserved. `-I` omits the sibling tools directory, so the wrapper
adds that trusted directory explicitly; no external module/SUT is run.

```bash
BASE="$PWD/08_experiments/E1_pilot/runs/$sut/${stamp}_e5_${site}_control_s1"
TREAT="$PWD/08_experiments/E1_pilot/runs/$sut/${stamp}_e5_${site}_mutant_s1"
ANALYSIS="$MUT/analysis-s1"
mkdir "$ANALYSIS"
pytool() {
  /usr/bin/python3 -I -B - "$PWD/08_experiments/tools/$1" "${@:2}" <<'TOOL_PY'
import pathlib, runpy, sys
script = pathlib.Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(script.parent))
sys.argv[0] = str(script)
runpy.run_path(str(script), run_name='__main__')
TOOL_PY
}
for oracle in default sut; do
  rejects=400,422
  [[ $sut != market || $oracle != sut ]] || rejects=400,406,422
  for role in control mutant; do
    RUN=$BASE
    [[ $role != mutant ]] || RUN=$TREAT
    pytool conformance.py "$BASE/spec.original.json" "$RUN/exchanges.jsonl" \
      --deploy-origin "http://sut-$sut:8080" --reject-statuses "$rejects" \
      > "$ANALYSIS/$role-$oracle.violations.jsonl"
  done
  pytool attribute.py "$ANALYSIS/control-$oracle.violations.jsonl" \
    "$ANALYSIS/mutant-$oracle.violations.jsonl" "$MUT/manifest.json" --mode fresh \
    > "$ANALYSIS/attribution-$oracle.csv"
done
```

`../tools/conformance.py:399–442,455–467` implements the signals and oracle flags. Market's
406 variant is required alongside the generic variant (codebook §10.8,
`../R1_triage_codebook.md:251–259`). Other SUTs' two variants are identical by
construction and can be reported once. Empty checker output needs explicit
counts/inspection, not an assumed pass.

Fresh `attribute.py` gives NEW on a mapped operation **NEEDS_MANUAL**, NEW off the
mapped operations **UNEXPLAINED**, and keeps baseline/mutant occurrence counts
(`../tools/attribute.py:18–57`). It deliberately does **not** claim IMPL from a
code manifest. PERSISTENT fingerprints can have increased occurrences; inspect
these deltas too. Unexplained off-operation effects may be real state propagation,
and a field mutation can merge with an existing fingerprint. Review exchanges,
not just CSV totals (`../E1_pilot/pilot_results/PILOT_SUMMARY.md:84–85`; `OPERATORS.md`, shared model sites).

Never use replay mode for E5: replaying the same saved exchanges against the
unchanged spec cannot observe a new executable behavior. Replay's expected-label
assignment would make accuracy circular (`../tools/attribute.py:1–7,33–39`;
`../E1_pilot/pilot_results/PILOT_SUMMARY.md:97–100`). The manifest is the **injection intent** and reviewed
edit provenance, not an independent diagnostic prediction or proof that every
new failure is caused by that edit.

The existing `triage.py` CLI is specific to P001 spreadsheet fault/message data
(`../tools/triage.py:852–864`). It cannot directly consume these
E5 violation JSONL files. No E5 adapter is implemented here. Use independent
blinded source/log/request review under codebook §6/§10, or first design and
validate a separate E5 adapter. Withhold site/operator/expected labels from the
predictor/labellers until their outputs are frozen, then join against the
manifest. Report pre-existing/BOTH/TEST cases separately; source location alone
does not make a schema mismatch IMPL (codebook §5, §10.6–10.8).

For each selected mutant retain: build-invalid; equivalent or oracle-blind;
unexposed; causally killed; surviving exposed; flaky/inconclusive. Require the
identical controlled request to pass on the control and fail on the mutant,
with a trace or serialization witness that links the edit to the signal, before
claiming a causal kill. A 2xx HTTP witness alone need not meet a response-schema
oracle. Record any pre-existing diagnostic separately. Keep all ten selections
in the denominator ledger and report eligible/compiled/exposed/killed counts
separately, plus independent attribution precision/recall only over adjudicated
causal failures. These are proposed evaluation rules [H], not measured E5
results (`OPERATORS.md`, First E5 batch; codebook §5/§6).
'''
(E/'README.md').write_text(text)
# Correct stale out-of-range citations in the operator doc and its generator.
for f in [E/'OPERATORS.md', Path('09_collab/logs/T19_scratch/write_operators.py')]:
    s = f.read_text().replace('90–114,228–279', '90–114,228–259').replace('39–52,119–137', '39–52,79–112')
    f.write_text(s)
print('README and exact embedded diff written; documentation citations corrected.')
