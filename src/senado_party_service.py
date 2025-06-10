"""Utilities to fetch Brazilian senators' party information."""
from __future__ import annotations

import logging
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from unidecode import unidecode

logger = logging.getLogger(__name__)

SENADORES_URL = "https://legis.senado.leg.br/dadosabertos/senador/lista/atual"


def fetch_senator_parties() -> dict[str, str]:
    """Return mapping of senator normalized name to party acronym."""
    req = Request(SENADORES_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    parties: dict[str, str] = {}
    for parlamentar in root.findall("./Parlamentares/Parlamentar"):
        ident = parlamentar.find("IdentificacaoParlamentar")
        if ident is None:
            continue
        name = ident.findtext("NomeParlamentar")
        party = ident.findtext("SiglaPartidoParlamentar")
        if not name or not party:
            continue
        norm = unidecode(name).upper()
        parties[norm] = party
    return parties
