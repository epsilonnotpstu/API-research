# RESUME HERE: work paused by the user, 2026-11-17 ~20:45 (+06); updated 23:15 after a reboot
All background jobs are stopped: no Codex run, no build. Nothing is half-written. Claude + Codex access runs until 2026-11-24.
To resume, tell Claude: "RESUME_HERE.md dekhe kaj abar suru koro."

## R1 ("Spec or Bug?"), `research/`: done except one user task
- **Status:**
  - Paper v0.4 is polished, with all 25 T52 findings fixed.
  - Venue: ISSTA 2027 (deadline about 8–11 Jan 2027; ACM acmsmall, double-anonymous).
  - LaTeX: `research/10_paper/latex/main.tex`. Regenerate with `md2acm.py`, then compile on Overleaf; there is no acmart locally.
  - Anonymous replication archive: `/run/media/afridi/Shared Data/R1_replication/R1_anon_49f92e2/`. Reproduction 15/15, freezes OK.
- **Waiting on the user:** the human spot-check, `research/09_collab/human_check/kind_spotcheck.csv`.
  - The user is re-coding it by themselves.
  - The first fill is NOT to be reported.
  - Do nothing until the user says it is done.
- **After the spot-check:**
  1. Compute κ against `08_experiments/E9_hybrid/spotcheck_model_codes.csv`.
  2. Fill the only remaining [TODO] in §6 Threats.
  3. Regenerate the LaTeX.
  4. Rebuild the archive with `10_paper/reproduce/build_archive.py --anonymize`.
- **Open user decision:** a 15-character prefix of a public demo credential is in the history of commit 930ba0a. It has since been replaced by a hash. Rewriting history needs a force push, so ask the user before doing anything.

## R3 ("Silent behavioural changes in REST APIs"), `R3_silent_breaking/`: scored (2026-11-18)
- Everything is done up to and including the single scoring run, as commit 286ffad.
  - **Push status:** the push failed because the network was down (DNS). Run `git push origin main` once the network is back.
  - **Results** (`plan/R3_RESULTS.md`):
    - 136 commits from 47 repositories.
    - Observable change: 60/136 = 0.44.
    - Breaking: 32/136 = 0.24 with GPT codes, versus 12/136 with Claude codes. **The breaking label is model-dependent.**
    - H-R3-1 PASS: 29/32 breaking changes edit no contract annotation.
    - H-R3-2 INSUFFICIENT: only 1 change concerns specified behaviour.
    - H-R3-3 PASS: κ 0.94.
  - Paper draft v0.2: `paper/R3_draft.md` (abstract, results, discussion and conclusion written).
- **Remaining for R3:**
  1. A human spot-check of about 20 items, focused on `client_impact`, by the user.
  2. A venue decision, and LaTeX via a copy of `research/10_paper/latex/md2acm.py`.
  3. A replication archive like R1's.
  4. A final paper polish. A Codex numeric-consistency review like T52 is recommended.
- **Rules:**
  - Blind roles (G1/G2, H1/H2) are never done by Claude itself.
  - If Codex hits its limit, resume the same session after the reset.
  - Report to the user in Bengali.
