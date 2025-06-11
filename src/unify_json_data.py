from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from unidecode import unidecode

JSON_DIR = Path(__file__).resolve().parent.parent / "json_data"


def _normalize(name: str) -> str:
    """Return normalized uppercase identifier for *name*."""
    return unidecode(name).upper().strip()


def _add_entry(mapping: Dict[str, str], canonical: Dict[str, str], name: str, party: str) -> None:
    """Add name/party pair to mapping if *party* is valid."""
    if not party or party == "UNKNOWN":
        return
    norm = _normalize(name)
    if norm not in mapping:
        canonical[norm] = name
        mapping[norm] = party


def _load_file(path: Path, mapping: Dict[str, str], canonical: Dict[str, str]) -> None:
    """Load data from *path* and update *mapping*."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        if "dados" in data:
            for item in data.get("dados", []):
                _add_entry(mapping, canonical, item.get("nome", ""), item.get("siglaPartido", ""))
        if any(key in data for key in ("deputados", "senadores")):
            for item in data.get("deputados", []):
                _add_entry(mapping, canonical, item.get("nome", ""), item.get("partido", ""))
            for item in data.get("senadores", []):
                _add_entry(mapping, canonical, item.get("nome", ""), item.get("partido", ""))
        else:
            for name, party in data.items():
                _add_entry(mapping, canonical, name, party)


def build_mapping() -> Dict[str, str]:
    """Return unified mapping from politician name to party."""
    mapping: Dict[str, str] = {}
    canonical: Dict[str, str] = {}

    for path in sorted(JSON_DIR.glob("*.json")):
        _load_file(path, mapping, canonical)

    return {canonical[n]: mapping[n] for n in sorted(mapping)}


def main() -> None:
    mapping = build_mapping()
    out_path = JSON_DIR / "politicos_partidos_unificado.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated {out_path} with {len(mapping)} entries.")


if __name__ == "__main__":
    main()
