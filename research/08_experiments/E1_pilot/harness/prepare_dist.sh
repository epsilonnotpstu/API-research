#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
EXP=$(cd -- "$HERE/../.." && pwd)
EMB="$EXP/_external/emb"
[[ $# == 1 && $1 == scout-api ]] || { echo 'Usage: prepare_dist.sh scout-api' >&2; exit 2; }
for tool in curl sha1sum cp cmp mktemp flock; do command -v "$tool" >/dev/null || { echo "Missing tool: $tool" >&2; exit 1; }; done
source_jar="$EMB/jdk_8_maven/cs/rest/original/scout-api/api/target/scout-api-sut.jar"
[[ -s $source_jar ]] || { echo "Missing built SUT: $source_jar" >&2; exit 1; }
echo "Plan: copy $source_jar to $EMB/dist/scout-api-sut.jar if changed."
echo 'Plan: fetch/verify JaCoCo 0.8.12 runtime agent and CLI against Maven Central SHA-1 (HTTPS).'
mkdir -p "$EMB/dist"
exec 9>"$EMB/dist/.pilot-prepare.lock"
flock -n 9 || { echo 'Another prepare_dist is running' >&2; exit 1; }
stage=$(mktemp -d "$EMB/dist/.prepare.XXXXXXXX")
trap 'rm -rf -- "$stage"' EXIT
fetch() {
    local artifact=$1 classifier=$2 dest=$3 url expected actual
    url="https://repo.maven.apache.org/maven2/org/jacoco/$artifact/0.8.12/$artifact-0.8.12-$classifier.jar"
    curl --fail --show-error --silent --location --proto '=https' --proto-redir '=https' \
        --connect-timeout 15 --max-time 120 "$url.sha1" -o "$stage/$dest.sha1"
    expected=$(tr -d '[:space:]' < "$stage/$dest.sha1")
    [[ $expected =~ ^[[:xdigit:]]{40}$ ]] || { echo "Invalid SHA-1: $url.sha1" >&2; exit 1; }
    if [[ -f $EMB/dist/$dest ]]; then
        actual=$(sha1sum "$EMB/dist/$dest"); actual=${actual%% *}
        if [[ ${actual,,} == ${expected,,} ]]; then
            echo "Verified existing $dest: $expected"
            cp "$stage/$dest.sha1" "$EMB/dist/$dest.sha1"
            return
        fi
    fi
    curl --fail --show-error --silent --location --proto '=https' --proto-redir '=https' \
        --connect-timeout 15 --max-time 120 "$url" -o "$stage/$dest"
    actual=$(sha1sum "$stage/$dest"); actual=${actual%% *}
    [[ ${actual,,} == ${expected,,} ]] || { echo "SHA-1 mismatch: $url" >&2; exit 1; }
    mv "$stage/$dest" "$EMB/dist/$dest"
    cp "$stage/$dest.sha1" "$EMB/dist/$dest.sha1"
    echo "Installed verified $dest: $expected"
}
fetch org.jacoco.agent runtime jacocoagent.jar
fetch org.jacoco.cli nodeps jacococli.jar
if ! cmp -s "$source_jar" "$EMB/dist/scout-api-sut.jar"; then
    cp "$source_jar" "$stage/scout-api-sut.jar"
    mv "$stage/scout-api-sut.jar" "$EMB/dist/scout-api-sut.jar"
fi
echo "Ready: $EMB/dist (runtime agent + CLI pinned to 0.8.12)."
