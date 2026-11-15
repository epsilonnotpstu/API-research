# E5 blind labelling v3 — pre-registration (Claude, 2026-11-15; written before any v3 labelling)

**Purpose:** the held-out evaluation of codebook v0.6 §11.4, the intent-evidence search procedure. It is step (iii) of the §12.1 Q7 decision.

## Package
- Built with `build_e5_blind.py --out ../E2_labelling/e5_blind_v3 --key blind_key_v3.csv --salt e5-blind-v3-2026-11-15 --example-rule discriminating`. Log: `work/build_blind_v3.log`.
- **Contents:** 38 items (17 targets, 21 decoys) in 12 packages (K01–K12).
  - The new pairs are market-response-field-v2, petstore-reject-valid-v2 and petstore-reject-valid-v3.
  - The new salt shuffles both the item IDs and the package names.
- **Strata:** assigned by `stratify_blind_v3.py`, which reads the key and `e5_summary.csv`.
  - A target that matches a v2 item (pair, seed, fingerprint) inherits its v2 stratum.
  - New targets get the v2 rule.
- **Primary (n=11):**
  - E009, E014, E018, E021, E022, E027, E029, E032, E033: v2-comparable, matching v2 E024, E023, E016, E015, E025, E021, E019, E013, E009;
  - plus new E008 (market-response-field-v2) and E016 (petstore-reject-valid-v3).
- **Other strata:** target_other 5, v1_comparable_only 1 (E026 = v2 E014), decoy 21.

## Labellers and codebook
- **Labellers:** new Codex sessions D1 and D2 (gpt-6.1-sol, effort xhigh). They must not have read v1/v2 packages or labels.
- **Codebook:** `CODEBOOK_v0.6.md`, a labeller copy.
  - It contains §§1–11 as in the v0.5 labeller copy, plus §11.4: the proposal's §11.4.1–11.4.6 procedure, with the §12.1 decisions folded in.
  - It does **not** contain:
    - E5/H8 references;
    - §11.3;
    - §12's "held-out = E5" sentence;
    - worked examples that name E5.
  - It is built after the T36 pilot. Pilot-driven procedure fixes are allowed **before** labelling starts and will be listed here. No changes after labelling starts.
- **Tool:** labellers may run `/usr/bin/python3 -I -B ../../tools/intent_evidence.py` on `K??/source` and `K??/spec.json`.
  - The packages have no VCS history, so E-HISTORY is unavailable. Labellers must record it as a coverage gap, not as `none_found`.

## Pre-registered measures
**Primary set (n=11), per labeller:**
- (a) IMPL* rate, where IMPL* = IMPL or IMPL_PARTIAL;
- (b) **misattribution** count, where misattribution = SPEC, SPEC_PARTIAL or TEST;
- (c) UNDECIDABLE count, and how many of them have `both_candidate=true`;
- (d) `intent_search_status` distribution, and the share of items where search was mandatory;
- (e) accepted evidence types.

**v2-comparable subset (n=9):** v3 D1/D2 versus v2 C1/C2 on the same fingerprints. v2 baseline on these 9 items:
- C1: IMPL* 7, misattribution 0, UNDECIDABLE 2.
- C2: IMPL* 6, misattribution 0, UNDECIDABLE 3.

**Intent-looking subset (n=4):**
- v3 items E029 (scout-wrong-status), E027 (market-wrong-status), E014 and E009 (petstore-response-field);
- = v2 items E019, E021, E023, E024.
- v2 result: C1 IMPL* 2/4, C2 IMPL* 1/4. Every non-IMPL* result was UNDECIDABLE + both.

## Success criteria (fixed now)
- **S1 (safety):** misattribution on the primary set is 0 for **both** labellers.
- **S2 (benefit):** on the intent-looking subset, the IMPL* count is higher than in v2 for **at least one** labeller and lower for **neither**. v2 counts: C1 2, C2 1.
- **S3 (no regression):** on the v2-comparable subset, each labeller's IMPL* count is ≥ the lower of C1/C2 (6).

§11.4 counts as supported only if S1 and S2 both hold. If S1 fails, the procedure is unsafe whatever S2 shows. If S1 holds but S2 does not, record that the procedure adds cost without a measurable benefit at this n.

## Limitations (known in advance)
- Same model family as the v2 labellers; n is small; no statistical test.
- The ground truth is IMPL by construction (code mutants). The evaluation cannot measure SPEC recall. A procedure that only ever says IMPL would pass S1/S2, which is why the decoy distribution and the rationale quality are reported too.
- The mutant source trees may contain tests that assert the original behaviour. That is realistic, and it is exactly the E-TEST evidence §11.4 is meant to find.
