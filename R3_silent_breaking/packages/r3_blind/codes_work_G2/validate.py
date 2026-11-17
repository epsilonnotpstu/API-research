"""Validate the deliverable as data; never execute supplied item code."""
import csv
import re
from collections import Counter
from pathlib import Path

with Path("items.csv").open(newline="") as stream:
    expected = [row["item_id"] for row in csv.DictReader(stream)]
with Path("codes_G2.csv").open(newline="") as stream:
    reader = csv.DictReader(stream)
    assert reader.fieldnames == ["item_id", "observable_change", "change_kind", "client_impact", "contract_specified", "confidence", "locators", "rationale"]
    rows = list(reader)
assert [row["item_id"] for row in rows] == expected
kinds = set("STATUS_OR_ERROR_MAPPING INPUT_STRICTER INPUT_LOOSER DEFAULT_OR_OPTIONALITY RESPONSE_CONTENT RESPONSE_SHAPE HEADER_OR_MEDIA_TYPE AUTHZ_OR_AUTH SIDE_EFFECT_OR_STATE ORDERING_PAGINATION_LIMITS OTHER".split())
for row in rows:
    assert None not in row and all(value for value in row.values()), row["item_id"]
    assert row["observable_change"] in {"YES", "NO", "UNCLEAR"}
    assert row["confidence"] in {"1", "2", "3"}
    if row["observable_change"] == "YES":
        assert row["change_kind"] in kinds
        assert row["client_impact"] in {"BREAKING", "COMPATIBLE", "UNCLEAR"}
        assert row["contract_specified"] in {"SPECIFIED", "UNSPECIFIED"}
    else:
        assert all(row[key] == "NA" for key in ("change_kind", "client_impact", "contract_specified"))
    assert len(row["rationale"].split()) <= 40, row["item_id"]
    if row["contract_specified"] == "SPECIFIED":
        assert "/contract/" in row["locators"], row["item_id"]
    for locator in row["locators"].split(";"):
        filename, line = locator.rsplit(":", 1)
        path = Path(filename)
        assert path.parts[0] == row["item_id"]
        assert "/after/" in filename or "/contract/" in filename or path.name == "diff.patch"
        lines = path.read_text().splitlines()
        assert 1 <= int(line) <= len(lines), (row["item_id"], locator, len(lines))
        if path.name == "diff.patch":
            print(f"{row['item_id']}:{line}: {lines[int(line) - 1]}")
print("Rows:", len(rows))
print("Observable:", dict(Counter(row["observable_change"] for row in rows)))
print("Impact:", dict(Counter(row["client_impact"] for row in rows)))
print("Empty contract folders:", ", ".join(item for item in expected if not any((Path(item) / "contract").rglob("*.*"))))
print("UNCLEAR:", ", ".join(row["item_id"] for row in rows if row["observable_change"] == "UNCLEAR"))
