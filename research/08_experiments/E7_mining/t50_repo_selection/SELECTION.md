# T50 repository selection (Claude, 2026-11-17). Metadata only; no commit content was read.
**Seed** (`seed.txt`):
- (a) server applications from a GitHub topic search (`search_raw.tsv`; topics openapi/swagger/rest-api/openapi3; Java/Kotlin/Go; ≥50 stars; pushed ≥2026-01; created <2025). Libraries, frameworks, clients, tools and tutorials were excluded by name and topic.
- (b) a curated list of well-known OSS REST servers, written down before any check.

Both exclude the 37 repositories used earlier (T42–T49 and the pilot).

**Mechanical criteria** (`check.sh` → `meta.tsv`), applied to every seed repository:
1. A checked-in OpenAPI/Swagger document at HEAD, outside test, example, mock and vendor paths.
2. GitHub's primary language is Java, Kotlin or Go.
3. At least 300 commits on the default branch.
4. Size ≤ 1 GB.
5. Not archived, not a fork.
6. The HEAD licence is OSI-approved. Restrictive, source-available and non-commercial licences are excluded. NOASSERTION licences were read from the LICENSE file.

Every repository that meets all six criteria is selected (no top-N choice): **20 repositories** (`selected.tsv`).
**Excluded:**
- lakeFS: Business Source License.
- grafana and kafka-ui: TypeScript primary.
- oathkeeper: 1.3 GB.
- wgrest: 95 commits.
- No spec file at HEAD: android-sms-gateway, para, DSpace, im-server, moneropay, restheart, bk-cmdb, linkis, metersphere, ntfy, gotify, woodpecker, thingsboard, killbill, dolphinscheduler, hawkbit, conductor.
