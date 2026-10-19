# Codex independent search log

## Search date and boundaries

- Search date: 2026-10-19 (Asia/Dhaka).
- Broad recent filter used in initial mapping: 2021-01-01 through 2026-12-31; focused searches also allowed older work to recover foundations.
- Target: original computer-science/software-engineering research and rigorous surveys about software APIs.
- Independence rule: no Claude candidate files, notes, or conclusions were opened or used.

## Databases and sources searched

- **OpenAlex API:** broad and focused discovery, authors, years, types, venues, cited-by counts, abstracts, OA locations. API was reachable.
- **Crossref REST API:** DOI title/author/year/container reconciliation. Reachable for DOI publications; arXiv DOI aliases returned 404 as expected and were verified through arXiv/OpenAlex instead.
- **DBLP:** DOI-based API searches were attempted, but the selected query form returned no exact batch hits. Targeted web verification confirmed at least RESTler and the GPTAid preprint records. DBLP was not counted as a per-row verification source.
- **Semantic Scholar Graph API:** one individual DOI query succeeded during tool checking; the 60-record batch request returned HTTP 429. It was not used as a verification source and no retries were looped.
- **arXiv:** landing and PDF endpoints were checked for explicit arXiv records and versions linked from peer-reviewed papers.
- **Publisher/institutional locations:** DOI landing pages and OA PDF candidates from ACM, IEEE, Springer, Elsevier, NDSS, HAL, institutional repositories, and SciOpen were checked where available.
- **ACM Digital Library, IEEE Xplore, SpringerLink, ScienceDirect:** represented through publisher DOI/landing/PDF endpoints found in OpenAlex/Crossref; automated access sometimes returned 403 or cookie redirects.

## Exact broad-mapping searches

- `REST API fuzzing software testing`
- `REST API security authorization testing`
- `OpenAPI specification inference generation validation`
- `API documentation consistency software engineering`
- `API evolution breaking changes detection`
- `GraphQL API testing security performance`
- `microservice API evolution testing`
- `API monitoring observability anomaly`
- `web API discovery recommendation composition`
- `large language model API testing API engineering`

## Exact focused searches

- `RESTler stateful REST API fuzzing ICSE`
- `EvoMaster REST API test generation`
- `RESTest RESTful APIs automated testing`
- `MOREST RESTful APIs testing`
- `QuickREST property based testing REST API`
- `API documentation smells software engineering`
- `API documentation quality developers empirical`
- `API specification inference REST web services`
- `breaking API changes Java libraries empirical`
- `API evolution REST empirical study`
- `GraphQL empirical study software engineering`
- `GraphQL security testing software engineering`
- `API recommendation mashup service composition software`
- `API usability empirical software engineering`
- `API performance REST GraphQL gRPC empirical`
- `REST API authorization vulnerabilities empirical software engineering`
- `REST API security testing fuzzing academic`
- `API misuse security empirical study libraries`
- `web API access control testing research`
- `microservice API fault injection chaos testing`
- `microservice observability tracing anomaly detection API`
- `API reliability testing microservices software engineering`
- `API specification conformance testing OpenAPI`
- `REST API specification mining inference`
- `web API code examples documentation empirical`
- `RESTler stateful REST API fuzzing ICSE 2019 DOI`
- `site:dblp.org RESTler ICSE 2019`
- `site:ndss-symposium.org "Generating API Parameter Security Rules"`
- `"Generating API Parameter Security Rules with LLM" DOI`

## Useful result counts and screening

OpenAlex keyword `meta.count` values were often extremely broad (for example, `REST API testing` produced more than 100,000 full-text-ranked matches), so raw counts were not interpreted as relevant-paper counts. The broad pass inspected the top eight results per query; focused passes inspected the top seven or eight. Candidates were screened for direct API relevance, scholarly identity, technical contribution, venue credibility, and coverage diversity. Near-duplicate preprint/published versions were collapsed to the peer-reviewed version when available.

## Link and metadata checks

- Every candidate was queried by DOI in OpenAlex and Crossref (except arXiv aliases, for which Crossref returned 404).
- PDF candidates were tested with redirect-following HTTP HEAD requests. Only HTTP 200 responses with a PDF content type are counted as verified direct PDFs.
- HTTP 403 publisher endpoints are retained as publisher-reported PDF candidates but explicitly marked inaccessible from this environment.
- A wrong/inconsistent NDSS DOI suffix (`...230465`) appeared in one deposited/indexed record. The catalog uses `10.14722/NDSS.2025.23465`, supported by the official NDSS file naming and arXiv record; the discrepancy remains documented.

## Limitations and failed/inaccessible searches

- Semantic Scholar batch verification was rate-limited (HTTP 429); no unbounded retry was attempted.
- DBLP DOI query syntax did not yield usable batch matches, so DBLP is not claimed as a verification source for all rows.
- ACM PDF endpoints generally returned HTTP 403 to automated HEAD requests even where OpenAlex classified the URL as open access.
- One HAL endpoint and one Springer PDF URL resolved to HTML rather than PDF; they are not counted as verified direct PDF links.
- ScienceDirect and some publisher PDFs returned 403; paywalls and authentication were not bypassed.
- Google Scholar was not used because no supported official API was available.
- Retraction/correction checking was limited to visible queried metadata; no dedicated retraction database was available.
