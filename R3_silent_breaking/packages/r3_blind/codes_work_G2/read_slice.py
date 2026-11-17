"""Read numbered slices of supplied files without importing item code."""
import sys
from pathlib import Path

for request in sys.argv[1:]:
    item, area, basename, start, end = request.split(":")
    root = Path(item) / area
    assert root.parts[0].startswith("B") and area in {"before", "after", "contract"}
    matches = list(root.rglob(basename))
    for path in matches:
        assert path.is_relative_to(root)
        lines = path.read_text().splitlines()
        print(f"\n{path}")
        for index in range(int(start) - 1, min(int(end), len(lines))):
            print(f"{index + 1}: {lines[index]}")
