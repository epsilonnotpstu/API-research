# Coordinator notes on T19 (Claude, 2026-11-14)

## Maven build images (resolves README "Required unresolved input")
| Variable | Tag | Immutable ID | Used by |
|---|---|---|---|
| `MAVEN8_IMAGE` | `maven:3.8.8-eclipse-temurin-8` | `sha256:daa5d635ffdeb1a3c31d12079b6829115214701828e43d61e4e7f6a61640e62c` | swagger-petstore original build (Claude) |
| `MAVEN11_IMAGE` | `maven:3.8.8-eclipse-temurin-11` | `sha256:a9023829d06570e9e4f99928b360aca6a6ebec642901fa15b69726221dd2eda4` | market, cwa-verification original builds (Claude) |

- ⚠️ The supervisor built the **scout-api** original jar; its build image is not recorded.
- This is acceptable under T19's design: every mutant is compared with a **control** rebuilt from the same copied tree with the same image, never with the original jar. Use `MAVEN8_IMAGE` above for both scout's control and its mutants.
- Original build command (petstore, market, cwa): `docker run --rm -v m2cache:/root/.m2 -v "$SRC":/src -w /src <image> mvn -q -B -DskipTests package`. The files it writes are root-owned.

## Review status
- **Accepted:**
  - 22/22 synthetic tests (re-run by Claude).
  - Codex wrote nothing in harness_v2, tools or `_external` during T19 (mtime check from 16:33).
- **Harness diff (`harness.proposed.diff`):** applied on 2026-11-14 after the negative-data batch finished. `patch -p1` applied cleanly on the recorded base hashes, and `static_validate.py` passes.
- **First E5 batch:** the 10 mutants listed in README/OPERATORS.md, each paired with a control.

## Build results (2026-11-14)
- **9/10 pairs built:** control and mutant images, with distinct jar hashes and equal resolved Maven artifacts (`resolved-artifacts.json` per pair). Log: `build_all.log`.
- **BUILD-INVALID: `market-response-field`** (`work/market-response-field_20261114T114642Z/build-mutant.log`).
  - javac reports `AssertionError: typeSig ERROR` / "unknown compilation problem" in `market-core`.
  - The mutation adds a fully qualified `@com.fasterxml.jackson.annotation.JsonProperty` to `ProductDTO.getPrice()`.
  - ⚠️ [H] jackson-annotations is not on `market-core`'s compile classpath (`grep jackson market-core/pom.xml` finds no direct dependency; transitive dependencies not checked), and the Lombok/javac annotation processing crashes on the unresolved type.
  - Per README: recorded as build-invalid, not replaced. A replacement RESP_FIELD site for market (in `market-rest`, which has Jackson) is a follow-up.
