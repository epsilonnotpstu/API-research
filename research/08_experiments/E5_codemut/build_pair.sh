#!/usr/bin/env bash
# Build one E5 control/mutant pair (jar + runtime image), following README.md
# "Future build commands for Claude" verbatim except for the parameters below.
# Usage: build_pair.sh SUT OPERATOR SITE        (run from research/)
# Writes 08_experiments/E5_codemut/work/<site>_<stamp>/ and prints that path last.
set -euo pipefail
[[ $# == 3 ]] || { echo 'Usage: build_pair.sh SUT OPERATOR SITE' >&2; exit 2; }
sut=$1; operator=$2; site=$3
E5="$PWD/08_experiments/E5_codemut"
EMB="$PWD/08_experiments/_external/emb"
[[ -f $E5/codemut.py && -d $EMB ]] || { echo 'Run from research/' >&2; exit 2; }
# Coordinator-recorded inputs (COORDINATOR_NOTES.md).
MAVEN8_IMAGE=${MAVEN8_IMAGE:-maven:3.8.8-eclipse-temurin-8}
MAVEN11_IMAGE=${MAVEN11_IMAGE:-maven:3.8.8-eclipse-temurin-11}
: "${MAVEN_CACHE:?absolute path to the warmed Maven repository (export of the m2cache volume)}"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
MUT="$E5/work/${site}_${stamp}"
case "$sut" in
  scout-api)
    BUILD_IMAGE=$MAVEN8_IMAGE; ROOT="$EMB/jdk_8_maven/cs/rest/original/scout-api"
    JAR_REL=api/target/scout-api-sut.jar; MVN_ARGS=(-B -pl api -am -Dmaven.test.skip=true package)
    RUNTIME_TAG=amazoncorretto:8-alpine-jdk ;;
  swagger-petstore)
    BUILD_IMAGE=$MAVEN8_IMAGE; ROOT="$EMB/jdk_8_maven/cs/rest/original/swagger-petstore"
    JAR_REL=target/swagger-petstore-sut.jar; MVN_ARGS=(-B -Dmaven.test.skip=true package)
    RUNTIME_TAG=amazoncorretto:8-alpine-jdk ;;
  market)
    BUILD_IMAGE=$MAVEN11_IMAGE; ROOT="$EMB/jdk_11_maven/cs/rest-gui/market"
    JAR_REL=market-rest/target/market-sut.jar; MVN_ARGS=(-B -pl market-rest -am -Dmaven.test.skip=true package)
    RUNTIME_TAG=amazoncorretto:11-alpine-jdk ;;
  cwa-verification)
    BUILD_IMAGE=$MAVEN11_IMAGE; ROOT="$EMB/jdk_11_maven/cs/rest/cwa-verification-server"
    JAR_REL=target/cwa-verification-sut.jar; MVN_ARGS=(-B -Dmaven.test.skip=true -Dcheckstyle.skip=true package)
    RUNTIME_TAG=amazoncorretto:11-alpine-jdk ;;
  *) exit 2 ;;
esac
BUILD_IMAGE=$(docker image inspect --format '{{.Id}}' "$BUILD_IMAGE")
RUNTIME_BASE=$(docker image inspect --format '{{index .RepoDigests 0}}' "$RUNTIME_TAG")
[[ $BUILD_IMAGE == sha256:* && $RUNTIME_BASE == *@sha256:* ]]
[[ $MAVEN_CACHE == /* && -d $MAVEN_CACHE ]]
/usr/bin/python3 -I -B "$E5/codemut.py" --sut "$sut" --operator "$operator" \
  --source "$ROOT" --site "$site" --seed 1 --out "$MUT" >/dev/null
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
    > "$MUT/build-$role.log" 2>&1 || { echo "BUILD-INVALID: $role (see $MUT/build-$role.log)" >&2; echo "$MUT"; exit 3; }
  test -s "$tree/$JAR_REL"
done
/usr/bin/python3 -I -B - "$E5/codemut.py" "$MUT" <<'VERIFY_PY'
import importlib.util, json, pathlib, sys
spec = importlib.util.spec_from_file_location('codemut', sys.argv[1])
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
p = pathlib.Path(sys.argv[2]); m = json.loads((p / 'manifest.json').read_text())
for folder, key in [('control.source', 'source_tree_sha256'), ('source', 'mutated_tree_sha256')]:
    assert c.canonical_hash(c.inventory(p / folder)) == m[key], folder
deps = {}
for role in ('control', 'mutant'):
    root = p / ('m2-' + role)
    deps[role] = {f.relative_to(root).as_posix(): c.sha(f.read_bytes())
                  for f in sorted(root.rglob('*')) if f.is_file() and f.suffix in ('.jar', '.pom')}
assert deps['control'] == deps['mutant'], 'Resolved Maven artifacts differ'
(p / 'resolved-artifacts.json').write_text(json.dumps(deps, indent=2) + '\n')
VERIFY_PY
for role in control mutant; do
  tree="$MUT/source"; key=mutated_tree_sha256
  [[ $role != control ]] || { tree="$MUT/control.source"; key=source_tree_sha256; }
  ctx="$MUT/context-$role"
  mkdir -p "$ctx/dist" "$ctx/dockerfiles" "$ctx/scripts/dockerize/data/additional_files"
  cp "$tree/$JAR_REL" "$ctx/dist/$sut-sut.jar"
  cp "$EMB/dist/jacocoagent.jar" "$ctx/dist/jacocoagent.jar"
  if [[ $sut == scout-api || $sut == swagger-petstore ]]; then
    cp -a "$EMB/scripts/dockerize/data/additional_files/$sut" "$ctx/scripts/dockerize/data/additional_files/"
  fi
  /usr/bin/python3 -I -B - "$EMB/dockerfiles/$sut.dockerfile" "$ctx/dockerfiles/$sut.dockerfile" "$RUNTIME_BASE" <<'DOCKERFILE_PY'
import pathlib, sys
src, dst, base = sys.argv[1:]
lines = pathlib.Path(src).read_text().splitlines(keepends=True)
assert lines[0].startswith('FROM ') and sum(x.startswith('FROM ') for x in lines) == 1
lines[0] = 'FROM ' + base + '\n'
pathlib.Path(dst).write_text(''.join(lines))
DOCKERFILE_PY
  source_sha=$(/usr/bin/python3 -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$MUT/manifest.json" "$key")
  jar_sha=$(sha256sum "$ctx/dist/$sut-sut.jar"); jar_sha=${jar_sha%% *}
  image="r1-$sut-sut:e5-${site}-${stamp}-${role}"
  image=${image,,}
  if docker image inspect "$image" >/dev/null 2>&1; then exit 2; fi
  docker build --pull=false --label "org.r1.jar_sha256=$jar_sha" \
    --label "org.r1.source_tree_sha256=$source_sha" --tag "$image" \
    --file "$ctx/dockerfiles/$sut.dockerfile" "$ctx" > "$MUT/image-$role.log" 2>&1
  printf '%s\n' "$image" > "$MUT/tag-$role.txt"
  docker image inspect "$image" > "$MUT/image-$role.json"
  (cd "$ctx" && find . -type f -print0 | sort -z | xargs -0 sha256sum) > "$MUT/context-$role.sha256"
done
echo "$MUT"
