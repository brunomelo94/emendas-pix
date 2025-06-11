from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from unidecode import unidecode
import pandas as pd

JSON_DIR = Path(__file__).resolve().parent.parent / "json_data"
DATA_CSV = Path(__file__).resolve().parent.parent / "data" / "emendas_por_favorecido.csv"


STOP_WORDS = {
    "DEP",
    "DEPUTADO",
    "SEN",
    "SENADOR",
    "PROF",
    "PROFESSOR",
    "PASTOR",
    "CAPITAO",
    "CAP",
    "DR",
    "DRA",
}


def _normalize(name: str) -> str:
    """Return normalized uppercase identifier for *name* without titles."""
    text = unidecode(name).replace(".", " ").upper()
    tokens = [t for t in text.split() if t not in STOP_WORDS]
    return " ".join(tokens).strip()


def _add_entry(mapping: Dict[str, str], canonical: Dict[str, str], name: str, party: str) -> None:
    """Add name/party pair to mapping if *party* is valid."""
    if not party or party == "UNKNOWN":
        return
    norm = _normalize(name)
    if norm not in mapping:
        canonical[norm] = name
        mapping[norm] = party

    tokens = norm.split()
    if tokens and tokens[0] == "JUNIOR":
        alt = " ".join(tokens[1:])
        if alt and alt not in mapping:
            canonical[alt] = name
            mapping[alt] = party


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


def build_mapping() -> tuple[Dict[str, str], Dict[str, str]]:
    """Return (canonical_map, normalized_map) built from bundled JSON files."""
    mapping: Dict[str, str] = {}
    canonical: Dict[str, str] = {}

    for path in sorted(JSON_DIR.glob("*.json")):
        _load_file(path, mapping, canonical)

    canonical_map = {canonical[n]: mapping[n] for n in sorted(mapping)}
    return canonical_map, mapping


def _build_dataset_map(normalized_map: Dict[str, str]) -> Dict[str, str]:
    """Return mapping using names exactly as in emendas_por_favorecido.csv."""
    df = pd.read_csv(DATA_CSV)
    dataset_map: Dict[str, str] = {}
    for name in sorted(df["Nome do Autor da Emenda"].unique()):
        norm = _normalize(name)
        party = normalized_map.get(norm)
        if not party and norm.startswith("JUNIOR "):
            party = normalized_map.get(norm.split(" ", 1)[1])
        if party:
            dataset_map[name] = party
    return dataset_map


def main() -> None:
    canonical_map, normalized_map = build_mapping()

    out_path = JSON_DIR / "politicos_partidos_unificado.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(canonical_map, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated {out_path} with {len(canonical_map)} entries.")

    dataset_map = _build_dataset_map(normalized_map)
    csv_out = JSON_DIR / "politicos_partidos_padronizado.json"
    with csv_out.open("w", encoding="utf-8") as f:
        json.dump(dataset_map, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated {csv_out} with {len(dataset_map)} entries.")


if __name__ == "__main__":
    main()
