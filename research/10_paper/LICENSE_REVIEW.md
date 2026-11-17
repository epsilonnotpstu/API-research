# Upstream licence review for the replication package (2026-11-16, Claude)

**Method:**
- Each repository's licence was read from the bare clones in `/run/media/afridi/Shared Data/api_research_upstream/`, using `git --git-dir … show HEAD:<LICENSE file>`. Only the first lines of each file were classified.
- The Iced-Latte licence history was read with `git log -- LICENSE`.
- Nothing was executed.
- ⚠️ A repository's licence can change over time. The licence that applies to an excerpt is the one in force at the **parent commit** of that excerpt, not the one at HEAD. Below, HEAD is used except where the history was checked.

## Repositories contributing items (E7 + T47; T48 will add more)
| Licence (HEAD) | Repositories | Redistributing excerpts in the replication package |
|---|---|---|
| Apache-2.0 | apicurio-registry, catwatch, dockstore, eudi-srv-verifier-endpoint, fineract, gravitee-api-management, harbor, hivemq-edge, hydra, kratos, microcks, nessie, polaris, strimzi-kafka-bridge, service-api ⚠️ | Allowed. Keep the LICENSE and NOTICE files; mark modified (excerpted) files. |
| MIT | basyx-java-server-sdk, cwms-data-api, pay-publicapi | Allowed with the copyright notice. |
| EPL-2.0 | ditto, kapua (EPL-2.0 with a GPL secondary licence) | Allowed as source under EPL-2.0, with the licence text. |
| GPL-3.0 | rhsm-subscriptions | Allowed if the excerpts are released under GPL-3.0 with the licence text. That means the package needs per-directory licences. |
| AGPL-3.0 | open-banking-gateway ⚠️ (T48 candidate) | Same as GPL: per-directory AGPL. |
| Apache-2.0 (checked at each parent commit) | cwa-verification-server, swagger-petstore (clones in `08_experiments/_external/upstream/`) | Allowed, as for Apache-2.0 above. |
| **Custom, restrictive** | **Iced-Latte** (see below) | **Depends on the commit date.** |

## Iced-Latte
**Licence history:**
| Period | Licence |
|---|---|
| 2022-12 to 2026-02-22 | MIT |
| 2026-02-23 to 2026-05-03 | CC BY-NC 4.0 |
| 2026-05-04 to 2026-06-03 | "Iced Latte Personal Evaluation License 2026" |
| **2026-06-04 to 2026-07-11** | **Apache-2.0** (commits c7a8a816, dd055789; found in the commit-level re-check, below) |
| from 2026-07-12 | Personal Evaluation again ("Restore personal evaluation license", 8bb559a3) |

**What the current (HEAD) licence permits:** private viewing, cloning and local evaluation only.

**What it forbids without signed permission:**
- distributing or publishing the material or its derivatives;
- using it as a "benchmark target … shared or operated beyond your own private local evaluation";
- using, referencing or presenting the project in "articles … conference talks … or other public content".

| Item | Fix date | LICENSE file at parent commit and at fix commit (checked) | Kind (final) | Truth |
|---|---|---|---|---|
| X41, X63 | 2024-02-17 | MIT / MIT | — | — |
| X54 | 2024-04-21 | MIT / MIT | — | — |
| W24 | 2024-04-20 | MIT / MIT | DELIBERATE | IMPL |
| X11 (exploratory) | 2026-02-22 | MIT / MIT | — | — |
| W15 | 2026-04-12 | CC BY-NC 4.0 / CC BY-NC 4.0 | DELIBERATE | SPEC |
| W01, W16, W32 | 2026-06-06 | **Apache-2.0 / Apache-2.0** (parent fffd0c78 descends from dd055789 and not from 8bb559a3) | DELIBERATE | SPEC |

**Commit-level re-check (2026-11-16, later the same day; script `licence_at_parent.py`, read-only `git show <commit>:LICENSE`):**
- The first version of this review dated W01, W16 and W32 into the Personal Evaluation period. That was wrong.
- Their parent and fix commits carry Apache-2.0. An Apache-2.0 grant for those versions is not withdrawn by the later restrictive licence. ⚠️ This is the standard reading of Apache-2.0 §2 (a perpetual, irrevocable grant); it is not legal advice.
- All other repositories were re-checked the same way at each item's parent commit:
  - fineract carries Apache-2.0 (in `LICENSE_SOURCE`);
  - every other repository matches the HEAD table above;
  - cwa-verification-server (X36, X37, X52) and swagger-petstore (X58) are still unchecked, because their clones are elsewhere.

## Decision (Claude, supervisor-delegated; **confirmed by the user on 2026-11-16**)
**Revised after the commit-level re-check.** The first version excluded W01, W16 and W32.

**User confirmation (2026-11-16):** the user approved the revised proposal below as written. That means W01, W16 and W32 under Apache-2.0, the MIT-era items with the MIT notice, W15 and the T48 item V14 (also CC BY-NC 4.0 at its parent commit) under CC BY-NC 4.0, and the repository anonymised in the paper. **Closed later on 2026-11-16:** cwa-verification-server (X36, X37, X52) and swagger-petstore (X58) are Apache-2.0 at each parent commit. This was read with `git show <parent>:LICENSE` from `08_experiments/_external/upstream/`.
1. **Replication package:**
   - Release W01, W16 and W32 under Apache-2.0, with that version's LICENSE and copyright notice and a note naming the source commit.
   - Release the MIT-era items (X11, X41, X54, X63, W24) with the MIT notice.
   - Release W15 under CC BY-NC 4.0 only. The package is non-commercial research material. Alternatively, exclude W15.
   - Every Iced-Latte excerpt carries a note that the project's *current* licence is restrictive and that the excerpt comes from an earlier, permissively licensed version.
2. **Paper:**
   - ⚠️ The current licence's clause against referencing the project in articles cannot bind use of the earlier permissively licensed versions. Anonymising the repository is still the conservative option and costs nothing, so the provisional choice is to keep it anonymised.
   - The sensitivity table below stays as a robustness check.
3. **Future mining (after T48):** exclude repositories whose licence restricts research use or publication. Check each repository's licence at the parent commit during acceptance.

## Sensitivity: excluding W01, W16, W32 (all DELIBERATE / SPEC; a robustness check, no longer required by the licence)
| Analysis | As frozen | Without W01, W16, W32 |
|---|---|---|
| E8b pooled primary (SAME) | 39/48 vs 0/10, p = 1.8e-6 | 37/46 vs 0/10, p = 2.6e-6 (W01 was PARTIAL, so not in the primary) |
| T47 items, miner text (E9 descriptive) | 23/28 vs 0/13, p = 4.9e-7 | 20/25 vs 0/13, p = 1.6e-6 |
| E9 H-E9-1 | INSUFFICIENT | unchanged: the only discordant item is X22, an X item, not one of these three |

Neither conclusion depends on these items.

## T49 items (U01–U36), checked at each parent commit on 2026-11-17 (Claude)
The check uses `licence_at_parent.py` on `accepted_full_t49.csv`. Nothing is restrictive or non-commercial:
- Apache-2.0: 23 items (dockstore 3, gravitee 4, harbor 6, open-banking-gateway 2, service-api 8);
- EPL-2.0: 9 items (ditto);
- GPL: 4 items (dockstore 2, service-api 2).

Both dockstore and service-api changed licence during their history, so the licence is read per item at its parent commit. The GPL items follow the same rule as rhsm-subscriptions: per-directory GPL text in the replication package. The open-banking-gateway items are Apache-2.0 at their parent commits, although the repository's HEAD is AGPL.

## T50 items (Q01–Q61), checked at each parent commit on 2026-11-17 (Claude)
The check uses `licence_at_parent.py` on `accepted_full_t50.csv`. Nothing is restrictive or non-commercial:
- Apache-2.0: 54 items (answer 4, authelia 3, casdoor 1, datarhei-core 6, dependency-track 4, fess 5, flagr 8, harness 2, keto 9, keycloak 2, nifi 5, traccar 5);
- MPL-2.0: 3 items (tyk);
- AGPL-3.0: 3 items (photoprism);
- GPL-3.0: 1 item (halo).

**Classifier correction.** Codex's `licence_at_parent` column in `accepted_full_t50.csv` records AGPL-3.0 for the tyk and halo items. At their parent commits the files are actually MPL-2.0 (`LICENSE.md`) and GPL-3.0 (`LICENSE`).
- The cause is that both licence texts mention "Affero".
- `licence_at_parent.py` had the same blind spot, because it had no MPL rule. Claude added an MPL rule, plus a Business Source License → RESTRICTIVE rule, ahead of the AGPL rule. T48 and T49 re-ran with the same results.
- The gate decision is unaffected: all four classes are OSI-approved.
- Codex's file is left unmodified, and the classes above are authoritative.

The T50 gate rejected two dependency-track candidates because no open-source licence could be established at their parents (`LICENCE:` reason). The copyleft items follow the existing rule: per-directory licence text in the replication package.
