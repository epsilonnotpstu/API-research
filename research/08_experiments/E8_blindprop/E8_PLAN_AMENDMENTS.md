# E8 plan amendments

## B1 — E8b: enlarge the sample after an INSUFFICIENT primary (added 2026-11-16, after the E8 result)
**Reason.** The E8 primary was INSUFFICIENT: the ACCIDENTAL arm had 6 items against a minimum of 8. This is a sequential extension decided after seeing E8's result, and is disclosed as such.

**Rule: only one further look.** After E8b, the pooled analysis below is run once and reported, whatever it shows. No further extension follows.

**Data.**
- **New items:** Codex task T47 continues the frozen T46 pool2 review, beyond the ranks already reviewed. It stays hypothesis-blind and uses the same acceptance gate, the same reason codes and the same per-repo cap. The cap is raised from 6 to 10 per repo, counting T45 and T46 items. Target: 40 new accepted items, or pool2 ranks 61–150 reviewed.
- **Proposition:** the miner writes the E7-style proposition only, as the reference for matching.
- **Package:** a new parent-state package in `E2_labelling/e8b_blind/` holds the T47 items only.
- **Pipeline:** the same as E8, with fresh sessions.
  - Writer W2 works on a copy of the package without propositions.
  - Judge J2 matches the propositions.
  - Coders C5 and C6 code them; final code = agreement, otherwise UNCLEAR.
  - Coder P3 codes without files (descriptive).
  - The task texts are byte-identical to the E8 task texts.

**Primary analysis.**
- **H-E8-1, pooled:** set=new, SPEC/IMPL truth, match = SAME, from the E8 items plus the T47 items.
- **Test:** one-sided Fisher test, α = 0.05.
- **Size rule:** if either arm has fewer than 8 items, the verdict is INSUFFICIENT, which is final.

**Secondary and descriptive analyses.**
- H-E8-1 on the T47 items alone.
- The miss-rate test, now pre-registered: P(DIFFERENT or PARTIAL | E7-style ACCIDENTAL) > P(DIFFERENT or PARTIAL | DELIBERATE), one-sided Fisher test on the T47 items. The E7-style kind here comes from a proposition-only code of the miner's proposition by coder P4, who uses the A3 task text.
