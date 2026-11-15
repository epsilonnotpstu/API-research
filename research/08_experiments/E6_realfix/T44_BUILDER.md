# Offline blind-package builder

`build_e6_blind.py` uses Python's standard library and an allowlisted read-only
`git --git-dir=...` interface. It never checks out, builds, imports, or executes
upstream code. Synthetic tests construct loose Git objects with Python; even
the tests do not invoke a Git write operation.

Inputs are `combined_accepted.csv`, the upstream Git stores named in T44,
the three explicitly authorized E4 task/codebook templates, and all 15 EMB
`auth/*-auth.yaml` fixtures. Existing research artifacts are never overwritten.
The production destinations are the `e6_blind/` directory, `e6_key.csv`, and
`e6_build_log.json`. Existence of any destination, including a dangling symlink,
stops publication before upstream reads. The script has no overwrite switch.

## Inclusion and provenance

For every parent-side contract, implementation or route evidence path:

1. Keep the complete `src/` tree of its containing module, including tests,
   resources, DTOs, validators and exception mapping. Also retain that module's
   `test/`, `tests/`, README/docs, and build descriptors.
2. Expand to other checked-in Java/Kotlin source modules referenced by local
   imports until no further modules are found. Include each such module's tests.
3. Keep parent contract files and recursively follow local `$ref` files.
   Contract files live only in `source/`; the manifest gives their paths.
4. Keep root README, `docs/`, `doc/`, `documentation/`, and build descriptors.
   Evidence paths outside `src/` are included explicitly.
5. Omit `.git`, build/dependency output, archives, compiled artifacts,
   symlinks/submodules, all binary blobs, and all files over 2 MiB. The binary
   exclusion and text-size cap are intentionally stronger than the minimum.

Every selected path has a Git parent object identity; the hidden log records
parent SHA-256, delivered SHA-256 and size for every retained file. Redactions
preserve physical line count. Attribute/contact metadata and credential values
are removed; schema field names and structural types are retained. JSON contract
validity is independently checked. Redaction is the only permitted content edit.
No child content, history export, or separate contract duplicate is written.

## Ordering and cross-item exclusions

Order the input by `HMAC-SHA256(salt, original item_id)` and reserve K01–K25
**before** exclusions. The salt is fixed in the builder and recorded only in
the hidden log. The input CSV's physical row order does not affect allocation.
"Later-sorted" means the numerically larger K identifier, regardless of temporal
order. The salt is not searched or adjusted to improve the resulting balance.

Enumerate every same-repository ordered pair whose first item's resolution is
an ancestor of the second item's parent and whose resolution paths intersect
the second package. Use all Git diff paths, with rename detection disabled so
both old and new names count. Remove overlapping optional paths from the
revealing package. All parent evidence paths and local contract references
are protected; a protected-path conflict excludes the larger K item. Process
pairs in K order and retain a record even when an endpoint is already excluded.
Assert again that no retained pair has an overlapping resolution path.

Excluded IDs have no package or scored key row. Their reserved IDs remain in
the hidden decision ledger, so surviving IDs need not be consecutive.

## Mechanical safeguards

- Compare every raw and delivered source blob against **every** different child
  blob of that item's resolution paths, including copies under another filename.
  A blob identical to its parent is allowed, including a mode-only difference.
- Apply the T43 full/short SHA, exact subject and issue/PR/JIRA-reference scan to
  the actual selected output bytes, covering all items from that repository.
  Optional files with references are removed and audited; protected references
  stop the build. Publication verifies disk hashes against the scanned bytes.
- Apply the inherited email, attribution, private-key, GitHub/AWS-token, query
  credential and URL credential scans, extended for literal auth arguments,
  credential examples and JWTs. Check literal, JSON-escaped and URL-escaped
  variants of every authentication fixture value, plus Basic/Bearer payloads.
- Check the exact metadata word prohibition, manifest/key columns, propositions
  copied verbatim, and the unchanged inherited codebook. Task authorization
  paragraphs are copied verbatim from the two authorized task templates.

These are bounded lexical checks, not proof that paraphrased intent, arbitrary
personal names, every credential encoding, or runtime dependencies are absent.
The module/import selection is a static review scope; there is no runtime claim.

## Commands and delivered audit

Run our tests with:

```sh
/usr/bin/python3 -I -B 08_experiments/E6_realfix/test_build_e6_blind.py
```

An audit-only invocation performs the same assertions without publishing:

```sh
/usr/bin/python3 -I -B 08_experiments/E6_realfix/build_e6_blind.py --audit-only --progress
```

The production command, already executed once for this delivery, is:

```sh
/usr/bin/python3 -I -B 08_experiments/E6_realfix/build_e6_blind.py --progress
```

See `e6_build_log.json` for all hashes, all 19 cross-item pairs and all inclusion,
redaction and exclusion decisions; `09_collab/logs/T44_scratch/preflight.json`
for the matching pre-publication plan; and
`09_collab/logs/T44_scratch/production_verification.json` for disk-based checks.
The latter verifier also runs the existing E4 credential-scan function verbatim,
without loading any other blind package or key.

Task drafts permit source/contract/proposition review only. No runtime exchanges
are supplied. History is unavailable, the intent tool is allowed only for M2,
and cross-package file comparison is forbidden. No labellers are launched and
no labels are created by this builder task.
