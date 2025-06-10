"""Generate unified mapping of amendment authors to parties for 2024."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict

import pandas as pd
from unidecode import unidecode

from party_service import fetch_party
from senado_party_service import fetch_senator_parties
from wikipedia_party_service import fetch_party_from_wikipedia



logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _normalize(name: str) -> str:
    """Return a normalized uppercase identifier for *name*."""
    return unidecode(name).upper().strip()


def load_local_mappings() -> Dict[str, str]:
    """Load mappings from bundled JSON files."""
    mapping: Dict[str, str] = {}

    # Deputies from dadosabertos
    with (DATA_DIR / "deputados_dados_partidos.json").open(
        "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
    for item in data.get("dados", []):
        mapping[_normalize(item.get("nome", ""))] = item.get("siglaPartido", "")

    # Deputies and senators scraped earlier
    with (DATA_DIR / "deputados_senadores.json").open(
        "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
    for item in data.get("deputados", []):
        mapping[_normalize(item.get("nome", ""))] = item.get("partido", "")
    for item in data.get("senadores", []):
        mapping[_normalize(item.get("nome", ""))] = item.get("partido", "")

    # Previous manual mapping
    with (DATA_DIR / "autor_partido.json").open("r", encoding="utf-8") as f:
        data = json.load(f)
    for name, party in data.items():
        if party and party != "UNKNOWN":
            mapping[_normalize(name)] = party
    return mapping


def build_party_mapping(names: list[str]) -> Dict[str, str]:
    """Return mapping from author name to party using 2024 data."""
    mapping = load_local_mappings()

    # Add current senator parties (fresh data)
    try:
        mapping.update(fetch_senator_parties())
    except Exception as exc:  # pragma: no cover - network issues
        logger.warning("Failed to fetch senator parties: %s", exc)

    final: Dict[str, str] = {}
    for name in names:
        norm = _normalize(name)
        party = mapping.get(norm)
        wiki_party = None
        if not party or party == "UNKNOWN":
            wiki_party = fetch_party_from_wikipedia(name)
            if wiki_party:
                party = wiki_party
                mapping[norm] = party
        if (not party or party == "UNKNOWN") and not wiki_party:
            party = fetch_party(name)
            if party and party != "UNKNOWN":

        if not party:
            party = fetch_party(name)
            if party:

                mapping[norm] = party
        final[name] = party or "UNKNOWN"
    return final


def main() -> None:
    """Generate JSON mapping for amendment authors."""
    logging.basicConfig(level=logging.WARNING)
    emendas_path = DATA_DIR / "emendas_por_favorecido.csv"
    df = pd.read_csv(emendas_path)
    authors = sorted(df["Nome do Autor da Emenda"].unique())
    mapping = build_party_mapping(authors)

    out_path = DATA_DIR / "autor_partido_2024.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated {out_path} with {len(mapping)} entries.")


if __name__ == "__main__":
    main()
