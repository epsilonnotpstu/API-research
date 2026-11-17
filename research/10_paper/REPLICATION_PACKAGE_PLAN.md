# R1 replication package: plan
Claude, 2026-11-17. This is a working plan; the archive has not been built yet. Everything below is derived from the repository state at the time of writing.

## 1. What a reader must be able to do
1. **Re-score every confirmatory hypothesis from the frozen data.**
   - This works today: `10_paper/reproduce/reproduce_scores.sh` re-runs all 11 frozen scorer invocations (E6–E13) on a scratch copy.
   - All 15 outputs came back byte-identical (2026-11-17).
2. **Check that nothing changed after it was frozen.**
   - `10_paper/reproduce/check_freezes.py` verifies 26 freeze files.
   - Two post-freeze changes are documented: E12 D1, and E7 A3 appended. No unexplained mismatch.
3. **Re-run the blind coding or labelling with another model** on the same item packages, with the same task text.
4. **Re-mine** from the upstream repositories, using the recorded commit SHAs and the mining scripts.

## 2. Contents, by tier
| Tier | Content | Where it lives now | Shipped as |
|---|---|---|---|
| **A: in git (public)** | Plans, amendments, deviations, results; scorers and self-tests; keys (`E7_mining/key/*_key.csv`, `accepted_full_*.csv`); codes, labels and coder reports; freezes; mining and build scripts; per-candidate decision records; pool inventories; repository selection with HEAD SHAs; collaboration task specs and reports; paper and figures | git (`research/`) | git tag + archive snapshot |
| **B: item excerpts** | Per-item `contract/` and `impl/` excerpts of upstream source, one copy per package. The `m1`, `m1f`, `kb*` and batch copies are byte-identical duplicates (tree hashes in the freezes) | local only (gitignored: `E2_labelling/*/[XWVUQK]*/`) | archive, with per-repository licence texts (§3) |
| **C: regenerable, not shipped** | Bare upstream clones, frozen pools (`pool2.json`, `pool3.json`, `*_sources.json`), review evidence, previews | NTFS volume / local, with hashes in `freeze*.json` | re-clone script and the recorded SHAs. The pools rebuild deterministically: the T46/T50 tests check this |
| **D: withheld** | Codex transcripts that echo upstream patches, attribution trailers, or a credential-like literal (T42, T45–T47, T49, T50 logs, E6–E9 logs); T35 contact dumps | local only (gitignored in `09_collab/.gitignore`) | not shipped. The summaries are in the reports, and the log hashes can be published |

## 3. Licences (from `LICENSE_REVIEW.md`, checked at each item's parent commit)
- **Permissive** (Apache-2.0, MIT): ship the excerpts with the licence text and any NOTICE file per repository directory.
- **Copyleft** (GPL, AGPL-3.0, EPL-2.0, MPL-2.0): ship each repository's excerpts in their own directory with the full licence text. The excerpts are unmodified source.
- **CC BY-NC 4.0** (the Iced-Latte items W15 and V14, as approved): mark them non-commercial. The repository is anonymised as approved.
- Before building, re-run `10_paper/licence_at_parent.py` over every `accepted_full_*.csv`. Since 2026-11-17 it has an MPL rule.

## 4. Privacy and safety gates before release
- **Secret scan:**
  - auth headers;
  - long encoded literals;
  - credential assignments;
  - the known demo credential pattern (scanned for, never printed).
- **Attribution scan:**
  - commit author names and emails;
  - `Co-authored-by`, `Signed-off-by` and `Reviewed-by` trailers;
  - `@handles`.
- **No author identity of the study team** in any shipped file. Strip git metadata from the archive snapshot.
- **Double-blind review:** use an anonymised archive link and remove the repository URL from the paper.

## 5. Build steps (when the venue is chosen)
1. Run `reproduce_scores.sh` and `check_freezes.py`. Both must pass.
2. Export tier A with `git archive` at a release tag.
3. Build tier B:
   - copy one canonical package per experiment (`e7_blind`, `e8_write`, `e8b_write`, `e9_m1`, `e10_blind`, `e12_blind`, `e13_blind`, plus `e4_blind`, `e5_blind_v3`, `e6_blind`);
   - verify each package's tree hash against its freeze;
   - add a licence directory per repository.
4. Write the README:
   - the experiment map, from `RESEARCH_STATE.md` §9;
   - how to re-score;
   - how to re-code with another model, using `TASK_CODE.md`, `TASK_M1.md` and `TASK_M1F.md` unchanged;
   - the known deviations.
5. Run the privacy gates (§4) over the whole archive.
6. Deposit with a DOI.

## 6. Open decisions for the user
- The venue, and whether it is double-blind. This decides anonymisation.
- Whether to publish the hashes of the withheld logs.
