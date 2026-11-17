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

## R3 ("Silent behavioural changes in REST APIs"), `R3_silent_breaking/`
- **Done:**
  - Pre-registration and plan freeze (`plan/r3_plan_freeze.sha256`, commit ed528bd). Verify it with `sha256sum -c` from `R3_silent_breaking/`.
  - Related work verified from full text (`notes/NOVELTY_VERIFIED.md`). Paper draft v0.1 at `paper/R3_draft.md`.
  - **pool4 frozen:** 18,590 candidates from 54 repositories (`mining/freeze4.json`, `pool4_inventory.json`; `pool4.json` is local and gitignored).
  - **Sample frozen:** 136 commits (`mining/sample4.json`, `freeze4_sample.json`).
  - Codex's T53 scripts carry Claude fixes F1–F5. All are logged in `plan/R3_DEVIATIONS.md` (D1). Codex reviewed F1–F3 in T54 (`collab/reports/T54_report.md`). Tests: `test_t53.py --synthetic-only` 29/29. In `test_t54.py`, 23 tests pass and 1 characterisation test fails, as expected after F4.
- **Next step: build the packages, which has not succeeded yet.**
  - Run from `R3_silent_breaking/mining`: `/usr/bin/python3 -I -B t53_build.py`. It takes about 10 minutes and publishes nothing if it fails.
  - Last attempt: failed at the package scan, before F5 and the improved error message were in place. The re-run with the informative error (`Package scan failed; kinds=...`) was stopped by the pause. **Run it again first.**
  - If a scan kind appears, fix it mechanically, log it as F6 in `R3_DEVIATIONS.md`, re-run `test_t53.py --synthetic-only`, and rebuild.
- **After the build:**
  0. **First, the drive must be mounted.** The machine rebooted at 23:05, and "Shared Data" (`/dev/nvme0n1p4`, holding the clones and the archive) was not mounted afterwards. Claude does not enter passwords. The user mounts it by clicking "Shared Data" in the file manager.
1. Run `R3_silent_breaking/collab/scripts/r3_prepare.py` to build the `r3_kb*` Claude batches (at most 15 items each).
  2. Run `collab/scripts/r3_freeze_packages.sh`, which writes `plan/r3_packages_freeze.sha256`.
  3. Commit and push.
  4. Start coding:
     - **G1/G2 (Codex, blind):** `collab/scripts/r3_launch_gpt.sh`. To resume after a usage limit: `r3_launch_gpt.sh resume K G1 G2`.
     - **H1/H2 (Claude sonnet subagents, fresh context):** one per `r3_kb*` batch, with the prompt in `collab/scripts/r3_claude_prompt.txt` (replace @ID@ and @B@).
  5. Audit, write the output freeze, and score once: `/usr/bin/python3 -I -B plan/score_r3.py --out plan/r3_scores.csv`.
  6. Write the results into `paper/R3_draft.md`.
- **Rules:**
  - Blind roles (G1/G2, H1/H2) are never done by Claude itself.
  - If Codex hits its limit, resume the same session after the reset.
  - Report to the user in Bengali.
