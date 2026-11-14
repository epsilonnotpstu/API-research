"""Read one EMB fixed Authorization header at runtime, never include values in errors."""
from pathlib import Path
import sys

import yaml


def main():
    try:
        config = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
        roles = [role for role in config["auth"] if role["name"] == sys.argv[2]]
        if len(roles) != 1:
            raise ValueError
        headers = roles[0]["fixedHeaders"]
        # This harness supports the fixed-header fixtures used by these SUTs only.
        if len(headers) != 1 or headers[0]["name"].lower() != "authorization":
            raise ValueError
        name, value = headers[0]["name"], headers[0]["value"]
        if not isinstance(value, str) or not value or any(c in name + value for c in "\r\n"):
            raise ValueError
    except Exception:
        raise SystemExit("Cannot load a single fixed Authorization header for the selected role") from None
    print(name + ": " + value)


if __name__ == "__main__":
    main()
