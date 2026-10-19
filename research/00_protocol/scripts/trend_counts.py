#!/usr/bin/env python3
"""Per-area publication counts by year from OpenAlex (title+abstract match, CS field 17).
Counts are rough volume indicators only: keyword matching over-/under-counts."""
import csv, datetime as dt, json, os, sys, time, requests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AREAS = [
 ("REST/Web API testing & fuzzing", '("REST API" OR RESTful OR "web API") AND (testing OR fuzzing OR "test generation")'),
 ("GraphQL", 'GraphQL'),
 ("gRPC / RPC APIs", 'gRPC'),
 ("API security & authorization", '(API) AND (vulnerability OR "access control" OR authorization) AND (REST OR "web API" OR GraphQL)'),
 ("OpenAPI / API specification", '(OpenAPI OR Swagger OR "API specification")'),
 ("API evolution / breaking changes", '("breaking change" OR "breaking changes" OR "API evolution" OR "API deprecation")'),
 ("API documentation", '("API documentation")'),
 ("API misuse", '("API misuse" OR "API misuses")'),
 ("API recommendation", '("API recommendation")'),
 ("LLM tool use / function calling", '("tool learning" OR "tool use" OR "function calling" OR "tool-augmented") AND ("language model" OR LLM)'),
 ("Model Context Protocol", '"Model Context Protocol"'),
 ("Microservice APIs", 'microservice AND API'),
 ("API anomaly / monitoring", 'API AND ("anomaly detection" OR observability OR monitoring) AND (traffic OR microservice OR REST)'),
]
rows = []
for name, q in AREAS:
    url = "https://api.openalex.org/works"
    p = {"filter": f"title_and_abstract.search:{q},primary_topic.field.id:17,from_publication_date:2018-01-01,to_publication_date:2026-12-31",
         "group_by": "publication_year"}
    r = requests.get(url, params=p, timeout=60); r.raise_for_status()
    g = {int(x["key"]): x["count"] for x in r.json()["group_by"]}
    rows.append({"area": name, "query": q, **{str(y): g.get(y, 0) for y in range(2018, 2027)}})
    print(name, [g.get(y, 0) for y in range(2018, 2027)], flush=True)
    time.sleep(1)
out = os.path.join(ROOT, "00_protocol", "trend_counts_openalex.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(rows)
print("retrieved", dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "->", out)
