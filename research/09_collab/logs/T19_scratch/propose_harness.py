"""Generate a review-only diff and staged files; never edit the live harness."""
from pathlib import Path
import difflib
import hashlib
import json

h = Path("08_experiments/E1_pilot/harness_v2")
out = Path("08_experiments/E5_codemut")
staged = Path("09_collab/logs/T19_scratch/harness_proposal")
staged.mkdir(exist_ok=True)
patches, originals = [], {}
for name in ("run_pilot.sh", "run_metadata.py"):
    original = (h / name).read_text()
    text = original
    originals[str(h / name)] = hashlib.sha256(original.encode()).hexdigest()
    if name == "run_pilot.sh":
        anchor = 'for jar in "$sut-sut.jar" jacocoagent.jar jacococli.jar; do'
        assert text.count(anchor) == 1
        text = text.replace(anchor, '''# Proposed E5: prebuilt images only; never replace EMB/dist or a fixed pilot tag.
export PILOT_CODE_ROLE=${CODE_ROLE:-}
export PILOT_CODE_SOURCE_SHA256=${CODE_SOURCE_TREE_SHA256:-}
export PILOT_SUT_JAR_PATH=${SUT_JAR_OVERRIDE:-$EMB_DIR/dist/$sut-sut.jar}
if [[ -n $PILOT_CODE_ROLE || -n ${SUT_IMAGE_OVERRIDE:-} || -n ${SUT_JAR_OVERRIDE:-} || -n ${CODE_MANIFEST:-} ]]; then
    [[ $PILOT_CODE_ROLE == control || $PILOT_CODE_ROLE == mutant ]] || { echo 'E5 requires CODE_ROLE=control|mutant' >&2; exit 2; }
    [[ $mode == baseline && $fault == NONE && $severity == 0 ]] || { echo 'E5 keeps the spec unchanged' >&2; exit 2; }
    [[ -n ${SUT_IMAGE_OVERRIDE:-} && -n ${SUT_JAR_OVERRIDE:-} && -s ${CODE_MANIFEST:-} && -s $PILOT_SUT_JAR_PATH ]] || { echo 'E5 image/jar/manifest missing' >&2; exit 2; }
    [[ $PILOT_CODE_SOURCE_SHA256 =~ ^[a-f0-9]{64}$ ]] || { echo 'Missing E5 source-tree digest' >&2; exit 2; }
    export SUT_IMAGE="$SUT_IMAGE_OVERRIDE"
fi
[[ -s $PILOT_SUT_JAR_PATH ]] || { echo 'Missing selected SUT jar' >&2; exit 1; }
for jar in jacocoagent.jar jacococli.jar; do''', 1)
        anchor = 'cp "$HERE/suts/$sut.env" "$run_dir/sut-config.env"'
        assert text.count(anchor) == 1
        text = text.replace(anchor, anchor + '''
if [[ -n $PILOT_CODE_ROLE ]]; then
    # Pin to immutable local image ID and require the build labels from the E5 plan.
    e5_image_id=$(docker image inspect --format '{{.Id}}' "$SUT_IMAGE_OVERRIDE")
    e5_jar_sha=$(sha256sum "$PILOT_SUT_JAR_PATH"); e5_jar_sha=${e5_jar_sha%% *}
    [[ $(docker image inspect --format '{{index .Config.Labels "org.r1.jar_sha256"}}' "$e5_image_id") == "$e5_jar_sha" ]] || { echo 'E5 image/jar label mismatch' >&2; exit 1; }
    [[ $(docker image inspect --format '{{index .Config.Labels "org.r1.source_tree_sha256"}}' "$e5_image_id") == "$PILOT_CODE_SOURCE_SHA256" ]] || { echo 'E5 image/source label mismatch' >&2; exit 1; }
    cp "$CODE_MANIFEST" "$run_dir/code.manifest.json"
    /usr/bin/python3 -I -B - "$run_dir/code.manifest.json" "$sut" "$PILOT_CODE_ROLE" "$PILOT_CODE_SOURCE_SHA256" "$run_dir/compose.code-image.json" "$SUT_SERVICE" "$e5_image_id" <<'E5_PY'
import json, pathlib, sys
manifest, sut, role, expected, dest, service, image = sys.argv[1:]
m = json.loads(pathlib.Path(manifest).read_text())
assert m['injection_side'] == 'IMPL' and m['sut'] == sut
key = 'source_tree_sha256' if role == 'control' else 'mutated_tree_sha256'
assert m[key] == expected, 'E5 source digest differs from manifest'
with open(dest, 'x') as stream:
    json.dump({'services': {service: {'image': image}}}, stream)
E5_PY
    compose+=(-f "$run_dir/compose.code-image.json")
fi''', 1)
        anchor = 'if docker image inspect "$SUT_IMAGE" >/dev/null 2>&1; then'
        assert text.count(anchor) == 1
        text = text.replace(anchor, '''if [[ -n $PILOT_CODE_ROLE ]]; then
    "${compose[@]}" up -d --no-build >"$run_dir/compose-up.log" 2>&1
elif docker image inspect "$SUT_IMAGE" >/dev/null 2>&1; then''', 1)
    else:
        anchor = "'sut_jar_sha256': sha(emb / 'dist' / f'{sut}-sut.jar'),"
        assert text.count(anchor) == 1
        text = text.replace(anchor, """'sut_jar_sha256': sha(Path(os.environ.get('PILOT_SUT_JAR_PATH', str(emb / 'dist' / f'{sut}-sut.jar')))),
        'code_mutation': ({'role': os.environ['PILOT_CODE_ROLE'],
                           'source_tree_sha256': os.environ['PILOT_CODE_SOURCE_SHA256'],
                           'manifest_sha256': sha(run / 'code.manifest.json')}
                          if os.environ.get('PILOT_CODE_ROLE') else None),""", 1)
    (staged / name).write_text(text)
    patches.extend(difflib.unified_diff(original.splitlines(keepends=True), text.splitlines(keepends=True),
                                     fromfile="a/" + str(h / name), tofile="b/" + str(h / name)))
(out / "harness.proposed.diff").write_text("".join(patches))
(out / "harness.proposal.base-sha256.json").write_text(json.dumps(originals, indent=2) + "\n")
print("Prepared review-only diff; live harness untouched.")
