# API research landscape

## Scope and evidence boundary

This independent mapping contains 60 unique papers discovered and screened on 2026-10-19. It covers research on software APIs, with an emphasis on 2023–2026 and selected older foundations. Claims below are based on bibliographic metadata and abstracts only; no item is represented as fully read.

## Identified domains

### API testing, automated testing, and fuzzing

The largest cluster concerns stateful request-sequence generation, dependency inference, realistic input generation, automated oracles, property-based testing, reinforcement learning, and LLM assistance. RESTler (C018), EvoMaster (C017), and QuickREST (C016) are foundational; RESTest (C003), Morest (C004), ARTE (C005), AGORA (C006), KAT (C009), and LlamaRestTest (C013) show the move toward richer constraints, feedback, and learned models. Contemporary work increasingly asks whether gains transfer from benchmarks to live industrial systems.

### API security and authorization

This cluster covers mass-assignment vulnerability detection, web-to-mobile inconsistencies, and security-rule generation for API misuse. C019 and C020 offer a tight pair on automated mass-assignment analysis; C021 is an older security foundation; C022 connects LLMs to executable validation of parameter-security rules. Authorization-specific and business-logic vulnerability testing remains underrepresented.

### Specification inference, generation, and validation

Work spans inter-parameter dependency models (C023), carving specifications from UI tests (C024), extracting contracts from HTML (C025), path-sensitive inference (C026), cross-API recommendation (C027), and LLM-assisted OpenAPI recovery (C028). A major current direction is combining noisy documentation evidence with code/execution evidence so generated contracts remain faithful.

### Documentation and usability

Representative work detects documentation smells and code/documentation directive inconsistencies, synthesizes usage examples, mines crowd knowledge, and adds interactivity or natural-language generation. C029–C034 show that documentation quality is both a static consistency problem and a human usability problem.

### Evolution and breaking changes

This area ranges from foundational classifications of Java and REST API change (C040–C041) to ecosystem-scale studies of Maven and npm (C038, C037), behavioral changes (C036), and microservice evolution practice (C035). A contemporary shift is from signature compatibility alone toward behavioral and operational compatibility.

### GraphQL and alternative API architectures

C042 maps the literature; C043 and C044 test GraphQL with fuzzing/property-based methods; C045 compares REST and GraphQL experimentally; C046 discusses engineering tradeoffs. GraphQL-specific authorization, cost attacks, and production reliability deserve deeper coverage.

### Discovery, recommendation, composition, and reuse

C047–C051 address diversity, compatibility, knowledge graphs, popularity bias, and multi-objective composition. The current challenge is moving from offline registry benchmarks to dynamic, explainable, and bias-aware recommendation under changing APIs.

### Microservice reliability, testing, and observability

This cluster covers API-pattern detection, industrial tracing, anomaly datasets, service-level fault injection, and a recent systematic review (C052–C056). The literature connects API behavior to distributed traces, logs, metrics, and resilience experiments, but comparatively few studies unify contract violations with operational telemetry.

### LLM- and AI-assisted API engineering

C057–C060 cover API selection/invocation, migration, OpenAPI completion, and specification generation. The key contemporary questions are correctness, hallucination control, evaluation leakage, tool/API churn, and whether smaller specialized models can outperform general LLM prompting.

## Important contemporary directions

- Stateful, dependency-aware API testing that combines specifications, runtime feedback, and learned guidance.
- Test-oracle generation and realistic value synthesis, not merely request generation.
- Behavioral breaking-change detection and compatibility analysis for microservices and package ecosystems.
- LLM-assisted specification recovery, API migration, and tool use with executable validation.
- Security testing for mass assignment, parameter misuse, authorization, and state-dependent logic.
- GraphQL-specific fuzzing and property-based testing.
- Trace/log/metric datasets and fault injection for microservice API reliability.
- Recommendation systems that address diversity, compatibility, explanation, and popularity bias.

## Areas requiring deeper investigation

- Broken object-level authorization, tenant isolation, and API business-logic flaws.
- API gateways, rate limiting, denial-of-service resilience, and cost-aware performance testing.
- gRPC, event-driven APIs, AsyncAPI, WebSockets, and schema evolution beyond REST/GraphQL.
- API observability studies that explicitly tie runtime anomalies to contract or version changes.
- Replication studies and shared benchmarks for comparing REST/GraphQL fuzzers.
- Human factors: learnability, developer productivity, and accessibility of API documentation.
- Retractions/corrections: no retraction was surfaced by the queried metadata, but a dedicated Crossmark/Retraction Watch audit was not available and should be performed for a final corpus.
