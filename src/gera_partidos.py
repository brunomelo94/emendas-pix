#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def fetch_deputies_current():
    """
    Fetch all deputies of the 57th legislature (2023–2027),
    paging 100 per request and sorting by name.
    """
    mapping = {}
    page = 1
    while True:
        params = {
            "idLegislatura": 57,
            "itens": 100,
            "pagina": page,
            "ordenarPor": "nome",
            "ordem": "ASC"               # must be 'ordem', not 'ordenar' :contentReference[oaicite:0]{index=0}
        }
        resp = requests.get(
            "https://dadosabertos.camara.leg.br/api/v2/deputados",
            params=params,
            headers={"Accept": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json().get("dados", [])
        if not data:
            break
        for d in data:
            mapping[d["nome"].upper()] = d["siglaPartido"]
        page += 1

    return mapping

def fetch_senators():
    """
    Fetch all senators currently in exercise from the official JSON feed.
    """
    url = "https://www12.senado.leg.br/dados-abertos/conjuntos/senadores-em-exercicio.json"
    resp = requests.get(url)
    resp.raise_for_status()
    items = resp.json().get("List", {}).get("Parlamentares", [])

    mapping = {}
    for item in items:
        ident = item.get("IdentificacaoParlamentar", {})
        nome = ident.get("NomeParlamentar", "").upper()
        partido = ident.get("SiglaPartido", "")
        if nome:
            mapping[nome] = partido
    return mapping  # feed URL: 

def main():
    deputies = fetch_deputies_current()  # uses idLegislatura=57 :contentReference[oaicite:2]{index=2}
    senators = fetch_senators()
    full_map = {**deputies, **senators}

    with open("partidos_2023_2024.json", "w", encoding="utf-8") as f:
        json.dump(full_map, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated partidos_2023_2024.json with {len(full_map)} entries.")

if __name__ == "__main__":
    main()
