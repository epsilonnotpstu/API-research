#!/usr/bin/env python3
"""Append a search_log.csv row for a search run through a non-scripted tool
(Consensus MCP, WebSearch). Results are summarised in the note field.

Usage: log_manual.py <source> "<query>" <retrieved> "<note>" [--pass 1] [--total N]
"""
import argparse, csv, datetime as dt, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG = os.path.join(ROOT, "00_protocol", "search_log.csv")
FIELDS = ["query_id", "pass", "retrieval_utc", "source", "query", "filters",
          "sort", "total_results", "retrieved", "request_url", "note"]

ap = argparse.ArgumentParser()
ap.add_argument("source")
ap.add_argument("query")
ap.add_argument("retrieved")
ap.add_argument("note")
ap.add_argument("--pass", dest="pas", default="1")
ap.add_argument("--total", default="Not reported")
a = ap.parse_args()

with open(LOG, encoding="utf-8") as fh:
    n = sum(1 for r in csv.DictReader(fh) if r["source"] == a.source)
with open(LOG, "a", newline="", encoding="utf-8") as fh:
    csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL).writerow({
        "query_id": f"{a.source[:2].upper()}{n + 1:03d}", "pass": a.pas,
        "retrieval_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source": a.source, "query": a.query, "filters": "none", "sort": "relevance (tool default)",
        "total_results": a.total, "retrieved": a.retrieved, "request_url": "n/a (MCP/agent tool)",
        "note": a.note})
