import csv
import json
from urllib.parse import quote
from urllib.request import Request, urlopen
from time import sleep
from unidecode import unidecode
from pathlib import Path


API_URL = "https://dadosabertos.camara.leg.br/api/v2/deputados?nome={name}"


def fetch_party(name: str) -> str:
    """Return party acronym for a deputy name using Câmara API.

    If no result is found, try cleaning common titles and querying again.
    """
    def query(query_name: str) -> str | None:
        url = API_URL.format(name=quote(query_name))
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as resp:
            data = json.load(resp)
        deputados = data.get("dados", [])
        if deputados:
            return deputados[0].get("siglaPartido")
        return None

    # First attempt with provided name
    party = query(name)
    if party:
        return party

    # Fallback: remove titles like 'PROF.', 'PASTOR', etc.
    clean = unidecode(name)
    tokens = [t for t in clean.replace('.', ' ').split() if t.upper() not in {"PROF", "PROFESSOR", "DEPUTADO", "PASTOR", "SENADOR"}]
    if tokens:
        party = query(" ".join(tokens))
        if party:
            return party
    return "UNKNOWN"


def main(csv_path: str) -> None:
    path = Path(csv_path)
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    unique_names = sorted({row["Nome do Autor da Emenda"] for row in rows})
    name_to_party = {}
    for name in unique_names:
        party = fetch_party(name)
        name_to_party[name] = party
        # Be gentle with the API
        sleep(0.2)

    for row in rows:
        row["SG_PARTIDO"] = name_to_party.get(row["Nome do Autor da Emenda"], "UNKNOWN")

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add SG_PARTIDO column to emendas CSV")
    parser.add_argument("csv_path", help="Path to emendas_por_favorecido.csv")

    args = parser.parse_args()
    main(args.csv_path)
