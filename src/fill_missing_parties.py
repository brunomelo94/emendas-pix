from __future__ import annotations

import json
from pathlib import Path

from wikipedia_party_service import fetch_party_from_wikipedia

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    path = DATA_DIR / "autor_partido_2024.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for name, party in list(data.items()):
        if party == "UNKNOWN":
            wiki_party = fetch_party_from_wikipedia(name)
            if wiki_party:
                data[name] = wiki_party
                updated += 1

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Updated {updated} entries")


if __name__ == "__main__":
    main()
