from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from time import sleep
from urllib.parse import quote
from urllib.request import Request, urlopen

from unidecode import unidecode

logger = logging.getLogger(__name__)

API_URL = "https://dadosabertos.camara.leg.br/api/v2/deputados?nome={name}"


def _query_api(query_name: str) -> str | None:
    """Query Camara API for a deputy and return party acronym if found."""
    url = API_URL.format(name=quote(query_name))
    logger.info("GET %s", url)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as resp:
        data = json.load(resp)
    deputados = data.get("dados", [])
    if deputados:
        party = deputados[0].get("siglaPartido")
        logger.info("Party for '%s' -> %s", query_name, party)
        return party
    logger.info("No match for '%s'", query_name)
    return None


def fetch_party(name: str) -> str:
    """Return party acronym for a deputy name using Camara API."""
    # First attempt with provided name
    party = _query_api(name)
    if party:
        return party

    # Fallback: remove common titles
    clean = unidecode(name)
    tokens = [
        t
        for t in clean.replace(".", " ").split()
        if t.upper() not in {"PROF", "PROFESSOR", "DEPUTADO", "PASTOR", "SENADOR"}
    ]
    if tokens:
        logger.info("Retrying without titles: %s", " ".join(tokens))
        party = _query_api(" ".join(tokens))
        if party:
            return party
    return "UNKNOWN"


def add_parties_to_csv(csv_path: str) -> int:
    """Add SG_PARTIDO column to CSV file. Return number of rows processed."""
    path = Path(csv_path)
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    unique_names = sorted({row["Nome do Autor da Emenda"] for row in rows})
    name_to_party: dict[str, str] = {}
    for name in unique_names:
        logger.info("Fetching party for '%s'", name)
        party = fetch_party(name)
        name_to_party[name] = party
        sleep(0.2)  # be gentle with the API

    for row in rows:
        row["SG_PARTIDO"] = name_to_party.get(row["Nome do Autor da Emenda"], "UNKNOWN")

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)