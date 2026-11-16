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
| Not checked locally | cwa-verification-server, swagger-petstore (E6 clones live elsewhere) | ⚠️ Expected to be Apache-2.0. Verify before release. |
| **Custom, restrictive** | **Iced-Latte** (see below) | **Depends on the commit date.** |

## Iced-Latte
**Licence history:**
| Period | Licence |
|---|---|
| 2022-12 to 2026-02-22 | MIT |
| from 2026-02-23 | CC BY-NC 4.0 |
| from 2026-05-04 | "Iced Latte Personal Evaluation License 2026" |

**What the current licence permits:** private viewing, cloning and local evaluation only.

**What it forbids without signed permission:**
- distributing or publishing the material or its derivatives;
- using it as a "benchmark target … shared or operated beyond your own private local evaluation";
- using, referencing or presenting the project in "articles … conference talks … or other public content".

| Item | Fix date | Licence in force (by date) | Kind (final) | Truth |
|---|---|---|---|---|
| X41, X63 | 2024-02-17 | MIT | — | — |
| X54 | 2024-04-21 | MIT | — | — |
| W24 | 2024-04-20 | MIT | DELIBERATE | IMPL |
| X11 (exploratory) | 2026-02-22 | MIT ⚠️ (the change to CC BY-NC came one day later) | — | — |
| W15 | 2026-04-12 | CC BY-NC 4.0 | DELIBERATE | SPEC |
| **W01, W16, W32** | **2026-06-06** | **Personal Evaluation** | DELIBERATE | SPEC |

⚠️ The rows above give the licence by commit date only. Each parent commit's own LICENSE file should be checked before release.

## Decision (Claude, supervisor-delegated; provisional; **the user must confirm before any public release or submission**)
1. **Replication package:**
   - Exclude every excerpt and proposition of W01, W16 and W32, and do not mention them by repository.
   - Release W15 only under CC BY-NC terms (non-commercial, with attribution), or exclude it too.
   - Release the MIT-era Iced-Latte items with the MIT notice.
2. **Paper:**
   - Do not name Iced-Latte. Refer to it as an anonymised repository, with a footnote explaining the licence.
   - Report the headline results with and without W01, W16 and W32 (sensitivity below). The frozen primary analyses are unchanged.
3. **Future mining (after T48):** exclude repositories whose licence restricts research use or publication. Check each repository's licence at the parent commit during acceptance.

## Sensitivity: excluding W01, W16, W32 (all DELIBERATE / SPEC)
| Analysis | As frozen | Without W01, W16, W32 |
|---|---|---|
| E8b pooled primary (SAME) | 39/48 vs 0/10, p = 1.8e-6 | 37/46 vs 0/10, p = 2.6e-6 (W01 was PARTIAL, so not in the primary) |
| T47 items, miner text (E9 descriptive) | 23/28 vs 0/13, p = 4.9e-7 | 20/25 vs 0/13, p = 1.6e-6 |
| E9 H-E9-1 | INSUFFICIENT | unchanged: the only discordant item is X22, an X item, not one of these three |

Neither conclusion depends on these items.
